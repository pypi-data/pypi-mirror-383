"""
Communication channels for agent messaging.

Provides different channel types for agent communication.
"""

from abc import ABC, abstractmethod
from typing import List, Set, Optional
from .message import Message, MessageType
from .message_bus import MessageBus


class Channel(ABC):
    """
    Abstract base class for communication channels.

    Channels provide different communication patterns over MessageBus.
    """

    def __init__(self, message_bus: MessageBus, name: Optional[str] = None):
        """
        Initialize channel.

        Args:
            message_bus: MessageBus instance
            name: Channel name
        """
        self.message_bus = message_bus
        self.name = name or self.__class__.__name__

    @abstractmethod
    def send(self, message: Message) -> bool:
        """
        Send message through channel.

        Args:
            message: Message to send

        Returns:
            True if sent successfully
        """
        pass

    @abstractmethod
    def receive(self, agent_id: str, **kwargs) -> List[Message]:
        """
        Receive messages from channel.

        Args:
            agent_id: Agent identifier
            **kwargs: Additional parameters

        Returns:
            List of messages
        """
        pass


class DirectChannel(Channel):
    """
    Direct point-to-point communication channel.

    Sends messages directly from one agent to another.

    Example:
        >>> bus = MessageBus()
        >>> channel = DirectChannel(bus)
        >>>
        >>> bus.register_agent("agent-1")
        >>> bus.register_agent("agent-2")
        >>>
        >>> msg = Message(
        ...     sender="agent-1",
        ...     receiver="agent-2",
        ...     message_type=MessageType.INFORM,
        ...     content="Hello"
        ... )
        >>> channel.send(msg)
        >>> messages = channel.receive("agent-2")
    """

    def send(self, message: Message) -> bool:
        """Send message directly to receiver."""
        return self.message_bus.send(message)

    def receive(
        self,
        agent_id: str,
        max_messages: int = 10,
        timeout: float = 0,
        filter_type: Optional[MessageType] = None
    ) -> List[Message]:
        """Receive direct messages."""
        return self.message_bus.receive(
            agent_id=agent_id,
            max_messages=max_messages,
            timeout=timeout,
            filter_type=filter_type
        )


class BroadcastChannel(Channel):
    """
    Broadcast communication channel.

    Sends messages to all registered agents.

    Example:
        >>> bus = MessageBus()
        >>> channel = BroadcastChannel(bus)
        >>>
        >>> for i in range(5):
        ...     bus.register_agent(f"agent-{i}")
        >>>
        >>> msg = Message(
        ...     sender="agent-0",
        ...     receiver="*",
        ...     message_type=MessageType.BROADCAST,
        ...     content="Announcement"
        ... )
        >>> channel.broadcast(msg)
        >>>
        >>> # All agents (except sender) will receive
        >>> messages = channel.receive("agent-1")
    """

    def send(self, message: Message) -> bool:
        """
        Broadcast message to all agents.

        Args:
            message: Message to broadcast

        Returns:
            True if broadcast succeeded
        """
        # Ensure it's a broadcast message
        message.receiver = "*"
        message.message_type = MessageType.BROADCAST
        return self.message_bus.send(message)

    def broadcast(self, sender: str, content: any, **kwargs) -> bool:
        """
        Convenience method to broadcast content.

        Args:
            sender: Sender agent ID
            content: Content to broadcast
            **kwargs: Additional message parameters

        Returns:
            True if broadcast succeeded
        """
        message = Message(
            sender=sender,
            receiver="*",
            message_type=MessageType.BROADCAST,
            content=content,
            **kwargs
        )
        return self.send(message)

    def receive(
        self,
        agent_id: str,
        max_messages: int = 10,
        timeout: float = 0
    ) -> List[Message]:
        """Receive broadcast messages."""
        return self.message_bus.receive(
            agent_id=agent_id,
            max_messages=max_messages,
            timeout=timeout
        )


class MulticastChannel(Channel):
    """
    Topic-based multicast communication channel.

    Implements pub/sub pattern with topics.

    Example:
        >>> bus = MessageBus()
        >>> channel = MulticastChannel(bus)
        >>>
        >>> bus.register_agent("agent-1")
        >>> bus.register_agent("agent-2")
        >>> bus.register_agent("agent-3")
        >>>
        >>> # Subscribe to topics
        >>> channel.subscribe("agent-1", "updates")
        >>> channel.subscribe("agent-2", "updates")
        >>> channel.subscribe("agent-3", "alerts")
        >>>
        >>> # Publish to topic
        >>> channel.publish(
        ...     sender="system",
        ...     topic="updates",
        ...     content="New update available"
        ... )
        >>>
        >>> # agent-1 and agent-2 will receive, agent-3 won't
        >>> messages = channel.receive("agent-1")
    """

    def __init__(self, message_bus: MessageBus, name: Optional[str] = None):
        """Initialize multicast channel."""
        super().__init__(message_bus, name)
        self._topics: Set[str] = set()

    def subscribe(self, agent_id: str, topic: str):
        """
        Subscribe agent to topic.

        Args:
            agent_id: Agent identifier
            topic: Topic name
        """
        self._topics.add(topic)
        self.message_bus.subscribe(agent_id, topic)

    def unsubscribe(self, agent_id: str, topic: str):
        """
        Unsubscribe agent from topic.

        Args:
            agent_id: Agent identifier
            topic: Topic name
        """
        self.message_bus.unsubscribe(agent_id, topic)

    def publish(
        self,
        sender: str,
        topic: str,
        content: any,
        **kwargs
    ) -> bool:
        """
        Publish message to topic.

        Args:
            sender: Sender agent ID
            topic: Topic name
            content: Message content
            **kwargs: Additional message parameters

        Returns:
            True if published successfully
        """
        message = Message(
            sender=sender,
            receiver=topic,  # Topic as receiver
            message_type=MessageType.MULTICAST,
            content=content,
            metadata={"topic": topic},
            **kwargs
        )
        return self.send(message)

    def send(self, message: Message) -> bool:
        """
        Send message to topic subscribers.

        Args:
            message: Message to send

        Returns:
            True if sent successfully
        """
        # Ensure it's a multicast message
        message.message_type = MessageType.MULTICAST
        return self.message_bus.send(message)

    def receive(
        self,
        agent_id: str,
        max_messages: int = 10,
        timeout: float = 0,
        topic: Optional[str] = None
    ) -> List[Message]:
        """
        Receive multicast messages.

        Args:
            agent_id: Agent identifier
            max_messages: Maximum messages to receive
            timeout: Wait timeout
            topic: Filter by topic

        Returns:
            List of messages
        """
        messages = self.message_bus.receive(
            agent_id=agent_id,
            max_messages=max_messages,
            timeout=timeout
        )

        # Filter by topic if specified
        if topic:
            messages = [
                msg for msg in messages
                if msg.metadata.get("topic") == topic
            ]

        return messages

    def get_topics(self) -> Set[str]:
        """Get all topics."""
        return self._topics.copy()

    def get_subscribers(self, topic: str) -> Set[str]:
        """
        Get subscribers for a topic.

        Args:
            topic: Topic name

        Returns:
            Set of subscriber agent IDs
        """
        return self.message_bus.get_subscribers(topic)
