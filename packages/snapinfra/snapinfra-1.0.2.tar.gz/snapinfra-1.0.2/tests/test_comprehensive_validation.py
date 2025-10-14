"""Comprehensive test suite for the SnapInfra validation system."""

import json
import pytest
from pathlib import Path
from typing import Dict

from src.snapinfra.validation.core import (
    ValidationSeverity,
    ValidationIssue,
    ValidationResult,
    CodeQualityValidator,
    create_default_validator
)
from src.snapinfra.validation.syntax import (
    JSONSyntaxValidator,
    PythonSyntaxValidator,
    JavaScriptSyntaxValidator,
    YAMLSyntaxValidator
)
from src.snapinfra.validation.imports import ImportValidator
from src.snapinfra.validation.architecture import TechnologyStackValidator
from src.snapinfra.validation.completeness import CompletenessValidator, APIConsistencyValidator
from src.snapinfra.validation.auto_fix import AutoFixEngine, AutoFixResult


class TestValidationCore:
    """Test core validation framework."""
    
    def test_validation_issue_creation(self):
        """Test ValidationIssue creation and string representation."""
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            message="Test error message",
            file_path="test.py",
            line_number=10,
            column_number=5,
            rule_id="test_rule",
            suggestion="Fix this issue",
            auto_fixable=True
        )
        
        assert issue.severity == ValidationSeverity.ERROR
        assert issue.message == "Test error message"
        assert issue.file_path == "test.py"
        assert issue.line_number == 10
        assert issue.column_number == 5
        assert issue.rule_id == "test_rule"
        assert issue.suggestion == "Fix this issue"
        assert issue.auto_fixable is True
        assert "ERROR" in str(issue)
        assert "test.py:10:5" in str(issue)
    
    def test_validation_result_aggregation(self):
        """Test ValidationResult aggregation and properties."""
        result = ValidationResult()
        
        # Add various types of issues
        critical_issue = ValidationIssue(ValidationSeverity.CRITICAL, "Critical", "test.py")
        error_issue = ValidationIssue(ValidationSeverity.ERROR, "Error", "test.py")
        warning_issue = ValidationIssue(ValidationSeverity.WARNING, "Warning", "test.py")
        auto_fixable_issue = ValidationIssue(ValidationSeverity.WARNING, "Fixable", "test.py", auto_fixable=True)
        
        result.add_issue(critical_issue)
        result.add_issue(error_issue)
        result.add_issue(warning_issue)
        result.add_issue(auto_fixable_issue)
        
        assert len(result.issues) == 4
        assert len(result.critical_issues) == 1
        assert len(result.error_issues) == 1
        assert len(result.warning_issues) == 2
        assert len(result.auto_fixable_issues) == 1
        assert result.has_blocking_issues is True
        assert result.passed is False
    
    def test_code_quality_validator_registration(self):
        """Test CodeQualityValidator validator registration."""
        validator = CodeQualityValidator()
        json_validator = JSONSyntaxValidator()
        
        validator.register_validator(json_validator)
        
        assert len(validator.validators) == 1
        assert validator.get_validator("json_syntax") == json_validator
    
    def test_create_default_validator(self):
        """Test default validator creation with all validators registered."""
        validator = create_default_validator()
        
        assert len(validator.validators) > 5  # Should have multiple validators
        assert validator.get_validator("syntax_registry") is not None
        assert validator.get_validator("import_validator") is not None
        assert validator.get_validator("technology_stack_validator") is not None


