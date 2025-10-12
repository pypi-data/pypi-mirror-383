"""
Infrastructure Security Demo

Demonstrates the security system (v0.11.0 - Part 3/5):
- RBAC: Role-Based Access Control
- Sandbox: Isolated execution environment
- AuditLogger: Comprehensive audit trail
- SecretsManager: Secure secrets storage

Part of Layer 4 (Agentic Infrastructure) implementation.
"""

import tempfile
import os
from pathlib import Path

from react_agent_framework.infrastructure.security import (
    Permission,
    Role,
    RBACManager,
    PermissionDeniedError,
    Sandbox,
    SandboxViolation,
    SandboxConfig,
    AuditLogger,
    AuditEvent,
    AuditLevel,
    SecretsManager,
)


def demo_1_rbac():
    """Demo 1: Role-Based Access Control"""
    print("=" * 80)
    print("DEMO 1: Role-Based Access Control (RBAC)")
    print("=" * 80)

    # Create RBAC manager
    rbac = RBACManager()

    print("\n1. Default roles:")
    for role_name in rbac.list_roles():
        role = rbac.get_role(role_name)
        print(f"   - {role_name}: {len(role.permissions)} permissions")

    # Create custom role
    print("\n2. Creating custom role 'api_user':")
    api_role = rbac.create_role(
        "api_user",
        description="API user with limited permissions"
    )
    api_role.add_permission(Permission.TOOL_EXECUTE.value)
    api_role.add_permission(Permission.NETWORK_HTTPS.value)
    print(f"   ✓ Role created with {len(api_role.permissions)} permissions")

    # Assign roles to users
    print("\n3. Assigning roles to users:")
    rbac.assign_role("john", "user")
    rbac.assign_role("alice", "admin")
    rbac.assign_role("bob", "api_user")

    for user in ["john", "alice", "bob"]:
        roles = rbac.get_user_roles(user)
        print(f"   - {user}: {', '.join(roles)}")

    # Check permissions
    print("\n4. Permission checks:")
    test_cases = [
        ("john", Permission.FILE_READ, "Should ALLOW"),
        ("john", Permission.FILE_WRITE, "Should DENY"),
        ("alice", Permission.ADMIN_ALL, "Should ALLOW (admin)"),
        ("bob", Permission.TOOL_EXECUTE, "Should ALLOW"),
    ]

    for user, permission, expected in test_cases:
        has_perm = rbac.check_permission(user, permission.value)
        status = "✓ ALLOWED" if has_perm else "✗ DENIED"
        print(f"   {user} + {permission.value}: {status} ({expected})")

    # Try requiring permission
    print("\n5. Requiring permission (will raise if denied):")
    try:
        rbac.require_permission("john", Permission.FILE_WRITE.value)
        print("   ✓ Permission granted")
    except PermissionDeniedError as e:
        print(f"   ✗ {e}")


def demo_2_sandbox():
    """Demo 2: Sandbox for Isolated Execution"""
    print("\n" + "=" * 80)
    print("DEMO 2: Sandbox for Isolated Execution")
    print("=" * 80)

    # Create sandbox
    sandbox = Sandbox(
        config=SandboxConfig(
            allowed_paths={tempfile.gettempdir()},
            allow_network=False,
            allow_subprocess=False,
        )
    )

    print("\n1. Sandbox configuration:")
    print(f"   Allowed paths: {list(sandbox.config.allowed_paths)}")
    print(f"   Network access: {sandbox.config.allow_network}")
    print(f"   Subprocess: {sandbox.config.allow_subprocess}")

    # Test file access
    print("\n2. Testing file access:")
    test_paths = [
        (tempfile.gettempdir() + "/test.txt", "Should ALLOW"),
        ("/etc/passwd", "Should DENY"),
        ("/root/.ssh/id_rsa", "Should DENY"),
    ]

    for path, expected in test_paths:
        allowed = sandbox.check_file_access(path)
        status = "✓ ALLOWED" if allowed else "✗ DENIED"
        print(f"   {path}: {status} ({expected})")

    # Try accessing blocked file
    print("\n3. Attempting to access blocked file:")
    try:
        sandbox.require_file_access("/etc/passwd", "read")
        print("   ✓ Access granted")
    except SandboxViolation as e:
        print(f"   ✗ {e}")

    # Execute function in sandbox
    print("\n4. Executing function in sandbox:")

    def safe_operation():
        temp_file = Path(tempfile.gettempdir()) / "sandbox_test.txt"
        temp_file.write_text("Hello from sandbox!")
        return temp_file.read_text()

    try:
        result = sandbox.execute(safe_operation)
        print(f"   ✓ Result: {result}")
    except SandboxViolation as e:
        print(f"   ✗ {e}")

    # Show stats
    print("\n5. Sandbox statistics:")
    stats = sandbox.get_stats()
    print(f"   Violations: {stats['violations']}")
    print(f"   Allowed operations: {stats['allowed_operations']}")


