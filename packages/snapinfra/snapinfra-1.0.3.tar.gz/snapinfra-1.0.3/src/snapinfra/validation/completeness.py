"""Completeness validation to ensure all referenced components are implemented."""

import ast
import json
import re
from typing import Dict, List, Set, Optional, Tuple, Any
from pathlib import Path

from .core import BaseValidator, ValidationResult, ValidationSeverity


class ComponentReference:
    """Represents a reference to a component that should be implemented."""
    
    def __init__(self, name: str, type: str, file_path: str, line_number: int):
        self.name = name
        self.type = type  # 'function', 'class', 'component', 'api_endpoint', 'file'
        self.file_path = file_path
        self.line_number = line_number
    
    def __str__(self):
        return f"{self.type}:{self.name} in {self.file_path}:{self.line_number}"


class ComponentImplementation:
    """Represents an implemented component."""
    
    def __init__(self, name: str, type: str, file_path: str, line_number: int):
        self.name = name
        self.type = type
        self.file_path = file_path
        self.line_number = line_number
    
    def __str__(self):
        return f"{self.type}:{self.name} implemented in {self.file_path}:{self.line_number}"


class CompletenessValidator(BaseValidator):
    """Validates that all referenced components are implemented."""
    
    def __init__(self):
        super().__init__("completeness_validator")
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        """Validate completeness of component implementations."""
        result = ValidationResult()
        
        # Extract all references and implementations
        references = self._extract_all_references(files)
        implementations = self._extract_all_implementations(files)
        
        # Check for missing implementations
        self._check_missing_implementations(references, implementations, result)
        
        # Check for unreferenced implementations (dead code)
        self._check_unreferenced_implementations(references, implementations, result)
        
        return result
    
    def _extract_all_references(self, files: Dict[str, str]) -> List[ComponentReference]:
        """Extract all component references from files."""
        references = []
        
        for file_path, content in files.items():
            if file_path.endswith('.py'):
                references.extend(self._extract_python_references(file_path, content))
            elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                references.extend(self._extract_javascript_references(file_path, content))
        
        return references
    
    def _extract_all_implementations(self, files: Dict[str, str]) -> List[ComponentImplementation]:
        """Extract all component implementations from files."""
        implementations = []
        
        for file_path, content in files.items():
            if file_path.endswith('.py'):
                implementations.extend(self._extract_python_implementations(file_path, content))
            elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                implementations.extend(self._extract_javascript_implementations(file_path, content))
        
        return implementations
    
    def _extract_python_references(self, file_path: str, content: str) -> List[ComponentReference]:
        """Extract Python component references."""
        references = []
        lines = content.split('\\n')
        
        for line_num, line in enumerate(lines, 1):
            # Function calls
            func_calls = re.findall(r'(\\w+)\\s*\\(', line)
            for func_name in func_calls:
                if not func_name in ['print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set']:
                    references.append(ComponentReference(func_name, 'function', file_path, line_num))
            
            # Class instantiations
            class_insts = re.findall(r'(\\w+)\\s*\\(.*\\)', line)
            for class_name in class_insts:
                if class_name.istitle():  # Likely a class if starts with capital
                    references.append(ComponentReference(class_name, 'class', file_path, line_num))
        
        return references
    
    def _extract_javascript_references(self, file_path: str, content: str) -> List[ComponentReference]:
        """Extract JavaScript component references."""
        references = []
        lines = content.split('\\n')
        
        for line_num, line in enumerate(lines, 1):
            # React component references in JSX
            jsx_components = re.findall(r'<(\\w+)[^>]*>', line)
            for component in jsx_components:
                if component.istitle() and component not in ['Html', 'Head', 'Body', 'Div']:
                    references.append(ComponentReference(component, 'component', file_path, line_num))
            
            # Function calls
            func_calls = re.findall(r'(\\w+)\\s*\\(', line)
            for func_name in func_calls:
                if not func_name in ['console', 'require', 'import', 'export', 'return']:
                    references.append(ComponentReference(func_name, 'function', file_path, line_num))
        
        return references
    
    def _extract_python_implementations(self, file_path: str, content: str) -> List[ComponentImplementation]:
        """Extract Python implementations."""
        implementations = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    implementations.append(
                        ComponentImplementation(node.name, 'function', file_path, node.lineno)
                    )
                elif isinstance(node, ast.ClassDef):
                    implementations.append(
                        ComponentImplementation(node.name, 'class', file_path, node.lineno)
                    )
        
        except SyntaxError:
            # Fallback to regex
            lines = content.split('\\n')
            for line_num, line in enumerate(lines, 1):
                # Function definitions
                func_match = re.match(r'\\s*def\\s+(\\w+)', line)
                if func_match:
                    implementations.append(
                        ComponentImplementation(func_match.group(1), 'function', file_path, line_num)
                    )
                
                # Class definitions
                class_match = re.match(r'\\s*class\\s+(\\w+)', line)
                if class_match:
                    implementations.append(
                        ComponentImplementation(class_match.group(1), 'class', file_path, line_num)
                    )
        
        return implementations
    
    def _extract_javascript_implementations(self, file_path: str, content: str) -> List[ComponentImplementation]:
        """Extract JavaScript implementations."""
        implementations = []
        lines = content.split('\\n')
        
        for line_num, line in enumerate(lines, 1):
            # Function declarations and expressions
            func_patterns = [
                r'function\\s+(\\w+)',
                r'const\\s+(\\w+)\\s*=\\s*(?:async\\s+)?function',
                r'const\\s+(\\w+)\\s*=\\s*(?:async\\s+)?\\(',
                r'let\\s+(\\w+)\\s*=\\s*(?:async\\s+)?function',
                r'var\\s+(\\w+)\\s*=\\s*(?:async\\s+)?function',
                r'export\\s+function\\s+(\\w+)',
                r'exports\\.(\\w+)\\s*=',
            ]
            
            for pattern in func_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    implementations.append(
                        ComponentImplementation(match, 'function', file_path, line_num)
                    )
            
            # Class declarations
            class_match = re.search(r'class\\s+(\\w+)', line)
            if class_match:
                implementations.append(
                    ComponentImplementation(class_match.group(1), 'class', file_path, line_num)
                )
            
            # React component (arrow functions)
            react_component = re.search(r'const\\s+(\\w+)\\s*=\\s*\\([^)]*\\)\\s*=>', line)
            if react_component and react_component.group(1).istitle():
                implementations.append(
                    ComponentImplementation(react_component.group(1), 'component', file_path, line_num)
                )
        
        return implementations
    
    def _check_missing_implementations(self, references: List[ComponentReference], 
                                     implementations: List[ComponentImplementation], 
                                     result: ValidationResult):
        """Check for references without implementations."""
        impl_names = {(impl.name, impl.type) for impl in implementations}
        
        missing_refs = {}
        for ref in references:
            ref_key = (ref.name, ref.type)
            if ref_key not in impl_names:
                if ref_key not in missing_refs:
                    missing_refs[ref_key] = []
                missing_refs[ref_key].append(ref)
        
        for (name, type_), ref_list in missing_refs.items():
            # Skip common built-ins and likely external references
            if self._is_likely_external(name, type_):
                continue
            
            # Create issue for missing implementation
            first_ref = ref_list[0]
            issue = self.create_issue(
                severity=ValidationSeverity.ERROR,
                message=f"Referenced {type_} '{name}' is not implemented (referenced {len(ref_list)} times)",
                file_path=first_ref.file_path,
                line_number=first_ref.line_number,
                rule_id="missing_implementation",
                suggestion=f"Implement {type_} '{name}' or check if import is missing"
            )
            result.add_issue(issue)
    
    def _check_unreferenced_implementations(self, references: List[ComponentReference], 
                                          implementations: List[ComponentImplementation], 
                                          result: ValidationResult):
        """Check for implementations without references (potential dead code)."""
        ref_names = {(ref.name, ref.type) for ref in references}
        
        for impl in implementations:
            impl_key = (impl.name, impl.type)
            if impl_key not in ref_names:
                # Skip entry points and common patterns
                if self._is_likely_entry_point(impl.name, impl.type, impl.file_path):
                    continue
                
                issue = self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Implemented {impl.type} '{impl.name}' appears to be unused",
                    file_path=impl.file_path,
                    line_number=impl.line_number,
                    rule_id="unreferenced_implementation",
                    suggestion=f"Consider removing unused {impl.type} or ensure it's properly exported/called"
                )
                result.add_issue(issue)
    
    def _is_likely_external(self, name: str, type_: str) -> bool:
        """Check if a reference is likely to an external library or built-in."""
        # Python built-ins and common libraries
        if type_ == 'function':
            common_functions = {
                'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
                'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed',
                'open', 'input', 'abs', 'max', 'min', 'sum', 'any', 'all',
                # Common library functions
                'json', 'yaml', 'requests', 'datetime', 'os', 'sys', 'path'
            }
            return name in common_functions
        
        # Common React/JS components and functions
        if type_ == 'component':
            common_components = {
                'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'a', 'img', 'button', 'input', 'form', 'ul', 'li', 'table', 'tr', 'td'
            }
            return name.lower() in common_components
        
        return False
    
    def _is_likely_entry_point(self, name: str, type_: str, file_path: str) -> bool:
        """Check if an implementation is likely an entry point."""
        # Main functions
        if name in ['main', '__init__', 'index', 'app']:
            return True
        
        # Test functions
        if name.startswith('test_') or name.startswith('Test'):
            return True
        
        # React components at top level
        if type_ == 'component' and name.istitle():
            return True
        
        # Functions in main files
        if file_path.endswith(('main.py', 'index.js', 'app.py', 'server.js')):
            return True
        
        return False


