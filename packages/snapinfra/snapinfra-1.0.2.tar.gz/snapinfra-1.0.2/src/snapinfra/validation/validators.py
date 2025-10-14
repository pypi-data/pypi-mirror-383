"""Specific validator implementations."""

import json
import ast
import re
from typing import Dict, List, Optional

from .core import BaseValidator, ValidationResult, ValidationSeverity, ValidationIssue


class SyntaxValidator(BaseValidator):
    """Validates syntax for various file types."""
    
    def __init__(self):
        super().__init__("syntax")
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        """Validate syntax for all files."""
        result = ValidationResult()
        result.total_files_checked = len(files)
        
        for file_path, content in files.items():
            file_result = self._validate_file(file_path, content)
            result.merge(file_result)
        
        return result
    
    def _validate_file(self, file_path: str, content: str) -> ValidationResult:
        """Validate syntax for a single file."""
        result = ValidationResult()
        
        # Determine file type by extension
        file_lower = file_path.lower()
        
        if file_lower.endswith('.json'):
            self._validate_json(file_path, content, result)
        elif file_lower.endswith(('.yaml', '.yml')):
            self._validate_yaml(file_path, content, result)
        elif file_lower.endswith('.py'):
            self._validate_python(file_path, content, result)
        elif file_lower.endswith('.js'):
            self._validate_javascript(file_path, content, result)
        elif file_lower.endswith('dockerfile') or 'dockerfile' in file_lower:
            self._validate_dockerfile(file_path, content, result)
        
        return result
    
    def _validate_json(self, file_path: str, content: str, result: ValidationResult):
        """Validate JSON syntax."""
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            issue = self.create_issue(
                severity=ValidationSeverity.ERROR,
                message=f"JSON syntax error: {str(e)}",
                file_path=file_path,
                line_number=getattr(e, 'lineno', None),
                auto_fixable=False
            )
            result.add_issue(issue)
    
    def _validate_yaml(self, file_path: str, content: str, result: ValidationResult):
        """Validate YAML syntax."""
        # Check for tabs
        for line_num, line in enumerate(content.split('\n'), 1):
            if '\t' in line:
                issue = self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="YAML cannot contain tab characters",
                    file_path=file_path,
                    line_number=line_num,
                    suggestion="Replace tabs with spaces",
                    auto_fixable=True
                )
                result.add_issue(issue)
    
    def _validate_python(self, file_path: str, content: str, result: ValidationResult):
        """Validate Python syntax."""
        try:
            ast.parse(content)
        except SyntaxError as e:
            issue = self.create_issue(
                severity=ValidationSeverity.ERROR,
                message=f"Python syntax error: {e.msg}",
                file_path=file_path,
                line_number=e.lineno,
                column_number=e.offset,
                auto_fixable=False
            )
            result.add_issue(issue)
    
    def _validate_javascript(self, file_path: str, content: str, result: ValidationResult):
        """Validate JavaScript syntax (basic checks)."""
        # Basic bracket matching
        open_brackets = content.count('(') - content.count(')')
        if open_brackets != 0:
            issue = self.create_issue(
                severity=ValidationSeverity.ERROR,
                message="Unmatched parentheses in JavaScript",
                file_path=file_path,
                auto_fixable=False
            )
            result.add_issue(issue)
    
    def _validate_dockerfile(self, file_path: str, content: str, result: ValidationResult):
        """Validate Dockerfile syntax."""
        lines = content.strip().split('\n')
        if not lines:
            return
        
        # Check if first instruction is FROM
        first_line = lines[0].strip().upper()
        if not first_line.startswith('FROM'):
            issue = self.create_issue(
                severity=ValidationSeverity.ERROR,
                message="Dockerfile must start with FROM instruction",
                file_path=file_path,
                line_number=1,
                suggestion="Add FROM instruction as the first line",
                auto_fixable=False
            )
            result.add_issue(issue)


class ImportValidator(BaseValidator):
    """Validates import statements and dependencies."""
    
    def __init__(self):
        super().__init__("imports")
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        """Validate imports across all files."""
        result = ValidationResult()
        result.total_files_checked = len(files)
        
        for file_path, content in files.items():
            if file_path.endswith('.py'):
                self._validate_python_imports(file_path, content, result)
            elif file_path.endswith('.js'):
                self._validate_javascript_imports(file_path, content, result)
        
        return result
    
    def _validate_python_imports(self, file_path: str, content: str, result: ValidationResult):
        """Validate Python imports."""
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                # Check for circular imports (basic check)
                if 'from __future__' not in stripped and line_num > 50:
                    issue = self.create_issue(
                        severity=ValidationSeverity.WARNING,
                        message="Import statements should be at the top of the file",
                        file_path=file_path,
                        line_number=line_num,
                        suggestion="Move import to the top of the file"
                    )
                    result.add_issue(issue)
    
    def _validate_javascript_imports(self, file_path: str, content: str, result: ValidationResult):
        """Validate JavaScript imports."""
        # Basic validation for now
        pass


class TechStackValidator(BaseValidator):
    """Validates technology stack consistency."""
    
    def __init__(self):
        super().__init__("tech_stack")
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        """Validate technology stack consistency."""
        result = ValidationResult()
        result.total_files_checked = len(files)
        
        # Check for consistent technology usage
        has_python = any(f.endswith('.py') for f in files.keys())
        has_javascript = any(f.endswith('.js') for f in files.keys())
        has_dockerfile = any('dockerfile' in f.lower() for f in files.keys())
        
        if has_python and has_javascript:
            issue = ValidationIssue(
                severity=ValidationSeverity.INFO,
                message="Project contains both Python and JavaScript - consider consistency",
                file_path="<project>",
                suggestion="Consider standardizing on one primary language"
            )
            result.add_issue(issue)
        
        return result


# Create aliases for backward compatibility
SyntaxValidatorRegistry = SyntaxValidator
TechnologyStackValidator = TechStackValidator