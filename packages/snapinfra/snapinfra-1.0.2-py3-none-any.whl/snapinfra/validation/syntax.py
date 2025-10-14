"""Syntax validation for various file types."""

import ast
import json
import re
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path

from .core import BaseValidator, ValidationResult, ValidationSeverity


class SyntaxValidator(BaseValidator):
    """Base class for syntax validators."""
    
    def __init__(self, name: str, file_extensions: List[str]):
        super().__init__(name)
        self.file_extensions = file_extensions
    
    def should_validate(self, file_path: str) -> bool:
        """Check if this validator should validate the given file."""
        return any(file_path.endswith(ext) for ext in self.file_extensions)


class JSONSyntaxValidator(SyntaxValidator):
    """Validator for JSON files."""
    
    def __init__(self):
        super().__init__("json_syntax", [".json"])
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        result = ValidationResult()
        
        for file_path, content in files.items():
            if not self.should_validate(file_path):
                continue
                
            try:
                # Attempt to parse JSON
                json.loads(content)
                
                # Check for common JSON issues
                self._check_json_quality(file_path, content, result)
                
            except json.JSONDecodeError as e:
                # Try to detect if it's AI-generated text instead of JSON
                if self._looks_like_ai_explanation(content):
                    issue = self.create_issue(
                        severity=ValidationSeverity.CRITICAL,
                        message="File contains explanatory text instead of valid JSON. This commonly happens when AI generates explanations instead of pure JSON.",
                        file_path=file_path,
                        line_number=e.lineno if hasattr(e, 'lineno') else None,
                        column_number=e.colno if hasattr(e, 'colno') else None,
                        rule_id="json_invalid_format",
                        suggestion="Ensure the file contains only valid JSON syntax without explanatory text.",
                        auto_fixable=True
                    )
                else:
                    issue = self.create_issue(
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Invalid JSON syntax: {str(e)}",
                        file_path=file_path,
                        line_number=e.lineno if hasattr(e, 'lineno') else None,
                        column_number=e.colno if hasattr(e, 'colno') else None,
                        rule_id="json_syntax_error",
                        suggestion="Fix JSON syntax errors.",
                        auto_fixable=False
                    )
                result.add_issue(issue)
        
        return result
    
    def _looks_like_ai_explanation(self, content: str) -> bool:
        """Detect if content looks like AI-generated explanation text."""
        # Common patterns in AI explanations
        explanation_patterns = [
            r'full_output=',
            r'Based on the user.*requirements',
            r'Here.*breakdown of the generated',
            r'This.*file.*tailored to',
            r'```json\\n.*```',
            r'The.*code.*justified by'
        ]
        
        content_lower = content.lower()
        return any(re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL) for pattern in explanation_patterns)
    
    def _check_json_quality(self, file_path: str, content: str, result: ValidationResult) -> None:
        """Check JSON quality issues."""
        # Check for duplicate keys (basic check)
        lines = content.split('\\n')
        seen_keys = set()
        
        for line_num, line in enumerate(lines, 1):
            # Simple key extraction for basic duplicate detection
            match = re.search(r'"([^"]+)"\\s*:', line.strip())
            if match:
                key = match.group(1)
                if key in seen_keys:
                    issue = self.create_issue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Potential duplicate key '{key}' in JSON",
                        file_path=file_path,
                        line_number=line_num,
                        rule_id="json_duplicate_key",
                        suggestion=f"Remove or rename duplicate key '{key}'"
                    )
                    result.add_issue(issue)
                seen_keys.add(key)


class PythonSyntaxValidator(SyntaxValidator):
    """Validator for Python files."""
    
    def __init__(self):
        super().__init__("python_syntax", [".py"])
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        result = ValidationResult()
        
        for file_path, content in files.items():
            if not self.should_validate(file_path):
                continue
            
            try:
                # Parse Python AST
                ast.parse(content)
                
                # Additional Python quality checks
                self._check_python_quality(file_path, content, result)
                
            except SyntaxError as e:
                issue = self.create_issue(
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Python syntax error: {e.msg}",
                    file_path=file_path,
                    line_number=e.lineno,
                    column_number=e.offset,
                    rule_id="python_syntax_error",
                    suggestion="Fix Python syntax error."
                )
                result.add_issue(issue)
            except Exception as e:
                issue = self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Python parsing error: {str(e)}",
                    file_path=file_path,
                    rule_id="python_parse_error"
                )
                result.add_issue(issue)
        
        return result
    
    def _check_python_quality(self, file_path: str, content: str, result: ValidationResult) -> None:
        """Check Python code quality."""
        lines = content.split('\\n')
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for common issues
            if 'import *' in stripped and not stripped.startswith('#'):
                issue = self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message="Avoid wildcard imports (import *)",
                    file_path=file_path,
                    line_number=line_num,
                    rule_id="python_wildcard_import",
                    suggestion="Import specific modules or use qualified imports"
                )
                result.add_issue(issue)


