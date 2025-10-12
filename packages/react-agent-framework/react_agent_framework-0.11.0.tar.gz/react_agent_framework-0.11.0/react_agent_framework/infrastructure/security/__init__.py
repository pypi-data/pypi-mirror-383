"""
Security System for AI Agents

Provides security mechanisms for production agents:
- RBAC: Role-Based Access Control
- Sandbox: Isolated execution environment
- Audit: Comprehensive audit logging
- Secrets: Secure secrets management
"""

from react_agent_framework.infrastructure.security.permissions import (
    Permission,
    Role,
    RBACManager,
    PermissionDeniedError,
)
from react_agent_framework.infrastructure.security.sandbox import (
    Sandbox,
    SandboxViolation,
    SandboxConfig,
)
from react_agent_framework.infrastructure.security.audit import (
    AuditLogger,
    AuditEvent,
    AuditLevel,
)
from react_agent_framework.infrastructure.security.secrets import (
    SecretsManager,
    Secret,
)

__all__ = [
    "Permission",
    "Role",
    "RBACManager",
    "PermissionDeniedError",
    "Sandbox",
    "SandboxViolation",
    "SandboxConfig",
    "AuditLogger",
    "AuditEvent",
    "AuditLevel",
    "SecretsManager",
    "Secret",
]
