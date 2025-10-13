"""
Collaboration module for multi-agent systems.

Provides team management, patterns, negotiation, and knowledge sharing.
"""

from .team import Team, TeamManager
from .patterns import CollaborationPattern, HierarchicalPattern, PeerToPeerPattern
from .negotiation import NegotiationProtocol, ContractNetProtocol, Bid
from .knowledge_sharing import KnowledgeBase, SharedKnowledge

__all__ = [
    "Team",
    "TeamManager",
    "CollaborationPattern",
    "HierarchicalPattern",
    "PeerToPeerPattern",
    "NegotiationProtocol",
    "ContractNetProtocol",
    "Bid",
    "KnowledgeBase",
    "SharedKnowledge",
]
