"""Architecture and technology stack validation."""

import re
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from .core import BaseValidator, ValidationResult, ValidationSeverity


@dataclass
class TechnologyDetection:
    """Represents a detected technology."""
    name: str
    category: str  # 'frontend', 'backend', 'database', 'deployment', etc.
    confidence: float  # 0.0 to 1.0
    files: List[str]  # Files where this technology was detected


class TechnologyDetector:
    """Detects technologies used in a codebase."""
    
    TECHNOLOGY_PATTERNS = {
        # Frontend Frameworks
        'react': {
            'category': 'frontend',
            'patterns': [
                (r'import.*from [\'"]react[\'"]', 0.9),
                (r'React\.Component', 0.8),
                (r'jsx?$', 0.3),  # File extension
                (r'useState|useEffect|useContext', 0.7),
            ],
            'files': ['.jsx', '.tsx']
        },
        'vue': {
            'category': 'frontend',
            'patterns': [
                (r'import.*Vue', 0.9),
                (r'<template>', 0.8),
                (r'\.vue$', 0.9),
                (r'new Vue\\(', 0.8),
            ],
            'files': ['.vue']
        },
        'angular': {
            'category': 'frontend',
            'patterns': [
                (r'@angular/', 0.9),
                (r'@Component', 0.8),
                (r'@Injectable', 0.8),
                (r'angular\.json', 0.9),
            ],
            'files': ['angular.json']
        },
        
        # Backend Frameworks
        'flask': {
            'category': 'backend',
            'patterns': [
                (r'from flask import', 0.9),
                (r'Flask\\(__name__\\)', 0.9),
                (r'@app\\.route', 0.8),
            ],
        },
        'fastapi': {
            'category': 'backend',
            'patterns': [
                (r'from fastapi import', 0.9),
                (r'FastAPI\\(\\)', 0.9),
                (r'@app\\.(get|post|put|delete)', 0.8),
            ],
        },
        'django': {
            'category': 'backend',
            'patterns': [
                (r'from django', 0.9),
                (r'django', 0.6),
                (r'settings\\.py', 0.8),
                (r'manage\\.py', 0.9),
            ],
            'files': ['manage.py', 'settings.py']
        },
        'express': {
            'category': 'backend',
            'patterns': [
                (r'express', 0.8),
                (r'app\\.get\\(|app\\.post\\(', 0.7),
                (r'require\\([\'"]express[\'"]\\)', 0.9),
            ],
        },
        'nest': {
            'category': 'backend',
            'patterns': [
                (r'@nestjs/', 0.9),
                (r'@Controller', 0.8),
                (r'@Module', 0.8),
            ],
        },
        
        # Desktop UI
        'pyqt5': {
            'category': 'desktop',
            'patterns': [
                (r'from PyQt5', 0.9),
                (r'QApplication|QWidget|QMainWindow', 0.8),
                (r'pyqt5', 0.7),
            ],
        },
        'tkinter': {
            'category': 'desktop',
            'patterns': [
                (r'import tkinter', 0.9),
                (r'from tkinter import', 0.9),
                (r'Tk\\(\\)', 0.8),
            ],
        },
        'electron': {
            'category': 'desktop',
            'patterns': [
                (r'electron', 0.8),
                (r'BrowserWindow', 0.8),
                (r'main\\.js.*electron', 0.7),
            ],
        },
        
        # Databases
        'postgresql': {
            'category': 'database',
            'patterns': [
                (r'postgresql|postgres', 0.8),
                (r'psycopg2', 0.9),
                (r'pg_', 0.6),
            ],
        },
        'mysql': {
            'category': 'database',
            'patterns': [
                (r'mysql', 0.8),
                (r'pymysql|MySQLdb', 0.9),
            ],
        },
        'mongodb': {
            'category': 'database',
            'patterns': [
                (r'mongodb|mongo', 0.8),
                (r'pymongo', 0.9),
                (r'mongoose', 0.9),
            ],
        },
        'sqlite': {
            'category': 'database',
            'patterns': [
                (r'sqlite', 0.8),
                (r'\.db$|\.sqlite$', 0.7),
            ],
        },
        
        # Containerization/Deployment
        'docker': {
            'category': 'deployment',
            'patterns': [
                (r'FROM .*', 0.9),  # Dockerfile
                (r'docker-compose', 0.9),
                (r'COPY|ADD|RUN|WORKDIR', 0.7),
            ],
            'files': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml']
        },
        'kubernetes': {
            'category': 'deployment',
            'patterns': [
                (r'apiVersion:|kind:', 0.8),
                (r'kubectl', 0.7),
                (r'deployment\\.yaml|service\\.yaml', 0.8),
            ],
        },
        
        # Testing
        'pytest': {
            'category': 'testing',
            'patterns': [
                (r'import pytest', 0.9),
                (r'def test_', 0.7),
                (r'pytest\\.', 0.8),
            ],
        },
        'jest': {
            'category': 'testing',
            'patterns': [
                (r'jest', 0.8),
                (r'describe\\(|it\\(|test\\(', 0.7),
                (r'expect\\(.*\\)\\.toBe', 0.8),
            ],
        },
    }
    
    def detect_technologies(self, files: Dict[str, str]) -> List[TechnologyDetection]:
        """Detect technologies used in the codebase."""
        detections = {}
        
        for tech_name, tech_config in self.TECHNOLOGY_PATTERNS.items():
            detection = self._detect_technology(tech_name, tech_config, files)
            if detection.confidence > 0.1:  # Only include if reasonably confident
                detections[tech_name] = detection
        
        return list(detections.values())
    
    def _detect_technology(self, tech_name: str, tech_config: dict, files: Dict[str, str]) -> TechnologyDetection:
        """Detect a specific technology."""
        total_score = 0.0
        max_possible_score = 0.0
        matching_files = []
        
        # Check file patterns
        for file_path in files.keys():
            file_matches = False
            
            # Check filename patterns
            if 'files' in tech_config:
                for file_pattern in tech_config['files']:
                    if file_path.endswith(file_pattern) or file_pattern in file_path:
                        total_score += 0.9
                        max_possible_score += 1.0
                        file_matches = True
                        break
            
            # Check content patterns
            content = files[file_path]
            for pattern, weight in tech_config['patterns']:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    total_score += weight
                    file_matches = True
                max_possible_score += weight
            
            if file_matches:
                matching_files.append(file_path)
        
        confidence = total_score / max_possible_score if max_possible_score > 0 else 0.0
        
        return TechnologyDetection(
            name=tech_name,
            category=tech_config['category'],
            confidence=min(confidence, 1.0),  # Cap at 1.0
            files=matching_files
        )


