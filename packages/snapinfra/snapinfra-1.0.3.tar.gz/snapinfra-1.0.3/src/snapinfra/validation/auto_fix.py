"""Auto-fix engine for automatically correcting validation issues."""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from .core import ValidationIssue, ValidationSeverity


class AutoFixResult:
    """Result of an auto-fix operation."""
    
    def __init__(self, success: bool, message: str, fixed_content: Optional[str] = None):
        self.success = success
        self.message = message
        self.fixed_content = fixed_content


class AutoFixEngine:
    """Engine for automatically fixing validation issues."""
    
    def __init__(self):
        self.fixers = {
            'json_invalid_format': self._fix_json_invalid_format,
            'yaml_tabs_indentation': self._fix_yaml_tabs,
            'python_wildcard_import': self._fix_python_wildcard_import,
            'js_console_log_production': self._fix_js_console_log,
            'dockerfile_latest_tag': self._fix_dockerfile_latest_tag,
        }
    
    def can_auto_fix(self, issue: ValidationIssue) -> bool:
        """Check if an issue can be automatically fixed."""
        return issue.auto_fixable and issue.rule_id in self.fixers
    
    def fix_issue(self, issue: ValidationIssue, file_content: str) -> AutoFixResult:
        """Attempt to automatically fix a validation issue."""
        if not self.can_auto_fix(issue):
            return AutoFixResult(False, "Issue cannot be auto-fixed")
        
        fixer = self.fixers[issue.rule_id]
        try:
            return fixer(issue, file_content)
        except Exception as e:
            return AutoFixResult(False, f"Auto-fix failed: {str(e)}")
    
    def fix_multiple_issues(self, issues: List[ValidationIssue], 
                          files: Dict[str, str]) -> Dict[str, Tuple[str, List[str]]]:
        """Fix multiple issues across multiple files."""
        results = {}
        
        # Group issues by file
        issues_by_file = {}
        for issue in issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
        
        # Fix issues for each file
        for file_path, file_issues in issues_by_file.items():
            if file_path not in files:
                continue
                
            content = files[file_path]
            fixed_issues = []
            
            # Sort issues by line number (descending) to avoid offset issues
            file_issues.sort(key=lambda x: x.line_number or 0, reverse=True)
            
            for issue in file_issues:
                if self.can_auto_fix(issue):
                    fix_result = self.fix_issue(issue, content)
                    if fix_result.success and fix_result.fixed_content:
                        content = fix_result.fixed_content
                        fixed_issues.append(fix_result.message)
            
            if fixed_issues:
                results[file_path] = (content, fixed_issues)
        
        return results
    
    def _fix_json_invalid_format(self, issue: ValidationIssue, content: str) -> AutoFixResult:
        """Fix JSON files that contain explanatory text instead of valid JSON."""
        # Try to extract JSON from explanatory text
        
        # Pattern 1: Look for JSON code blocks
        json_block_match = re.search(r'```json\\n(.*?)\\n```', content, re.DOTALL)
        if json_block_match:
            json_content = json_block_match.group(1).strip()
            try:
                # Validate it's proper JSON
                json.loads(json_content)
                return AutoFixResult(
                    True,
                    "Extracted JSON from code block",
                    json_content
                )
            except json.JSONDecodeError:
                pass
        
        # Pattern 2: Look for JSON after "code=" pattern
        code_match = re.search(r"code='({.*?})'", content, re.DOTALL)
        if code_match:
            json_content = code_match.group(1)
            try:
                # Validate and reformat
                parsed = json.loads(json_content)
                formatted = json.dumps(parsed, indent=2)
                return AutoFixResult(
                    True,
                    "Extracted and formatted JSON from code field",
                    formatted
                )
            except json.JSONDecodeError:
                pass
        
        # Pattern 3: Try to find any JSON-like structure
        json_pattern = r'({[\\s\\S]*})'
        json_match = re.search(json_pattern, content)
        if json_match:
            potential_json = json_match.group(1)
            try:
                parsed = json.loads(potential_json)
                formatted = json.dumps(parsed, indent=2)
                return AutoFixResult(
                    True,
                    "Extracted and formatted JSON structure",
                    formatted
                )
            except json.JSONDecodeError:
                pass
        
        return AutoFixResult(False, "Could not extract valid JSON from content")
    
    def _fix_yaml_tabs(self, issue: ValidationIssue, content: str) -> AutoFixResult:
        """Fix YAML files that use tabs instead of spaces."""
        lines = content.split('\\n')
        fixed_lines = []
        
        for line in lines:
            # Replace tabs with 2 spaces
            fixed_line = line.replace('\\t', '  ')
            fixed_lines.append(fixed_line)
        
        fixed_content = '\\n'.join(fixed_lines)
        return AutoFixResult(
            True,
            "Replaced tabs with spaces in YAML file",
            fixed_content
        )
    
    def _fix_python_wildcard_import(self, issue: ValidationIssue, content: str) -> AutoFixResult:
        """Fix Python wildcard imports by suggesting specific imports."""
        if not issue.line_number:
            return AutoFixResult(False, "Cannot fix without line number")
        
        lines = content.split('\\n')
        if issue.line_number > len(lines):
            return AutoFixResult(False, "Line number out of range")
        
        line_index = issue.line_number - 1
        line = lines[line_index]
        
        # This is a complex fix that would require static analysis
        # For now, just add a comment suggesting specific imports
        if 'import *' in line:
            lines[line_index] = f"# TODO: Replace wildcard import with specific imports\\n{line}"
            
            fixed_content = '\\n'.join(lines)
            return AutoFixResult(
                True,
                "Added TODO comment for wildcard import",
                fixed_content
            )
        
        return AutoFixResult(False, "No wildcard import found on specified line")
    
    def _fix_js_console_log(self, issue: ValidationIssue, content: str) -> AutoFixResult:
        """Remove or comment out console.log statements in production code."""
        if not issue.line_number:
            return AutoFixResult(False, "Cannot fix without line number")
        
        lines = content.split('\\n')
        if issue.line_number > len(lines):
            return AutoFixResult(False, "Line number out of range")
        
        line_index = issue.line_number - 1
        line = lines[line_index]
        
        # Comment out the console.log line
        if 'console.log' in line:
            indentation = len(line) - len(line.lstrip())
            lines[line_index] = ' ' * indentation + '// ' + line.strip()
            
            fixed_content = '\\n'.join(lines)
            return AutoFixResult(
                True,
                "Commented out console.log statement",
                fixed_content
            )
        
        return AutoFixResult(False, "No console.log found on specified line")
    
    def _fix_dockerfile_latest_tag(self, issue: ValidationIssue, content: str) -> AutoFixResult:
        """Fix Dockerfile that uses 'latest' tag."""
        if not issue.line_number:
            return AutoFixResult(False, "Cannot fix without line number")
        
        lines = content.split('\\n')
        if issue.line_number > len(lines):
            return AutoFixResult(False, "Line number out of range")
        
        line_index = issue.line_number - 1
        line = lines[line_index]
        
        # Suggest specific versions for common base images
        version_suggestions = {
            'node': 'node:18-alpine',
            'python': 'python:3.11-slim',
            'ubuntu': 'ubuntu:22.04',
            'alpine': 'alpine:3.18',
            'nginx': 'nginx:1.25-alpine',
            'postgres': 'postgres:15-alpine',
            'redis': 'redis:7-alpine',
        }
        
        if line.strip().startswith('FROM'):
            for base_image, suggested_version in version_suggestions.items():
                if base_image in line and (':latest' in line or line.count(':') == 0):
                    # Replace with suggested version
                    if ':latest' in line:
                        new_line = line.replace(f'{base_image}:latest', suggested_version)
                    else:
                        new_line = line.replace(base_image, suggested_version)
                    
                    lines[line_index] = new_line
                    fixed_content = '\\n'.join(lines)
                    return AutoFixResult(
                        True,
                        f"Updated {base_image} to use specific version: {suggested_version}",
                        fixed_content
                    )
        
        return AutoFixResult(False, "Could not determine appropriate version for base image")


