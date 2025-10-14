"""API server and client for diagram operations."""

from typing import Dict, List, Optional, Any
import json
import requests
from dataclasses import dataclass

from .models import Diagram


@dataclass
class APIResponse:
    """API response wrapper."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class APIClient:
    """Client for diagram API operations."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    def create_diagram(self, data: Dict[str, Any]) -> APIResponse:
        """Create a new diagram."""
        try:
            response = requests.post(f"{self.base_url}/diagrams", json=data)
            response.raise_for_status()
            return APIResponse(success=True, data=response.json())
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def get_diagram(self, diagram_id: str) -> APIResponse:
        """Get a diagram by ID."""
        try:
            response = requests.get(f"{self.base_url}/diagrams/{diagram_id}")
            response.raise_for_status()
            return APIResponse(success=True, data=response.json())
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def update_diagram(self, diagram_id: str, data: Dict[str, Any]) -> APIResponse:
        """Update a diagram."""
        try:
            response = requests.put(f"{self.base_url}/diagrams/{diagram_id}", json=data)
            response.raise_for_status()
            return APIResponse(success=True, data=response.json())
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def delete_diagram(self, diagram_id: str) -> APIResponse:
        """Delete a diagram."""
        try:
            response = requests.delete(f"{self.base_url}/diagrams/{diagram_id}")
            response.raise_for_status()
            return APIResponse(success=True, data={'deleted': True})
        except Exception as e:
            return APIResponse(success=False, error=str(e))


class MockAPIServer:
    """Mock API server for testing."""
    
    def __init__(self):
        self.diagrams: Dict[str, Dict[str, Any]] = {}
        self.shares: Dict[str, Dict[str, Any]] = {}
        self._running = False
        
    def start(self) -> None:
        """Start the mock server."""
        self._running = True
        
    def stop(self) -> None:
        """Stop the mock server."""
        self._running = False
        
    def create_diagram(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a diagram."""
        import uuid
        diagram_id = str(uuid.uuid4())
        diagram_data = {
            'id': diagram_id,
            **data,
            'created_at': '2023-01-01T00:00:00Z'
        }
        self.diagrams[diagram_id] = diagram_data
        return diagram_data
        
    def get_diagram(self, diagram_id: str) -> Optional[Dict[str, Any]]:
        """Get a diagram by ID."""
        return self.diagrams.get(diagram_id)
        
    def update_diagram(self, diagram_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a diagram."""
        if diagram_id in self.diagrams:
            self.diagrams[diagram_id].update(data)
            return self.diagrams[diagram_id]
        return None
        
    def delete_diagram(self, diagram_id: str) -> bool:
        """Delete a diagram."""
        if diagram_id in self.diagrams:
            del self.diagrams[diagram_id]
            return True
        return False
        
    def create_share(self, diagram_id: str, permissions: str) -> Dict[str, Any]:
        """Create a diagram share."""
        import uuid
        share_id = str(uuid.uuid4())
        share_data = {
            'share_id': share_id,
            'diagram_id': diagram_id,
            'permissions': permissions,
            'created_at': '2023-01-01T00:00:00Z'
        }
        self.shares[share_id] = share_data
        return share_data