class TechnologyStackValidator(BaseValidator):
    """Validates technology stack coherence."""
    
    # Define incompatible technology combinations
    INCOMPATIBLE_COMBINATIONS = [
        # Can't have multiple frontend frameworks
        (['react', 'vue', 'angular'], 'Multiple frontend frameworks detected'),
        
        # Can't have multiple Python web frameworks  
        (['flask', 'django', 'fastapi'], 'Multiple Python web frameworks detected'),
        
        # Can't mix desktop and web UI frameworks significantly
        (['pyqt5', 'tkinter', 'electron'], ['react', 'vue', 'angular'], 
         'Desktop UI frameworks mixed with web frameworks'),
        
        # Can't have multiple primary databases (unless specifically multi-db)
        (['postgresql', 'mysql', 'mongodb'], 'Multiple primary databases detected'),
    ]
    
    def __init__(self):
        super().__init__("technology_stack_validator")
        self.detector = TechnologyDetector()
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        """Validate technology stack coherence."""
        result = ValidationResult()
        
        # Detect technologies
        technologies = self.detector.detect_technologies(files)
        
        # Check for incompatible combinations
        self._check_incompatible_combinations(technologies, result)
        
        # Check for missing dependencies
        self._check_missing_dependencies(technologies, files, result)
        
        # Check for architectural inconsistencies
        self._check_architectural_consistency(technologies, result)
        
        return result
    
    def _check_incompatible_combinations(self, technologies: List[TechnologyDetection], result: ValidationResult):
        """Check for incompatible technology combinations."""
        tech_names = {tech.name for tech in technologies if tech.confidence > 0.3}
        
        for incompatible in self.INCOMPATIBLE_COMBINATIONS:
            if len(incompatible) == 2:
                # Simple list of incompatible technologies
                tech_list, message = incompatible
                found_techs = [tech for tech in tech_list if tech in tech_names]
                
                if len(found_techs) > 1:
                    issue = self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"{message}: {', '.join(found_techs)}",
                        file_path="<architecture>",
                        rule_id="incompatible_tech_combo",
                        suggestion=f"Choose one of: {', '.join(found_techs)}"
                    )
                    result.add_issue(issue)
            
            elif len(incompatible) == 3:
                # Two lists of mutually incompatible technologies
                list1, list2, message = incompatible
                found_list1 = [tech for tech in list1 if tech in tech_names]
                found_list2 = [tech for tech in list2 if tech in tech_names]
                
                if found_list1 and found_list2:
                    issue = self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"{message}: {', '.join(found_list1)} + {', '.join(found_list2)}",
                        file_path="<architecture>",
                        rule_id="incompatible_tech_categories",
                        suggestion="Choose either desktop OR web architecture, not both"
                    )
                    result.add_issue(issue)
    
    def _check_missing_dependencies(self, technologies: List[TechnologyDetection], files: Dict[str, str], result: ValidationResult):
        """Check for missing required dependencies."""
        tech_names = {tech.name for tech in technologies if tech.confidence > 0.5}
        
        # Check for package files
        has_package_json = any(f.endswith('package.json') for f in files.keys())
        has_requirements_txt = any(f.endswith('requirements.txt') for f in files.keys())
        has_poetry_toml = any(f.endswith('pyproject.toml') for f in files.keys())
        
        # If we have JS technologies but no package.json
        js_techs = {'react', 'vue', 'angular', 'express', 'nest'}
        if any(tech in tech_names for tech in js_techs) and not has_package_json:
            issue = self.create_issue(
                severity=ValidationSeverity.ERROR,
                message="JavaScript technologies detected but no package.json found",
                file_path="<architecture>",
                rule_id="missing_package_json",
                suggestion="Add package.json to manage JavaScript dependencies"
            )
            result.add_issue(issue)
        
        # If we have Python technologies but no requirements management
        python_techs = {'flask', 'django', 'fastapi', 'pyqt5'}
        if (any(tech in tech_names for tech in python_techs) and 
            not has_requirements_txt and not has_poetry_toml):
            issue = self.create_issue(
                severity=ValidationSeverity.WARNING,
                message="Python technologies detected but no dependency management file found",
                file_path="<architecture>",
                rule_id="missing_python_deps",
                suggestion="Add requirements.txt or pyproject.toml to manage Python dependencies"
            )
            result.add_issue(issue)
    
    def _check_architectural_consistency(self, technologies: List[TechnologyDetection], result: ValidationResult):
        """Check for architectural consistency."""
        tech_by_category = {}
        for tech in technologies:
            if tech.confidence > 0.3:
                if tech.category not in tech_by_category:
                    tech_by_category[tech.category] = []
                tech_by_category[tech.category].append(tech.name)
        
        # Check for complete architecture gaps
        has_frontend = 'frontend' in tech_by_category
        has_backend = 'backend' in tech_by_category
        has_desktop = 'desktop' in tech_by_category
        
        if has_frontend and not has_backend and not has_desktop:
            issue = self.create_issue(
                severity=ValidationSeverity.WARNING,
                message="Frontend framework detected but no backend framework found",
                file_path="<architecture>",
                rule_id="incomplete_architecture",
                suggestion="Consider adding a backend framework or API layer"
            )
            result.add_issue(issue)


