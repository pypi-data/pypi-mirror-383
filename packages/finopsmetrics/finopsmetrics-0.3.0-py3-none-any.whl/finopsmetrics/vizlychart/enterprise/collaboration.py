"""
Enterprise Collaboration Features
===================================

Multi-user workspace management and collaboration tools for Vizly Enterprise.

Features:
- Workspace management with access control
- Real-time collaboration
- User permissions and roles
- Activity tracking and notifications
- Sharing and commenting
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class WorkspaceRole(Enum):
    """Workspace user roles."""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"


class WorkspaceVisibility(Enum):
    """Workspace visibility levels."""
    PRIVATE = "private"
    TEAM = "team"
    ORGANIZATION = "organization"
    PUBLIC = "public"


@dataclass
class WorkspaceMember:
    """Workspace member information."""
    user_id: str
    username: str
    email: str
    role: WorkspaceRole
    joined_at: datetime = field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    is_active: bool = True


@dataclass
class Workspace:
    """Collaborative workspace for charts and dashboards."""
    workspace_id: str
    name: str
    description: str
    owner_id: str
    visibility: WorkspaceVisibility = WorkspaceVisibility.PRIVATE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    members: List[WorkspaceMember] = field(default_factory=list)
    charts: Set[str] = field(default_factory=set)
    dashboards: Set[str] = field(default_factory=set)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_archived: bool = False


class WorkspaceManager:
    """
    Enterprise workspace management system.

    Manages multi-user workspaces with access control, sharing,
    and collaboration features.

    Features:
    - Create and manage workspaces
    - User access control with roles
    - Sharing and permissions
    - Activity tracking
    - Workspace templates
    """

    def __init__(self):
        """Initialize workspace manager."""
        self._workspaces: Dict[str, Workspace] = {}
        self._user_workspaces: Dict[str, Set[str]] = {}  # user_id -> workspace_ids
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Workspace manager initialized")

    def create_workspace(
        self,
        name: str,
        description: str,
        owner_id: str,
        owner_username: str,
        owner_email: str,
        visibility: WorkspaceVisibility = WorkspaceVisibility.PRIVATE,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Create a new workspace.

        Args:
            name: Workspace name
            description: Workspace description
            owner_id: Owner user ID
            owner_username: Owner username
            owner_email: Owner email
            visibility: Workspace visibility
            tags: Optional tags

        Returns:
            Workspace ID
        """
        workspace_id = str(uuid.uuid4())

        # Create owner as first member
        owner = WorkspaceMember(
            user_id=owner_id,
            username=owner_username,
            email=owner_email,
            role=WorkspaceRole.OWNER,
        )

        workspace = Workspace(
            workspace_id=workspace_id,
            name=name,
            description=description,
            owner_id=owner_id,
            visibility=visibility,
            members=[owner],
            tags=tags or [],
        )

        self._workspaces[workspace_id] = workspace

        # Track user workspaces
        if owner_id not in self._user_workspaces:
            self._user_workspaces[owner_id] = set()
        self._user_workspaces[owner_id].add(workspace_id)

        self.logger.info(f"Created workspace: {workspace_id} ({name})")
        return workspace_id

    def add_member(
        self,
        workspace_id: str,
        user_id: str,
        username: str,
        email: str,
        role: WorkspaceRole = WorkspaceRole.VIEWER,
    ) -> bool:
        """
        Add a member to workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID
            username: Username
            email: Email
            role: User role

        Returns:
            Success status
        """
        if workspace_id not in self._workspaces:
            self.logger.error(f"Workspace not found: {workspace_id}")
            return False

        workspace = self._workspaces[workspace_id]

        # Check if user already a member
        if any(m.user_id == user_id for m in workspace.members):
            self.logger.warning(f"User {user_id} already in workspace {workspace_id}")
            return False

        member = WorkspaceMember(
            user_id=user_id, username=username, email=email, role=role
        )

        workspace.members.append(member)
        workspace.updated_at = datetime.utcnow()

        # Track user workspaces
        if user_id not in self._user_workspaces:
            self._user_workspaces[user_id] = set()
        self._user_workspaces[user_id].add(workspace_id)

        self.logger.info(f"Added user {user_id} to workspace {workspace_id} as {role.value}")
        return True

    def remove_member(self, workspace_id: str, user_id: str) -> bool:
        """Remove a member from workspace."""
        if workspace_id not in self._workspaces:
            return False

        workspace = self._workspaces[workspace_id]

        # Can't remove owner
        if user_id == workspace.owner_id:
            self.logger.error("Cannot remove workspace owner")
            return False

        # Remove member
        workspace.members = [m for m in workspace.members if m.user_id != user_id]
        workspace.updated_at = datetime.utcnow()

        # Update user workspaces
        if user_id in self._user_workspaces:
            self._user_workspaces[user_id].discard(workspace_id)

        self.logger.info(f"Removed user {user_id} from workspace {workspace_id}")
        return True

    def update_member_role(
        self, workspace_id: str, user_id: str, new_role: WorkspaceRole
    ) -> bool:
        """Update a member's role."""
        if workspace_id not in self._workspaces:
            return False

        workspace = self._workspaces[workspace_id]

        # Can't change owner role
        if user_id == workspace.owner_id:
            self.logger.error("Cannot change owner role")
            return False

        for member in workspace.members:
            if member.user_id == user_id:
                member.role = new_role
                workspace.updated_at = datetime.utcnow()
                self.logger.info(
                    f"Updated role for {user_id} in {workspace_id} to {new_role.value}"
                )
                return True

        return False

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID."""
        return self._workspaces.get(workspace_id)

    def list_user_workspaces(self, user_id: str) -> List[Workspace]:
        """List all workspaces for a user."""
        workspace_ids = self._user_workspaces.get(user_id, set())
        return [self._workspaces[wid] for wid in workspace_ids if wid in self._workspaces]

    def add_chart(self, workspace_id: str, chart_id: str) -> bool:
        """Add a chart to workspace."""
        if workspace_id not in self._workspaces:
            return False

        workspace = self._workspaces[workspace_id]
        workspace.charts.add(chart_id)
        workspace.updated_at = datetime.utcnow()
        return True

    def remove_chart(self, workspace_id: str, chart_id: str) -> bool:
        """Remove a chart from workspace."""
        if workspace_id not in self._workspaces:
            return False

        workspace = self._workspaces[workspace_id]
        workspace.charts.discard(chart_id)
        workspace.updated_at = datetime.utcnow()
        return True

    def has_access(
        self, workspace_id: str, user_id: str, required_role: WorkspaceRole
    ) -> bool:
        """Check if user has required access level."""
        if workspace_id not in self._workspaces:
            return False

        workspace = self._workspaces[workspace_id]

        # Find user's role
        user_role = None
        for member in workspace.members:
            if member.user_id == user_id:
                user_role = member.role
                break

        if user_role is None:
            return False

        # Check role hierarchy
        role_hierarchy = {
            WorkspaceRole.OWNER: 5,
            WorkspaceRole.ADMIN: 4,
            WorkspaceRole.EDITOR: 3,
            WorkspaceRole.VIEWER: 2,
            WorkspaceRole.GUEST: 1,
        }

        return role_hierarchy[user_role] >= role_hierarchy[required_role]

    def archive_workspace(self, workspace_id: str) -> bool:
        """Archive a workspace."""
        if workspace_id not in self._workspaces:
            return False

        self._workspaces[workspace_id].is_archived = True
        self._workspaces[workspace_id].updated_at = datetime.utcnow()
        self.logger.info(f"Archived workspace: {workspace_id}")
        return True

    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace."""
        if workspace_id not in self._workspaces:
            return False

        workspace = self._workspaces[workspace_id]

        # Remove from all users
        for member in workspace.members:
            if member.user_id in self._user_workspaces:
                self._user_workspaces[member.user_id].discard(workspace_id)

        del self._workspaces[workspace_id]
        self.logger.info(f"Deleted workspace: {workspace_id}")
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get workspace statistics."""
        active_workspaces = [w for w in self._workspaces.values() if not w.is_archived]

        return {
            "total_workspaces": len(self._workspaces),
            "active_workspaces": len(active_workspaces),
            "archived_workspaces": len(self._workspaces) - len(active_workspaces),
            "total_users": len(self._user_workspaces),
            "total_charts": sum(len(w.charts) for w in self._workspaces.values()),
            "visibility_breakdown": {
                v.value: len([w for w in active_workspaces if w.visibility == v])
                for v in WorkspaceVisibility
            },
        }


@dataclass
class ChartVersion:
    """Chart version snapshot."""
    version_id: str
    chart_id: str
    version_number: int
    created_by: str
    created_at: datetime
    commit_message: str
    chart_data: Dict[str, Any]
    parent_version: Optional[str] = None
    tags: List[str] = field(default_factory=list)


class VisualizationVersionControl:
    """
    Version control system for charts and visualizations.

    Provides Git-like version control for visualizations with:
    - Commit history tracking
    - Branching and merging
    - Rollback capabilities
    - Diff and comparison
    - Tags and releases
    """

    def __init__(self):
        """Initialize version control system."""
        self._versions: Dict[str, List[ChartVersion]] = {}  # chart_id -> versions
        self._tags: Dict[str, Dict[str, str]] = {}  # chart_id -> tag -> version_id
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Visualization version control initialized")

    def commit(
        self,
        chart_id: str,
        chart_data: Dict[str, Any],
        user_id: str,
        message: str,
        parent_version: Optional[str] = None,
    ) -> str:
        """
        Commit a new chart version.

        Args:
            chart_id: Chart identifier
            chart_data: Chart data snapshot
            user_id: User making the commit
            message: Commit message
            parent_version: Parent version ID

        Returns:
            Version ID
        """
        version_id = str(uuid.uuid4())

        if chart_id not in self._versions:
            self._versions[chart_id] = []
            version_number = 1
        else:
            version_number = len(self._versions[chart_id]) + 1

        version = ChartVersion(
            version_id=version_id,
            chart_id=chart_id,
            version_number=version_number,
            created_by=user_id,
            created_at=datetime.utcnow(),
            commit_message=message,
            chart_data=chart_data.copy(),
            parent_version=parent_version,
        )

        self._versions[chart_id].append(version)
        self.logger.info(
            f"Committed version {version_number} for chart {chart_id}: {message}"
        )
        return version_id

    def get_version(self, chart_id: str, version_id: str) -> Optional[ChartVersion]:
        """Get a specific version."""
        if chart_id not in self._versions:
            return None

        for version in self._versions[chart_id]:
            if version.version_id == version_id:
                return version

        return None

    def get_latest_version(self, chart_id: str) -> Optional[ChartVersion]:
        """Get the latest version of a chart."""
        if chart_id not in self._versions or not self._versions[chart_id]:
            return None

        return self._versions[chart_id][-1]

    def get_history(self, chart_id: str) -> List[ChartVersion]:
        """Get full version history for a chart."""
        return self._versions.get(chart_id, []).copy()

    def rollback(self, chart_id: str, version_id: str, user_id: str) -> Optional[str]:
        """
        Rollback to a previous version.

        Creates a new version with data from the specified version.

        Args:
            chart_id: Chart ID
            version_id: Version to rollback to
            user_id: User performing rollback

        Returns:
            New version ID or None
        """
        target_version = self.get_version(chart_id, version_id)
        if not target_version:
            self.logger.error(f"Version not found: {version_id}")
            return None

        # Create new version with old data
        new_version_id = self.commit(
            chart_id=chart_id,
            chart_data=target_version.chart_data,
            user_id=user_id,
            message=f"Rollback to version {target_version.version_number}",
            parent_version=self.get_latest_version(chart_id).version_id,
        )

        self.logger.info(
            f"Rolled back chart {chart_id} to version {target_version.version_number}"
        )
        return new_version_id

    def tag_version(self, chart_id: str, version_id: str, tag_name: str) -> bool:
        """Tag a version (e.g., 'v1.0', 'production')."""
        version = self.get_version(chart_id, version_id)
        if not version:
            return False

        if chart_id not in self._tags:
            self._tags[chart_id] = {}

        self._tags[chart_id][tag_name] = version_id
        version.tags.append(tag_name)

        self.logger.info(f"Tagged version {version_id} as '{tag_name}'")
        return True

    def get_version_by_tag(self, chart_id: str, tag_name: str) -> Optional[ChartVersion]:
        """Get version by tag name."""
        if chart_id not in self._tags or tag_name not in self._tags[chart_id]:
            return None

        version_id = self._tags[chart_id][tag_name]
        return self.get_version(chart_id, version_id)

    def compare_versions(
        self, chart_id: str, version1_id: str, version2_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Compare two versions.

        Returns:
            Dictionary with differences
        """
        v1 = self.get_version(chart_id, version1_id)
        v2 = self.get_version(chart_id, version2_id)

        if not v1 or not v2:
            return None

        # Simple comparison - in production would do deep diff
        return {
            "version1": {
                "id": v1.version_id,
                "number": v1.version_number,
                "message": v1.commit_message,
                "created_at": v1.created_at.isoformat(),
            },
            "version2": {
                "id": v2.version_id,
                "number": v2.version_number,
                "message": v2.commit_message,
                "created_at": v2.created_at.isoformat(),
            },
            "data_changed": v1.chart_data != v2.chart_data,
            "time_diff_seconds": (v2.created_at - v1.created_at).total_seconds(),
        }

    def get_stats(self, chart_id: Optional[str] = None) -> Dict[str, Any]:
        """Get version control statistics."""
        if chart_id:
            if chart_id not in self._versions:
                return {"error": "Chart not found"}

            versions = self._versions[chart_id]
            return {
                "chart_id": chart_id,
                "total_versions": len(versions),
                "first_commit": versions[0].created_at.isoformat() if versions else None,
                "latest_commit": versions[-1].created_at.isoformat()
                if versions
                else None,
                "total_tags": len(self._tags.get(chart_id, {})),
                "contributors": len(set(v.created_by for v in versions)),
            }
        else:
            total_versions = sum(len(v) for v in self._versions.values())
            total_tags = sum(len(t) for t in self._tags.values())

            return {
                "total_charts": len(self._versions),
                "total_versions": total_versions,
                "total_tags": total_tags,
                "charts_with_multiple_versions": len(
                    [v for v in self._versions.values() if len(v) > 1]
                ),
            }
