"""Consensus mechanisms for multi-agent coordination."""
import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Set, Optional, Any

class ConsensusType(str, Enum):
    MAJORITY = "majority"
    UNANIMOUS = "unanimous"
    QUORUM = "quorum"

@dataclass
class Vote:
    agent_id: str
    value: bool
    timestamp: float = field(default_factory=time.time)

@dataclass
class Proposal:
    proposal_id: str
    proposer: str
    content: Any
    votes: Dict[str, Vote] = field(default_factory=dict)
    required_votes: int = 2
    consensus_type: ConsensusType = ConsensusType.MAJORITY

    def add_vote(self, agent_id: str, value: bool):
        self.votes[agent_id] = Vote(agent_id, value)

    def has_consensus(self) -> bool:
        if not self.votes:
            return False
        yes_votes = sum(1 for v in self.votes.values() if v.value)
        total_votes = len(self.votes)
        
        if self.consensus_type == ConsensusType.UNANIMOUS:
            return yes_votes == total_votes and total_votes >= self.required_votes
        elif self.consensus_type == ConsensusType.MAJORITY:
            return yes_votes > total_votes / 2 and total_votes >= self.required_votes
        return yes_votes >= self.required_votes

class ConsensusManager:
    def __init__(self):
        self._proposals: Dict[str, Proposal] = {}
        self._lock = threading.Lock()

    def create_proposal(self, proposal_id: str, proposer: str, content: Any, 
                       consensus_type: ConsensusType = ConsensusType.MAJORITY) -> Proposal:
        with self._lock:
            proposal = Proposal(proposal_id, proposer, content, consensus_type=consensus_type)
            self._proposals[proposal_id] = proposal
            return proposal

    def vote(self, proposal_id: str, agent_id: str, value: bool) -> bool:
        with self._lock:
            if proposal_id in self._proposals:
                self._proposals[proposal_id].add_vote(agent_id, value)
                return True
            return False

    def get_result(self, proposal_id: str) -> Optional[bool]:
        proposal = self._proposals.get(proposal_id)
        return proposal.has_consensus() if proposal else None
