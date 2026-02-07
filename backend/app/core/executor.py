"""
CloudRun IDE - Code Executor
Handles code execution in Docker containers.
"""

import os
import tempfile
from typing import Optional, Dict, Any, AsyncGenerator
import asyncio

from app.core.docker_manager import docker_manager
from app.utils.constants import EXECUTION_COMMANDS, FILE_EXTENSIONS, CODE_TEMPLATES
from app.utils.helpers import (
    generate_execution_id,
    extract_java_classname,
    validate_code,
    get_timestamp,
)


class CodeExecutor:
    """Executes code in isolated Docker containers."""
    
    def __init__(self):
        """Initialize the executor."""
        self.active_executions: Dict[str, Any] = {}
    
    async def execute_code(
        self,
        language: str,
        code: str,
        stdin: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute code in a Docker container.
        
        Args:
            language: Programming language
            code: Source code to execute
            stdin: Standard input for the program
            
        Returns:
            Execution result dictionary
        """
        # Generate execution ID
        execution_id = generate_execution_id()
        
        # Validate code
        is_valid, error_msg = validate_code(code, language)
        if not is_valid:
            return {
                "execution_id": execution_id,
                "status": "error",
                "stdout": "",
                "stderr": error_msg,
                "exit_code": 1,
            }
        
        # Create temporary directory for code files
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Prepare code file
                file_path = self._prepare_code_file(temp_dir, language, code)
                
                # Prepare execution command
                command = self._prepare_command(language, file_path, code)
                
                # Prepare stdin file if provided
                stdin_file = None
                if stdin:
                    stdin_file = self._prepare_stdin_file(temp_dir, stdin)
                
                # Create container
                container = docker_manager.create_container(
                    execution_id=execution_id,
                    language=language,
                    command=command,
                    working_dir="/workspace",
                )
                
                if not container:
                    return {
                        "execution_id": execution_id,
                        "status": "error",
                        "stdout": "",
                        "stderr": "Failed to create Docker container",
                        "exit_code": 1,
                    }
                
                # Store active execution
                self.active_executions[execution_id] = container
                
                # Copy files to container
                await self._copy_files_to_container(container, temp_dir, stdin_file)
                
                # Start container
                if not docker_manager.start_container(container):
                    docker_manager.remove_container(container)
                    return {
                        "execution_id": execution_id,
                        "status": "error",
                        "stdout": "",
                        "stderr": "Failed to start container",
                        "exit_code": 1,
                    }
                
                # Wait for execution to complete
                result = docker_manager.wait_container(container)
                
                # Get logs
                stdout, stderr = docker_manager.get_logs(container)
                
                # Cleanup
                docker_manager.cleanup_container(container)
                del self.active_executions[execution_id]
                
                # Determine status
                exit_code = result.get("StatusCode", -1)
                if exit_code == -1:
                    status = "timeout"
                elif exit_code == 0:
                    status = "completed"
                else:
                    status = "error"
                
                return {
                    "execution_id": execution_id,
                    "status": status,
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": exit_code,
                }
                
            except Exception as e:
                # Cleanup on error
                if execution_id in self.active_executions:
                    container = self.active_executions[execution_id]
                    docker_manager.cleanup_container(container)
                    del self.active_executions[execution_id]
                
                return {
                    "execution_id": execution_id,
                    "status": "error",
                    "stdout": "",
                    "stderr": f"Execution error: {str(e)}",
                    "exit_code": 1,
                }
    
    async def execute_code_stream(
        self,
        language: str,
        code: str,
        stdin: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute code and stream output in real-time.
        
        Args:
            language: Programming language
            code: Source code to execute
            stdin: Standard input for the program
            
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
                # Prepare code file
                file_path = self._prepare_code_file(temp_dir, language, code)
                
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
                container = docker_manager.create_container(
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
                
                # Copy files to container
                await self._copy_files_to_container(container, temp_dir, stdin_file)
                
                # Start container
                if not docker_manager.start_container(container):
                    docker_manager.remove_container(container)
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
                
                # Stream output
                for line in docker_manager.get_logs_stream(container):
                    yield {
                        "type": "stdout",
                        "content": line,
                        "timestamp": get_timestamp(),
                    }
                
                # Wait for completion
                result = docker_manager.wait_container(container, timeout=1)
                
                # Send completion status
                exit_code = result.get("StatusCode", 0)
                if exit_code == 0:
                    yield {
                        "type": "status",
                        "content": "Execution completed successfully",
                        "timestamp": get_timestamp(),
                    }
                else:
                    yield {
                        "type": "status",
                        "content": f"Execution failed with exit code {exit_code}",
                        "timestamp": get_timestamp(),
                    }
                
                # Cleanup
                docker_manager.cleanup_container(container)
                del self.active_executions[execution_id]
                
            except Exception as e:
                yield {
                    "type": "error",
                    "content": f"Execution error: {str(e)}",
                    "timestamp": get_timestamp(),
                }
                
                if execution_id in self.active_executions:
                    container = self.active_executions[execution_id]
                    docker_manager.cleanup_container(container)
                    del self.active_executions[execution_id]
    
    def stop_execution(self, execution_id: str) -> bool:
        """
        Stop a running execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            True if stopped successfully
        """
        if execution_id not in self.active_executions:
            return False
        
        container = self.active_executions[execution_id]
        docker_manager.cleanup_container(container)
        del self.active_executions[execution_id]
        return True
    
    def _prepare_code_file(self, temp_dir: str, language: str, code: str) -> str:
        """
        Write code to a temporary file.
        
        Args:
            temp_dir: Temporary directory path
            language: Programming language
            code: Source code
            
        Returns:
            Path to the code file
        """
        extension = FILE_EXTENSIONS.get(language, ".txt")
        
        # Special handling for Java (needs specific filename)
        if language == "java":
            classname = extract_java_classname(code)
            filename = f"{classname}.java"
        else:
            filename = f"main{extension}"
        
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return file_path
    
    def _prepare_stdin_file(self, temp_dir: str, stdin: str) -> str:
        """
        Write stdin to a file.
        
        Args:
            temp_dir: Temporary directory path
            stdin: Input content
            
        Returns:
            Path to stdin file
        """
        stdin_path = os.path.join(temp_dir, "input.txt")
        
        with open(stdin_path, 'w', encoding='utf-8') as f:
            f.write(stdin)
        
        return stdin_path
    
    async def _copy_files_to_container(
        self, 
        container: Any, 
        temp_dir: str, 
        stdin_file: Optional[str] = None
    ):
        """
        Copy code and stdin files to container.
        
        Args:
            container: Docker container
            temp_dir: Temporary directory with files
            stdin_file: Path to stdin file (optional)
        """
        import tarfile
        import io
        
        # Create tar archive with all files
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            # Add all files from temp_dir
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                tar.add(file_path, arcname=filename)
        
        tar_stream.seek(0)
        container.put_archive('/workspace', tar_stream)
    
    def _prepare_command(self, language: str, file_path: str, code: str) -> list:
        """
        Prepare execution command for the language.
        
        Args:
            language: Programming language
            file_path: Path to code file
            code: Source code (for inline execution)
            
        Returns:
            Command list for Docker
        """
        if language not in EXECUTION_COMMANDS:
            return ["echo", "Unsupported language"]
        
        command_template = EXECUTION_COMMANDS[language]
        filename = os.path.basename(file_path)
        
        # Replace placeholders
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
        """
        Get starter code template for a language.
        
        Args:
            language: Programming language
            
        Returns:
            Code template string
        """
        return CODE_TEMPLATES.get(language, "")


# Global executor instance
code_executor = CodeExecutor()