class TestSyntaxValidators:
    """Test syntax validation functionality."""
    
    def test_json_syntax_validator_valid_json(self):
        """Test JSON validator with valid JSON."""
        validator = JSONSyntaxValidator()
        files = {
            "package.json": json.dumps({"name": "test", "version": "1.0.0"}, indent=2)
        }
        
        result = validator.validate(files)
        assert result.passed is True
        assert len(result.issues) == 0
    
    def test_json_syntax_validator_invalid_json(self):
        """Test JSON validator with invalid JSON."""
        validator = JSONSyntaxValidator()
        files = {
            "package.json": "{ invalid json }"
        }
        
        result = validator.validate(files)
        assert result.passed is False
        assert len(result.issues) == 1
        assert result.issues[0].severity == ValidationSeverity.CRITICAL
        assert "Invalid JSON syntax" in result.issues[0].message
    
    def test_json_syntax_validator_ai_explanation_detection(self):
        """Test JSON validator detecting AI-generated explanatory text."""
        validator = JSONSyntaxValidator()
        files = {
            "package.json": """Based on the user's requirements, here is the generated package.json:
            {
              "name": "test-app",
              "version": "1.0.0"
            }
            This package.json is tailored to the project needs."""
        }
        
        result = validator.validate(files)
        assert result.passed is False
        assert len(result.issues) == 1
        assert "explanatory text instead of valid JSON" in result.issues[0].message
        assert result.issues[0].auto_fixable is True
    
    def test_python_syntax_validator_valid_code(self):
        """Test Python validator with valid Python code."""
        validator = PythonSyntaxValidator()
        files = {
            "main.py": """
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
"""
        }
        
        result = validator.validate(files)
        assert result.passed is True
        assert len(result.issues) == 0
    
    def test_python_syntax_validator_syntax_error(self):
        """Test Python validator with syntax error."""
        validator = PythonSyntaxValidator()
        files = {
            "main.py": """
def hello_world(
    print("Hello, World!")  # Missing closing parenthesis
"""
        }
        
        result = validator.validate(files)
        assert result.passed is False
        assert len(result.issues) == 1
        assert result.issues[0].severity == ValidationSeverity.CRITICAL
        assert "Python syntax error" in result.issues[0].message
    
    def test_python_wildcard_import_detection(self):
        """Test Python validator detecting wildcard imports."""
        validator = PythonSyntaxValidator()
        files = {
            "main.py": "from os import *\\nprint('test')"
        }
        
        result = validator.validate(files)
        assert len(result.issues) == 1
        assert "wildcard imports" in result.issues[0].message
        assert result.issues[0].severity == ValidationSeverity.WARNING
    
    def test_javascript_syntax_validator(self):
        """Test JavaScript validator basic functionality."""
        validator = JavaScriptSyntaxValidator()
        files = {
            "app.js": """
function greet(name) {
    console.log("Hello, " + name);
    return "Greeting sent";
}

greet("World");
"""
        }
        
        result = validator.validate(files)
        # Should detect console.log in production code
        assert len(result.issues) == 1
        assert "console.log" in result.issues[0].message


class TestImportValidator:
    """Test import resolution validation."""
    
    def test_python_import_resolution_success(self):
        """Test successful Python import resolution."""
        validator = ImportValidator()
        files = {
            "main.py": "from utils import helper\\nhelper()",
            "utils.py": "def helper():\\n    pass"
        }
        
        result = validator.validate(files)
        # Should have no critical import issues
        critical_import_issues = [
            issue for issue in result.issues 
            if issue.rule_id == "import_not_found" and issue.severity == ValidationSeverity.CRITICAL
        ]
        assert len(critical_import_issues) == 0
    
    def test_python_import_resolution_failure(self):
        """Test Python import resolution with missing files."""
        validator = ImportValidator()
        files = {
            "main.py": "from nonexistent import something\\nsomething()"
        }
        
        result = validator.validate(files)
        # Should detect missing import
        import_issues = [
            issue for issue in result.issues 
            if issue.rule_id == "import_not_found"
        ]
        assert len(import_issues) >= 1
        assert any("nonexistent" in issue.message for issue in import_issues)
    
    def test_javascript_import_resolution(self):
        """Test JavaScript import resolution."""
        validator = ImportValidator()
        files = {
            "app.js": "import { helper } from './utils';\\nhelper();",
            "utils.js": "export function helper() { return true; }"
        }
        
        result = validator.validate(files)
        # Should resolve local imports
        critical_import_issues = [
            issue for issue in result.issues 
            if issue.rule_id == "import_not_found" and issue.severity == ValidationSeverity.CRITICAL
        ]
        # May have some issues due to simplified resolution, but shouldn't be critical for relative imports
        assert len(critical_import_issues) == 0


