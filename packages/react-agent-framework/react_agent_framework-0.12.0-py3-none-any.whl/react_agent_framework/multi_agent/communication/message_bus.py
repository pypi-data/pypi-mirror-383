"""
Message bus for inter-agent communication.

Provides pub/sub messaging, routing, and delivery guarantees.
"""

import threading
import time
from collections import defaultdict, deque
from typing import Dict, List, Set, Optional, Callable, Deque
from dataclasses import dataclass, field

from .message import Message, MessageType, MessagePriority


@dataclass
class MessageStats:
    """Statistics for message bus."""

    total_sent: int = 0
    total_received: int = 0
    total_dropped: int = 0
    total_expired: int = 0
    messages_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    messages_by_priority: Dict[int, int] = field(default_factory=lambda: defaultdict(int))


class MessageBus:
    """
    Central message bus for agent communication.

    Features:
    - Point-to-point messaging
    - Broadcast messaging
    - Topic-based pub/sub
    - Message priorities
    - Message expiration
    - Delivery guarantees
    - Thread-safe operations

    Example:
        >>> bus = MessageBus()
        >>> bus.register_agent("agent-1")
        >>> bus.register_agent("agent-2")
        >>>
        >>> msg = Message(
        ...     sender="agent-1",
        ...     receiver="agent-2",
        ...     message_type=MessageType.INFORM,
        ...     content="Hello"
        ... )
        >>> bus.send(msg)
        >>>
        >>> messages = bus.receive("agent-2")
        >>> print(messages[0].content)
        Hello
    """

    def __init__(
        self,
        max_queue_size: int = 1000,
        enable_dead_letter: bool = True,
        message_ttl: float = 300.0  # 5 minutes default TTL
    ):
        """
        Initialize message bus.

        Args:
            max_queue_size: Maximum messages per agent queue
            enable_dead_letter: Enable dead letter queue for undeliverable messages
            message_ttl: Default message time-to-live in seconds
        """
        self.max_queue_size = max_queue_size
        self.enable_dead_letter = enable_dead_letter
        self.message_ttl = message_ttl

        # Agent message queues (agent_id -> queue)
        self._queues: Dict[str, Deque[Message]] = {}

        # Topic subscriptions (topic -> set of agent_ids)
        self._subscriptions: Dict[str, Set[str]] = defaultdict(set)

        # Dead letter queue
        self._dead_letter_queue: Deque[Message] = deque(maxlen=1000)

        # Statistics
        self._stats = MessageStats()

        # Thread safety
        self._lock = threading.RLock()

        # Registered agents
        self._agents: Set[str] = set()

    def register_agent(self, agent_id: str):
        """
        Register an agent with the message bus.

        Args:
            agent_id: Unique agent identifier
        """
        with self._lock:
            if agent_id not in self._agents:
                self._agents.add(agent_id)
                self._queues[agent_id] = deque(maxlen=self.max_queue_size)

    def unregister_agent(self, agent_id: str):
        """
        Unregister an agent from the message bus.

        Args:
            agent_id: Agent identifier
        """
        with self._lock:
            if agent_id in self._agents:
                self._agents.remove(agent_id)
                self._queues.pop(agent_id, None)

                # Remove from all subscriptions
                for subscribers in self._subscriptions.values():
                    subscribers.discard(agent_id)

    def send(self, message: Message) -> bool:
        """
        Send a message through the bus.

        Args:
            message: Message to send

        Returns:
            True if message was sent successfully
        """
        # Check expiration
        if message.is_expired():
            self._stats.total_expired += 1
            return False

        # Set expiration if not set
        if message.expires_at is None:
            message.expires_at = time.time() + self.message_ttl

        with self._lock:
            self._stats.total_sent += 1
            self._stats.messages_by_type[message.message_type.value] += 1
            self._stats.messages_by_priority[message.priority.value] += 1

            # Handle different message types
            if message.message_type == MessageType.BROADCAST:
                return self._broadcast(message)
            elif message.message_type == MessageType.MULTICAST:
                return self._multicast(message)
            else:
                return self._send_direct(message)

    def _send_direct(self, message: Message) -> bool:
        """Send message to specific receiver."""
        receiver = message.receiver

        if receiver not in self._agents:
            if self.enable_dead_letter:
                self._dead_letter_queue.append(message)
            self._stats.total_dropped += 1
            return False

        # Add to receiver's queue
        queue = self._queues[receiver]

        # Insert by priority (higher priority first)
        if message.priority == MessagePriority.CRITICAL or message.priority == MessagePriority.URGENT:
            # Insert at beginning for high priority
            queue.appendleft(message)
        else:
            # Append normally
            queue.append(message)

        return True

    def _broadcast(self, message: Message) -> bool:
        """Broadcast message to all agents except sender."""
        sent = False
        for agent_id in self._agents:
            if agent_id != message.sender:
                msg_copy = Message(
                    sender=message.sender,
                    receiver=agent_id,
                    message_type=MessageType.INFORM,  # Convert to INFORM
                    content=message.content,
                    priority=message.priority,
                    metadata=message.metadata,
                    conversation_id=message.conversation_id
                )
                if self._send_direct(msg_copy):
                    sent = True
        return sent

    def _multicast(self, message: Message) -> bool:
        """Send message to topic subscribers."""
        topic = message.receiver
        subscribers = self._subscriptions.get(topic, set())

        if not subscribers:
            if self.enable_dead_letter:
                self._dead_letter_queue.append(message)
            self._stats.total_dropped += 1
            return False

        sent = False
        for agent_id in subscribers:
            if agent_id != message.sender:
                msg_copy = Message(
                    sender=message.sender,
                    receiver=agent_id,
                    message_type=MessageType.INFORM,
                    content=message.content,
                    priority=message.priority,
                    metadata={**message.metadata, "topic": topic},
                    conversation_id=message.conversation_id
                )
                if self._send_direct(msg_copy):
                    sent = True
        return sent

    def receive(
        self,
        agent_id: str,
        max_messages: int = 10,
        timeout: float = 0,
        filter_type: Optional[MessageType] = None
    ) -> List[Message]:
        """
        Receive messages for an agent.

        Args:
            agent_id: Agent identifier
            max_messages: Maximum messages to retrieve
            timeout: Wait timeout in seconds (0 = non-blocking)
            filter_type: Only return messages of this type

        Returns:
            List of messages
        """
        if agent_id not in self._agents:
            return []

        start_time = time.time()
        messages = []

        while len(messages) < max_messages:
            with self._lock:
                queue = self._queues.get(agent_id)
                if not queue:
                    break

                # Get message from queue
                if queue:
                    message = queue.popleft()

                    # Check expiration
                    if message.is_expired():
                        self._stats.total_expired += 1
                        continue

                    # Check filter
                    if filter_type and message.message_type != filter_type:
                        # Put back non-matching message
                        queue.append(message)
                        continue

                    messages.append(message)
                    self._stats.total_received += 1
                else:
                    break

            # Check timeout
            if timeout > 0 and (time.time() - start_time) >= timeout:
                break

            # If no messages and timeout, wait a bit
            if not messages and timeout > 0:
                time.sleep(0.01)

        return messages

    def peek(self, agent_id: str, max_messages: int = 10) -> List[Message]:
        """
        Peek at messages without removing them.

        Args:
            agent_id: Agent identifier
            max_messages: Maximum messages to peek

        Returns:
            List of messages (not removed from queue)
        """
        if agent_id not in self._agents:
            return []

        with self._lock:
            queue = self._queues.get(agent_id, deque())
            return list(queue)[:max_messages]

    def subscribe(self, agent_id: str, topic: str):
        """
        Subscribe agent to a topic.

        Args:
            agent_id: Agent identifier
            topic: Topic name
        """
        with self._lock:
            if agent_id in self._agents:
                self._subscriptions[topic].add(agent_id)

    def unsubscribe(self, agent_id: str, topic: str):
        """
        Unsubscribe agent from a topic.

        Args:
            agent_id: Agent identifier
            topic: Topic name
        """
        with self._lock:
            self._subscriptions[topic].discard(agent_id)

    def get_subscribers(self, topic: str) -> Set[str]:
        """Get all subscribers for a topic."""
        with self._lock:
            return self._subscriptions.get(topic, set()).copy()

    def get_queue_size(self, agent_id: str) -> int:
        """Get number of pending messages for agent."""
        with self._lock:
            queue = self._queues.get(agent_id)
            return len(queue) if queue else 0

    def clear_queue(self, agent_id: str):
        """Clear all messages for an agent."""
        with self._lock:
            if agent_id in self._queues:
                self._queues[agent_id].clear()

    def get_dead_letters(self) -> List[Message]:
        """Get all dead letter messages."""
        with self._lock:
            return list(self._dead_letter_queue)

    def get_stats(self) -> Dict[str, any]:
        """Get message bus statistics."""
        with self._lock:
            return {
                "total_sent": self._stats.total_sent,
                "total_received": self._stats.total_received,
                "total_dropped": self._stats.total_dropped,
                "total_expired": self._stats.total_expired,
                "registered_agents": len(self._agents),
                "total_queued": sum(len(q) for q in self._queues.values()),
                "dead_letters": len(self._dead_letter_queue),
                "messages_by_type": dict(self._stats.messages_by_type),
                "messages_by_priority": dict(self._stats.messages_by_priority),
                "topics": len(self._subscriptions)
            }

    def get_agents(self) -> Set[str]:
        """Get all registered agents."""
        with self._lock:
            return self._agents.copy()

    def is_registered(self, agent_id: str) -> bool:
        """Check if agent is registered."""
        with self._lock:
            return agent_id in self._agents

    def reset(self):
        """Reset message bus (clear all queues and stats)."""
        with self._lock:
            for queue in self._queues.values():
                queue.clear()
            self._dead_letter_queue.clear()
            self._stats = MessageStats()
