"""
Communication protocols for agent interaction.

Provides ACL-like (Agent Communication Language) protocols.
"""

from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass

from .message import Message, MessageType, MessagePriority


class Performative(str, Enum):
    """
    ACL performatives (speech acts).

    Based on FIPA ACL specification.
    """

    # Passing information
    INFORM = "inform"  # Inform that proposition is true
    CONFIRM = "confirm"  # Confirm truth of proposition
    DISCONFIRM = "disconfirm"  # Inform that proposition is false
    INFORM_IF = "inform_if"  # Inform if proposition is true
    INFORM_REF = "inform_ref"  # Inform about object

    # Requesting information
    QUERY_IF = "query_if"  # Query if proposition is true
    QUERY_REF = "query_ref"  # Query about object
    SUBSCRIBE = "subscribe"  # Subscribe to notifications

    # Requesting action
    REQUEST = "request"  # Request action
    REQUEST_WHEN = "request_when"  # Request action when condition
    REQUEST_WHENEVER = "request_whenever"  # Request action whenever condition

    # Negotiation
    CFP = "cfp"  # Call for proposal
    PROPOSE = "propose"  # Propose action
    ACCEPT_PROPOSAL = "accept_proposal"  # Accept proposal
    REJECT_PROPOSAL = "reject_proposal"  # Reject proposal

    # Agreement/Disagreement
    AGREE = "agree"  # Agree to perform action
    REFUSE = "refuse"  # Refuse to perform action
    CANCEL = "cancel"  # Cancel previous request

    # Notification
    FAILURE = "failure"  # Action failed
    NOT_UNDERSTOOD = "not_understood"  # Message not understood


class Protocol:
    """
    Base protocol for agent communication.

    Protocols define rules and patterns for agent interaction.
    """

    def __init__(self, name: str):
        """
        Initialize protocol.

        Args:
            name: Protocol name
        """
        self.name = name

    def validate_message(self, message: Message) -> bool:
        """
        Validate message conforms to protocol.

        Args:
            message: Message to validate

        Returns:
            True if valid
        """
        return True  # Base implementation accepts all

    def create_message(
        self,
        sender: str,
        receiver: str,
        performative: Performative,
        content: Any,
        **kwargs
    ) -> Message:
        """
        Create protocol-compliant message.

        Args:
            sender: Sender agent ID
            receiver: Receiver agent ID
            performative: Message performative
            content: Message content
            **kwargs: Additional message parameters

        Returns:
            Protocol-compliant message
        """
        # Map performative to message type
        message_type = self._map_performative_to_type(performative)

        return Message(
            sender=sender,
            receiver=receiver,
            message_type=message_type,
            content=content,
            metadata={
                "protocol": self.name,
                "performative": performative.value,
                **kwargs.get("metadata", {})
            },
            **{k: v for k, v in kwargs.items() if k != "metadata"}
        )

    def _map_performative_to_type(self, performative: Performative) -> MessageType:
        """Map ACL performative to MessageType."""
        mapping = {
            Performative.INFORM: MessageType.INFORM,
            Performative.CONFIRM: MessageType.INFORM,
            Performative.DISCONFIRM: MessageType.INFORM,
            Performative.QUERY_IF: MessageType.QUERY,
            Performative.QUERY_REF: MessageType.QUERY,
            Performative.REQUEST: MessageType.REQUEST,
            Performative.REQUEST_WHEN: MessageType.REQUEST,
            Performative.REQUEST_WHENEVER: MessageType.REQUEST,
            Performative.PROPOSE: MessageType.PROPOSE,
            Performative.ACCEPT_PROPOSAL: MessageType.ACCEPT,
            Performative.REJECT_PROPOSAL: MessageType.REJECT,
            Performative.AGREE: MessageType.AGREE,
            Performative.REFUSE: MessageType.REFUSE,
            Performative.FAILURE: MessageType.ERROR,
        }
        return mapping.get(performative, MessageType.INFORM)


