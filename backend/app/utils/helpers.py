"""
CloudRun IDE - Helper Functions
Utility functions used across the application.
"""

import uuid
import re
from datetime import datetime, timezone
from typing import Optional, Tuple


def generate_execution_id() -> str:
    """Generate a unique execution ID."""
    return f"exec_{uuid.uuid4().hex[:12]}"


def generate_container_name(execution_id: str, language: str) -> str:
    """Generate a unique container name."""
    return f"cloudrun_{language}_{execution_id}"


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def extract_java_classname(code: str) -> str:
    """Extract the main class name from Java code."""
    match = re.search(r'public\s+class\s+(\w+)', code)
    if match:
        return match.group(1)
    return "Main"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal."""
    # Remove any path components
    filename = filename.split('/')[-1].split('\\')[-1]
    # Remove any potentially dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    return filename


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def validate_code(code: str, language: str) -> Tuple[bool, Optional[str]]:
    """Basic code validation."""
    if not code or not code.strip():
        return False, "Code cannot be empty"
    
    if len(code) > 1_000_000:  # 1MB limit
        return False, "Code is too large (max 1MB)"
    
    if language == "java":
        if "class" not in code:
            return False, "Java code must contain a class"
    
    return True, None


def is_safe_command(command: str) -> bool:
    """Check if a shell command is safe to execute."""
    dangerous_patterns = [
        r'\brm\s+-rf\s+/',
        r'\bdd\s+if=',
        r':\(\)\{.*\}',  # Fork bomb
        r'\bkillall\b',
        r'\breboot\b',
        r'\bshutdown\b',
        r'\bmkfs\b',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False
    
    return True
