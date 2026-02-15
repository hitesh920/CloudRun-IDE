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


class CodeExecutor:
    """Executes code in isolated Docker containers."""
    
    def __init__(self):
        self.active_executions: Dict[str, Any] = {}
    
    async def execute_code_stream(
        self,
        language: str,
        code: str,
        stdin: Optional[str] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        install_packages: Optional[List[str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute code and stream output. Optionally install packages first."""
        if language in NO_DOCKER_LANGUAGES:
            async for msg in self._handle_html_preview(language, code):
                yield msg
            return
        
        execution_id = generate_execution_id()
        needs_install = bool(install_packages and language in ("python", "nodejs"))
        
        print(f"🚀 Starting execution {execution_id} for {language}" + 
              (f" (installing: {', '.join(install_packages)})" if needs_install else ""))
        
        is_valid, error_msg = validate_code(code, language)
        if not is_valid:
            yield {"type": "error", "content": error_msg, "timestamp": get_timestamp()}
            return
        
        if needs_install:
            yield {
                "type": "install_start",
                "content": f"📦 Installing: {', '.join(install_packages)}...",
                "packages": install_packages,
                "timestamp": get_timestamp(),
            }
        else:
            yield {"type": "status", "content": "Starting execution...", "timestamp": get_timestamp()}
        
        container = None
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir = temp_dir_obj.name
        
        try:
            file_path = self._prepare_code_file(temp_dir, language, code)
            
            if files:
                for file_data in files:
                    self._prepare_additional_file(temp_dir, file_data.get('name'), file_data.get('content', ''))
            
            if needs_install:
                command = self._prepare_install_and_run_command(
                    language, file_path, code, install_packages, bool(stdin)
                )
            else:
                command = self._prepare_command(language, file_path, code)
                if stdin and language != "ubuntu":
                    command = ["sh", "-c", f"{' '.join(command)} < /workspace/input.txt"]
            
            if stdin:
                self._prepare_stdin_file(temp_dir, stdin)
            
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
                yield {"type": "error", "content": "Failed to create Docker container. Is Docker running?", "timestamp": get_timestamp()}
                return
            
            self.active_executions[execution_id] = container
            await self._copy_files_to_container(container, temp_dir)
            
            started = await loop.run_in_executor(
                _thread_pool, lambda: get_docker_manager().start_container(container)
            )
            if not started:
                await loop.run_in_executor(_thread_pool, lambda: get_docker_manager().remove_container(container))
                yield {"type": "error", "content": "Failed to start container", "timestamp": get_timestamp()}
                return
            
            yield {
                "type": "status",
                "content": "Installing packages..." if needs_install else "Running...",
                "timestamp": get_timestamp(),
            }
            
            output_lines = []
            timed_out = False
            timeout = settings.MAX_EXECUTION_TIME * (3 if needs_install else 1)
            
            try:
                async for line in self._stream_logs_async(container, timeout=timeout):
                    output_lines.append(line)
                    
                    msg_type = "stdout"
                    if needs_install and "▶▶▶ RUNNING CODE ▶▶▶" in line:
                        msg_type = "install_complete"
                    elif needs_install and "❌ INSTALL FAILED" in line:
                        msg_type = "install_error"
                    
                    yield {"type": msg_type, "content": line, "timestamp": get_timestamp()}
            except asyncio.TimeoutError:
                timed_out = True
                yield {"type": "error", "content": f"Execution timed out after {timeout}s", "timestamp": get_timestamp()}
            
            if not timed_out:
                try:
                    result = await loop.run_in_executor(
                        _thread_pool, lambda: get_docker_manager().wait_container(container, timeout=2)
                    )
                    exit_code = result.get("StatusCode", 0)
                except Exception:
                    exit_code = -1
            else:
                exit_code = -1
            
            # Detect missing deps only on normal (non-install) runs
            if exit_code != 0 and not timed_out and not needs_install:
                full_output = ''.join(output_lines)
                missing_dep = dependency_detector.detect_missing_dependency(full_output, language)
                if missing_dep:
                    package_manager, package_name = missing_dep
                    install_cmd = dependency_detector.get_install_command(language, package_manager, package_name)
                    yield {
                        "type": "dependency",
                        "content": f"Missing dependency detected: {package_name}",
                        "package_manager": package_manager,
                        "package_name": package_name,
                        "install_command": install_cmd,
                        "timestamp": get_timestamp(),
                    }
            
            if exit_code == 0:
                yield {"type": "complete", "content": "Execution completed successfully", "timestamp": get_timestamp()}
            elif timed_out:
                yield {"type": "complete", "content": "Execution timed out", "timestamp": get_timestamp()}
            else:
                yield {"type": "complete", "content": f"Execution failed with exit code {exit_code}", "timestamp": get_timestamp()}
            
        except Exception as e:
            print(f"❌ Execution error: {e}")
            yield {"type": "error", "content": f"Execution error: {str(e)}", "timestamp": get_timestamp()}
        finally:
            if container:
                try:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(_thread_pool, lambda: get_docker_manager().cleanup_container(container))
                except Exception as e:
                    print(f"⚠️ Cleanup error: {e}")
            self.active_executions.pop(execution_id, None)
            try:
                temp_dir_obj.cleanup()
            except Exception:
                pass
            print(f"✅ Execution completed for {language} ({execution_id})")
    
    async def _handle_html_preview(self, language: str, code: str) -> AsyncGenerator[Dict[str, Any], None]:
        yield {"type": "status", "content": "Rendering HTML preview...", "timestamp": get_timestamp()}
        yield {"type": "html_preview", "content": code, "timestamp": get_timestamp()}
        yield {"type": "complete", "content": "HTML rendered successfully", "timestamp": get_timestamp()}
    
    async def _stream_logs_async(self, container, timeout=None) -> AsyncGenerator[str, None]:
        loop = asyncio.get_event_loop()
        queue = asyncio.Queue()
        timeout = timeout or settings.MAX_EXECUTION_TIME
        
        def _read_logs():
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
                try: container.stop(timeout=1)
                except Exception: pass
                raise asyncio.TimeoutError()
            try:
                line = await asyncio.wait_for(queue.get(), timeout=remaining)
                if line is None:
                    break
                yield line
            except asyncio.TimeoutError:
                try: container.stop(timeout=1)
                except Exception: pass
                raise
    
    def stop_execution(self, execution_id: str) -> bool:
        if execution_id not in self.active_executions:
            return False
        container = self.active_executions[execution_id]
        get_docker_manager().cleanup_container(container)
        del self.active_executions[execution_id]
        return True
    
    def _prepare_code_file(self, temp_dir, language, code):
        extension = FILE_EXTENSIONS.get(language, ".txt")
        if language == "java":
            filename = f"{extract_java_classname(code)}.java"
        else:
            filename = f"main{extension}"
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        return file_path
    
    def _prepare_additional_file(self, temp_dir, filename, content):
        file_path = os.path.join(temp_dir, sanitize_filename(filename))
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _prepare_stdin_file(self, temp_dir, stdin):
        path = os.path.join(temp_dir, "input.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(stdin)
        return path
    
    async def _copy_files_to_container(self, container, temp_dir):
        import tarfile, io
        def _do_copy():
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                for fn in os.listdir(temp_dir):
                    tar.add(os.path.join(temp_dir, fn), arcname=fn)
            tar_stream.seek(0)
            container.put_archive('/workspace', tar_stream)
        await asyncio.get_event_loop().run_in_executor(_thread_pool, _do_copy)
    
    def _prepare_command(self, language, file_path, code):
        if language not in EXECUTION_COMMANDS:
            return ["echo", "Unsupported language"]
        command_template = EXECUTION_COMMANDS[language]
        filename = os.path.basename(file_path)
        command = []
        for part in command_template:
            part = part.replace("{file}", f"/workspace/{filename}")
            if language == "java":
                part = part.replace("{classname}", extract_java_classname(code))
            if language == "ubuntu":
                part = part.replace("{code}", code)
            command.append(part)
        return command
    
    def _prepare_install_and_run_command(self, language, file_path, code, packages, has_stdin):
        """Build install-then-run command with PROPER error separation.
        
        Key fix: install and run use if/then/else so install failure
        doesn't bleed into code failure and vice versa.
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
            return self._prepare_command(language, file_path, code)
        
        if has_stdin:
            run_cmd += " < /workspace/input.txt"
        
        # FIXED: Proper if/then/else — install and code errors are separate
        script = f'''
{install_cmd} 2>&1
INSTALL_RC=$?
if [ $INSTALL_RC -ne 0 ]; then
    echo ""
    echo "❌ INSTALL FAILED — check package name and try again"
    exit $INSTALL_RC
fi
echo ""
echo "✅ Installation complete!"
echo "▶▶▶ RUNNING CODE ▶▶▶"
echo ""
{run_cmd}
'''
        
        return ["sh", "-c", script.strip()]
    
    def get_code_template(self, language):
        return CODE_TEMPLATES.get(language, "")


code_executor = CodeExecutor()
