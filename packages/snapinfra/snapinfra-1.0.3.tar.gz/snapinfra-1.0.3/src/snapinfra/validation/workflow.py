"""Validation workflow management."""

from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from .core import ValidationResult, ValidationSeverity, BaseValidator
from .validators import SyntaxValidator, ImportValidator, TechStackValidator
from .architecture import ArchitectureValidator
from .completeness import CompletenessValidator
from .auto_fix import AutoFixEngine
from .reporter import ValidationReporter


class ValidationWorkflow:
    """Manages validation workflow execution."""
    
    def __init__(self, validators: Optional[List[BaseValidator]] = None):
        """Initialize with optional custom validators."""
        self.validators = validators or self._create_default_validators()
        self.auto_fix_engine = AutoFixEngine()
        self.reporter = ValidationReporter()
    
    def _create_default_validators(self) -> List[BaseValidator]:
        """Create default set of validators."""
        return [
            SyntaxValidator(),
            ImportValidator(),
            TechStackValidator(),
            ArchitectureValidator(),
            CompletenessValidator()
        ]
    
    def run_validation(
        self, 
        files: Dict[str, str], 
        enable_auto_fix: bool = False,
        max_iterations: int = 3
    ) -> Tuple[ValidationResult, Dict[str, str]]:
        """Run complete validation workflow."""
        current_files = files.copy()
        iteration = 0
        
        while iteration < max_iterations:
            # Run all validators
            result = self._run_validators(current_files)
            
            # If no auto-fixable issues or auto-fix disabled, return
            if not enable_auto_fix or not result.auto_fixable_issues:
                return result, current_files
            
            # Apply auto-fixes
            fix_results = self.auto_fix_engine.fix_multiple_issues(
                result.auto_fixable_issues,
                current_files
            )
            
            if not fix_results:
                # No fixes were applied
                return result, current_files
            
            # Update files with fixes
            for file_path, (fixed_content, _) in fix_results.items():
                current_files[file_path] = fixed_content
            
            iteration += 1
        
        # Final validation after max iterations
        final_result = self._run_validators(current_files)
        return final_result, current_files
    
    def _run_validators(self, files: Dict[str, str]) -> ValidationResult:
        """Run all validators and combine results."""
        combined_result = ValidationResult()
        combined_result.total_files_checked = len(files)
        
        for validator in self.validators:
            try:
                validator_result = validator.validate(files)
                combined_result.merge(validator_result)
            except Exception as e:
                # Don't let one validator failure break everything
                from .core import ValidationIssue
                issue = ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Validator '{validator.name}' failed: {str(e)}",
                    file_path="<validation_system>",
                    rule_id=f"{validator.name}_failure"
                )
                combined_result.add_issue(issue)
        
        return combined_result
    
    def generate_report(self, result: ValidationResult, format: str = "detailed") -> str:
        """Generate validation report."""
        if format == "json":
            return self.reporter.generate_json_report(result)
        elif format == "summary":
            return self.reporter.generate_summary_report(result)
        else:
            return self.reporter.generate_detailed_report(result)
    
    def save_report(self, result: ValidationResult, output_path: Path, format: str = "json") -> None:
        """Save validation report to file."""
        self.reporter.save_report(result, output_path, format)