"""
CloudRun IDE - Dependency Detector
Detects missing packages from error messages and suggests installation.
"""

import re
from typing import Optional, Tuple, List
from app.utils.constants import DEPENDENCY_PATTERNS, INSTALL_COMMANDS


class DependencyDetector:
    """Detects and manages missing dependencies."""
    
    def detect_missing_dependency(
        self, 
        error_output: str, 
        language: str
    ) -> Optional[Tuple[str, str]]:
        """
        Detect missing package from error output.
        
        Args:
            error_output: Error message from execution
            language: Programming language
            
        Returns:
            Tuple of (package_manager, package_name) or None
        """
        if language not in DEPENDENCY_PATTERNS:
            return None
        
        for manager, patterns in DEPENDENCY_PATTERNS[language].items():
            for pattern in patterns:
                match = re.search(pattern, error_output, re.MULTILINE)
                if match:
                    package_name = match.group(1)
                    return (manager, package_name)
        
        return None
    
    def get_install_command(
        self, 
        language: str, 
        package_manager: str, 
        package_name: str
    ) -> Optional[str]:
        """
        Get installation command for a package.
        
        Args:
            language: Programming language
            package_manager: Package manager (pip, npm, etc.)
            package_name: Name of package to install
            
        Returns:
            Installation command string or None
        """
        if language not in INSTALL_COMMANDS:
            return None
        
        if package_manager not in INSTALL_COMMANDS[language]:
            return None
        
        command_template = INSTALL_COMMANDS[language][package_manager]
        return command_template.format(package=package_name)
    
    def suggest_dependencies(self, error_output: str, language: str) -> List[dict]:
        """
        Suggest multiple dependencies if multiple are missing.
        
        Args:
            error_output: Error message from execution
            language: Programming language
            
        Returns:
            List of dependency suggestions
        """
        suggestions = []
        seen_packages = set()
        
        if language not in DEPENDENCY_PATTERNS:
            return suggestions
        
        for manager, patterns in DEPENDENCY_PATTERNS[language].items():
            for pattern in patterns:
                matches = re.finditer(pattern, error_output, re.MULTILINE)
                for match in matches:
                    package_name = match.group(1)
                    
                    # Avoid duplicates
                    if package_name not in seen_packages:
                        seen_packages.add(package_name)
                        
                        install_cmd = self.get_install_command(
                            language, 
                            manager, 
                            package_name
                        )
                        
                        suggestions.append({
                            'package_manager': manager,
                            'package_name': package_name,
                            'install_command': install_cmd,
                        })
        
        return suggestions


# Global detector instance
dependency_detector = DependencyDetector()
