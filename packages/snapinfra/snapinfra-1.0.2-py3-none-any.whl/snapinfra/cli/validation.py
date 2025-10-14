"""CLI validation integration for SnapInfra code generation."""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..validation import (
    create_default_validator,
    ValidationResult,
    ValidationSeverity,
    AutoFixEngine,
    ValidationReporter
)
from .prompts import get_user_choice


console = Console()


class ValidationWorkflow:
    """Manages the validation workflow for generated code."""
    
    def __init__(self):
        self.validator = create_default_validator()
        self.auto_fix_engine = AutoFixEngine()
        self.reporter = ValidationReporter()
        
        # Load configuration settings
        from ..config.loader import load_config
        try:
            config = load_config()
            self.validation_enabled = config.validation_enabled
            self.auto_fix_enabled = config.auto_fix_enabled
        except Exception:
            self.validation_enabled = True  # Default to enabled
            self.auto_fix_enabled = True   # Default to enabled
    
    async def validate_generated_code(
        self,
        files: Dict[str, str],
        show_progress: bool = True,
        auto_fix: bool = None,
        max_fix_iterations: int = 3
    ) -> Tuple[ValidationResult, Dict[str, str]]:
        """
        Validate generated code and optionally apply auto-fixes.
        
        Args:
            files: Dictionary mapping file paths to file contents
            show_progress: Whether to show progress indicators
            auto_fix: Whether to attempt automatic fixes (None = use config default)
            max_fix_iterations: Maximum number of fix iterations
            
        Returns:
            Tuple of (final_validation_result, potentially_fixed_files)
        """
        # Skip validation entirely if disabled in config
        if not self.validation_enabled:
            if show_progress:
                console.print("⚠️ Code validation is disabled in configuration", style="yellow")
            # Return a passing validation result
            from ..validation import ValidationResult
            dummy_result = ValidationResult(
                passed=True,
                total_files_checked=len(files),
                issues=[]
            )
            return dummy_result, files
            
        # Use config default for auto_fix if not specified
        if auto_fix is None:
            auto_fix = self.auto_fix_enabled
            
        current_files = files.copy()
        iteration = 0
        
        while iteration < max_fix_iterations:
            # Run validation
            if show_progress:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task(f"🔍 Running validation (iteration {iteration + 1})...", total=None)
                    result = self.validator.validate_all(current_files)
                    progress.update(task, completed=100)
            else:
                result = self.validator.validate_all(current_files)
            
            # If no auto-fixable issues or auto-fix disabled, return
            if not auto_fix or not result.auto_fixable_issues:
                return result, current_files
            
            # Apply auto-fixes
            if show_progress:
                console.print(f"🔧 Attempting to auto-fix {len(result.auto_fixable_issues)} issues...")
            
            fix_results = self.auto_fix_engine.fix_multiple_issues(
                result.auto_fixable_issues,
                current_files
            )
            
            if not fix_results:
                # No fixes were applied
                return result, current_files
            
            # Update files with fixes
            for file_path, (fixed_content, fix_messages) in fix_results.items():
                current_files[file_path] = fixed_content
                if show_progress:
                    for message in fix_messages:
                        console.print(f"  ✅ {file_path}: {message}")
            
            iteration += 1
        
        # Final validation after max iterations
        if show_progress:
            console.print("🔍 Final validation after auto-fixes...")
        
        final_result = self.validator.validate_all(current_files)
        return final_result, current_files
    
    def display_validation_summary(self, result: ValidationResult) -> None:
        """Display a comprehensive validation summary."""
        # Create summary table
        table = Table(title="🔍 Validation Summary", show_header=True, header_style="bold blue")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Count", style="magenta", width=10)
        table.add_column("Status", style="green", width=15)
        
        table.add_row("Files Checked", str(result.total_files_checked), "✅" if result.total_files_checked > 0 else "⚠️")
        table.add_row("Total Issues", str(len(result.issues)), "✅" if len(result.issues) == 0 else "❌")
        table.add_row("Critical", str(len(result.critical_issues)), "✅" if len(result.critical_issues) == 0 else "🔴")
        table.add_row("Errors", str(len(result.error_issues)), "✅" if len(result.error_issues) == 0 else "🟠")
        table.add_row("Warnings", str(len(result.warning_issues)), "✅" if len(result.warning_issues) == 0 else "🟡")
        table.add_row("Auto-fixable", str(len(result.auto_fixable_issues)), "🔧" if len(result.auto_fixable_issues) > 0 else "✅")
        
        console.print(table)
        
        # Overall status
        if result.passed:
            console.print(Panel("✅ All validations passed! Code is production-ready.", 
                               title="Validation Status", border_style="green"))
        elif result.has_blocking_issues:
            console.print(Panel("❌ Critical issues found that prevent deployment. Please review and fix.", 
                               title="Validation Status", border_style="red"))
        else:
            console.print(Panel("⚠️ Some warnings found, but code is generally deployable.", 
                               title="Validation Status", border_style="yellow"))
    
    def display_detailed_issues(self, result: ValidationResult, max_issues_per_file: int = 10) -> None:
        """Display detailed validation issues."""
        if not result.issues:
            return
        
        console.print("\n📝 Detailed Issues:")
        
        # Group issues by file
        issues_by_file = {}
        for issue in result.issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
        
        for file_path, file_issues in issues_by_file.items():
            console.print(f"\n📄 [bold cyan]{file_path}[/bold cyan]:")
            
            # Sort issues by line number and severity
            sorted_issues = sorted(
                file_issues, 
                key=lambda x: (
                    x.severity.value != 'critical',  # Critical first
                    x.severity.value != 'error',     # Then errors
                    x.line_number or 0
                )
            )
            
            displayed = 0
            for issue in sorted_issues:
                if displayed >= max_issues_per_file:
                    remaining = len(sorted_issues) - displayed
                    console.print(f"  ... and {remaining} more issues")
                    break
                
                # Severity icon
                severity_icon = {
                    'critical': '🔴',
                    'error': '🟠',
                    'warning': '🟡',
                    'info': '🔵'
                }.get(issue.severity.value, '⚪')
                
                location = f":{issue.line_number}" if issue.line_number else ""
                auto_fix_indicator = " 🔧" if issue.auto_fixable else ""
                
                console.print(f"  {severity_icon} Line{location}: {issue.message}{auto_fix_indicator}")
                
                if issue.suggestion:
                    console.print(f"    💡 [dim]{issue.suggestion}[/dim]")
                
                displayed += 1
    
    async def interactive_validation_workflow(
        self,
        files: Dict[str, str],
        allow_user_fixes: bool = True
    ) -> Tuple[ValidationResult, Dict[str, str], bool]:
        """
        Interactive validation workflow with user choices.
        
        Returns:
            Tuple of (validation_result, final_files, user_approved_deployment)
        """
        console.print("\n🔍 [bold blue]Starting Code Quality Validation[/bold blue]")
        
        # Initial validation with auto-fix
        result, fixed_files = await self.validate_generated_code(files, show_progress=True, auto_fix=True)
        
        # Display results
        self.display_validation_summary(result)
        
        if result.issues:
            self.display_detailed_issues(result, max_issues_per_file=5)
            
            # Ask user what to do
            if result.has_blocking_issues:
                console.print("\\n❌ [bold red]Critical issues prevent deployment.[/bold red]")
                
                if allow_user_fixes:
                    choices = [
                        "Regenerate code with validation feedback",
                        "Show full issue report",
                        "Continue anyway (not recommended)",
                        "Cancel"
                    ]
                else:
                    choices = [
                        "Show full issue report", 
                        "Continue anyway (not recommended)",
                        "Cancel"
                    ]
                
                choice = get_user_choice("What would you like to do?", choices)
                
                if "Regenerate" in choice and allow_user_fixes:
                    return result, fixed_files, False  # Signal regeneration needed
                elif "Show full" in choice:
                    console.print(self.reporter.generate_console_report(result))
                    return await self.interactive_validation_workflow(fixed_files, allow_user_fixes=False)
                elif "Continue anyway" in choice:
                    console.print("⚠️ [yellow]Proceeding with known issues...[/yellow]")
                    return result, fixed_files, True
                else:  # Cancel
                    return result, fixed_files, False
                    
            else:
                # Only warnings
                console.print("\\n⚠️ [yellow]Some warnings found, but code is generally deployable.[/yellow]")
                
                if get_user_choice("Would you like to proceed with deployment?"):
                    return result, fixed_files, True
                else:
                    return result, fixed_files, False
        else:
            console.print("\\n🎉 [bold green]All validations passed! Code is ready for deployment.[/bold green]")
            return result, fixed_files, True
    
    def save_validation_report(
        self, 
        result: ValidationResult, 
        output_path: Path,
        format: str = "markdown"
    ) -> None:
        """Save validation report to file."""
        try:
            if format.lower() == "json":
                content = self.reporter.generate_json_report(result)
                output_file = output_path / "validation_report.json"
            elif format.lower() == "markdown":
                content = self.reporter.generate_markdown_report(result)
                output_file = output_path / "validation_report.md"
            else:
                content = self.reporter.generate_console_report(result)
                output_file = output_path / "validation_report.txt"
            
            output_file.write_text(content, encoding='utf-8')
            console.print(f"📄 Validation report saved to: {output_file}")
            
        except Exception as e:
            console.print(f"❌ Failed to save validation report: {e}")