class TestTechnologyStackValidator:
    """Test technology stack coherence validation."""
    
    def test_coherent_web_stack(self):
        """Test validation of coherent web technology stack."""
        validator = TechnologyStackValidator()
        files = {
            "package.json": json.dumps({"dependencies": {"react": "^18.0.0", "express": "^4.18.0"}}),
            "app.js": "const express = require('express');\\nconst app = express();",
            "frontend.jsx": "import React from 'react';\\nexport default function App() { return <div>Hello</div>; }"
        }
        
        result = validator.validate(files)
        
        # Should not have incompatible technology warnings
        incompatible_issues = [
            issue for issue in result.issues 
            if issue.rule_id in ["incompatible_tech_combo", "incompatible_tech_categories"]
        ]
        assert len(incompatible_issues) == 0
    
    def test_incompatible_technology_mix(self):
        """Test detection of incompatible technology combinations."""
        validator = TechnologyStackValidator()
        files = {
            "main.py": "from PyQt5.QtWidgets import QApplication\\nfrom flask import Flask",
            "app.jsx": "import React from 'react';\\nexport default function App() { return <div>Hello</div>; }"
        }
        
        result = validator.validate(files)
        
        # Should detect incompatible desktop + web mix
        incompatible_issues = [
            issue for issue in result.issues 
            if issue.rule_id == "incompatible_tech_categories"
        ]
        assert len(incompatible_issues) >= 1
        assert any("Desktop UI frameworks mixed with web frameworks" in issue.message for issue in incompatible_issues)
    
    def test_missing_package_files(self):
        """Test detection of missing package management files."""
        validator = TechnologyStackValidator()
        files = {
            "app.js": "const express = require('express');"
        }
        
        result = validator.validate(files)
        
        # Should detect missing package.json
        missing_package_issues = [
            issue for issue in result.issues 
            if issue.rule_id == "missing_package_json"
        ]
        assert len(missing_package_issues) == 1
        assert "no package.json found" in missing_package_issues[0].message


class TestCompletenessValidator:
    """Test implementation completeness validation."""
    
    def test_python_function_implementation_complete(self):
        """Test complete Python function implementation."""
        validator = CompletenessValidator()
        files = {
            "main.py": "helper()\\nprint('done')",
            "utils.py": "def helper():\\n    return True"
        }
        
        result = validator.validate(files)
        
        # Should not have missing implementation issues for helper
        missing_impl_issues = [
            issue for issue in result.issues 
            if issue.rule_id == "missing_implementation" and "helper" in issue.message
        ]
        assert len(missing_impl_issues) == 0
    
    def test_python_function_implementation_missing(self):
        """Test missing Python function implementation."""
        validator = CompletenessValidator()
        files = {
            "main.py": "nonexistent_function()\\nprint('done')"
        }
        
        result = validator.validate(files)
        
        # Should detect missing function
        missing_impl_issues = [
            issue for issue in result.issues 
            if issue.rule_id == "missing_implementation"
        ]
        # Filter out known builtins
        custom_missing = [
            issue for issue in missing_impl_issues 
            if "nonexistent_function" in issue.message
        ]
        assert len(custom_missing) >= 1


