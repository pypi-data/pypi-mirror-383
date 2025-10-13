"""
Multi-Agent Systems module for agent communication and collaboration.

This module provides Layer 3 (Multi-Agent Systems) functionality:
- Communication: Message passing, protocols, channels
- Orchestration: Workflows, task delegation, role management
- Coordination: Shared state, consensus, conflict resolution
- Collaboration: Teams, patterns, negotiation, knowledge sharing
"""

from react_agent_framework.multi_agent.communication import (
    Message,
    MessageType,
    MessagePriority,
    MessageBus,
    Protocol,
    ACLProtocol,
    Channel,
    DirectChannel,
    BroadcastChannel,
    MulticastChannel,
)

__all__ = [
    # Communication
    "Message",
    "MessageType",
    "MessagePriority",
    "MessageBus",
    "Protocol",
    "ACLProtocol",
    "Channel",
    "DirectChannel",
    "BroadcastChannel",
    "MulticastChannel",
]

__version__ = "0.12.0"
