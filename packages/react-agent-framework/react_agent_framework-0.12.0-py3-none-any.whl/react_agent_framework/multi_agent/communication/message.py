"""
Message classes for agent communication.

Provides message structure, types, and priorities for inter-agent communication.
"""

import uuid
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime


class MessageType(str, Enum):
    """Types of messages between agents."""

    # Basic communication
    INFORM = "inform"  # Share information
    REQUEST = "request"  # Request action/information
    RESPONSE = "response"  # Response to request
    QUERY = "query"  # Query for information

    # Collaboration
    PROPOSE = "propose"  # Propose action/plan
    ACCEPT = "accept"  # Accept proposal
    REJECT = "reject"  # Reject proposal
    AGREE = "agree"  # Agree to perform action
    REFUSE = "refuse"  # Refuse to perform action

    # Coordination
    SUBSCRIBE = "subscribe"  # Subscribe to topic
    UNSUBSCRIBE = "unsubscribe"  # Unsubscribe from topic
    BROADCAST = "broadcast"  # Broadcast to all
    MULTICAST = "multicast"  # Send to group

    # Control
    START = "start"  # Start task/workflow
    STOP = "stop"  # Stop task/workflow
    PAUSE = "pause"  # Pause execution
    RESUME = "resume"  # Resume execution

    # Status
    STATUS = "status"  # Status update
    ERROR = "error"  # Error notification
    DONE = "done"  # Task completed


class MessagePriority(int, Enum):
    """Priority levels for messages."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3
    CRITICAL = 4


@dataclass
class Message:
    """
    Message for agent-to-agent communication.

    Attributes:
        message_id: Unique message identifier
        sender: Sender agent ID
        receiver: Receiver agent ID (or topic for broadcast/multicast)
        message_type: Type of message
        content: Message content (any serializable data)
        priority: Message priority
        timestamp: Creation timestamp
        metadata: Additional metadata
        reply_to: ID of message this is replying to
        conversation_id: ID linking related messages
        expires_at: Message expiration timestamp

    Example:
        >>> msg = Message(
        ...     sender="agent-1",
        ...     receiver="agent-2",
        ...     message_type=MessageType.REQUEST,
        ...     content={"action": "search", "query": "test"}
        ... )
        >>> print(msg.message_id)
        msg-...
    """

    sender: str
    receiver: str
    message_type: MessageType
    content: Any

    # Auto-generated fields
    message_id: str = field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:12]}")
    timestamp: float = field(default_factory=time.time)

    # Optional fields
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    reply_to: Optional[str] = None
    conversation_id: Optional[str] = None
    expires_at: Optional[float] = None

    def is_expired(self) -> bool:
        """Check if message has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def age(self) -> float:
        """Get message age in seconds."""
        return time.time() - self.timestamp

    def create_reply(
        self,
        sender: str,
        content: Any,
        message_type: MessageType = MessageType.RESPONSE
    ) -> "Message":
        """
        Create a reply to this message.

        Args:
            sender: Sender of reply
            content: Reply content
            message_type: Type of reply message

        Returns:
            New Message that replies to this one
        """
        return Message(
            sender=sender,
            receiver=self.sender,  # Reply to original sender
            message_type=message_type,
            content=content,
            reply_to=self.message_id,
            conversation_id=self.conversation_id or self.message_id,
            priority=self.priority
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type.value,
            "content": self.content,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "reply_to": self.reply_to,
            "conversation_id": self.conversation_id,
            "expires_at": self.expires_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        return cls(
            message_id=data["message_id"],
            sender=data["sender"],
            receiver=data["receiver"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            priority=MessagePriority(data["priority"]),
            timestamp=data["timestamp"],
            metadata=data.get("metadata", {}),
            reply_to=data.get("reply_to"),
            conversation_id=data.get("conversation_id"),
            expires_at=data.get("expires_at")
        )

    def __repr__(self) -> str:
        return (
            f"Message(id={self.message_id}, "
            f"from={self.sender}, to={self.receiver}, "
            f"type={self.message_type.value}, "
            f"priority={self.priority.value})"
        )


def create_inform_message(
    sender: str,
    receiver: str,
    content: Any,
    **kwargs
) -> Message:
    """Create an INFORM message."""
    return Message(
        sender=sender,
        receiver=receiver,
        message_type=MessageType.INFORM,
        content=content,
        **kwargs
    )


def create_request_message(
    sender: str,
    receiver: str,
    content: Any,
    **kwargs
) -> Message:
    """Create a REQUEST message."""
    return Message(
        sender=sender,
        receiver=receiver,
        message_type=MessageType.REQUEST,
        content=content,
        **kwargs
    )


def create_broadcast_message(
    sender: str,
    content: Any,
    **kwargs
) -> Message:
    """Create a BROADCAST message."""
    return Message(
        sender=sender,
        receiver="*",  # Wildcard for broadcast
        message_type=MessageType.BROADCAST,
        content=content,
        **kwargs
    )


def create_error_message(
    sender: str,
    receiver: str,
    error: str,
    **kwargs
) -> Message:
    """Create an ERROR message."""
    return Message(
        sender=sender,
        receiver=receiver,
        message_type=MessageType.ERROR,
        content={"error": error},
        priority=MessagePriority.HIGH,
        **kwargs
    )
