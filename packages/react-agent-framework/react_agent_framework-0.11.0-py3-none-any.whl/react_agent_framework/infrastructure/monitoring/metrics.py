"""
Agent Metrics Collection

Collects and exports metrics for monitoring agent performance:
- Execution metrics (count, duration, success/failure)
- Token usage metrics
- Cost metrics
- Tool usage metrics

Supports export to:
- Prometheus (default)
- CloudWatch
- DataDog
- Custom exporters
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict
import threading


@dataclass
class MetricPoint:
    """A single metric data point"""

    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""


class AgentMetrics:
    """
    Metrics collection for AI agents

    Tracks:
    - Execution count, duration, success rate
    - Token usage (input, output, total)
    - Cost per execution
    - Tool usage statistics
    - Error rates by type

    Example:
        ```python
        metrics = AgentMetrics(agent_name="research-assistant")

        # Track execution
        with metrics.track_execution():
            result = agent.run("query")

        # Track tokens
        metrics.record_tokens(input=100, output=50, cost=0.001)

        # Track tool usage
        metrics.record_tool_call("search", duration=1.2, success=True)

        # Export metrics
        prometheus_data = metrics.export_prometheus()
        ```
    """

    def __init__(
        self,
        agent_name: str = "default",
        enabled: bool = True,
    ):
        """
        Initialize metrics collector

        Args:
            agent_name: Name of the agent being monitored
            enabled: Whether metrics collection is enabled
        """
        self.agent_name = agent_name
        self.enabled = enabled

        # Thread-safe counters
        self._lock = threading.Lock()

        # Execution metrics
        self.execution_count = 0
        self.execution_success = 0
        self.execution_failure = 0
        self.execution_durations: List[float] = []

        # Token metrics
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_tokens = 0

        # Cost metrics
        self.total_cost = 0.0
        self.cost_by_model: Dict[str, float] = defaultdict(float)

        # Tool metrics
        self.tool_calls: Dict[str, int] = defaultdict(int)
        self.tool_durations: Dict[str, List[float]] = defaultdict(list)
        self.tool_success: Dict[str, int] = defaultdict(int)
        self.tool_failure: Dict[str, int] = defaultdict(int)

        # Error metrics
        self.errors_by_type: Dict[str, int] = defaultdict(int)

        # Custom metrics
        self.custom_metrics: List[MetricPoint] = []

    def track_execution(self, labels: Optional[Dict[str, str]] = None):
        """
        Context manager to track execution time and success

        Args:
            labels: Additional labels for this execution

        Example:
            ```python
            with metrics.track_execution(labels={"user": "john"}):
                result = agent.run("query")
            ```
        """
        return _ExecutionTracker(self, labels or {})

    def record_execution(
        self,
        duration: float,
        success: bool = True,
        error_type: Optional[str] = None,
    ) -> None:
        """
        Record an execution

        Args:
            duration: Execution duration in seconds
            success: Whether execution succeeded
            error_type: Type of error if failed
        """
        if not self.enabled:
            return

        with self._lock:
            self.execution_count += 1
            self.execution_durations.append(duration)

            if success:
                self.execution_success += 1
            else:
                self.execution_failure += 1
                if error_type:
                    self.errors_by_type[error_type] += 1

    def record_tokens(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
        model: Optional[str] = None,
    ) -> None:
        """
        Record token usage and cost

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost: Cost in USD
            model: Model name
        """
        if not self.enabled:
            return

        with self._lock:
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_tokens += input_tokens + output_tokens
            self.total_cost += cost

            if model:
                self.cost_by_model[model] += cost

    def record_tool_call(
        self,
        tool_name: str,
        duration: float,
        success: bool = True,
    ) -> None:
        """
        Record a tool call

        Args:
            tool_name: Name of the tool
            duration: Duration in seconds
            success: Whether call succeeded
        """
        if not self.enabled:
            return

        with self._lock:
            self.tool_calls[tool_name] += 1
            self.tool_durations[tool_name].append(duration)

            if success:
                self.tool_success[tool_name] += 1
            else:
                self.tool_failure[tool_name] += 1

    def record_custom(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        unit: str = "",
    ) -> None:
        """
        Record a custom metric

        Args:
            name: Metric name
            value: Metric value
            labels: Additional labels
            unit: Unit of measurement
        """
        if not self.enabled:
            return

        metric = MetricPoint(
            name=name,
            value=value,
            labels=labels or {},
            unit=unit,
        )

        with self._lock:
            self.custom_metrics.append(metric)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get metrics summary

        Returns:
            Dictionary with all metrics
        """
        with self._lock:
            avg_duration = (
                sum(self.execution_durations) / len(self.execution_durations)
                if self.execution_durations
                else 0.0
            )

            success_rate = (
                self.execution_success / self.execution_count
                if self.execution_count > 0
                else 0.0
            )

            return {
                "agent": self.agent_name,
                "execution": {
                    "total": self.execution_count,
                    "success": self.execution_success,
                    "failure": self.execution_failure,
                    "success_rate": success_rate,
                    "avg_duration": avg_duration,
                },
                "tokens": {
                    "input": self.total_input_tokens,
                    "output": self.total_output_tokens,
                    "total": self.total_tokens,
                },
                "cost": {
                    "total": self.total_cost,
                    "by_model": dict(self.cost_by_model),
                },
                "tools": {
                    "calls": dict(self.tool_calls),
                    "success": dict(self.tool_success),
                    "failure": dict(self.tool_failure),
                },
                "errors": dict(self.errors_by_type),
            }

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format

        Returns:
            Prometheus-formatted metrics string
        """
        summary = self.get_summary()
        lines = []

        # Execution metrics
        lines.append(f"# HELP agent_executions_total Total number of executions")
        lines.append(f"# TYPE agent_executions_total counter")
        lines.append(
            f'agent_executions_total{{agent="{self.agent_name}"}} {self.execution_count}'
        )

        lines.append(
            f"# HELP agent_execution_success_total Successful executions"
        )
        lines.append(f"# TYPE agent_execution_success_total counter")
        lines.append(
            f'agent_execution_success_total{{agent="{self.agent_name}"}} {self.execution_success}'
        )

        lines.append(
            f"# HELP agent_execution_success_rate Execution success rate"
        )
        lines.append(f"# TYPE agent_execution_success_rate gauge")
        lines.append(
            f'agent_execution_success_rate{{agent="{self.agent_name}"}} {summary["execution"]["success_rate"]:.2f}'
        )

        # Token metrics
        lines.append(f"# HELP agent_tokens_total Total tokens used")
        lines.append(f"# TYPE agent_tokens_total counter")
        lines.append(
            f'agent_tokens_total{{agent="{self.agent_name}",type="input"}} {self.total_input_tokens}'
        )
        lines.append(
            f'agent_tokens_total{{agent="{self.agent_name}",type="output"}} {self.total_output_tokens}'
        )

        # Cost metrics
        lines.append(f"# HELP agent_cost_usd_total Total cost in USD")
        lines.append(f"# TYPE agent_cost_usd_total counter")
        lines.append(
            f'agent_cost_usd_total{{agent="{self.agent_name}"}} {self.total_cost:.4f}'
        )

        # Tool metrics
        for tool, count in self.tool_calls.items():
            lines.append(
                f'agent_tool_calls_total{{agent="{self.agent_name}",tool="{tool}"}} {count}'
            )

        return "\n".join(lines) + "\n"

    def reset(self) -> None:
        """Reset all metrics"""
        with self._lock:
            self.execution_count = 0
            self.execution_success = 0
            self.execution_failure = 0
            self.execution_durations.clear()
            self.total_input_tokens = 0
            self.total_output_tokens = 0
            self.total_tokens = 0
            self.total_cost = 0.0
            self.cost_by_model.clear()
            self.tool_calls.clear()
            self.tool_durations.clear()
            self.tool_success.clear()
            self.tool_failure.clear()
            self.errors_by_type.clear()
            self.custom_metrics.clear()


class _ExecutionTracker:
    """Context manager for tracking execution time"""

    def __init__(self, metrics: AgentMetrics, labels: Dict[str, str]):
        self.metrics = metrics
        self.labels = labels
        self.start_time = 0.0
        self.success = True
        self.error_type: Optional[str] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time

        if exc_type is not None:
            self.success = False
            self.error_type = exc_type.__name__

        self.metrics.record_execution(
            duration=duration,
            success=self.success,
            error_type=self.error_type,
        )

        return False  # Don't suppress exceptions