def demo_3_audit_logging():
    """Demo 3: Audit Logging"""
    print("\n" + "=" * 80)
    print("DEMO 3: Comprehensive Audit Logging")
    print("=" * 80)

    # Create audit logger
    audit = AuditLogger(
        log_file=tempfile.gettempdir() + "/audit.log",
        enable_console=False,
        json_format=True,
    )

    print("\n1. Logging various events:")

    # Security event
    audit.log_security_event(
        action="authentication",
        user="john",
        result="success",
        details="User logged in successfully",
    )
    print("   ✓ Logged authentication event")

    # Access attempt (denied)
    audit.log_access_attempt(
        user="john",
        resource="/etc/passwd",
        operation="read",
        allowed=False,
        reason="Insufficient permissions",
    )
    print("   ✓ Logged denied access attempt")

    # Tool execution
    audit.log_tool_execution(
        tool="search",
        user="alice",
        parameters={"query": "AI agents"},
        result="success",
        duration=1.5,
    )
    print("   ✓ Logged tool execution")

    # Configuration change
    audit.log_config_change(
        user="admin",
        setting="max_tokens",
        old_value=1000,
        new_value=2000,
    )
    print("   ✓ Logged configuration change")

    # Error
    audit.log_error(
        action="api_call",
        error="Connection timeout",
        user="bob",
        endpoint="https://api.example.com",
    )
    print("   ✓ Logged error event")

    # Query events
    print("\n2. Querying audit events:")
    security_events = audit.get_events(level=AuditLevel.SECURITY)
    print(f"   Security events: {len(security_events)}")

    access_events = audit.get_events(category="access_control")
    print(f"   Access control events: {len(access_events)}")

    # Generate report
    print("\n3. Security report:")
    report = audit.get_security_report()
    print(f"   Total events: {report['total_events']}")
    print(f"   Security events: {report['security_events']}")
    print(f"   Denied access: {report['denied_access_attempts']}")
    print(f"   By category: {report['by_category']}")


def demo_4_secrets_management():
    """Demo 4: Secrets Management"""
    print("\n" + "=" * 80)
    print("DEMO 4: Secure Secrets Management")
    print("=" * 80)

    # Create secrets manager
    secrets = SecretsManager(
        storage_path=tempfile.gettempdir() + "/secrets.enc",
        encryption_key="demo-encryption-key-2024",
    )

    print("\n1. Storing secrets:")

    # Store API key
    secrets.set_secret(
        "openai_api_key",
        "sk-demo-key-12345",
        expires_in_days=90,
        metadata={"service": "openai", "env": "production"},
    )
    print("   ✓ Stored OpenAI API key (expires in 90 days)")

    # Store database password
    secrets.set_secret(
        "db_password",
        "super-secret-password",
        metadata={"database": "postgres", "host": "localhost"},
    )
    print("   ✓ Stored database password")

    # Store token
    secrets.set_secret(
        "github_token",
        "ghp_demo_token_xyz",
        expires_in_days=30,
    )
    print("   ✓ Stored GitHub token (expires in 30 days)")

    # Retrieve secrets
    print("\n2. Retrieving secrets:")
    api_key = secrets.get_secret("openai_api_key")
    if api_key:
        print(f"   OpenAI Key: {api_key[:10]}... (masked)")

    db_pass = secrets.get_secret("db_password")
    if db_pass:
        print(f"   DB Password: {'*' * len(db_pass)} (masked)")

    # List secrets
    print("\n3. Listing all secrets:")
    for name in secrets.list_secrets():
        info = secrets.get_secret_info(name)
        print(f"   - {name}")
        print(f"     Created: {info['created_at'][:19]}")
        print(f"     Expires: {info['expires_at'][:19] if info['expires_at'] else 'Never'}")
        print(f"     Accessed: {info['access_count']} times")

    # Rotate secret
    print("\n4. Rotating secret:")
    secrets.rotate_secret("openai_api_key", "sk-new-key-67890")
    print("   ✓ OpenAI API key rotated")

    # Statistics
    print("\n5. Secrets statistics:")
    stats = secrets.get_stats()
    print(f"   Total secrets: {stats['total_secrets']}")
    print(f"   Active secrets: {stats['active_secrets']}")
    if stats['most_accessed']:
        print(f"   Most accessed: {stats['most_accessed'][0][0]} ({stats['most_accessed'][0][1]} times)")


