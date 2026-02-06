"""
CloudRun IDE - Constants
Language configurations and system constants.
"""

# Docker image mappings for each language
DOCKER_IMAGES = {
    "python": "python:3.11-slim",
    "nodejs": "node:20-alpine",
    "java": "eclipse-temurin:21-jre",
    "cpp": "gcc:12",
    "ubuntu": "ubuntu:22.04",
}

# File extensions for each language
FILE_EXTENSIONS = {
    "python": ".py",
    "nodejs": ".js",
    "java": ".java",
    "cpp": ".cpp",
    "html": ".html",
}

# Execution commands for each language
EXECUTION_COMMANDS = {
    "python": ["python", "-u", "{file}"],
    "nodejs": ["node", "{file}"],
    "java": [
        "sh", "-c",
        "javac {file} && java {classname}"
    ],
    "cpp": [
        "sh", "-c",
        "g++ {file} -o /tmp/program && /tmp/program"
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
</head>
<body>
    <h1>Hello, World!</h1>
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
            r"Cannot find module '([\w-]+)'",
            r"Error: Cannot find module '([\w-]+)'",
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

# Container resource limits (will be overridden by config)
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