async def validate_and_fix_code(
    files: Dict[str, str],
    interactive: bool = True,
    auto_fix: bool = True,
    save_report: bool = False,
    report_format: str = "markdown",
    output_path: Optional[Path] = None
) -> Tuple[ValidationResult, Dict[str, str], bool]:
    """
    Main validation entry point for CLI.
    
    Args:
        files: Generated files to validate
        interactive: Whether to use interactive workflow
        auto_fix: Whether to attempt automatic fixes
        save_report: Whether to save validation report
        report_format: Format for saved report (markdown, json, text)
        output_path: Path to save report (if save_report is True)
        
    Returns:
        Tuple of (validation_result, final_files, approved_for_deployment)
    """
    workflow = ValidationWorkflow()
    
    try:
        if interactive:
            result, final_files, approved = await workflow.interactive_validation_workflow(
                files, allow_user_fixes=True
            )
        else:
            result, final_files = await workflow.validate_generated_code(
                files, show_progress=True, auto_fix=auto_fix
            )
            approved = not result.has_blocking_issues
            
            # Display results in non-interactive mode
            workflow.display_validation_summary(result)
            if result.issues:
                workflow.display_detailed_issues(result)
        
        # Save report if requested
        if save_report and output_path:
            workflow.save_validation_report(result, output_path, report_format)
        
        return result, final_files, approved
        
    except Exception as e:
        console.print(f"❌ Validation failed with error: {e}")
        return ValidationResult(passed=False), files, False