"""Import resolution validation for various programming languages."""

import ast
import re
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path

from .core import BaseValidator, ValidationResult, ValidationSeverity


class ImportExtractor:
    """Extract import statements from different file types."""
    
    @staticmethod
    def extract_python_imports(content: str, file_path: str) -> List[Tuple[str, int]]:
        """Extract Python import statements."""
        imports = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append((alias.name, node.lineno))
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Handle relative imports
                        if node.level > 0:
                            # Relative import
                            base_path = Path(file_path).parent
                            for _ in range(node.level - 1):
                                base_path = base_path.parent
                            
                            if node.module:
                                import_path = str(base_path / node.module.replace('.', '/'))
                            else:
                                import_path = str(base_path)
                        else:
                            # Absolute import
                            import_path = node.module.replace('.', '/')
                        
                        imports.append((import_path, node.lineno))
                        
        except SyntaxError:
            # Fallback to regex-based extraction if AST parsing fails
            imports.extend(ImportExtractor._extract_python_imports_regex(content))
            
        return imports
    
    @staticmethod
    def _extract_python_imports_regex(content: str) -> List[Tuple[str, int]]:
        """Fallback regex-based Python import extraction."""
        imports = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Match import statements
            import_match = re.match(r'\\s*import\\s+([\\w\\.]+)', line)
            if import_match:
                imports.append((import_match.group(1).replace('.', '/'), line_num))
            
            # Match from...import statements
            from_match = re.match(r'\\s*from\\s+([\\w\\.]+)\\s+import', line)
            if from_match:
                imports.append((from_match.group(1).replace('.', '/'), line_num))
        
        return imports
    
    @staticmethod
    def extract_javascript_imports(content: str, file_path: str) -> List[Tuple[str, int]]:
        """Extract JavaScript/TypeScript import statements."""
        imports = []
        lines = content.split('\\n')
        
        for line_num, line in enumerate(lines, 1):
            # Match ES6 imports
            import_patterns = [
                r'import\\s+.*?\\s+from\\s+[\'"]([^\'"]+)[\'"]',
                r'import\\s+[\'"]([^\'"]+)[\'"]',
                r'require\\s*\\(\\s*[\'"]([^\'"]+)[\'"]\\s*\\)',
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    # Resolve relative imports
                    if match.startswith('./') or match.startswith('../'):
                        base_path = Path(file_path).parent
                        import_path = str((base_path / match).resolve())
                    else:
                        import_path = match
                    
                    imports.append((import_path, line_num))
        
        return imports
    
    @staticmethod
    def extract_go_imports(content: str, file_path: str) -> List[Tuple[str, int]]:
        """Extract Go import statements."""
        imports = []
        lines = content.split('\\n')
        
        in_import_block = False
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Single line import
            single_match = re.match(r'import\\s+"([^"]+)"', stripped)
            if single_match:
                imports.append((single_match.group(1), line_num))
                continue
            
            # Multi-line import block
            if stripped == 'import (':
                in_import_block = True
                continue
            
            if in_import_block:
                if stripped == ')':
                    in_import_block = False
                    continue
                
                import_match = re.match(r'"([^"]+)"', stripped)
                if import_match:
                    imports.append((import_match.group(1), line_num))
        
        return imports


class ImportValidator(BaseValidator):
    """Validates that all imports resolve to existing files."""
    
    def __init__(self):
        super().__init__("import_validator")
        self.extractor = ImportExtractor()
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        """Validate all import statements."""
        result = ValidationResult()
        
        # Create a set of available files for quick lookup
        available_files = self._build_file_index(files)
        
        # Check each file's imports
        for file_path, content in files.items():
            file_result = self._validate_file_imports(file_path, content, available_files)
            result.merge(file_result)
        
        return result
    
    def _build_file_index(self, files: Dict[str, str]) -> Set[str]:
        """Build an index of all available files and their possible import paths."""
        available = set()
        
        for file_path in files.keys():
            path_obj = Path(file_path)
            
            # Add the file path as-is
            available.add(file_path)
            
            # Add without extension for Python/JS imports
            available.add(str(path_obj.with_suffix('')))
            
            # Add as module path (replace / with .)
            module_path = str(path_obj.with_suffix('')).replace('/', '.').replace('\\\\', '.')
            available.add(module_path)
            
            # Add relative paths from different starting points
            parts = path_obj.parts
            for i in range(len(parts)):
                partial_path = Path(*parts[i:])
                available.add(str(partial_path))
                available.add(str(partial_path.with_suffix('')))
        
        return available
    
    def _validate_file_imports(self, file_path: str, content: str, available_files: Set[str]) -> ValidationResult:
        """Validate imports for a single file."""
        result = ValidationResult()
        
        # Determine file type and extract imports accordingly
        if file_path.endswith('.py'):
            imports = self.extractor.extract_python_imports(content, file_path)
        elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            imports = self.extractor.extract_javascript_imports(content, file_path)
        elif file_path.endswith('.go'):
            imports = self.extractor.extract_go_imports(content, file_path)
        else:
            return result  # Skip unsupported file types
        
        # Check each import
        for import_path, line_num in imports:
            if not self._import_exists(import_path, available_files, file_path):
                # Skip standard library and external package imports
                if not self._is_external_import(import_path, file_path):
                    issue = self.create_issue(
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Import '{import_path}' cannot be resolved to an existing file",
                        file_path=file_path,
                        line_number=line_num,
                        rule_id="import_not_found",
                        suggestion=f"Ensure the file '{import_path}' exists or check the import path",
                        auto_fixable=False
                    )
                    result.add_issue(issue)
        
        return result
    
    def _import_exists(self, import_path: str, available_files: Set[str], current_file: str) -> bool:
        """Check if an import path exists in the available files."""
        # Try the import path as-is
        if import_path in available_files:
            return True
        
        # Try with common extensions
        extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.go']
        for ext in extensions:
            if f"{import_path}{ext}" in available_files:
                return True
        
        # Try as index file
        index_files = ['index.js', 'index.ts', '__init__.py']
        for index_file in index_files:
            if f"{import_path}/{index_file}" in available_files:
                return True
        
        # Try relative to current file
        current_dir = str(Path(current_file).parent)
        relative_path = f"{current_dir}/{import_path}"
        if relative_path in available_files:
            return True
        
        return False
    
    def _is_external_import(self, import_path: str, file_path: str) -> bool:
        """Check if an import is likely an external package/standard library."""
        # Python standard library and common packages
        if file_path.endswith('.py'):
            python_stdlib = {
                'os', 'sys', 'json', 'yaml', 'requests', 'numpy', 'pandas',
                'django', 'flask', 'fastapi', 'typing', 'pathlib', 're',
                'datetime', 'collections', 'functools', 'itertools'
            }
            first_part = import_path.split('.')[0].split('/')[0]
            return first_part in python_stdlib
        
        # JavaScript/TypeScript common packages
        elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            js_packages = {
                'react', 'vue', 'angular', 'express', 'lodash', 'axios',
                'moment', 'jquery', 'bootstrap', 'webpack', 'babel'
            }
            # Node.js built-in modules
            if not (import_path.startswith('./') or import_path.startswith('../')):
                first_part = import_path.split('/')[0]
                return first_part in js_packages or not '.' in first_part
        
        return False


class CrossReferenceValidator(BaseValidator):
    """Validates cross-references between files (function calls, class usage, etc.)."""
    
    def __init__(self):
        super().__init__("cross_reference_validator")
    
    def validate(self, files: Dict[str, str]) -> ValidationResult:
        """Validate cross-references between files."""
        result = ValidationResult()
        
        # Build symbol index
        symbol_index = self._build_symbol_index(files)
        
        # Check references in each file
        for file_path, content in files.items():
            file_result = self._validate_file_references(file_path, content, symbol_index, files)
            result.merge(file_result)
        
        return result
    
    def _build_symbol_index(self, files: Dict[str, str]) -> Dict[str, Set[str]]:
        """Build index of available symbols (functions, classes) in each file."""
        index = {}
        
        for file_path, content in files.items():
            symbols = set()
            
            if file_path.endswith('.py'):
                symbols.update(self._extract_python_symbols(content))
            elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                symbols.update(self._extract_javascript_symbols(content))
            
            index[file_path] = symbols
        
        return index
    
    def _extract_python_symbols(self, content: str) -> Set[str]:
        """Extract Python function and class names."""
        symbols = set()
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    symbols.add(node.name)
                    
        except SyntaxError:
            # Fallback to regex
            lines = content.split('\\n')
            for line in lines:
                # Function definitions
                func_match = re.match(r'\\s*def\\s+(\\w+)', line)
                if func_match:
                    symbols.add(func_match.group(1))
                
                # Class definitions  
                class_match = re.match(r'\\s*class\\s+(\\w+)', line)
                if class_match:
                    symbols.add(class_match.group(1))
        
        return symbols
    
    def _extract_javascript_symbols(self, content: str) -> Set[str]:
        """Extract JavaScript function and class names."""
        symbols = set()
        lines = content.split('\\n')
        
        for line in lines:
            # Function declarations
            func_patterns = [
                r'function\\s+(\\w+)',
                r'const\\s+(\\w+)\\s*=\\s*(?:async\\s+)?\\(?',
                r'let\\s+(\\w+)\\s*=\\s*(?:async\\s+)?\\(?',
                r'var\\s+(\\w+)\\s*=\\s*(?:async\\s+)?\\(?',
                r'export\\s+function\\s+(\\w+)',
                r'exports\\.(\\w+)\\s*=',
            ]
            
            for pattern in func_patterns:
                matches = re.findall(pattern, line)
                symbols.update(matches)
            
            # Class declarations
            class_match = re.search(r'class\\s+(\\w+)', line)
            if class_match:
                symbols.add(class_match.group(1))
        
        return symbols
    
    def _validate_file_references(self, file_path: str, content: str, symbol_index: Dict[str, Set[str]], files: Dict[str, str]) -> ValidationResult:
        """Validate that referenced symbols exist."""
        result = ValidationResult()
        
        # This is a simplified check - in practice, you'd need more sophisticated
        # analysis to track which imports bring which symbols into scope
        # For now, we'll do basic checks for obvious issues
        
        lines = content.split('\\n')
        for line_num, line in enumerate(lines, 1):
            # Look for function calls that might be missing
            # This is a basic heuristic and would need refinement
            if file_path.endswith('.py'):
                self._check_python_references(file_path, line, line_num, symbol_index, files, result)
            elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                self._check_javascript_references(file_path, line, line_num, symbol_index, files, result)
        
        return result
    
    def _check_python_references(self, file_path: str, line: str, line_num: int, symbol_index: Dict[str, Set[str]], files: Dict[str, str], result: ValidationResult):
        """Check Python function/class references."""
        # Look for calls to functions that might not exist
        # This is a simplified heuristic - real implementation would need import tracking
        pass  # Implementation would be quite complex for a demo
    
    def _check_javascript_references(self, file_path: str, line: str, line_num: int, symbol_index: Dict[str, Set[str]], files: Dict[str, str], result: ValidationResult):
        """Check JavaScript function/class references."""
        # Look for calls to functions that might not exist
        # This is a simplified heuristic - real implementation would need import tracking  
        pass  # Implementation would be quite complex for a demo