class TestAPIConsistencyValidator:
    """Test API consistency validation."""
    
    def test_api_consistency_complete(self):
        """Test complete API consistency."""
        validator = APIConsistencyValidator()
        files = {
            "frontend.js": "fetch('/api/users')",
            "backend.py": "@app.route('/api/users')\\ndef get_users():\\n    return []"
        }
        
        result = validator.validate(files)
        
        # Should not have missing endpoint issues
        missing_endpoint_issues = [
            issue for issue in result.issues 
            if issue.rule_id == "missing_api_endpoint"
        ]
        assert len(missing_endpoint_issues) == 0
    
    def test_api_consistency_missing_endpoint(self):
        """Test missing API endpoint detection."""
        validator = APIConsistencyValidator()
        files = {
            "frontend.js": "fetch('/api/missing-endpoint')"
        }
        
        result = validator.validate(files)
        
        # Should detect missing endpoint
        missing_endpoint_issues = [
            issue for issue in result.issues 
            if issue.rule_id == "missing_api_endpoint"
        ]
        assert len(missing_endpoint_issues) >= 1
        assert any("/api/missing-endpoint" in issue.message for issue in missing_endpoint_issues)


class TestAutoFixEngine:
    """Test automatic issue fixing functionality."""
    
    def test_json_auto_fix_from_code_block(self):
        """Test auto-fixing JSON extracted from code blocks."""
        engine = AutoFixEngine()
        
        issue = ValidationIssue(
            severity=ValidationSeverity.CRITICAL,
            message="Invalid JSON format",
            file_path="package.json",
            rule_id="json_invalid_format",
            auto_fixable=True
        )
        
        content = '''```json
{
  "name": "test-app",
  "version": "1.0.0"
}
```'''
        
        result = engine.fix_issue(issue, content)
        
        assert result.success is True
        assert result.fixed_content is not None
        # Should be valid JSON
        parsed = json.loads(result.fixed_content)
        assert parsed["name"] == "test-app"
        assert parsed["version"] == "1.0.0"
    
    def test_yaml_tabs_auto_fix(self):
        """Test auto-fixing YAML tabs to spaces."""
        engine = AutoFixEngine()
        
        issue = ValidationIssue(
            severity=ValidationSeverity.WARNING,
            message="YAML uses tabs",
            file_path="config.yaml",
            rule_id="yaml_tabs_indentation",
            auto_fixable=True
        )
        
        content = "key:\\n\\tvalue: test\\n\\t\\tnestedkey: nested"
        
        result = engine.fix_issue(issue, content)
        
        assert result.success is True
        assert "\\t" not in result.fixed_content  # No tabs should remain
        assert "  " in result.fixed_content  # Should have spaces
    
    def test_console_log_auto_fix(self):
        """Test auto-fixing console.log statements."""
        engine = AutoFixEngine()
        
        issue = ValidationIssue(
            severity=ValidationSeverity.WARNING,
            message="console.log in production",
            file_path="app.js",
            line_number=2,
            rule_id="js_console_log_production",
            auto_fixable=True
        )
        
        content = "function test() {\\n  console.log('debug message');\\n  return true;\\n}"
        
        result = engine.fix_issue(issue, content)
        
        assert result.success is True
        assert "// console.log" in result.fixed_content  # Should be commented
        assert "debug message" in result.fixed_content  # Original content preserved
    
    def test_dockerfile_latest_tag_auto_fix(self):
        """Test auto-fixing Dockerfile latest tags."""
        engine = AutoFixEngine()
        
        issue = ValidationIssue(
            severity=ValidationSeverity.WARNING,
            message="Uses latest tag",
            file_path="Dockerfile",
            line_number=1,
            rule_id="dockerfile_latest_tag",
            auto_fixable=True
        )
        
        content = "FROM node:latest\\nRUN npm install"
        
        result = engine.fix_issue(issue, content)
        
        assert result.success is True
        assert "node:18-alpine" in result.fixed_content  # Should use specific version
        assert "latest" not in result.fixed_content
    
    def test_multiple_issues_auto_fix(self):
        """Test fixing multiple issues across multiple files."""
        engine = AutoFixEngine()
        
        issues = [
            ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="YAML uses tabs",
                file_path="config.yaml",
                line_number=1,
                rule_id="yaml_tabs_indentation",
                auto_fixable=True
            ),
            ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="console.log in production",
                file_path="app.js",
                line_number=2,
                rule_id="js_console_log_production",
                auto_fixable=True
            )
        ]
        
        files = {
            "config.yaml": "key:\\n\\tvalue: test",
            "app.js": "function test() {\\n  console.log('debug');\\n}"
        }
        
        results = engine.fix_multiple_issues(issues, files)
        
        assert len(results) == 2  # Both files should be fixed
        assert "config.yaml" in results
        assert "app.js" in results
        
        # Check YAML fix
        yaml_content, yaml_messages = results["config.yaml"]
        assert "\\t" not in yaml_content
        assert len(yaml_messages) == 1
        
        # Check JS fix
        js_content, js_messages = results["app.js"]
        assert "// console.log" in js_content
        assert len(js_messages) == 1


