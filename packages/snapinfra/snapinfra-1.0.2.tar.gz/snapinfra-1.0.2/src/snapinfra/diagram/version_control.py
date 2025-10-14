"""Diagram version control functionality."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import os

from .models import Diagram


@dataclass
class DiagramVersion:
    """Represents a version of a diagram."""
    
    version_number: int
    user_id: str
    message: str
    diagram: Diagram
    timestamp: datetime = field(default_factory=datetime.now)
    changes: List[str] = field(default_factory=list)


@dataclass
class DiagramChange:
    """Represents a change to a diagram."""
    
    id: str
    diagram_id: str
    user_id: str
    change_type: str
    before: Optional[Dict[str, Any]]
    after: Optional[Dict[str, Any]]
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class DiagramVersionControl:
    """Manages diagram versioning."""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path('./diagram_storage')
        self.storage_dir.mkdir(exist_ok=True)
        
        self.versions: Dict[str, List[DiagramVersion]] = {}
        self.changes: Dict[str, List[DiagramChange]] = {}
        self._load_existing_data()
    
    def _load_existing_data(self) -> None:
        """Load existing version control data from storage."""
        # In a real implementation, this would load from persistent storage
        pass
    
    def create_version(
        self, 
        diagram: Diagram, 
        user_id: str, 
        message: str,
        changes: List[str] = None
    ) -> DiagramVersion:
        """Create a new version of a diagram."""
        diagram_id = diagram.id
        
        if diagram_id not in self.versions:
            self.versions[diagram_id] = []
        
        version_number = len(self.versions[diagram_id]) + 1
        version = DiagramVersion(
            version_number=version_number,
            user_id=user_id,
            message=message,
            diagram=diagram,
            changes=changes or []
        )
        
        self.versions[diagram_id].append(version)
        return version
    
    def save_version_snapshot(self, diagram: Diagram, version_number: int) -> None:
        """Save a snapshot of a diagram version to storage."""
        # In a real implementation, this would save to persistent storage
        pass
    
    def record_change(
        self,
        diagram_id: str,
        user_id: str,
        change_type: str,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None,
        description: str = ""
    ) -> DiagramChange:
        """Record a change to a diagram."""
        import uuid
        
        change = DiagramChange(
            id=str(uuid.uuid4()),
            diagram_id=diagram_id,
            user_id=user_id,
            change_type=change_type,
            before=before,
            after=after,
            description=description
        )
        
        if diagram_id not in self.changes:
            self.changes[diagram_id] = []
        
        self.changes[diagram_id].append(change)
        return change
    
    def get_versions(self, diagram_id: str) -> List[DiagramVersion]:
        """Get all versions of a diagram."""
        return self.versions.get(diagram_id, [])
    
    def get_changes(self, diagram_id: str) -> List[DiagramChange]:
        """Get all changes for a diagram."""
        return self.changes.get(diagram_id, [])
    
    def get_user_changes(self, diagram_id: str, user_id: str) -> List[DiagramChange]:
        """Get changes made by a specific user."""
        all_changes = self.get_changes(diagram_id)
        return [c for c in all_changes if c.user_id == user_id]
    
    def get_collaboration_stats(self, diagram_id: str) -> Dict[str, Any]:
        """Get collaboration statistics for a diagram."""
        versions = self.get_versions(diagram_id)
        changes = self.get_changes(diagram_id)
        
        users = set()
        user_activity = {}
        
        for version in versions:
            users.add(version.user_id)
            user_activity[version.user_id] = user_activity.get(version.user_id, 0) + 1
        
        for change in changes:
            users.add(change.user_id)
            user_activity[change.user_id] = user_activity.get(change.user_id, 0) + 1
        
        return {
            'total_versions': len(versions),
            'total_changes': len(changes),
            'unique_contributors': len(users),
            'user_activity': user_activity
        }
    
    def compare_versions(
        self, 
        diagram_id: str, 
        version1: int, 
        version2: int
    ) -> Dict[str, Any]:
        """Compare two versions of a diagram."""
        versions = self.get_versions(diagram_id)
        
        v1 = next((v for v in versions if v.version_number == version1), None)
        v2 = next((v for v in versions if v.version_number == version2), None)
        
        if not v1 or not v2:
            raise ValueError("One or both versions not found")
        
        # Get changes between versions
        changes_between = [
            c for c in self.get_changes(diagram_id)
            if v1.timestamp <= c.timestamp <= v2.timestamp
        ]
        
        return {
            'version1': {
                'version_number': v1.version_number,
                'user_id': v1.user_id,
                'message': v1.message,
                'timestamp': v1.timestamp.isoformat()
            },
            'version2': {
                'version_number': v2.version_number,
                'user_id': v2.user_id,
                'message': v2.message,
                'timestamp': v2.timestamp.isoformat()
            },
            'total_changes': len(changes_between),
            'changes': [
                {
                    'type': c.change_type,
                    'user': c.user_id,
                    'description': c.description,
                    'timestamp': c.timestamp.isoformat()
                }
                for c in changes_between
            ]
        }
    
    def cleanup_old_data(
        self, 
        diagram_id: str, 
        keep_versions: int = 10, 
        keep_changes: int = 100
    ) -> None:
        """Clean up old versions and changes."""
        # Clean up old versions
        if diagram_id in self.versions:
            versions = self.versions[diagram_id]
            if len(versions) > keep_versions:
                # Keep the most recent versions
                versions_to_keep = sorted(versions, key=lambda v: v.timestamp)[-keep_versions:]
                self.versions[diagram_id] = versions_to_keep
        
        # Clean up old changes  
        if diagram_id in self.changes:
            changes = self.changes[diagram_id]
            if len(changes) > keep_changes:
                # Keep the most recent changes
                changes_to_keep = sorted(changes, key=lambda c: c.timestamp)[-keep_changes:]
                self.changes[diagram_id] = changes_to_keep
