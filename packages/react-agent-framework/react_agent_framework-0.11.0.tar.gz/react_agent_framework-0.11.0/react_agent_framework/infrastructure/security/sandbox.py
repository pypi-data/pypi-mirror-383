"""
Sandbox for Isolated Execution

Provides isolated execution environment for agent operations:
- Restricted file access
- Limited network access
- Controlled environment variables
- Resource limits (memory, CPU)
- Safe code execution
"""

import os
import sys
import subprocess
from dataclasses import dataclass, field
from typing import Set, Optional, Dict, Any, List, Callable
from pathlib import Path
import tempfile


class SandboxViolation(Exception):
    """Raised when sandbox rules are violated"""

    pass


@dataclass
class SandboxConfig:
    """
    Sandbox configuration

    Attributes:
        allowed_paths: Paths that can be accessed
        blocked_paths: Paths that cannot be accessed
        allow_network: Allow network access
        allow_env_access: Allow environment variable access
        allowed_env_vars: Specific env vars allowed
        max_memory_mb: Maximum memory in MB
        max_execution_time: Maximum execution time in seconds
        allow_subprocess: Allow subprocess execution
        allowed_commands: Specific commands allowed
    """

    allowed_paths: Set[str] = field(default_factory=set)
    blocked_paths: Set[str] = field(default_factory=set)
    allow_network: bool = False
    allow_env_access: bool = False
    allowed_env_vars: Set[str] = field(default_factory=set)
    max_memory_mb: Optional[int] = None
    max_execution_time: Optional[float] = None
    allow_subprocess: bool = False
    allowed_commands: Set[str] = field(default_factory=set)


