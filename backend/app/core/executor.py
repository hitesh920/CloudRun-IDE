"""
CloudRun IDE - Code Executor
Handles code execution in Docker containers with streaming output.
Supports package installation with live output streaming.
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

# Install commands per language
INSTALL_COMMANDS_MAP = {
    "python": "pip install --no-cache-dir {packages}",
    "nodejs": "cd /workspace && npm install {packages}",
}


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
        install_packages: Optional[List[str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute code and stream output in real-time.
        
        If install_packages is provided, installs them first (with network)
        then runs the code — all in a single container with live streaming.
        """
        # Handle HTML preview (no Docker needed)
        if language in NO_DOCKER_LANGUAGES:
            async for msg in self._handle_html_preview(language, code):
                yield msg
            return
        
        execution_id = generate_execution_id()
        needs_install = bool(install_packages and language in INSTALL_COMMANDS_MAP)
        
        print(f"🚀 Starting execution {execution_id} for {language}" + 
              (f" (installing: {', '.join(install_packages)})" if needs_install else ""))
        
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
        
        # Show install status if installing
        if needs_install:
            pkgs_str = ", ".join(install_packages)
            yield {
                "type": "install_start",
                "content": f"📦 Installing: {pkgs_str}...",
                "packages": install_packages,
                "timestamp": get_timestamp(),
            }
        else:
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
            
            # Build command — with or without install prefix
            if needs_install:
                command = self._prepare_install_and_run_command(
                    language, file_path, code, install_packages, bool(stdin)
                )
            else:
                command = self._prepare_command(language, file_path, code)
                # Handle stdin redirect for normal execution
                if stdin and language != "ubuntu":
                    command = ["sh", "-c", f"{' '.join(command)} < /workspace/input.txt"]
            
            # Prepare stdin file if provided
            if stdin:
                self._prepare_stdin_file(temp_dir, stdin)
            
            # Create container — enable network if installing packages
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                _thread_pool,
                lambda: get_docker_manager().create_container(
                    execution_id=execution_id,
                    language=language,
                    command=command,
                    working_dir="/workspace",
                    enable_network=needs_install,
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
            
            if needs_install:
                yield {
                    "type": "status",
                    "content": "Installing packages...",
                    "timestamp": get_timestamp(),
                }
            else:
                yield {
                    "type": "status",
                    "content": "Running...",
                    "timestamp": get_timestamp(),
                }
            
            # Stream logs with timeout (longer for install+run)
            output_lines = []
            timed_out = False
            timeout = settings.MAX_EXECUTION_TIME * (2 if needs_install else 1)
            
            try:
                async for line in self._stream_logs_async(container, timeout=timeout):
                    output_lines.append(line)
                    
                    # Detect install → run transition
                    msg_type = "stdout"
                    if needs_install and "▶▶▶ RUNNING CODE ▶▶▶" in line:
                        msg_type = "install_complete"
                    elif needs_install and "❌ INSTALL FAILED" in line:
                        msg_type = "install_error"
                    
                    yield {
                        "type": msg_type,
                        "content": line,
                        "timestamp": get_timestamp(),
                    }
            except asyncio.TimeoutError:
                timed_out = True
                yield {
                    "type": "error",
                    "content": f"Execution timed out after {timeout} seconds",
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
            
            # Check for missing dependencies if execution failed (and not already installing)
            if exit_code != 0 and not timed_out and not needs_install:
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
    
    async def _stream_logs_async(self, container, timeout=None) -> AsyncGenerator[str, None]:
        """Stream container logs asynchronously with timeout."""
        loop = asyncio.get_event_loop()
        queue = asyncio.Queue()
        timeout = timeout or settings.MAX_EXECUTION_TIME
        
        def _read_logs():
            """Read logs in a thread and put them in the queue."""
            try:
                for line in container.logs(stream=True, follow=True):
                    decoded = line.decode('utf-8', errors='replace')
                    loop.call_soon_threadsafe(queue.put_nowait, decoded)
            except Exception:
                pass
            loop.call_soon_threadsafe(queue.put_nowait, None)
        
        loop.run_in_executor(_thread_pool, _read_logs)
        
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
    
    def _prepare_install_and_run_command(
        self, 
        language: str, 
        file_path: str, 
        code: str,
        packages: List[str],
        has_stdin: bool,
    ) -> list:
        """Build a command that installs packages then runs code.
        
        Creates a shell script that:
        1. Installs packages with live output
        2. Prints a separator marker
        3. Runs the user's code
        """
        filename = os.path.basename(file_path)
        pkgs_str = " ".join(packages)
        
        if language == "python":
            install_cmd = f"pip install --no-cache-dir {pkgs_str}"
            run_cmd = f"python -u /workspace/{filename}"
        elif language == "nodejs":
            install_cmd = f"cd /workspace && npm install {pkgs_str}"
            run_cmd = f"node /workspace/{filename}"
        else:
            # Fallback — no install support for this language
            return self._prepare_command(language, file_path, code)
        
        # Add stdin redirect if needed
        if has_stdin:
            run_cmd += " < /workspace/input.txt"
        
        # Build shell script: install → marker → run
        # The marker helps frontend detect the transition
        script = (
            f'echo "📦 Installing: {pkgs_str}" && '
            f'echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━" && '
            f'{install_cmd} 2>&1 && '
            f'echo "" && '
            f'echo "✅ Installation complete!" && '
            f'echo "▶▶▶ RUNNING CODE ▶▶▶" && '
            f'echo "" && '
            f'{run_cmd}'
        )
        
        # If install fails, show error
        full_script = (
            f'({install_cmd} 2>&1) && '
            f'echo "" && '
            f'echo "✅ Installation complete!" && '
            f'echo "▶▶▶ RUNNING CODE ▶▶▶" && '
            f'echo "" && '
            f'{run_cmd} || '
            f'(echo "" && echo "❌ INSTALL FAILED — check package name and try again")'
        )
        
        return ["sh", "-c", full_script]
    
    def get_code_template(self, language: str) -> str:
        """Get starter code template for a language."""
        return CODE_TEMPLATES.get(language, "")


# Global executor instance
code_executor = CodeExecutor()
