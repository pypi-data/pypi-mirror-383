"""
Role-Based Access Control (RBAC)

Provides fine-grained access control for agent operations:
- Permissions: Define what can be done
- Roles: Group permissions together
- RBAC Manager: Enforce access control
"""

from dataclasses import dataclass, field
from typing import Set, Optional, Dict, List, Any
from enum import Enum


class PermissionDeniedError(Exception):
    """Raised when permission is denied"""

    pass


class Permission(str, Enum):
    """
    Predefined permissions for agent operations

    Categories:
    - Tool execution
    - File operations
    - Network access
    - Environment access
    - Memory access
    """

    # Tool permissions
    TOOL_EXECUTE = "tool.execute"
    TOOL_REGISTER = "tool.register"
    TOOL_DELETE = "tool.delete"

    # File permissions
    FILE_READ = "file.read"
    FILE_WRITE = "file.write"
    FILE_DELETE = "file.delete"
    FILE_EXECUTE = "file.execute"

    # Network permissions
    NETWORK_HTTP = "network.http"
    NETWORK_HTTPS = "network.https"
    NETWORK_SOCKET = "network.socket"

    # Environment permissions
    ENV_READ = "env.read"
    ENV_WRITE = "env.write"
    SHELL_EXECUTE = "shell.execute"

    # Memory permissions
    MEMORY_READ = "memory.read"
    MEMORY_WRITE = "memory.write"
    MEMORY_DELETE = "memory.delete"

    # Agent permissions
    AGENT_CREATE = "agent.create"
    AGENT_DELETE = "agent.delete"
    AGENT_CONFIGURE = "agent.configure"

    # Admin permissions
    ADMIN_ALL = "admin.all"


@dataclass
class Role:
    """
    Role with a set of permissions

    Attributes:
        name: Role name
        permissions: Set of permissions
        description: Role description
        inherits_from: Parent roles to inherit from
    """

    name: str
    permissions: Set[str] = field(default_factory=set)
    description: str = ""
    inherits_from: Set[str] = field(default_factory=set)

    def add_permission(self, permission: str) -> None:
        """Add permission to role"""
        self.permissions.add(permission)

    def remove_permission(self, permission: str) -> None:
        """Remove permission from role"""
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        """Check if role has permission"""
        return permission in self.permissions

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "permissions": list(self.permissions),
            "description": self.description,
            "inherits_from": list(self.inherits_from),
        }


