"""Validation reporting functionality."""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from .core import ValidationResult, ValidationIssue, ValidationSeverity


class ValidationReporter:
    """Generates reports from validation results."""
    
    def __init__(self):
        pass
    
    def generate_json_report(self, result: ValidationResult) -> str:
        """Generate a JSON report."""
        return json.dumps(result.to_dict(), indent=2)
    
    def generate_summary_report(self, result: ValidationResult) -> str:
        """Generate a human-readable summary report."""
        lines = []
        lines.append("=== Validation Summary ===")
        lines.append(f"Files checked: {result.total_files_checked}")
        lines.append(f"Total issues: {len(result.issues)}")
        lines.append(f"Critical: {len(result.critical_issues)}")
        lines.append(f"Errors: {len(result.error_issues)}")
        lines.append(f"Warnings: {len(result.warning_issues)}")
        lines.append(f"Auto-fixable: {len(result.auto_fixable_issues)}")
        lines.append("")
        
        if result.passed:
            lines.append("✅ All validations passed!")
        else:
            lines.append("❌ Validation failed")
        
        return "\n".join(lines)
    
    def generate_detailed_report(self, result: ValidationResult) -> str:
        """Generate a detailed report with all issues."""
        lines = []
        lines.append(self.generate_summary_report(result))
        
        if result.issues:
            lines.append("\n=== Detailed Issues ===")
            
            # Group by file
            files_with_issues = {}
            for issue in result.issues:
                if issue.file_path not in files_with_issues:
                    files_with_issues[issue.file_path] = []
                files_with_issues[issue.file_path].append(issue)
            
            for file_path, file_issues in files_with_issues.items():
                lines.append(f"\n📄 {file_path}:")
                for issue in file_issues:
                    severity_icon = {
                        ValidationSeverity.CRITICAL: "🔴",
                        ValidationSeverity.ERROR: "🟠",
                        ValidationSeverity.WARNING: "🟡",
                        ValidationSeverity.INFO: "🔵"
                    }.get(issue.severity, "⚪")
                    
                    location = f":{issue.line_number}" if issue.line_number else ""
                    auto_fix = " [AUTO-FIXABLE]" if issue.auto_fixable else ""
                    
                    lines.append(f"  {severity_icon} Line{location}: {issue.message}{auto_fix}")
                    
                    if issue.suggestion:
                        lines.append(f"    💡 Suggestion: {issue.suggestion}")
        
        return "\n".join(lines)
    
    def save_report(self, result: ValidationResult, output_path: Path, format: str = "json") -> None:
        """Save validation report to file."""
        if format == "json":
            content = self.generate_json_report(result)
        elif format == "summary":
            content = self.generate_summary_report(result)
        elif format == "detailed":
            content = self.generate_detailed_report(result)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        output_path.write_text(content, encoding="utf-8")