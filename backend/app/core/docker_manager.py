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
            self.client = docker.from_env()
            self.client.ping()
            version = self.client.version()
            print(f"✅ Docker connected: API v{version.get('ApiVersion', 'unknown')}, Engine v{version.get('Version', 'unknown')}")
        except Exception as e:
            print(f"❌ Docker connection failed: {e}")
            raise
    
    def pull_image(self, language: str) -> bool:
        """Pull Docker image for specified language if not present."""
        if language not in DOCKER_IMAGES:
            print(f"❌ Unsupported language: {language}")
            return False
        
        image_name = DOCKER_IMAGES[language]
        
        try:
            self.client.images.get(image_name)
            return True
        except ImageNotFound:
            print(f"📥 Pulling image: {image_name}")
            try:
                self.client.images.pull(image_name)
                print(f"✅ Image pulled: {image_name}")
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
        """Create a Docker container for code execution."""
        if not self.pull_image(language):
            return None
        
        image_name = DOCKER_IMAGES[language]
        container_name = generate_container_name(execution_id, language)
        
        try:
            container = self.client.containers.create(
                image=image_name,
                command=command,
                name=container_name,
                working_dir=working_dir,
                environment=environment or {},
                detach=True,
                mem_limit=settings.MAX_MEMORY,
                cpu_quota=settings.MAX_CPU_QUOTA,
                cpu_period=settings.MAX_CPU_PERIOD,
                network_disabled=True,
            )
            
            print(f"✅ Container created: {container_name}")
            return container
            
        except APIError as e:
            print(f"❌ Failed to create container: {e}")
            return None
    
    def start_container(self, container: Any) -> bool:
        """Start a Docker container."""
        try:
            container.start()
            print(f"✅ Container started: {container.name}")
            return True
        except APIError as e:
            print(f"❌ Failed to start container: {e}")
            return False
    
    def wait_container(self, container: Any, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Wait for container to finish execution."""
        timeout = timeout or settings.MAX_EXECUTION_TIME
        
        try:
            result = container.wait(timeout=timeout)
            return result
        except Exception as e:
            print(f"⚠️ Container timeout/error: {e}")
            return {"StatusCode": -1, "Error": str(e)}
    
    def get_logs(self, container: Any) -> tuple:
        """Get stdout and stderr from container."""
        try:
            logs = container.logs(stdout=True, stderr=True, stream=False)
            output = logs.decode('utf-8', errors='replace')
            return output, ""
        except Exception as e:
            print(f"❌ Failed to get logs: {e}")
            return "", str(e)
    
    def get_logs_stream(self, container: Any):
        """Stream logs from container in real-time."""
        try:
            for line in container.logs(stream=True, follow=True):
                yield line.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"❌ Failed to stream logs: {e}")
            yield f"Error streaming logs: {e}"
    
    def stop_container(self, container: Any, timeout: int = 3) -> bool:
        """Stop a running container."""
        try:
            container.stop(timeout=timeout)
            print(f"✅ Container stopped: {container.name}")
            return True
        except Exception as e:
            print(f"⚠️ Failed to stop container (may already be stopped): {e}")
            return False
    
    def remove_container(self, container: Any, force: bool = True) -> bool:
        """Remove a container."""
        try:
            container.remove(force=force)
            print(f"✅ Container removed: {container.name}")
            return True
        except Exception as e:
            print(f"⚠️ Failed to remove container: {e}")
            return False
    
    def cleanup_container(self, container: Any) -> bool:
        """Stop and remove a container."""
        self.stop_container(container)
        return self.remove_container(container)
    
    def copy_to_container(self, container: Any, local_path: str, container_path: str) -> bool:
        """Copy files to container."""
        try:
            import tarfile
            import io
            
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                tar.add(local_path, arcname='.')
            
            tar_stream.seek(0)
            container.put_archive(container_path, tar_stream)
            return True
            
        except Exception as e:
            print(f"❌ Failed to copy files to container: {e}")
            return False
    
    def cleanup_orphaned_containers(self) -> int:
        """Remove any leftover cloudrun containers."""
        count = 0
        try:
            containers = self.client.containers.list(
                filters={"name": "cloudrun_"},
                all=True
            )
            for c in containers:
                try:
                    c.remove(force=True)
                    count += 1
                except Exception:
                    pass
        except Exception:
            pass
        return count


# Global Docker manager instance - initialized lazily
_docker_manager = None

def get_docker_manager():
    """Get or create the global Docker manager instance."""
    global _docker_manager
    if _docker_manager is None:
        _docker_manager = DockerManager()
    return _docker_manager