class RBACManager:
    """
    Role-Based Access Control Manager

    Features:
    - Role management (create, delete, update)
    - Permission checking
    - Role inheritance
    - User-role assignment
    - Audit integration

    Example:
        ```python
        # Create RBAC manager
        rbac = RBACManager()

        # Create roles
        admin_role = rbac.create_role("admin", description="Administrator")
        admin_role.add_permission(Permission.ADMIN_ALL)

        user_role = rbac.create_role("user", description="Regular user")
        user_role.add_permission(Permission.TOOL_EXECUTE)
        user_role.add_permission(Permission.FILE_READ)

        # Assign role to user
        rbac.assign_role("john", "user")

        # Check permission
        if rbac.check_permission("john", Permission.FILE_READ):
            # Allowed
            read_file()
        ```
    """

    def __init__(self):
        """Initialize RBAC manager"""
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = {}

        # Create default roles
        self._create_default_roles()

    def _create_default_roles(self) -> None:
        """Create default predefined roles"""
        # Admin role (all permissions)
        admin = Role(
            name="admin",
            description="Administrator with all permissions",
        )
        admin.add_permission(Permission.ADMIN_ALL.value)
        self.roles["admin"] = admin

        # User role (basic permissions)
        user = Role(
            name="user",
            description="Regular user with basic permissions",
        )
        user.add_permission(Permission.TOOL_EXECUTE.value)
        user.add_permission(Permission.FILE_READ.value)
        user.add_permission(Permission.MEMORY_READ.value)
        self.roles["user"] = user

        # Read-only role
        readonly = Role(
            name="readonly",
            description="Read-only access",
        )
        readonly.add_permission(Permission.FILE_READ.value)
        readonly.add_permission(Permission.MEMORY_READ.value)
        readonly.add_permission(Permission.ENV_READ.value)
        self.roles["readonly"] = readonly

        # Tool executor role
        tool_exec = Role(
            name="tool_executor",
            description="Can execute tools",
        )
        tool_exec.add_permission(Permission.TOOL_EXECUTE.value)
        tool_exec.add_permission(Permission.FILE_READ.value)
        self.roles["tool_executor"] = tool_exec

    def create_role(
        self,
        name: str,
        description: str = "",
        permissions: Optional[Set[str]] = None,
        inherits_from: Optional[Set[str]] = None,
    ) -> Role:
        """
        Create a new role

        Args:
            name: Role name
            description: Role description
            permissions: Initial permissions
            inherits_from: Parent roles

        Returns:
            Created role
        """
        role = Role(
            name=name,
            permissions=permissions or set(),
            description=description,
            inherits_from=inherits_from or set(),
        )

        self.roles[name] = role
        return role

    def get_role(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return self.roles.get(name)

    def delete_role(self, name: str) -> None:
        """Delete role"""
        if name in self.roles:
            del self.roles[name]

            # Remove from user assignments
            for user, roles in self.user_roles.items():
                roles.discard(name)

    def assign_role(self, user: str, role_name: str) -> None:
        """
        Assign role to user

        Args:
            user: User identifier
            role_name: Role name
        """
        if role_name not in self.roles:
            raise ValueError(f"Role '{role_name}' does not exist")

        if user not in self.user_roles:
            self.user_roles[user] = set()

        self.user_roles[user].add(role_name)

    def revoke_role(self, user: str, role_name: str) -> None:
        """
        Revoke role from user

        Args:
            user: User identifier
            role_name: Role name
        """
        if user in self.user_roles:
            self.user_roles[user].discard(role_name)

    def get_user_roles(self, user: str) -> Set[str]:
        """Get roles assigned to user"""
        return self.user_roles.get(user, set())

    def get_user_permissions(self, user: str) -> Set[str]:
        """
        Get all permissions for user (including inherited)

        Args:
            user: User identifier

        Returns:
            Set of permissions
        """
        permissions = set()

        for role_name in self.get_user_roles(user):
            role = self.roles.get(role_name)
            if role:
                # Add direct permissions
                permissions.update(role.permissions)

                # Check for admin permission (grants all)
                if Permission.ADMIN_ALL.value in role.permissions:
                    return {p.value for p in Permission}

                # Add inherited permissions
                for parent_role_name in role.inherits_from:
                    parent_role = self.roles.get(parent_role_name)
                    if parent_role:
                        permissions.update(parent_role.permissions)

        return permissions

    def check_permission(self, user: str, permission: str) -> bool:
        """
        Check if user has permission

        Args:
            user: User identifier
            permission: Permission to check

        Returns:
            True if user has permission
        """
        user_permissions = self.get_user_permissions(user)

        # Check for admin permission
        if Permission.ADMIN_ALL.value in user_permissions:
            return True

        # Check specific permission
        return permission in user_permissions

    def require_permission(self, user: str, permission: str) -> None:
        """
        Require permission or raise exception

        Args:
            user: User identifier
            permission: Required permission

        Raises:
            PermissionDeniedError: If user lacks permission
        """
        if not self.check_permission(user, permission):
            raise PermissionDeniedError(
                f"User '{user}' does not have permission '{permission}'"
            )

    def list_roles(self) -> List[str]:
        """List all role names"""
        return list(self.roles.keys())

    def get_stats(self) -> Dict[str, Any]:
        """Get RBAC statistics"""
        return {
            "total_roles": len(self.roles),
            "total_users": len(self.user_roles),
            "roles": {
                name: {
                    "permissions_count": len(role.permissions),
                    "users_count": sum(
                        1 for roles in self.user_roles.values()
                        if name in roles
                    ),
                }
                for name, role in self.roles.items()
            },
        }


# Decorator for permission checking

def requires_permission(permission: str, rbac: RBACManager, user: str):
    """
    Decorator to require permission for function

    Args:
        permission: Required permission
        rbac: RBAC manager instance
        user: User identifier

    Example:
        ```python
        rbac = RBACManager()

        @requires_permission(Permission.FILE_WRITE, rbac, "john")
        def write_file(path, content):
            with open(path, 'w') as f:
                f.write(content)
        ```
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            rbac.require_permission(user, permission)
            return func(*args, **kwargs)
        return wrapper
    return decorator
