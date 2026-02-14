"""
CloudRun IDE - Code Executor
Handles code execution in Docker containers with multi-file support and dependency detection.
"""

import os
import tempfile
from typing import Optional, Dict, Any, AsyncGenerator, List
import asyncio

from app.core.docker_manager import get_docker_manager
from app.services.dependency_detector import dependency_detector
from app.utils.constants import EXECUTION_COMMANDS, FILE_EXTENSIONS, CODE_TEMPLATES, DOCKER_IMAGES
from app.utils.helpers import (
    generate_execution_id,
    extract_java_classname,
    validate_code,
    get_timestamp,
    sanitize_filename,
)


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
        
        Args:
            language: Programming language
            code: Source code to execute (main file)
            stdin: Standard input for the program
            files: Additional files [{name: str, content: str}]
            
        Yields:
            Output messages as they become available
        """
        execution_id = generate_execution_id()
        
        # Validate code
        is_valid, error_msg = validate_code(code, language)
        if not is_valid:
            yield {
                "type": "error",
                "content": error_msg,
                "timestamp": get_timestamp(),
            }
            return
        
        # Send status: starting
        yield {
            "type": "status",
            "content": "Starting execution...",
            "timestamp": get_timestamp(),
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
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
                stdin_file = None
                if stdin:
                    stdin_file = self._prepare_stdin_file(temp_dir, stdin)
                    # Modify command to redirect stdin
                    if language != "ubuntu":
                        command = ["sh", "-c", f"{' '.join(command)} < /workspace/input.txt"]
                
                # Create container
                container = get_docker_manager().create_container(
                    execution_id=execution_id,
                    language=language,
                    command=command,
                    working_dir="/workspace",
                )
                
                if not container:
                    yield {
                        "type": "error",
                        "content": "Failed to create Docker container",
                        "timestamp": get_timestamp(),
                    }
                    return
                
                self.active_executions[execution_id] = container
                
                # Copy all files to container
                await self._copy_files_to_container(container, temp_dir)
                
                # Start container
                if not get_docker_manager().start_container(container):
                    get_docker_manager().remove_container(container)
                    yield {
                        "type": "error",
                        "content": "Failed to start container",
                        "timestamp": get_timestamp(),
                    }
                    return
                
                # Stream logs
                yield {
                    "type": "status",
                    "content": "Running...",
                    "timestamp": get_timestamp(),
                }
                
                # Collect output for dependency detection
                output_lines = []
                
                # Stream output
                for line in get_docker_manager().get_logs_stream(container):
                    output_lines.append(line)
                    yield {
                        "type": "stdout",
                        "content": line,
                        "timestamp": get_timestamp(),
                    }
                
                # Wait for completion
                result = get_docker_manager().wait_container(container, timeout=1)
                
                # Get exit code
                exit_code = result.get("StatusCode", 0)
                
                # Check for missing dependencies if execution failed
                if exit_code != 0:
                    full_output = ''.join(output_lines)
                    missing_dep = dependency_detector.detect_missing_dependency(
                        full_output, 
                        language
                    )
                    
                    if missing_dep:
                        package_manager, package_name = missing_dep
                        install_cmd = dependency_detector.get_install_command(
                            language,
                            package_manager,
                            package_name
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
                else:
                    yield {
                        "type": "complete",
                        "content": f"Execution failed with exit code {exit_code}",
                        "timestamp": get_timestamp(),
                    }
                
                # Cleanup
                get_docker_manager().cleanup_container(container)
                del self.active_executions[execution_id]
                
            except Exception as e:
                yield {
                    "type": "error",
                    "content": f"Execution error: {str(e)}",
                    "timestamp": get_timestamp(),
                }
                
                if execution_id in self.active_executions:
                    container = self.active_executions[execution_id]
                    get_docker_manager().cleanup_container(container)
                    del self.active_executions[execution_id]
    
    async def install_dependency(
        self,
        language: str,
        package_manager: str,
        package_name: str,
    ) -> Dict[str, Any]:
        """
        Install a dependency in a container.
        
        Args:
            language: Programming language
            package_manager: Package manager (pip, npm)
            package_name: Package to install
            
        Returns:
            Installation result
        """
        execution_id = generate_execution_id()
        
        try:
            # Get install command
            install_cmd = dependency_detector.get_install_command(
                language,
                package_manager,
                package_name
            )
            
            if not install_cmd:
                return {
                    "success": False,
                    "message": f"Unsupported package manager: {package_manager}",
                }
            
            # Pull image first
            get_docker_manager().pull_image(language)
            image_name = DOCKER_IMAGES.get(language, "python:3.11-slim")
            
            # Create container with network enabled for installation
            container = get_docker_manager().client.containers.create(
                image=image_name,
                command=["sh", "-c", install_cmd],
                name=f"cloudrun_install_{execution_id}",
                detach=True,
                network_disabled=False,  # Enable network for installation
                mem_limit="512m",
            )
            
            # Start and wait
            container.start()
            result = container.wait(timeout=60)
            
            # Get logs
            logs = container.logs().decode('utf-8', errors='replace')
            
            # Cleanup
            container.remove(force=True)
            
            success = result.get("StatusCode", 1) == 0
            
            return {
                "success": success,
                "message": logs if success else "Installation failed",
                "package": package_name,
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Installation error: {str(e)}",
            }
    
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
        
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                tar.add(file_path, arcname=filename)
        
        tar_stream.seek(0)
        container.put_archive('/workspace', tar_stream)
    
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
