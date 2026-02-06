"""
CloudRun IDE - Helper Functions
Utility functions used across the application.
"""

import uuid
import re
from datetime import datetime
from typing import Optional, Tuple


def generate_execution_id() -> str:
    """Generate a unique execution ID."""
    return f"exec_{uuid.uuid4().hex[:12]}"


def generate_container_name(execution_id: str, language: str) -> str:
    """Generate a unique container name."""
    return f"cloudrun_{language}_{execution_id}"


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


def extract_java_classname(code: str) -> Optional[str]:
    """Extract the main class name from Java code."""
    match = re.search(r'public\s+class\s+(\w+)', code)
    if match:
        return match.group(1)
    return "Main"


def detect_missing_package(error_output: str, language: str) -> Optional[Tuple[str, str]]:
    """
    Detect missing package from error output.
    
    Returns:
        Tuple of (package_manager, package_name) or None
    """
    from app.utils.constants import DEPENDENCY_PATTERNS
    
    if language not in DEPENDENCY_PATTERNS:
        return None
    
    for manager, patterns in DEPENDENCY_PATTERNS[language].items():
        for pattern in patterns:
            match = re.search(pattern, error_output)
            if match:
                package_name = match.group(1)
                return (manager, package_name)
    
    return None


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
    """
    Basic code validation.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not code or not code.strip():
        return False, "Code cannot be empty"
    
    if len(code) > 1_000_000:  # 1MB limit
        return False, "Code is too large (max 1MB)"
    
    # Language-specific validation
    if language == "java":
        if "public class" not in code:
            return False, "Java code must contain a public class"
    
    return True, None


def is_safe_command(command: str) -> bool:
    """
    Check if a shell command is safe to execute.
    Used for Ubuntu advanced mode.
    """
    dangerous_patterns = [
        r'\brm\s+-rf',
        r'\bdd\s+',
        r':\(\)\{.*\}',  # Fork bomb
        r'\bkill\b',
        r'\bkillall\b',
        r'\breboot\b',
        r'\bshutdown\b',
        r'\bmkfs\b',
        r'\bformat\b',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False
    
    return True