class JavaScriptSyntaxValidator(SyntaxValidator):
    """Validator for JavaScript files."""
    
    def __init__(self):
        super().__init__("javascript_syntax", [".js", ".jsx", ".ts", ".tsx"])
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        result = ValidationResult()
        
        for file_path, content in files.items():
            if not self.should_validate(file_path):
                continue
            
            # Basic JavaScript syntax checks
            self._check_javascript_basic(file_path, content, result)
        
        return result
    
    def _check_javascript_basic(self, file_path: str, content: str, result: ValidationResult) -> None:
        """Basic JavaScript syntax checks."""
        lines = content.split('\\n')
        
        brace_count = 0
        paren_count = 0
        bracket_count = 0
        
        for line_num, line in enumerate(lines, 1):
            # Count braces for basic balance check
            brace_count += line.count('{') - line.count('}')
            paren_count += line.count('(') - line.count(')')
            bracket_count += line.count('[') - line.count(']')
            
            # Check for common issues
            if 'console.log' in line and 'production' in file_path.lower():
                issue = self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message="console.log found in production code",
                    file_path=file_path,
                    line_number=line_num,
                    rule_id="js_console_log_production",
                    suggestion="Remove console.log statements from production code"
                )
                result.add_issue(issue)
        
        # Check for unbalanced braces/parens
        if brace_count != 0:
            issue = self.create_issue(
                severity=ValidationSeverity.ERROR,
                message=f"Unbalanced braces: {brace_count} excess {'opening' if brace_count > 0 else 'closing'} braces",
                file_path=file_path,
                rule_id="js_unbalanced_braces"
            )
            result.add_issue(issue)


class YAMLSyntaxValidator(SyntaxValidator):
    """Validator for YAML files."""
    
    def __init__(self):
        super().__init__("yaml_syntax", [".yaml", ".yml"])
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        result = ValidationResult()
        
        for file_path, content in files.items():
            if not self.should_validate(file_path):
                continue
            
            try:
                yaml.safe_load(content)
                
                # Additional YAML quality checks
                self._check_yaml_quality(file_path, content, result)
                
            except yaml.YAMLError as e:
                issue = self.create_issue(
                    severity=ValidationSeverity.CRITICAL,
                    message=f"YAML syntax error: {str(e)}",
                    file_path=file_path,
                    rule_id="yaml_syntax_error"
                )
                result.add_issue(issue)
        
        return result
    
    def _check_yaml_quality(self, file_path: str, content: str, result: ValidationResult) -> None:
        """Check YAML quality."""
        lines = content.split('\\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for tabs (YAML should use spaces)
            if '\\t' in line:
                issue = self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message="YAML should use spaces, not tabs for indentation",
                    file_path=file_path,
                    line_number=line_num,
                    rule_id="yaml_tabs_indentation",
                    suggestion="Replace tabs with spaces",
                    auto_fixable=True
                )
                result.add_issue(issue)


class DockerfileSyntaxValidator(SyntaxValidator):
    """Validator for Dockerfile syntax."""
    
    def __init__(self):
        super().__init__("dockerfile_syntax", ["Dockerfile", ".dockerfile"])
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        result = ValidationResult()
        
        for file_path, content in files.items():
            if not (file_path.endswith('Dockerfile') or file_path.endswith('.dockerfile')):
                continue
            
            self._check_dockerfile_quality(file_path, content, result)
        
        return result
    
    def _check_dockerfile_quality(self, file_path: str, content: str, result: ValidationResult) -> None:
        """Check Dockerfile quality."""
        lines = content.split('\\n')
        has_from = False
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip().upper()
            
            if stripped.startswith('FROM'):
                has_from = True
                # Check for latest tag usage
                if ':latest' in line or (not ':' in line and 'FROM' in stripped):
                    issue = self.create_issue(
                        severity=ValidationSeverity.WARNING,
                        message="Avoid using 'latest' tag in FROM instruction",
                        file_path=file_path,
                        line_number=line_num,
                        rule_id="dockerfile_latest_tag",
                        suggestion="Use specific version tags for reproducible builds"
                    )
                    result.add_issue(issue)
        
        if not has_from:
            issue = self.create_issue(
                severity=ValidationSeverity.CRITICAL,
                message="Dockerfile must contain a FROM instruction",
                file_path=file_path,
                rule_id="dockerfile_missing_from"
            )
            result.add_issue(issue)


class SyntaxValidatorRegistry(BaseValidator):
    """Registry that coordinates all syntax validators."""
    
    def __init__(self):
        super().__init__("syntax_registry")
        self.validators = [
            JSONSyntaxValidator(),
            PythonSyntaxValidator(),
            JavaScriptSyntaxValidator(),
            YAMLSyntaxValidator(),
            DockerfileSyntaxValidator(),
        ]
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        """Run all syntax validators."""
        result = ValidationResult()
        
        for validator in self.validators:
            validator_result = validator.validate(files)
            result.merge(validator_result)
        
        return result