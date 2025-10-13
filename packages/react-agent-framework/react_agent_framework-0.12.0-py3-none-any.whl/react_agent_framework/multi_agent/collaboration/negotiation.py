"""Negotiation protocols for multi-agent task allocation."""
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

@dataclass
class Bid:
    agent_id: str
    task_id: str
    bid_value: float
    timestamp: float = field(default_factory=time.time)

class NegotiationProtocol:
    def __init__(self, protocol_name: str):
        self.protocol_name = protocol_name

class ContractNetProtocol(NegotiationProtocol):
    def __init__(self):
        super().__init__("contract-net")
        self._bids: Dict[str, list[Bid]] = {}

    def call_for_proposals(self, task_id: str):
        self._bids[task_id] = []

    def submit_bid(self, task_id: str, agent_id: str, bid_value: float):
        if task_id in self._bids:
            self._bids[task_id].append(Bid(agent_id, task_id, bid_value))

    def select_winner(self, task_id: str) -> Optional[str]:
        bids = self._bids.get(task_id, [])
        if not bids:
            return None
        winner = min(bids, key=lambda b: b.bid_value)
        return winner.agent_id
