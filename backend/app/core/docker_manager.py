"""
CloudRun IDE - Docker Manager
Handles Docker container lifecycle for code execution.
"""

import docker
from docker.errors import DockerException, APIError, ImageNotFound
from typing import Optional, Dict, Any
import time

from app.config import settings
from app.utils.constants import DOCKER_IMAGES
from app.utils.helpers import generate_container_name


class DockerManager:
    """Manages Docker containers for code execution."""
    
    def __init__(self):
        """Initialize Docker client."""
        try:
            # Try to connect using unix socket directly
            self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
            self.client.ping()
            print("✅ Docker client connected successfully")
        except DockerException as e:
            print(f"❌ Docker connection failed: {e}")
            # Fallback to from_env()
            try:
                self.client = docker.from_env()
                self.client.ping()
                print("✅ Docker client connected via from_env()")
            except Exception as e2:
                print(f"❌ All Docker connection methods failed: {e2}")
                raise
    
    def pull_image(self, language: str) -> bool:
        """
        Pull Docker image for specified language if not present.
        
        Args:
            language: Programming language
            
        Returns:
            True if image is ready, False otherwise
        """
        if language not in DOCKER_IMAGES:
            print(f"❌ Unsupported language: {language}")
            return False
        
        image_name = DOCKER_IMAGES[language]
        
        try:
            # Check if image already exists
            self.client.images.get(image_name)
            print(f"✅ Image already exists: {image_name}")
            return True
        except ImageNotFound:
            print(f"📥 Pulling image: {image_name}")
            try:
                self.client.images.pull(image_name)
                print(f"✅ Image pulled successfully: {image_name}")
                return True
            except APIError as e:
                print(f"❌ Failed to pull image {image_name}: {e}")
                return False
    
    def create_container(
        self,
        execution_id: str,
        language: str,
        command: Optional[list] = None,
        working_dir: str = "/workspace",
        environment: Optional[Dict[str, str]] = None,
    ) -> Optional[Any]:
        """
        Create a Docker container for code execution.
        
        Args:
            execution_id: Unique execution identifier
            language: Programming language
            command: Command to execute
            working_dir: Working directory inside container
            environment: Environment variables
            
        Returns:
            Container object or None if failed
        """
        if not self.pull_image(language):
            return None
        
        image_name = DOCKER_IMAGES[language]
        container_name = generate_container_name(execution_id, language)
        
        # Resource limits
        resource_limits = {
            "mem_limit": settings.MAX_MEMORY,
            "cpu_quota": settings.MAX_CPU_QUOTA,
            "cpu_period": settings.MAX_CPU_PERIOD,
            "network_disabled": True,  # Disabled by default
        }
        
        try:
            container = self.client.containers.create(
                image=image_name,
                command=command,
                name=container_name,
                working_dir=working_dir,
                environment=environment or {},
                detach=True,
                stdout=True,
                stderr=True,
                remove=False,  # We'll remove manually after getting logs
                **resource_limits,
            )
            
            print(f"✅ Container created: {container_name}")
            return container
            
        except APIError as e:
            print(f"❌ Failed to create container: {e}")
            return None
    
    def start_container(self, container: Any) -> bool:
        """
        Start a Docker container.
        
        Args:
            container: Container object
            
        Returns:
            True if started successfully, False otherwise
        """
        try:
            container.start()
            print(f"✅ Container started: {container.name}")
            return True
        except APIError as e:
            print(f"❌ Failed to start container: {e}")
            return False
    
    def wait_container(self, container: Any, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Wait for container to finish execution.
        
        Args:
            container: Container object
            timeout: Maximum time to wait (uses settings if None)
            
        Returns:
            Dictionary with status code and error if timeout
        """
        timeout = timeout or settings.MAX_EXECUTION_TIME
        
        try:
            result = container.wait(timeout=timeout)
            return result
        except Exception as e:
            print(f"⚠️ Container execution timeout or error: {e}")
            return {"StatusCode": -1, "Error": str(e)}
    
    def get_logs(self, container: Any) -> tuple[str, str]:
        """
        Get stdout and stderr from container.
        
        Args:
            container: Container object
            
        Returns:
            Tuple of (stdout, stderr)
        """
        try:
            logs = container.logs(stdout=True, stderr=True, stream=False)
            # Docker combines stdout and stderr, we'll return as single output
            output = logs.decode('utf-8', errors='replace')
            return output, ""
        except Exception as e:
            print(f"❌ Failed to get logs: {e}")
            return "", str(e)
    
    def get_logs_stream(self, container: Any):
        """
        Stream logs from container in real-time.
        
        Args:
            container: Container object
            
        Yields:
            Log lines as they become available
        """
        try:
            for line in container.logs(stream=True, follow=True):
                yield line.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"❌ Failed to stream logs: {e}")
            yield f"Error streaming logs: {e}"
    
    def stop_container(self, container: Any, timeout: int = 5) -> bool:
        """
        Stop a running container.
        
        Args:
            container: Container object
            timeout: Seconds to wait before killing
            
        Returns:
            True if stopped successfully
        """
        try:
            container.stop(timeout=timeout)
            print(f"✅ Container stopped: {container.name}")
            return True
        except Exception as e:
            print(f"❌ Failed to stop container: {e}")
            return False
    
    def remove_container(self, container: Any, force: bool = True) -> bool:
        """
        Remove a container.
        
        Args:
            container: Container object
            force: Force removal even if running
            
        Returns:
            True if removed successfully
        """
        try:
            container.remove(force=force)
            print(f"✅ Container removed: {container.name}")
            return True
        except Exception as e:
            print(f"❌ Failed to remove container: {e}")
            return False
    
    def cleanup_container(self, container: Any) -> bool:
        """
        Stop and remove a container.
        
        Args:
            container: Container object
            
        Returns:
            True if cleaned up successfully
        """
        self.stop_container(container)
        return self.remove_container(container)
    
    def copy_to_container(self, container: Any, local_path: str, container_path: str) -> bool:
        """
        Copy files to container.
        
        Args:
            container: Container object
            local_path: Local file/directory path
            container_path: Destination path in container
            
        Returns:
            True if copied successfully
        """
        try:
            import tarfile
            import io
            
            # Create tar archive
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                tar.add(local_path, arcname='.')
            
            tar_stream.seek(0)
            container.put_archive(container_path, tar_stream)
            print(f"✅ Files copied to container: {container_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to copy files to container: {e}")
            return False
    
    def get_container_stats(self, container: Any) -> Optional[Dict[str, Any]]:
        """
        Get container resource usage stats.
        
        Args:
            container: Container object
            
        Returns:
            Stats dictionary or None
        """
        try:
            stats = container.stats(stream=False)
            return stats
        except Exception as e:
            print(f"❌ Failed to get container stats: {e}")
            return None


# Global Docker manager instance
docker_manager = DockerManager()