class ArchitectureValidator(BaseValidator):
    """Validates overall architecture patterns and consistency."""
    
    def __init__(self):
        super().__init__("architecture_validator")
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        """Validate architecture patterns."""
        result = ValidationResult()
        
        # Check file organization
        self._check_file_organization(files, result)
        
        # Check for configuration consistency
        self._check_configuration_consistency(files, result)
        
        # Check for security patterns
        self._check_security_patterns(files, result)
        
        return result
    
    def _check_file_organization(self, files: Dict[str, str], result: ValidationResult):
        """Check file organization patterns."""
        file_paths = list(files.keys())
        
        # Check for common structure issues
        python_files = [f for f in file_paths if f.endswith('.py')]
        js_files = [f for f in file_paths if f.endswith(('.js', '.jsx', '.ts', '.tsx'))]
        
        # If we have many files but no clear organization
        if len(python_files) > 5:
            # Check for some organization structure
            has_structure = any(
                '/' in f for f in python_files  # Files in subdirectories
            )
            
            if not has_structure:
                issue = self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message="Large number of Python files with flat structure",
                    file_path="<architecture>",
                    rule_id="flat_file_structure",
                    suggestion="Consider organizing files into modules/packages"
                )
                result.add_issue(issue)
    
    def _check_configuration_consistency(self, files: Dict[str, str], result: ValidationResult):
        """Check configuration file consistency."""
        config_files = {
            'package.json': None,
            'requirements.txt': None,
            'docker-compose.yml': None,
            'docker-compose.yaml': None,
            'Dockerfile': None,
        }
        
        # Find config files
        for file_path in files.keys():
            for config_name in config_files.keys():
                if file_path.endswith(config_name):
                    config_files[config_name] = file_path
        
        # Check for Docker inconsistencies
        has_dockerfile = config_files['Dockerfile'] is not None
        has_compose = (config_files['docker-compose.yml'] is not None or 
                      config_files['docker-compose.yaml'] is not None)
        
        if has_compose and not has_dockerfile:
            issue = self.create_issue(
                severity=ValidationSeverity.WARNING,
                message="docker-compose file found but no Dockerfile",
                file_path="<architecture>",
                rule_id="incomplete_docker_config",
                suggestion="Add Dockerfile to support docker-compose configuration"
            )
            result.add_issue(issue)
    
    def _check_security_patterns(self, files: Dict[str, str], result: ValidationResult):
        """Check for basic security patterns."""
        # Check for environment file patterns
        has_env_example = any('.env.example' in f for f in files.keys())
        has_env_file = any(('.env' in f and not f.endswith('.example')) for f in files.keys())
        
        # Look for hardcoded secrets (basic check)
        for file_path, content in files.items():
            if self._contains_potential_secrets(content):
                issue = self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Potential hardcoded secrets detected",
                    file_path=file_path,
                    rule_id="hardcoded_secrets",
                    suggestion="Move secrets to environment variables or secure configuration",
                    auto_fixable=False
                )
                result.add_issue(issue)
                break  # Only report once per validation run
        
        # If we find evidence of secrets but no .env.example
        if has_env_file and not has_env_example:
            issue = self.create_issue(
                severity=ValidationSeverity.WARNING,
                message="Environment file detected but no .env.example provided",
                file_path="<architecture>",
                rule_id="missing_env_example",
                suggestion="Add .env.example to document required environment variables"
            )
            result.add_issue(issue)
    
    def _contains_potential_secrets(self, content: str) -> bool:
        """Check if content contains potential hardcoded secrets."""
        secret_patterns = [
            r'password\\s*=\\s*[\'"][^\'"]+[\'"]',
            r'api_key\\s*=\\s*[\'"][^\'"]+[\'"]',
            r'secret\\s*=\\s*[\'"][^\'"]+[\'"]',
            r'token\\s*=\\s*[\'"][^\'"]+[\'"]',
            r'key\\s*=\\s*[\'"][a-zA-Z0-9]{20,}[\'"]',
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False