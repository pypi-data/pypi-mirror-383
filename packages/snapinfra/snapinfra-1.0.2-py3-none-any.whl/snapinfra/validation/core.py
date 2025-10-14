"""Core validation framework classes and interfaces."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from pathlib import Path


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"  # Prevents deployment/execution
    ERROR = "error"       # Major functionality issues
    WARNING = "warning"   # Best practice violations
    INFO = "info"         # Suggestions for improvement


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    
    severity: ValidationSeverity
    message: str
    file_path: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    rule_id: Optional[str] = None
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    
    def __str__(self) -> str:
        location = f"{self.file_path}"
        if self.line_number:
            location += f":{self.line_number}"
            if self.column_number:
                location += f":{self.column_number}"
        
        return f"[{self.severity.value.upper()}] {location}: {self.message}"


@dataclass
class ValidationResult:
    """Result of validation process."""
    
    issues: List[ValidationIssue] = field(default_factory=list)
    passed: bool = True
    total_files_checked: int = 0
    processing_time_ms: Optional[float] = None
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        """Get critical issues that prevent deployment."""
        return [i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]
    
    @property
    def error_issues(self) -> List[ValidationIssue]:
        """Get error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]
    
    @property
    def warning_issues(self) -> List[ValidationIssue]:
        """Get warning-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]
    
    @property
    def auto_fixable_issues(self) -> List[ValidationIssue]:
        """Get issues that can be automatically fixed."""
        return [i for i in self.issues if i.auto_fixable]
    
    @property
    def has_blocking_issues(self) -> bool:
        """Check if there are issues that prevent deployment."""
        return len(self.critical_issues) > 0 or len(self.error_issues) > 0
    
    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue."""
        self.issues.append(issue)
        if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]:
            self.passed = False
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result into this one."""
        self.issues.extend(other.issues)
        self.total_files_checked += other.total_files_checked
        if not other.passed:
            self.passed = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'passed': self.passed,
            'total_files_checked': self.total_files_checked,
            'processing_time_ms': self.processing_time_ms,
            'summary': {
                'critical': len(self.critical_issues),
                'errors': len(self.error_issues),
                'warnings': len(self.warning_issues),
                'auto_fixable': len(self.auto_fixable_issues),
            },
            'issues': [
                {
                    'severity': issue.severity.value,
                    'message': issue.message,
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'column_number': issue.column_number,
                    'rule_id': issue.rule_id,
                    'suggestion': issue.suggestion,
                    'auto_fixable': issue.auto_fixable,
                }
                for issue in self.issues
            ]
        }


class BaseValidator(ABC):
    """Base class for all validators."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        """
        Validate the provided files.
        
        Args:
            files: Dictionary mapping file paths to file contents
            
        Returns:
            ValidationResult with any issues found
        """
        pass
    
    def create_issue(
        self,
        severity: ValidationSeverity,
        message: str,
        file_path: str,
        line_number: Optional[int] = None,
        column_number: Optional[int] = None,
        rule_id: Optional[str] = None,
        suggestion: Optional[str] = None,
        auto_fixable: bool = False
    ) -> ValidationIssue:
        """Helper method to create validation issues."""
        return ValidationIssue(
            severity=severity,
            message=message,
            file_path=file_path,
            line_number=line_number,
            column_number=column_number,
            rule_id=rule_id,
            suggestion=suggestion,
            auto_fixable=auto_fixable
        )


class CodeQualityValidator:
    """Main validator that coordinates all validation checks."""
    
    def __init__(self):
        self.validators: List[BaseValidator] = []
        self._registry: Dict[str, BaseValidator] = {}
    
    def register_validator(self, validator: BaseValidator) -> None:
        """Register a validator."""
        self.validators.append(validator)
        self._registry[validator.name] = validator
    
    def get_validator(self, name: str) -> Optional[BaseValidator]:
        """Get validator by name."""
        return self._registry.get(name)
    
    def validate_all(self, files: Dict[str, str]) -> ValidationResult:
        """Run all registered validators."""
        result = ValidationResult()
        result.total_files_checked = len(files)
        
        for validator in self.validators:
            try:
                validator_result = validator.validate(files)
                result.merge(validator_result)
            except Exception as e:
                # Don't let one validator failure break everything
                issue = ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Validator '{validator.name}' failed: {str(e)}",
                    file_path="<validation_system>",
                    rule_id=f"{validator.name}_failure"
                )
                result.add_issue(issue)
        
        return result
    
    def validate_specific(self, files: Dict[str, str], validator_names: List[str]) -> ValidationResult:
        """Run specific validators only."""
        result = ValidationResult()
        result.total_files_checked = len(files)
        
        for name in validator_names:
            validator = self.get_validator(name)
            if validator:
                try:
                    validator_result = validator.validate(files)
                    result.merge(validator_result)
                except Exception as e:
                    issue = ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Validator '{name}' failed: {str(e)}",
                        file_path="<validation_system>",
                        rule_id=f"{name}_failure"
                    )
                    result.add_issue(issue)
        
        return result


def create_default_validator() -> CodeQualityValidator:
    """Create validator with all default validators registered."""
    from .syntax import SyntaxValidatorRegistry
    from .imports import ImportValidator
    from .architecture import ArchitectureValidator, TechnologyStackValidator
    from .completeness import CompletenessValidator, APIConsistencyValidator
    
    validator = CodeQualityValidator()
    
    # Register all validators
    syntax_registry = SyntaxValidatorRegistry()
    validator.register_validator(syntax_registry)
    validator.register_validator(ImportValidator())
    validator.register_validator(ArchitectureValidator())
    validator.register_validator(TechnologyStackValidator())
    validator.register_validator(CompletenessValidator())
    validator.register_validator(APIConsistencyValidator())
    
    return validator