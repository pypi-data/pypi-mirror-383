"""
Feedback collection and analysis for agent operations.

Provides mechanisms for collecting and analyzing human feedback.
"""

import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict


class FeedbackType(str, Enum):
    """Type of feedback."""

    RATING = "rating"  # Numeric rating
    COMMENT = "comment"  # Text comment
    CORRECTION = "correction"  # Correction to agent output
    BUG_REPORT = "bug_report"  # Bug report
    FEATURE_REQUEST = "feature_request"  # Feature request
    THUMBS = "thumbs"  # Thumbs up/down


class FeedbackRating(int, Enum):
    """Predefined rating values."""

    VERY_BAD = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    VERY_GOOD = 5


@dataclass
class Feedback:
    """Represents user feedback."""

    feedback_id: str
    feedback_type: FeedbackType
    agent_id: str
    user: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Rating feedback
    rating: Optional[int] = None

    # Text feedback
    comment: Optional[str] = None

    # Correction feedback
    original_output: Optional[str] = None
    corrected_output: Optional[str] = None

    # Thumbs feedback
    thumbs_up: Optional[bool] = None

    # Context
    operation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Response tracking
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    response_text: Optional[str] = None


class FeedbackCollector:
    """
    Collects and analyzes human feedback.

    Features:
    - Multiple feedback types
    - Rating aggregation
    - Comment analysis
    - Correction tracking
    - Feedback trends
    - Acknowledgment system

    Example:
        >>> collector = FeedbackCollector()
        >>>
        >>> # Submit rating
        >>> feedback = collector.submit_rating(
        ...     agent_id="agent-1",
        ...     user="user-1",
        ...     rating=5,
        ...     operation="search",
        ...     comment="Great results!"
        ... )
        >>>
        >>> # Get average rating
        >>> avg = collector.get_average_rating(agent_id="agent-1")
        >>> print(f"Average: {avg:.2f}")
    """

    def __init__(self):
        """Initialize feedback collector."""
        self._feedbacks: Dict[str, Feedback] = {}
        self._lock = threading.Lock()
        self._feedback_counter = 0

        # Analytics caches
        self._rating_cache: Dict[str, List[int]] = defaultdict(list)
        self._thumbs_cache: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"up": 0, "down": 0}
        )

    def submit_rating(
        self,
        agent_id: str,
        user: str,
        rating: int,
        operation: Optional[str] = None,
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Feedback:
        """
        Submit a rating feedback.

        Args:
            agent_id: Agent identifier
            user: User identifier
            rating: Rating value (1-5)
            operation: Operation being rated
            comment: Optional comment
            metadata: Additional metadata

        Returns:
            Feedback object
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        with self._lock:
            feedback_id = self._generate_id()
            feedback = Feedback(
                feedback_id=feedback_id,
                feedback_type=FeedbackType.RATING,
                agent_id=agent_id,
                user=user,
                rating=rating,
                comment=comment,
                operation=operation,
                metadata=metadata or {}
            )

            self._feedbacks[feedback_id] = feedback
            self._rating_cache[agent_id].append(rating)

            return feedback

    def submit_comment(
        self,
        agent_id: str,
        user: str,
        comment: str,
        operation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Feedback:
        """
        Submit a comment feedback.

        Args:
            agent_id: Agent identifier
            user: User identifier
            comment: Comment text
            operation: Operation being commented on
            metadata: Additional metadata

        Returns:
            Feedback object
        """
        with self._lock:
            feedback_id = self._generate_id()
            feedback = Feedback(
                feedback_id=feedback_id,
                feedback_type=FeedbackType.COMMENT,
                agent_id=agent_id,
                user=user,
                comment=comment,
                operation=operation,
                metadata=metadata or {}
            )

            self._feedbacks[feedback_id] = feedback
            return feedback

    def submit_correction(
        self,
        agent_id: str,
        user: str,
        original_output: str,
        corrected_output: str,
        operation: Optional[str] = None,
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Feedback:
        """
        Submit a correction feedback.

        Args:
            agent_id: Agent identifier
            user: User identifier
            original_output: Original agent output
            corrected_output: Corrected output
            operation: Operation being corrected
            comment: Optional comment
            metadata: Additional metadata

        Returns:
            Feedback object
        """
        with self._lock:
            feedback_id = self._generate_id()
            feedback = Feedback(
                feedback_id=feedback_id,
                feedback_type=FeedbackType.CORRECTION,
                agent_id=agent_id,
                user=user,
                original_output=original_output,
                corrected_output=corrected_output,
                comment=comment,
                operation=operation,
                metadata=metadata or {}
            )

            self._feedbacks[feedback_id] = feedback
            return feedback

    def submit_thumbs(
        self,
        agent_id: str,
        user: str,
        thumbs_up: bool,
        operation: Optional[str] = None,
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Feedback:
        """
        Submit thumbs up/down feedback.

        Args:
            agent_id: Agent identifier
            user: User identifier
            thumbs_up: True for thumbs up, False for thumbs down
            operation: Operation being rated
            comment: Optional comment
            metadata: Additional metadata

        Returns:
            Feedback object
        """
        with self._lock:
            feedback_id = self._generate_id()
            feedback = Feedback(
                feedback_id=feedback_id,
                feedback_type=FeedbackType.THUMBS,
                agent_id=agent_id,
                user=user,
                thumbs_up=thumbs_up,
                comment=comment,
                operation=operation,
                metadata=metadata or {}
            )

            self._feedbacks[feedback_id] = feedback

            # Update thumbs cache
            if thumbs_up:
                self._thumbs_cache[agent_id]["up"] += 1
            else:
                self._thumbs_cache[agent_id]["down"] += 1

            return feedback

    def submit_bug_report(
        self,
        agent_id: str,
        user: str,
        description: str,
        operation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Feedback:
        """
        Submit a bug report.

        Args:
            agent_id: Agent identifier
            user: User identifier
            description: Bug description
            operation: Operation where bug occurred
            metadata: Additional metadata (e.g., stack trace)

        Returns:
            Feedback object
        """
        with self._lock:
            feedback_id = self._generate_id()
            feedback = Feedback(
                feedback_id=feedback_id,
                feedback_type=FeedbackType.BUG_REPORT,
                agent_id=agent_id,
                user=user,
                comment=description,
                operation=operation,
                metadata=metadata or {}
            )

            self._feedbacks[feedback_id] = feedback
            return feedback

    def submit_feature_request(
        self,
        agent_id: str,
        user: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Feedback:
        """
        Submit a feature request.

        Args:
            agent_id: Agent identifier
            user: User identifier
            description: Feature description
            metadata: Additional metadata

        Returns:
            Feedback object
        """
        with self._lock:
            feedback_id = self._generate_id()
            feedback = Feedback(
                feedback_id=feedback_id,
                feedback_type=FeedbackType.FEATURE_REQUEST,
                agent_id=agent_id,
                user=user,
                comment=description,
                metadata=metadata or {}
            )

            self._feedbacks[feedback_id] = feedback
            return feedback

    def acknowledge_feedback(
        self,
        feedback_id: str,
        acknowledger: str,
        response: Optional[str] = None
    ) -> bool:
        """
        Acknowledge feedback.

        Args:
            feedback_id: Feedback ID
            acknowledger: Who is acknowledging
            response: Optional response text

        Returns:
            True if acknowledged, False if not found
        """
        with self._lock:
            feedback = self._feedbacks.get(feedback_id)
            if not feedback:
                return False

            feedback.acknowledged = True
            feedback.acknowledged_by = acknowledger
            feedback.acknowledged_at = datetime.now()
            feedback.response_text = response

            return True

    def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        """Get feedback by ID."""
        return self._feedbacks.get(feedback_id)

    def get_all_feedback(
        self,
        agent_id: Optional[str] = None,
        user: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None,
        operation: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        limit: int = 100
    ) -> List[Feedback]:
        """
        Get all feedback with optional filters.

        Args:
            agent_id: Filter by agent ID
            user: Filter by user
            feedback_type: Filter by feedback type
            operation: Filter by operation
            acknowledged: Filter by acknowledgment status
            limit: Maximum number of results

        Returns:
            List of feedback items
        """
        with self._lock:
            feedbacks = list(self._feedbacks.values())

            if agent_id:
                feedbacks = [f for f in feedbacks if f.agent_id == agent_id]

            if user:
                feedbacks = [f for f in feedbacks if f.user == user]

            if feedback_type:
                feedbacks = [f for f in feedbacks if f.feedback_type == feedback_type]

            if operation:
                feedbacks = [f for f in feedbacks if f.operation == operation]

            if acknowledged is not None:
                feedbacks = [f for f in feedbacks if f.acknowledged == acknowledged]

            # Sort by timestamp (newest first)
            feedbacks.sort(key=lambda f: f.timestamp, reverse=True)

            return feedbacks[:limit]

    def get_average_rating(
        self,
        agent_id: Optional[str] = None,
        operation: Optional[str] = None
    ) -> Optional[float]:
        """
        Get average rating.

        Args:
            agent_id: Filter by agent ID
            operation: Filter by operation

        Returns:
            Average rating or None if no ratings
        """
        ratings = [
            f.rating for f in self._feedbacks.values()
            if f.feedback_type == FeedbackType.RATING
            and f.rating is not None
            and (agent_id is None or f.agent_id == agent_id)
            and (operation is None or f.operation == operation)
        ]

        if not ratings:
            return None

        return sum(ratings) / len(ratings)

    def get_thumbs_stats(
        self,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get thumbs up/down statistics.

        Args:
            agent_id: Filter by agent ID

        Returns:
            Dictionary with thumbs statistics
        """
        if agent_id:
            cache = self._thumbs_cache.get(agent_id, {"up": 0, "down": 0})
            total = cache["up"] + cache["down"]
            return {
                "thumbs_up": cache["up"],
                "thumbs_down": cache["down"],
                "total": total,
                "thumbs_up_rate": cache["up"] / total if total > 0 else 0
            }

        # All agents
        total_up = sum(c["up"] for c in self._thumbs_cache.values())
        total_down = sum(c["down"] for c in self._thumbs_cache.values())
        total = total_up + total_down

        return {
            "thumbs_up": total_up,
            "thumbs_down": total_down,
            "total": total,
            "thumbs_up_rate": total_up / total if total > 0 else 0
        }

    def get_corrections(
        self,
        agent_id: Optional[str] = None,
        operation: Optional[str] = None,
        limit: int = 50
    ) -> List[Feedback]:
        """
        Get correction feedbacks.

        Args:
            agent_id: Filter by agent ID
            operation: Filter by operation
            limit: Maximum number of results

        Returns:
            List of correction feedbacks
        """
        return self.get_all_feedback(
            agent_id=agent_id,
            feedback_type=FeedbackType.CORRECTION,
            operation=operation,
            limit=limit
        )

    def get_bug_reports(
        self,
        agent_id: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        limit: int = 50
    ) -> List[Feedback]:
        """
        Get bug reports.

        Args:
            agent_id: Filter by agent ID
            acknowledged: Filter by acknowledgment status
            limit: Maximum number of results

        Returns:
            List of bug report feedbacks
        """
        return self.get_all_feedback(
            agent_id=agent_id,
            feedback_type=FeedbackType.BUG_REPORT,
            acknowledged=acknowledged,
            limit=limit
        )

    def get_feature_requests(
        self,
        agent_id: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        limit: int = 50
    ) -> List[Feedback]:
        """
        Get feature requests.

        Args:
            agent_id: Filter by agent ID
            acknowledged: Filter by acknowledgment status
            limit: Maximum number of results

        Returns:
            List of feature request feedbacks
        """
        return self.get_all_feedback(
            agent_id=agent_id,
            feedback_type=FeedbackType.FEATURE_REQUEST,
            acknowledged=acknowledged,
            limit=limit
        )

    def get_stats(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get feedback statistics.

        Args:
            agent_id: Filter by agent ID

        Returns:
            Dictionary with statistics
        """
        feedbacks = [
            f for f in self._feedbacks.values()
            if agent_id is None or f.agent_id == agent_id
        ]

        total = len(feedbacks)
        by_type = defaultdict(int)
        acknowledged_count = 0

        for feedback in feedbacks:
            by_type[feedback.feedback_type.value] += 1
            if feedback.acknowledged:
                acknowledged_count += 1

        avg_rating = self.get_average_rating(agent_id)
        thumbs_stats = self.get_thumbs_stats(agent_id)

        return {
            "total_feedbacks": total,
            "by_type": dict(by_type),
            "acknowledged": acknowledged_count,
            "acknowledgment_rate": acknowledged_count / total if total > 0 else 0,
            "average_rating": avg_rating,
            "thumbs_stats": thumbs_stats
        }

    def _generate_id(self) -> str:
        """Generate unique feedback ID."""
        self._feedback_counter += 1
        return f"feedback-{self._feedback_counter}-{int(datetime.now().timestamp())}"

    def clear_feedback(self, agent_id: Optional[str] = None):
        """
        Clear feedback data.

        Args:
            agent_id: Clear only for specific agent, or all if None
        """
        with self._lock:
            if agent_id:
                # Remove feedbacks for specific agent
                self._feedbacks = {
                    fid: f for fid, f in self._feedbacks.items()
                    if f.agent_id != agent_id
                }
                self._rating_cache.pop(agent_id, None)
                self._thumbs_cache.pop(agent_id, None)
            else:
                # Clear all
                self._feedbacks.clear()
                self._rating_cache.clear()
                self._thumbs_cache.clear()
                self._feedback_counter = 0

    def export_feedback(
        self,
        agent_id: Optional[str] = None,
        format: str = "dict"
    ) -> List[Dict[str, Any]]:
        """
        Export feedback data.

        Args:
            agent_id: Filter by agent ID
            format: Export format (currently only "dict" supported)

        Returns:
            List of feedback dictionaries
        """
        feedbacks = self.get_all_feedback(agent_id=agent_id, limit=1000000)

        if format == "dict":
            return [
                {
                    "feedback_id": f.feedback_id,
                    "feedback_type": f.feedback_type.value,
                    "agent_id": f.agent_id,
                    "user": f.user,
                    "timestamp": f.timestamp.isoformat(),
                    "rating": f.rating,
                    "comment": f.comment,
                    "original_output": f.original_output,
                    "corrected_output": f.corrected_output,
                    "thumbs_up": f.thumbs_up,
                    "operation": f.operation,
                    "acknowledged": f.acknowledged,
                    "acknowledged_by": f.acknowledged_by,
                    "acknowledged_at": f.acknowledged_at.isoformat()
                    if f.acknowledged_at else None,
                    "metadata": f.metadata
                }
                for f in feedbacks
            ]

        return []
