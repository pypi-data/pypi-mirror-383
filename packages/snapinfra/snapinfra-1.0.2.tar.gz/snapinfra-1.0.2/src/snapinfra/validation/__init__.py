"""SnapInfra Code Validation Framework.

This module provides comprehensive validation for generated infrastructure code,
ensuring production-ready, internally consistent codebases.
"""

from .core import ValidationIssue, ValidationResult, BaseValidator, CodeQualityValidator, ValidationSeverity
from .syntax import SyntaxValidatorRegistry
from .imports import ImportValidator
from .architecture import ArchitectureValidator, TechnologyStackValidator
from .completeness import CompletenessValidator, APIConsistencyValidator
from .auto_fix import AutoFixEngine
from .reporter import ValidationReporter
from .validators import SyntaxValidator, TechStackValidator
from .workflow import ValidationWorkflow

# Factory function for creating default validator
def create_default_validator():
    """Create a default validator with all standard validators."""
    from .core import CodeQualityValidator
    return CodeQualityValidator()

__all__ = [
    'ValidationIssue',
    'ValidationResult', 
    'BaseValidator',
    'CodeQualityValidator',
    'ValidationSeverity',
    'SyntaxValidatorRegistry',
    'SyntaxValidator',
    'ImportValidator',
    'ArchitectureValidator',
    'TechnologyStackValidator',
    'TechStackValidator',
    'CompletenessValidator',
    'APIConsistencyValidator',
    'AutoFixEngine',
    'ValidationReporter',
    'ValidationWorkflow',
    'create_default_validator',
]
