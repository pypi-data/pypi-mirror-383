"""Team management for multi-agent collaboration."""
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Set, Optional, Any

@dataclass
class Team:
    team_id: str
    name: str
    leader: Optional[str] = None
    members: Set[str] = field(default_factory=set)
    goals: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def add_member(self, agent_id: str):
        self.members.add(agent_id)

    def remove_member(self, agent_id: str):
        self.members.discard(agent_id)

    def set_leader(self, agent_id: str):
        if agent_id in self.members:
            self.leader = agent_id

class TeamManager:
    def __init__(self):
        self._teams: Dict[str, Team] = {}
        self._lock = threading.Lock()

    def create_team(self, team_id: str, name: str, leader: Optional[str] = None) -> Team:
        with self._lock:
            team = Team(team_id, name, leader)
            if leader:
                team.add_member(leader)
            self._teams[team_id] = team
            return team

    def add_member(self, team_id: str, agent_id: str):
        with self._lock:
            if team_id in self._teams:
                self._teams[team_id].add_member(agent_id)

    def get_team(self, team_id: str) -> Optional[Team]:
        return self._teams.get(team_id)

    def get_teams_for_agent(self, agent_id: str) -> list[Team]:
        return [t for t in self._teams.values() if agent_id in t.members]