class ACLProtocol(Protocol):
    """
    ACL (Agent Communication Language) protocol.

    Implements FIPA ACL-like communication patterns.

    Example:
        >>> protocol = ACLProtocol()
        >>>
        >>> # Request action
        >>> msg = protocol.request(
        ...     sender="agent-1",
        ...     receiver="agent-2",
        ...     action="search",
        ...     params={"query": "test"}
        ... )
        >>>
        >>> # Inform result
        >>> reply = protocol.inform(
        ...     sender="agent-2",
        ...     receiver="agent-1",
        ...     proposition="search completed",
        ...     reply_to=msg.message_id
        ... )
    """

    def __init__(self):
        """Initialize ACL protocol."""
        super().__init__("FIPA-ACL")

    def inform(
        self,
        sender: str,
        receiver: str,
        proposition: Any,
        **kwargs
    ) -> Message:
        """
        Inform that proposition is true.

        Args:
            sender: Sender agent ID
            receiver: Receiver agent ID
            proposition: Proposition content
            **kwargs: Additional parameters

        Returns:
            INFORM message
        """
        return self.create_message(
            sender=sender,
            receiver=receiver,
            performative=Performative.INFORM,
            content={"proposition": proposition},
            **kwargs
        )

    def request(
        self,
        sender: str,
        receiver: str,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Message:
        """
        Request an action.

        Args:
            sender: Sender agent ID
            receiver: Receiver agent ID
            action: Action to perform
            params: Action parameters
            **kwargs: Additional parameters

        Returns:
            REQUEST message
        """
        return self.create_message(
            sender=sender,
            receiver=receiver,
            performative=Performative.REQUEST,
            content={"action": action, "params": params or {}},
            **kwargs
        )

    def query_if(
        self,
        sender: str,
        receiver: str,
        proposition: str,
        **kwargs
    ) -> Message:
        """
        Query if proposition is true.

        Args:
            sender: Sender agent ID
            receiver: Receiver agent ID
            proposition: Proposition to query
            **kwargs: Additional parameters

        Returns:
            QUERY_IF message
        """
        return self.create_message(
            sender=sender,
            receiver=receiver,
            performative=Performative.QUERY_IF,
            content={"proposition": proposition},
            **kwargs
        )

    def propose(
        self,
        sender: str,
        receiver: str,
        proposal: Any,
        **kwargs
    ) -> Message:
        """
        Propose an action or plan.

        Args:
            sender: Sender agent ID
            receiver: Receiver agent ID
            proposal: Proposal content
            **kwargs: Additional parameters

        Returns:
            PROPOSE message
        """
        return self.create_message(
            sender=sender,
            receiver=receiver,
            performative=Performative.PROPOSE,
            content={"proposal": proposal},
            **kwargs
        )

    def accept_proposal(
        self,
        sender: str,
        receiver: str,
        proposal_id: str,
        **kwargs
    ) -> Message:
        """
        Accept a proposal.

        Args:
            sender: Sender agent ID
            receiver: Receiver agent ID
            proposal_id: ID of accepted proposal
            **kwargs: Additional parameters

        Returns:
            ACCEPT_PROPOSAL message
        """
        return self.create_message(
            sender=sender,
            receiver=receiver,
            performative=Performative.ACCEPT_PROPOSAL,
            content={"proposal_id": proposal_id},
            **kwargs
        )

    def reject_proposal(
        self,
        sender: str,
        receiver: str,
        proposal_id: str,
        reason: Optional[str] = None,
        **kwargs
    ) -> Message:
        """
        Reject a proposal.

        Args:
            sender: Sender agent ID
            receiver: Receiver agent ID
            proposal_id: ID of rejected proposal
            reason: Rejection reason
            **kwargs: Additional parameters

        Returns:
            REJECT_PROPOSAL message
        """
        return self.create_message(
            sender=sender,
            receiver=receiver,
            performative=Performative.REJECT_PROPOSAL,
            content={"proposal_id": proposal_id, "reason": reason},
            **kwargs
        )

    def agree(
        self,
        sender: str,
        receiver: str,
        action: str,
        **kwargs
    ) -> Message:
        """
        Agree to perform an action.

        Args:
            sender: Sender agent ID
            receiver: Receiver agent ID
            action: Action agreed to perform
            **kwargs: Additional parameters

        Returns:
            AGREE message
        """
        return self.create_message(
            sender=sender,
            receiver=receiver,
            performative=Performative.AGREE,
            content={"action": action},
            **kwargs
        )

    def refuse(
        self,
        sender: str,
        receiver: str,
        action: str,
        reason: Optional[str] = None,
        **kwargs
    ) -> Message:
        """
        Refuse to perform an action.

        Args:
            sender: Sender agent ID
            receiver: Receiver agent ID
            action: Action refused
            reason: Refusal reason
            **kwargs: Additional parameters

        Returns:
            REFUSE message
        """
        return self.create_message(
            sender=sender,
            receiver=receiver,
            performative=Performative.REFUSE,
            content={"action": action, "reason": reason},
            **kwargs
        )

    def failure(
        self,
        sender: str,
        receiver: str,
        action: str,
        error: str,
        **kwargs
    ) -> Message:
        """
        Report action failure.

        Args:
            sender: Sender agent ID
            receiver: Receiver agent ID
            action: Failed action
            error: Error description
            **kwargs: Additional parameters

        Returns:
            FAILURE message
        """
        return self.create_message(
            sender=sender,
            receiver=receiver,
            performative=Performative.FAILURE,
            content={"action": action, "error": error},
            priority=MessagePriority.HIGH,
            **kwargs
        )
