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

NETWORK_ENABLED_LANGUAGES = {"ubuntu"}


class DockerManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.client.ping()
            version = self.client.version()
            print(f"✅ Docker connected: API v{version.get('ApiVersion', 'unknown')}, Engine v{version.get('Version', 'unknown')}")
        except Exception as e:
            print(f"❌ Docker connection failed: {e}")
            raise

    def pull_image(self, language: str) -> bool:
        if language not in DOCKER_IMAGES:
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

    def create_container(self, execution_id, language, command=None, working_dir="/workspace", environment=None, enable_network=False):
        if not self.pull_image(language):
            return None
        image_name = DOCKER_IMAGES[language]
        container_name = generate_container_name(execution_id, language)
        disable_network = not (language in NETWORK_ENABLED_LANGUAGES or enable_network)
        try:
            container = self.client.containers.create(
                image=image_name, command=command, name=container_name,
                working_dir=working_dir, environment=environment or {},
                detach=True, mem_limit=settings.MAX_MEMORY,
                cpu_quota=settings.MAX_CPU_QUOTA, cpu_period=settings.MAX_CPU_PERIOD,
                network_disabled=disable_network,
            )
            net_label = "ON" if not disable_network else "OFF"
            print(f"✅ Container created: {container_name} (network: {net_label})")
            return container
        except APIError as e:
            print(f"❌ Failed to create container: {e}")
            return None

    def start_container(self, container):
        try:
            container.start()
            print(f"✅ Container started: {container.name}")
            return True
        except APIError as e:
            print(f"❌ Failed to start container: {e}")
            return False

    def wait_container(self, container, timeout=None):
        timeout = timeout or settings.MAX_EXECUTION_TIME
        try:
            return container.wait(timeout=timeout)
        except Exception as e:
            return {"StatusCode": -1, "Error": str(e)}

    def get_logs(self, container):
        try:
            logs = container.logs(stdout=True, stderr=True, stream=False)
            return logs.decode("utf-8", errors="replace"), ""
        except Exception as e:
            return "", str(e)

    def get_logs_stream(self, container):
        try:
            for line in container.logs(stream=True, follow=True):
                yield line.decode("utf-8", errors="replace")
        except Exception as e:
            yield f"Error streaming logs: {e}"

    def stop_container(self, container, timeout=3):
        try:
            container.stop(timeout=timeout)
            print(f"✅ Container stopped: {container.name}")
            return True
        except Exception:
            return False

    def remove_container(self, container, force=True):
        try:
            container.remove(force=force)
            print(f"✅ Container removed: {container.name}")
            return True
        except Exception:
            return False

    def cleanup_container(self, container):
        self.stop_container(container)
        return self.remove_container(container)

    def copy_to_container(self, container, local_path, container_path):
        try:
            import tarfile, io
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode="w") as tar:
                tar.add(local_path, arcname=".")
            tar_stream.seek(0)
            container.put_archive(container_path, tar_stream)
            return True
        except Exception as e:
            print(f"❌ Failed to copy files: {e}")
            return False

    def cleanup_orphaned_containers(self):
        count = 0
        try:
            for c in self.client.containers.list(filters={"name": "cloudrun_"}, all=True):
                try:
                    c.remove(force=True)
                    count += 1
                except Exception:
                    pass
        except Exception:
            pass
        return count


_docker_manager = None

def get_docker_manager():
    global _docker_manager
    if _docker_manager is None:
        _docker_manager = DockerManager()
    return _docker_manager