class ValidationReporter:
    """Generate validation reports in various formats."""
    
    def __init__(self):
        pass
    
    def generate_console_report(self, result) -> str:
        """Generate a console-friendly validation report."""
        from .core import ValidationResult
        
        if not isinstance(result, ValidationResult):
            return "Invalid result type"
        
        lines = []
        lines.append("🔍 SnapInfra Code Quality Validation Report")
        lines.append("=" * 50)
        
        if result.passed:
            lines.append("✅ All validations passed!")
        else:
            lines.append("❌ Validation issues found")
        
        lines.append(f"📁 Files checked: {result.total_files_checked}")
        lines.append(f"⚠️  Issues found: {len(result.issues)}")
        
        if result.issues:
            lines.append("\\n📋 Issue Summary:")
            lines.append(f"  🔴 Critical: {len(result.critical_issues)}")
            lines.append(f"  🟠 Errors: {len(result.error_issues)}")
            lines.append(f"  🟡 Warnings: {len(result.warning_issues)}")
            lines.append(f"  🔧 Auto-fixable: {len(result.auto_fixable_issues)}")
        
        # Group issues by file
        if result.issues:
            lines.append("\\n📝 Detailed Issues:")
            issues_by_file = {}
            for issue in result.issues:
                if issue.file_path not in issues_by_file:
                    issues_by_file[issue.file_path] = []
                issues_by_file[issue.file_path].append(issue)
            
            for file_path, file_issues in issues_by_file.items():
                lines.append(f"\\n📄 {file_path}:")
                for issue in sorted(file_issues, key=lambda x: x.line_number or 0):
                    severity_icon = {
                        'critical': '🔴',
                        'error': '🟠', 
                        'warning': '🟡',
                        'info': '🔵'
                    }.get(issue.severity.value, '⚪')
                    
                    location = f":{issue.line_number}" if issue.line_number else ""
                    auto_fix = " 🔧" if issue.auto_fixable else ""
                    
                    lines.append(f"  {severity_icon} Line{location}: {issue.message}{auto_fix}")
                    if issue.suggestion:
                        lines.append(f"     💡 {issue.suggestion}")
        
        return "\\n".join(lines)
    
    def generate_json_report(self, result) -> str:
        """Generate a JSON validation report."""
        from .core import ValidationResult
        
        if not isinstance(result, ValidationResult):
            return json.dumps({"error": "Invalid result type"})
        
        return json.dumps(result.to_dict(), indent=2)
    
    def generate_markdown_report(self, result) -> str:
        """Generate a Markdown validation report."""
        from .core import ValidationResult
        
        if not isinstance(result, ValidationResult):
            return "# Invalid result type"
        
        lines = []
        lines.append("# 🔍 SnapInfra Code Quality Validation Report")
        lines.append("")
        
        if result.passed:
            lines.append("✅ **All validations passed!**")
        else:
            lines.append("❌ **Validation issues found**")
        
        lines.append("")
        lines.append("## 📊 Summary")
        lines.append(f"- **Files checked:** {result.total_files_checked}")
        lines.append(f"- **Issues found:** {len(result.issues)}")
        
        if result.issues:
            lines.append(f"- **Critical:** {len(result.critical_issues)}")
            lines.append(f"- **Errors:** {len(result.error_issues)}")
            lines.append(f"- **Warnings:** {len(result.warning_issues)}")
            lines.append(f"- **Auto-fixable:** {len(result.auto_fixable_issues)}")
        
        # Detailed issues
        if result.issues:
            lines.append("")
            lines.append("## 📝 Issues by File")
            
            issues_by_file = {}
            for issue in result.issues:
                if issue.file_path not in issues_by_file:
                    issues_by_file[issue.file_path] = []
                issues_by_file[issue.file_path].append(issue)
            
            for file_path, file_issues in issues_by_file.items():
                lines.append(f"### 📄 `{file_path}`")
                lines.append("")
                
                for issue in sorted(file_issues, key=lambda x: x.line_number or 0):
                    severity_badge = {
                        'critical': '![Critical](https://img.shields.io/badge/Critical-red)',
                        'error': '![Error](https://img.shields.io/badge/Error-orange)',
                        'warning': '![Warning](https://img.shields.io/badge/Warning-yellow)',
                        'info': '![Info](https://img.shields.io/badge/Info-blue)'
                    }.get(issue.severity.value, '')
                    
                    location = f" (Line {issue.line_number})" if issue.line_number else ""
                    auto_fix = " 🔧 _Auto-fixable_" if issue.auto_fixable else ""
                    
                    lines.append(f"**{issue.message}**{location}{auto_fix}")
                    lines.append(f"{severity_badge}")
                    
                    if issue.suggestion:
                        lines.append(f"💡 _{issue.suggestion}_")
                    
                    lines.append("")
        
        return "\\n".join(lines)