def demo_5_integrated():
    """Demo 5: Integrated Security (All Together)"""
    print("\n" + "=" * 80)
    print("DEMO 5: Integrated Security (RBAC + Sandbox + Audit + Secrets)")
    print("=" * 80)

    # Setup all security components
    rbac = RBACManager()
    sandbox = Sandbox()
    audit = AuditLogger(enable_console=False)
    secrets = SecretsManager()

    print("\n1. Complete security workflow:")

    # User attempts operation
    user = "john"
    operation = "read_file"
    file_path = "/tmp/data.txt"

    print(f"   User '{user}' attempting '{operation}' on '{file_path}'")

    # Check RBAC permission
    print("\n   Step 1: Check RBAC permission...")
    try:
        rbac.require_permission(user, Permission.FILE_READ.value)
        print("   ✓ RBAC: Permission granted")

        # Log to audit
        audit.log_access_attempt(
            user=user,
            resource=file_path,
            operation="read",
            allowed=True,
        )

    except PermissionDeniedError as e:
        print(f"   ✗ RBAC: {e}")
        audit.log_access_attempt(
            user=user,
            resource=file_path,
            operation="read",
            allowed=False,
            reason=str(e),
        )
        return

    # Check sandbox restrictions
    print("\n   Step 2: Check sandbox restrictions...")
    try:
        sandbox.require_file_access(file_path, "read")
        print("   ✓ Sandbox: Access allowed")

    except SandboxViolation as e:
        print(f"   ✗ Sandbox: {e}")
        audit.log_security_event(
            action="sandbox_violation",
            user=user,
            resource=file_path,
            result="denied",
            details=str(e),
        )
        return

    # Get credentials from secrets if needed
    print("\n   Step 3: Retrieve credentials from secrets...")
    api_key = secrets.get_secret("api_key", default="no-key")
    print(f"   ✓ Retrieved API key: {api_key[:10] if len(api_key) > 10 else api_key}...")

    # Execute operation
    print("\n   Step 4: Execute operation...")
    try:
        def protected_operation():
            # Simulated file read
            return f"File content from {file_path}"

        result = sandbox.execute(protected_operation)
        print(f"   ✓ Operation successful: {result}")

        # Log successful execution
        audit.log_tool_execution(
            tool="read_file",
            user=user,
            parameters={"path": file_path},
            result="success",
        )

    except Exception as e:
        print(f"   ✗ Operation failed: {e}")
        audit.log_error(
            action="read_file",
            error=str(e),
            user=user,
        )

    # Summary
    print("\n2. Security summary:")
    print(f"   RBAC: {len(rbac.list_roles())} roles, {len(rbac.user_roles)} users")
    print(f"   Sandbox: {sandbox.get_stats()['violations']} violations")
    print(f"   Audit: {audit.get_stats()['total_events']} events logged")
    print(f"   Secrets: {secrets.get_stats()['total_secrets']} secrets stored")


if __name__ == "__main__":
    print("\n🔒 Infrastructure Security System Demo (v0.11.0 - Part 3/5)")
    print("=" * 80)
    print("Layer 4: Agentic Infrastructure - Security Component")
    print("=" * 80)

    demo_1_rbac()
    demo_2_sandbox()
    demo_3_audit_logging()
    demo_4_secrets_management()
    demo_5_integrated()

    print("\n" + "=" * 80)
    print("✅ All security demos completed successfully!")
    print("=" * 80)
    print("\n💡 Key Takeaways:")
    print("   - RBAC: Fine-grained access control")
    print("   - Sandbox: Isolated execution environment")
    print("   - Audit: Complete audit trail for compliance")
    print("   - Secrets: Secure credential management")
    print("   - Integrated: Production-ready security stack")