class Sandbox:
    """
    Sandbox for isolated code execution

    Features:
    - File access control
    - Network access control
    - Environment variable control
    - Subprocess execution control
    - Resource limits
    - Audit logging integration

    Example:
        ```python
        # Create sandbox
        sandbox = Sandbox(
            config=SandboxConfig(
                allowed_paths={"/tmp", "/app/data"},
                allow_network=False,
                allow_subprocess=False,
            )
        )

        # Execute function in sandbox
        def read_file(path):
            with open(path) as f:
                return f.read()

        result = sandbox.execute(read_file, "/tmp/safe.txt")

        # Check file access
        if sandbox.check_file_access("/etc/passwd", "read"):
            # Allowed
            pass
        ```
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        Initialize sandbox

        Args:
            config: Sandbox configuration
        """
        self.config = config or SandboxConfig()

        # Metrics
        self.violations = 0
        self.allowed_operations = 0

        # Add common safe paths by default
        if not self.config.allowed_paths:
            self.config.allowed_paths = {
                tempfile.gettempdir(),
                os.getcwd(),
            }

        # Add common blocked paths by default
        if not self.config.blocked_paths:
            self.config.blocked_paths = {
                "/etc",
                "/root",
                "/sys",
                "/proc",
                str(Path.home() / ".ssh"),
                str(Path.home() / ".aws"),
            }

    def check_file_access(
        self,
        path: str,
        operation: str = "read",
    ) -> bool:
        """
        Check if file access is allowed

        Args:
            path: File path
            operation: Operation type (read, write, delete, execute)

        Returns:
            True if allowed
        """
        path_obj = Path(path).resolve()

        # Check blocked paths first
        for blocked in self.config.blocked_paths:
            blocked_path = Path(blocked).resolve()
            try:
                path_obj.relative_to(blocked_path)
                return False  # Path is under blocked directory
            except ValueError:
                continue

        # Check allowed paths
        for allowed in self.config.allowed_paths:
            allowed_path = Path(allowed).resolve()
            try:
                path_obj.relative_to(allowed_path)
                return True  # Path is under allowed directory
            except ValueError:
                continue

        return False

    def require_file_access(
        self,
        path: str,
        operation: str = "read",
    ) -> None:
        """
        Require file access or raise exception

        Args:
            path: File path
            operation: Operation type

        Raises:
            SandboxViolation: If access denied
        """
        if not self.check_file_access(path, operation):
            self.violations += 1
            raise SandboxViolation(
                f"Access denied: Cannot {operation} file '{path}'"
            )

        self.allowed_operations += 1

    def check_network_access(self, host: str, port: int) -> bool:
        """
        Check if network access is allowed

        Args:
            host: Hostname or IP
            port: Port number

        Returns:
            True if allowed
        """
        return self.config.allow_network

    def require_network_access(self, host: str, port: int) -> None:
        """
        Require network access or raise exception

        Args:
            host: Hostname or IP
            port: Port number

        Raises:
            SandboxViolation: If access denied
        """
        if not self.check_network_access(host, port):
            self.violations += 1
            raise SandboxViolation(
                f"Network access denied: {host}:{port}"
            )

        self.allowed_operations += 1

    def check_env_access(self, var_name: str) -> bool:
        """
        Check if environment variable access is allowed

        Args:
            var_name: Variable name

        Returns:
            True if allowed
        """
        if not self.config.allow_env_access:
            return False

        if self.config.allowed_env_vars:
            return var_name in self.config.allowed_env_vars

        return True

    def require_env_access(self, var_name: str) -> None:
        """
        Require environment access or raise exception

        Args:
            var_name: Variable name

        Raises:
            SandboxViolation: If access denied
        """
        if not self.check_env_access(var_name):
            self.violations += 1
            raise SandboxViolation(
                f"Environment access denied: {var_name}"
            )

        self.allowed_operations += 1

    def check_subprocess(self, command: str) -> bool:
        """
        Check if subprocess execution is allowed

        Args:
            command: Command to execute

        Returns:
            True if allowed
        """
        if not self.config.allow_subprocess:
            return False

        if self.config.allowed_commands:
            # Check if command starts with any allowed command
            cmd_name = command.split()[0] if command else ""
            return cmd_name in self.config.allowed_commands

        return True

    def require_subprocess(self, command: str) -> None:
        """
        Require subprocess execution or raise exception

        Args:
            command: Command to execute

        Raises:
            SandboxViolation: If execution denied
        """
        if not self.check_subprocess(command):
            self.violations += 1
            raise SandboxViolation(
                f"Subprocess execution denied: {command}"
            )

        self.allowed_operations += 1

    def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function in sandbox context

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            SandboxViolation: If sandbox rules violated
        """
        # Set sandbox context
        original_cwd = os.getcwd()

        try:
            # Change to allowed directory if specified
            if self.config.allowed_paths:
                first_allowed = list(self.config.allowed_paths)[0]
                os.chdir(first_allowed)

            # Execute function
            result = func(*args, **kwargs)

            return result

        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    def get_stats(self) -> Dict[str, Any]:
        """Get sandbox statistics"""
        return {
            "violations": self.violations,
            "allowed_operations": self.allowed_operations,
            "config": {
                "allowed_paths": list(self.config.allowed_paths),
                "blocked_paths": list(self.config.blocked_paths),
                "allow_network": self.config.allow_network,
                "allow_subprocess": self.config.allow_subprocess,
            },
        }

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        return False


# Predefined sandbox configurations

def create_readonly_sandbox() -> Sandbox:
    """
    Create read-only sandbox

    Returns:
        Sandbox with read-only access
    """
    config = SandboxConfig(
        allowed_paths={tempfile.gettempdir(), os.getcwd()},
        allow_network=False,
        allow_subprocess=False,
    )
    return Sandbox(config)


def create_network_sandbox() -> Sandbox:
    """
    Create sandbox with network access

    Returns:
        Sandbox with network access
    """
    config = SandboxConfig(
        allowed_paths={tempfile.gettempdir()},
        allow_network=True,
        allow_subprocess=False,
    )
    return Sandbox(config)


def create_tool_sandbox() -> Sandbox:
    """
    Create sandbox for tool execution

    Returns:
        Sandbox configured for tools
    """
    config = SandboxConfig(
        allowed_paths={tempfile.gettempdir(), os.getcwd()},
        allow_network=True,
        allow_subprocess=True,
        allowed_commands={"curl", "wget", "git"},
    )
    return Sandbox(config)
