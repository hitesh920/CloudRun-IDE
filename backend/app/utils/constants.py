"""
CloudRun IDE - Constants
Language configurations and system constants.
"""

# Docker image mappings for each language
DOCKER_IMAGES = {
    "python": "python:3.11-slim",
    "nodejs": "node:20-alpine",
    "java": "eclipse-temurin:21-jdk",
    "cpp": "gcc:12",
    "ubuntu": "ubuntu:22.04",
    # HTML doesn't use Docker - handled separately in executor
}

# Languages that don't need Docker execution
NO_DOCKER_LANGUAGES = {"html"}

# File extensions for each language
FILE_EXTENSIONS = {
    "python": ".py",
    "nodejs": ".js",
    "java": ".java",
    "cpp": ".cpp",
    "html": ".html",
}

# Execution commands for each language
# All commands use unbuffered output where possible
EXECUTION_COMMANDS = {
    "python": ["python", "-u", "{file}"],
    "nodejs": ["node", "{file}"],
    "java": [
        "sh", "-c",
        "javac {file} && java -cp /workspace {classname}"
    ],
    "cpp": [
        "sh", "-c",
        "g++ -o /tmp/program {file} && /tmp/program"
    ],
    "ubuntu": ["bash", "-c", "{code}"],
}

# Default starter code templates
CODE_TEMPLATES = {
    "python": """# Python Code
print("Hello, World!")
""",
    "nodejs": """// Node.js Code
console.log("Hello, World!");
""",
    "java": """public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
""",
    "cpp": """#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
""",
    "html": """<!DOCTYPE html>
<html>
<head>
    <title>Page</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>Edit this HTML and click Run to preview.</p>
</body>
</html>
""",
    "ubuntu": """# Ubuntu Shell
echo "Hello, World!"
""",
}

# Dependency detection patterns
DEPENDENCY_PATTERNS = {
    "python": {
        "pip": [
            r"ModuleNotFoundError: No module named '(\w+)'",
            r"ImportError: No module named (\w+)",
        ]
    },
    "nodejs": {
        "npm": [
            r"Cannot find module '([\w\-@/]+)'",
            r"Error: Cannot find module '([\w\-@/]+)'",
            r"Error \[ERR_MODULE_NOT_FOUND\].*'([\w\-@/]+)'",
        ]
    },
}

# Package installation commands
INSTALL_COMMANDS = {
    "python": {
        "pip": "pip install --no-cache-dir {package}"
    },
    "nodejs": {
        "npm": "npm install {package}"
    },
}

# Container resource limits (defaults, overridden by config)
DEFAULT_LIMITS = {
    "memory": "1g",
    "cpu_quota": 100000,
    "cpu_period": 100000,
    "timeout": 60,
}

# WebSocket message types
WS_MESSAGE_TYPES = {
    "STDOUT": "stdout",
    "STDERR": "stderr",
    "STATUS": "status",
    "ERROR": "error",
    "COMPLETE": "complete",
    "DEPENDENCY": "dependency",
    "HTML_PREVIEW": "html_preview",
}

# Execution statuses
EXECUTION_STATUSES = {
    "PENDING": "pending",
    "RUNNING": "running",
    "COMPLETED": "completed",
    "ERROR": "error",
    "TIMEOUT": "timeout",
    "STOPPED": "stopped",
}
