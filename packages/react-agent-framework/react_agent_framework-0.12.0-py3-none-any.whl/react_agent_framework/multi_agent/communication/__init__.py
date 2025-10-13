"""
Communication module for multi-agent systems.

Provides message passing, protocols, and channels for agent-to-agent communication.
"""

from .message import Message, MessageType, MessagePriority
from .message_bus import MessageBus
from .protocols import Protocol, ACLProtocol, Performative
from .channels import Channel, DirectChannel, BroadcastChannel, MulticastChannel

__all__ = [
    # Message
    "Message",
    "MessageType",
    "MessagePriority",
    # Message Bus
    "MessageBus",
    # Protocols
    "Protocol",
    "ACLProtocol",
    "Performative",
    # Channels
    "Channel",
    "DirectChannel",
    "BroadcastChannel",
    "MulticastChannel",
]
