"""
CloudRun IDE - Code Executor
Handles code execution in Docker containers with streaming output.
"""

import os
import tempfile
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator, List
from concurrent.futures import ThreadPoolExecutor

from app.core.docker_manager import get_docker_manager
from app.services.dependency_detector import dependency_detector
from app.utils.constants import (
    EXECUTION_COMMANDS, FILE_EXTENSIONS, CODE_TEMPLATES, 
    DOCKER_IMAGES, NO_DOCKER_LANGUAGES,
)
from app.utils.helpers import (
    generate_execution_id,
    extract_java_classname,
    validate_code,
    get_timestamp,
    sanitize_filename,
)
from app.config import settings

# Thread pool for blocking Docker operations
_thread_pool = ThreadPoolExecutor(max_workers=4)


class CodeExecutor:
    """Executes code in isolated Docker containers."""
    
    def __init__(self):
        """Initialize the executor."""
        self.active_executions: Dict[str, Any] = {}
    
    async def execute_code_stream(
        self,
        language: str,
        code: str,
        stdin: Optional[str] = None,
        files: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute code and stream output in real-time.
        Yields output messages as they become available.
        """
        # Handle HTML preview (no Docker needed)
        if language in NO_DOCKER_LANGUAGES:
            async for msg in self._handle_html_preview(language, code):
                yield msg
            return
        
        execution_id = generate_execution_id()
        print(f"🚀 Starting execution {execution_id} for {language}")
        
        # Validate code
        is_valid, error_msg = validate_code(code, language)
        if not is_valid:
            print(f"❌ Validation failed: {error_msg}")
            yield {
                "type": "error",
                "content": error_msg,
                "timestamp": get_timestamp(),
            }
            return
        
        yield {
            "type": "status",
            "content": "Starting execution...",
            "timestamp": get_timestamp(),
        }
        
        container = None
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir = temp_dir_obj.name
        
        try:
            # Prepare main code file
            file_path = self._prepare_code_file(temp_dir, language, code)
            
            # Prepare additional files if provided
            if files:
                for file_data in files:
                    self._prepare_additional_file(
                        temp_dir,
                        file_data.get('name'),
                        file_data.get('content', '')
                    )
            
            # Prepare command
            command = self._prepare_command(language, file_path, code)
            
            # Prepare stdin file if provided
            if stdin:
                self._prepare_stdin_file(temp_dir, stdin)
                if language != "ubuntu":
                    command = ["sh", "-c", f"{' '.join(command)} < /workspace/input.txt"]
            
            # Create container (run in thread pool to not block)
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                _thread_pool,
                lambda: get_docker_manager().create_container(
                    execution_id=execution_id,
                    language=language,
                    command=command,
                    working_dir="/workspace",
                )
            )
            
            if not container:
                yield {
                    "type": "error",
                    "content": "Failed to create Docker container. Is Docker running?",
                    "timestamp": get_timestamp(),
                }
                return
            
            self.active_executions[execution_id] = container
            
            # Copy files to container
            await self._copy_files_to_container(container, temp_dir)
            
            # Start container
            started = await loop.run_in_executor(
                _thread_pool,
                lambda: get_docker_manager().start_container(container)
            )
            
            if not started:
                await loop.run_in_executor(
                    _thread_pool,
                    lambda: get_docker_manager().remove_container(container)
                )
                yield {
                    "type": "error",
                    "content": "Failed to start container",
                    "timestamp": get_timestamp(),
                }
                return
            
            yield {
                "type": "status",
                "content": "Running...",
                "timestamp": get_timestamp(),
            }
            
            # Stream logs asynchronously with timeout
            output_lines = []
            timed_out = False
            
            try:
                async for line in self._stream_logs_async(container):
                    output_lines.append(line)
                    yield {
                        "type": "stdout",
                        "content": line,
                        "timestamp": get_timestamp(),
                    }
            except asyncio.TimeoutError:
                timed_out = True
                yield {
                    "type": "error",
                    "content": f"Execution timed out after {settings.MAX_EXECUTION_TIME} seconds",
                    "timestamp": get_timestamp(),
                }
            
            # Get exit code
            if not timed_out:
                try:
                    result = await loop.run_in_executor(
                        _thread_pool,
                        lambda: get_docker_manager().wait_container(container, timeout=2)
                    )
                    exit_code = result.get("StatusCode", 0)
                except Exception:
                    exit_code = -1
            else:
                exit_code = -1
            
            # Check for missing dependencies if execution failed
            if exit_code != 0 and not timed_out:
                full_output = ''.join(output_lines)
                missing_dep = dependency_detector.detect_missing_dependency(
                    full_output, language
                )
                
                if missing_dep:
                    package_manager, package_name = missing_dep
                    install_cmd = dependency_detector.get_install_command(
                        language, package_manager, package_name
                    )
                    
                    yield {
                        "type": "dependency",
                        "content": f"Missing dependency detected: {package_name}",
                        "package_manager": package_manager,
                        "package_name": package_name,
                        "install_command": install_cmd,
                        "timestamp": get_timestamp(),
                    }
            
            # Send completion status
            if exit_code == 0:
                yield {
                    "type": "complete",
                    "content": "Execution completed successfully",
                    "timestamp": get_timestamp(),
                }
            elif timed_out:
                yield {
                    "type": "complete",
                    "content": "Execution timed out",
                    "timestamp": get_timestamp(),
                }
            else:
                yield {
                    "type": "complete",
                    "content": f"Execution failed with exit code {exit_code}",
                    "timestamp": get_timestamp(),
                }
            
        except Exception as e:
            print(f"❌ Execution error: {e}")
            yield {
                "type": "error",
                "content": f"Execution error: {str(e)}",
                "timestamp": get_timestamp(),
            }
        
        finally:
            # Always cleanup
            if container:
                try:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        _thread_pool,
                        lambda: get_docker_manager().cleanup_container(container)
                    )
                except Exception as e:
                    print(f"⚠️ Cleanup error: {e}")
            
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            try:
                temp_dir_obj.cleanup()
            except Exception:
                pass
            
            print(f"✅ Execution completed for {language} ({execution_id})")
    
    async def _handle_html_preview(self, language: str, code: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle HTML preview without Docker."""
        print(f"🌐 HTML preview requested")
        
        yield {
            "type": "status",
            "content": "Rendering HTML preview...",
            "timestamp": get_timestamp(),
        }
        
        # Send HTML content as a special preview message
        yield {
            "type": "html_preview",
            "content": code,
            "timestamp": get_timestamp(),
        }
        
        yield {
            "type": "complete",
            "content": "HTML rendered successfully",
            "timestamp": get_timestamp(),
        }
    
    async def _stream_logs_async(self, container) -> AsyncGenerator[str, None]:
        """Stream container logs asynchronously with timeout."""
        loop = asyncio.get_event_loop()
        queue = asyncio.Queue()
        
        def _read_logs():
            """Read logs in a thread and put them in the queue."""
            try:
                for line in container.logs(stream=True, follow=True):
                    decoded = line.decode('utf-8', errors='replace')
                    loop.call_soon_threadsafe(queue.put_nowait, decoded)
            except Exception:
                pass
            loop.call_soon_threadsafe(queue.put_nowait, None)
        
        # Start log reader in thread
        loop.run_in_executor(_thread_pool, _read_logs)
        
        # Read from queue with timeout
        timeout = settings.MAX_EXECUTION_TIME
        start_time = asyncio.get_event_loop().time()
        
        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            remaining = timeout - elapsed
            
            if remaining <= 0:
                try:
                    container.stop(timeout=1)
                except Exception:
                    pass
                raise asyncio.TimeoutError("Execution timed out")
            
            try:
                line = await asyncio.wait_for(queue.get(), timeout=remaining)
                if line is None:
                    break
                yield line
            except asyncio.TimeoutError:
                try:
                    container.stop(timeout=1)
                except Exception:
                    pass
                raise
    
    def stop_execution(self, execution_id: str) -> bool:
        """Stop a running execution."""
        if execution_id not in self.active_executions:
            return False
        
        container = self.active_executions[execution_id]
        get_docker_manager().cleanup_container(container)
        del self.active_executions[execution_id]
        return True
    
    def _prepare_code_file(self, temp_dir: str, language: str, code: str) -> str:
        """Write code to a temporary file."""
        extension = FILE_EXTENSIONS.get(language, ".txt")
        
        if language == "java":
            classname = extract_java_classname(code)
            filename = f"{classname}.java"
        else:
            filename = f"main{extension}"
        
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return file_path
    
    def _prepare_additional_file(self, temp_dir: str, filename: str, content: str):
        """Write an additional file to temporary directory."""
        safe_filename = sanitize_filename(filename)
        file_path = os.path.join(temp_dir, safe_filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _prepare_stdin_file(self, temp_dir: str, stdin: str) -> str:
        """Write stdin to a file."""
        stdin_path = os.path.join(temp_dir, "input.txt")
        
        with open(stdin_path, 'w', encoding='utf-8') as f:
            f.write(stdin)
        
        return stdin_path
    
    async def _copy_files_to_container(self, container: Any, temp_dir: str):
        """Copy all files from temp directory to container."""
        import tarfile
        import io
        
        def _do_copy():
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    tar.add(file_path, arcname=filename)
            
            tar_stream.seek(0)
            container.put_archive('/workspace', tar_stream)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(_thread_pool, _do_copy)
    
    def _prepare_command(self, language: str, file_path: str, code: str) -> list:
        """Prepare execution command for the language."""
        if language not in EXECUTION_COMMANDS:
            return ["echo", "Unsupported language"]
        
        command_template = EXECUTION_COMMANDS[language]
        filename = os.path.basename(file_path)
        
        command = []
        for part in command_template:
            part = part.replace("{file}", f"/workspace/{filename}")
            
            if language == "java":
                classname = extract_java_classname(code)
                part = part.replace("{classname}", classname)
            
            if language == "ubuntu":
                part = part.replace("{code}", code)
            
            command.append(part)
        
        return command
    
    def get_code_template(self, language: str) -> str:
        """Get starter code template for a language."""
        return CODE_TEMPLATES.get(language, "")


# Global executor instance
code_executor = CodeExecutor()
