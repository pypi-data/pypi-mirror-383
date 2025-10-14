"""Terraform configuration parser for diagram generation."""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..models import Component, Connection, DiagramData


@dataclass
class TerraformResource:
    """Represents a Terraform resource."""
    
    type: str
    name: str
    config: Dict[str, Any]
    line_number: int


class TerraformParser:
    """Parser for Terraform configuration files."""
    
    def __init__(self):
        self.resources: List[TerraformResource] = []
    
    def parse(self, content: str) -> DiagramData:
        """Parse Terraform content and return diagram data."""
        self.resources = []
        self._extract_resources(content)
        
        components = self._create_components()
        connections = self._create_connections()
        
        return DiagramData(
            components=components,
            connections=connections,
            metadata={'parser': 'terraform'}
        )
    
    def _extract_resources(self, content: str) -> None:
        """Extract Terraform resources from content."""
        lines = content.split('\n')
        current_resource = None
        brace_count = 0
        config_lines = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Look for resource declarations
            resource_match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{', stripped)
            if resource_match:
                resource_type = resource_match.group(1)
                resource_name = resource_match.group(2)
                current_resource = {
                    'type': resource_type,
                    'name': resource_name,
                    'line': i
                }
                brace_count = 1
                config_lines = []
                continue
            
            if current_resource:
                # Count braces to track resource block
                brace_count += stripped.count('{') - stripped.count('}')
                
                if brace_count > 0:
                    config_lines.append(stripped)
                else:
                    # End of resource block
                    config = self._parse_config_lines(config_lines)
                    self.resources.append(TerraformResource(
                        type=current_resource['type'],
                        name=current_resource['name'],
                        config=config,
                        line_number=current_resource['line']
                    ))
                    current_resource = None
    
    def _parse_config_lines(self, lines: List[str]) -> Dict[str, Any]:
        """Parse configuration lines into a dictionary."""
        config = {}
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                config[key] = value
        return config
    
    def _create_components(self) -> List[Component]:
        """Create diagram components from Terraform resources."""
        components = []
        
        for resource in self.resources:
            component = Component(
                id=f"{resource.type}.{resource.name}",
                name=resource.name,
                type=resource.type,
                properties=resource.config
            )
            components.append(component)
        
        return components
    
    def _create_connections(self) -> List[Connection]:
        """Create connections based on resource dependencies."""
        connections = []
        
        # Simple connection logic based on common reference patterns
        for resource in self.resources:
            for key, value in resource.config.items():
                if isinstance(value, str):
                    # Look for references to other resources
                    ref_match = re.search(r'\$\{([^}]+)\}', value)
                    if ref_match:
                        ref = ref_match.group(1)
                        if '.' in ref:
                            target_id = ref
                            source_id = f"{resource.type}.{resource.name}"
                            
                            connection = Connection(
                                source=source_id,
                                target=target_id,
                                type="reference",
                                properties={'via': key}
                            )
                            connections.append(connection)
        
        return connections