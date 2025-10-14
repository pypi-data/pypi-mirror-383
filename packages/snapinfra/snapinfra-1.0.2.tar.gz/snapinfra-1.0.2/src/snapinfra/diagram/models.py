"""Diagram data models."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


@dataclass
class Diagram:
    """Represents a diagram structure."""
    
    name: str
    type: str = "infrastructure"
    content: str = ""
    id: str = ""
    nodes: List['DiagramNode'] = field(default_factory=list)
    edges: List['DiagramEdge'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
    
    def update_content(self, content: str) -> None:
        """Update diagram content."""
        self.content = content
        self.updated_at = datetime.now()
    
    def add_node(self, node: 'DiagramNode') -> None:
        """Add a node to the diagram."""
        self.nodes.append(node)
        self.updated_at = datetime.now()
    
    def add_edge(self, edge: 'DiagramEdge') -> None:
        """Add an edge to the diagram."""
        self.edges.append(edge)
        self.updated_at = datetime.now()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Diagram':
        """Create diagram from dictionary."""
        nodes = [DiagramNode.from_dict(n) for n in data.get('nodes', [])]
        edges = [DiagramEdge.from_dict(e) for e in data.get('edges', [])]
        
        return cls(
            name=data['name'],
            type=data.get('type', 'infrastructure'),
            content=data.get('content', ''),
            id=data.get('id', ''),
            nodes=nodes,
            edges=edges,
            metadata=data.get('metadata', {})
        )


@dataclass
class Component:
    """Represents a diagram component."""
    
    id: str
    name: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    connections: List[str] = field(default_factory=list)


@dataclass
class Connection:
    """Represents a connection between components."""
    
    source: str
    target: str
    type: str = "default"
    properties: Dict[str, Any] = field(default_factory=dict)


class NodeType(Enum):
    """Types of diagram nodes."""
    COMPUTE = "compute"
    DATABASE = "database"
    STORAGE = "storage"
    NETWORK = "network"
    SERVICE = "service"
    GATEWAY = "gateway"
    # AWS Resource Types
    AWS_VPC = "aws_vpc"
    AWS_SUBNET = "aws_subnet"
    AWS_SECURITY_GROUP = "aws_security_group"
    AWS_INTERNET_GATEWAY = "aws_internet_gateway"
    AWS_ROUTE_TABLE = "aws_route_table"
    AWS_EC2 = "aws_ec2"
    AWS_RDS = "aws_rds"
    AWS_S3 = "aws_s3"
    AWS_LAMBDA = "aws_lambda"
    AWS_ELB = "aws_elb"
    AWS_ALB = "aws_alb"


class EdgeType(Enum):
    """Types of diagram edges."""
    CONNECTION = "connection"
    DEPENDENCY = "dependency"
    DATA_FLOW = "data_flow"
    REFERENCE = "reference"
    CONTAINS = "contains"
    ATTACHED_TO = "attached_to"
    ROUTES_TO = "routes_to"


@dataclass
class Position:
    """Position coordinates."""
    x: float
    y: float


@dataclass
class DiagramNode:
    """Represents a diagram node."""
    
    id: str
    type: NodeType
    label: str
    position: Position
    properties: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagramNode':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            type=NodeType(data['type']),
            label=data['label'],
            position=Position(data['position']['x'], data['position']['y']),
            properties=data.get('properties', {})
        )


@dataclass
class DiagramEdge:
    """Represents a diagram edge."""
    
    id: str
    source: str
    target: str
    type: EdgeType
    label: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagramEdge':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            source=data['source'],
            target=data['target'],
            type=EdgeType(data['type']),
            label=data.get('label', ''),
            properties=data.get('properties', {})
        )


@dataclass
class DiagramData:
    """Complete diagram data structure."""
    
    components: List[Component] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