class TestIntegrationScenarios:
    """Test end-to-end validation scenarios."""
    
    def test_music_production_app_scenario(self):
        """Test validation scenario based on the music production app issues."""
        validator = create_default_validator()
        
        # Simulate the problematic music production app files
        files = {
            "package.json": """full_output='Based on the user's requirements...' code='{
  "name": "music-production-app",
  "version": "1.0.0"
}'""",
            "src/main.py": "from src.ui.main_window import MainWindow\\napp = MainWindow()",
            "src/ui/mainwindow.py": "class MainWindow:\\n    def __init__(self):\\n        pass",
            "src/components/App.js": "import Dashboard from './Dashboard';\\nexport default function App() { return <Dashboard />; }"
        }
        
        result = validator.validate_all(files)
        
        # Should catch multiple critical issues
        assert result.passed is False
        assert len(result.critical_issues) >= 2  # JSON format + import issues
        
        # Check specific issues
        issue_types = {issue.rule_id for issue in result.issues}
        assert "json_invalid_format" in issue_types  # Bad package.json
        assert "import_not_found" in issue_types     # Missing imports
    
    def test_clean_web_app_scenario(self):
        """Test validation of a clean, well-structured web application."""
        validator = create_default_validator()
        
        files = {
            "package.json": json.dumps({
                "name": "clean-web-app",
                "version": "1.0.0",
                "dependencies": {
                    "react": "^18.0.0",
                    "express": "^4.18.0"
                }
            }, indent=2),
            "src/App.jsx": """import React from 'react';
import { UserList } from './UserList';

export default function App() {
    return <div><UserList /></div>;
}""",
            "src/UserList.jsx": """import React from 'react';

export function UserList() {
    return <ul><li>User 1</li></ul>;
}""",
            "server/app.js": """const express = require('express');
const app = express();

app.get('/api/users', (req, res) => {
    res.json([{ name: 'User 1' }]);
});

module.exports = app;"""
        }
        
        result = validator.validate_all(files)
        
        # Should have minimal issues (maybe some warnings)
        assert len(result.critical_issues) == 0
        assert len(result.error_issues) == 0
        # May have some warnings about architecture or missing tests, but should be deployable
        assert not result.has_blocking_issues


# Run specific test scenarios
if __name__ == "__main__":
    # Run a quick smoke test
    print("🧪 Running SnapInfra Validation Test Suite...")
    
    # Test core functionality
    test_core = TestValidationCore()
    test_core.test_validation_issue_creation()
    test_core.test_validation_result_aggregation()
    print("✅ Core validation tests passed")
    
    # Test syntax validators
    test_syntax = TestSyntaxValidators()
    test_syntax.test_json_syntax_validator_valid_json()
    test_syntax.test_json_syntax_validator_ai_explanation_detection()
    print("✅ Syntax validation tests passed")
    
    # Test auto-fix engine
    test_autofix = TestAutoFixEngine()
    test_autofix.test_json_auto_fix_from_code_block()
    test_autofix.test_yaml_tabs_auto_fix()
    print("✅ Auto-fix tests passed")
    
    # Test integration scenario
    test_integration = TestIntegrationScenarios()
    test_integration.test_music_production_app_scenario()
    print("✅ Integration tests passed")
    
    print("🎉 All tests completed successfully!")
    print("\\nSnapInfra validation system is ready for production use!")