class APIConsistencyValidator(BaseValidator):
    """Validates API endpoint consistency between frontend and backend."""
    
    def __init__(self):
        super().__init__("api_consistency_validator")
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        """Validate API consistency."""
        result = ValidationResult()
        
        # Extract API calls from frontend
        api_calls = self._extract_api_calls(files)
        
        # Extract API endpoints from backend
        api_endpoints = self._extract_api_endpoints(files)
        
        # Check for missing endpoints
        self._check_missing_endpoints(api_calls, api_endpoints, result)
        
        # Check for unused endpoints
        self._check_unused_endpoints(api_calls, api_endpoints, result)
        
        return result
    
    def _extract_api_calls(self, files: Dict[str, str]) -> List[Tuple[str, str, str, int]]:
        """Extract API calls from frontend files."""
        api_calls = []
        
        for file_path, content in files.items():
            if not file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                continue
            
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                # Common API call patterns
                patterns = [
                    r'fetch\s*\(\s*[\'"](.+?)[\'"]',  # fetch('url')
                    r'axios\.get\s*\(\s*[\'"](.+?)[\'"]',  # axios.get('url')  
                    r'axios\.post\s*\(\s*[\'"](.+?)[\'"]',  # axios.post('url')
                    r'axios\.put\s*\(\s*[\'"](.+?)[\'"]',   # axios.put('url')
                    r'axios\.delete\s*\(\s*[\'"](.+?)[\'"]',  # axios.delete('url')
                    r'\$\.get\s*\(\s*[\'"](.+?)[\'"]',  # jQuery $.get('url')
                    r'\$\.post\s*\(\s*[\'"](.+?)[\'"]',  # jQuery $.post('url')
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, line)
                    for url in matches:
                        # Extract method from pattern
                        if 'post' in pattern:
                            method = 'POST'
                        elif 'put' in pattern:
                            method = 'PUT'
                        elif 'delete' in pattern:
                            method = 'DELETE'
                        else:
                            method = 'GET'
                        
                        api_calls.append((method, url, file_path, line_num))
        
        return api_calls
    
    def _extract_api_endpoints(self, files: Dict[str, str]) -> List[Tuple[str, str, str, int]]:
        """Extract API endpoints from backend files."""
        endpoints = []
        
        for file_path, content in files.items():
            if file_path.endswith('.py'):
                endpoints.extend(self._extract_python_endpoints(file_path, content))
            elif file_path.endswith('.js'):
                endpoints.extend(self._extract_javascript_endpoints(file_path, content))
        
        return endpoints
    
    def _extract_python_endpoints(self, file_path: str, content: str) -> List[Tuple[str, str, str, int]]:
        """Extract Python API endpoints (Flask, FastAPI, Django)."""
        endpoints = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Flask routes
            flask_match = re.search(r'@app\\.route\\s*\\(\\s*[\\'"](.*?)[\\'"'].*?methods\\s*=\\s*\\[\\s*[\\'"](.*?)[\\'"']', line)
            if flask_match:
                endpoints.append((flask_match.group(2).upper(), flask_match.group(1), file_path, line_num))
                continue
            
            # FastAPI endpoints
            fastapi_patterns = [
                (r'@app\\.get\\s*\\(\\s*[\\'"](.*?)[\\'"']', 'GET'),
                (r'@app\\.post\\s*\\(\\s*[\\'"](.*?)[\\'"']', 'POST'),
                (r'@app\\.put\\s*\\(\\s*[\\'"](.*?)[\\'"']', 'PUT'),
                (r'@app\\.delete\\s*\\(\\s*[\\'"](.*?)[\\'"']', 'DELETE'),
            ]
            
            for pattern, method in fastapi_patterns:
                match = re.search(pattern, line)
                if match:
                    endpoints.append((method, match.group(1), file_path, line_num))
        
        return endpoints
    
    def _extract_javascript_endpoints(self, file_path: str, content: str) -> List[Tuple[str, str, str, int]]:
        """Extract JavaScript API endpoints (Express, etc.)."""
        endpoints = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Express routes
            express_patterns = [
                (r'app\\.get\\s*\\(\\s*[\\'"](.*?)[\\'"']', 'GET'),
                (r'app\\.post\\s*\\(\\s*[\\'"](.*?)[\\'"']', 'POST'),
                (r'app\\.put\\s*\\(\\s*[\\'"](.*?)[\\'"']', 'PUT'),
                (r'app\\.delete\\s*\\(\\s*[\\'"](.*?)[\\'"']', 'DELETE'),
                (r'router\\.get\\s*\\(\\s*[\\'"](.*?)[\\'"']', 'GET'),
                (r'router\\.post\\s*\\(\\s*[\\'"](.*?)[\\'"']', 'POST'),
            ]
            
            for pattern, method in express_patterns:
                match = re.search(pattern, line)
                if match:
                    endpoints.append((method, match.group(1), file_path, line_num))
        
        return endpoints
    
    def _check_missing_endpoints(self, api_calls: List[Tuple[str, str, str, int]], 
                                api_endpoints: List[Tuple[str, str, str, int]], 
                                result: ValidationResult):
        """Check for API calls without corresponding endpoints."""
        endpoint_set = {(method, self._normalize_url(url)) for method, url, _, _ in api_endpoints}
        
        for method, url, file_path, line_num in api_calls:
            normalized_url = self._normalize_url(url)
            if (method, normalized_url) not in endpoint_set:
                # Skip external URLs
                if self._is_external_url(url):
                    continue
                
                issue = self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"API call to {method} {url} has no corresponding backend endpoint",
                    file_path=file_path,
                    line_number=line_num,
                    rule_id="missing_api_endpoint",
                    suggestion=f"Implement {method} endpoint for {url} in backend"
                )
                result.add_issue(issue)
    
    def _check_unused_endpoints(self, api_calls: List[Tuple[str, str, str, int]], 
                               api_endpoints: List[Tuple[str, str, str, int]], 
                               result: ValidationResult):
        """Check for API endpoints without corresponding calls."""
        call_set = {(method, self._normalize_url(url)) for method, url, _, _ in api_calls}
        
        for method, url, file_path, line_num in api_endpoints:
            normalized_url = self._normalize_url(url)
            if (method, normalized_url) not in call_set:
                issue = self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message=f"API endpoint {method} {url} appears to be unused",
                    file_path=file_path,
                    line_number=line_num,
                    rule_id="unused_api_endpoint",
                    suggestion=f"Consider removing unused endpoint or ensure it's called from frontend"
                )
                result.add_issue(issue)
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison."""
        # Remove leading/trailing slashes and query parameters
        url = url.strip('/').split('?')[0]
        # Replace path parameters with placeholders
        url = re.sub(r'\\{\\w+\\}', '{param}', url)  # {id} -> {param}
        url = re.sub(r':\\w+', ':param', url)  # :id -> :param
        return url
    
    def _is_external_url(self, url: str) -> bool:
        """Check if URL is external."""
        return (url.startswith('http://') or 
                url.startswith('https://') or 
                url.startswith('//') or
                'api.example.com' in url)