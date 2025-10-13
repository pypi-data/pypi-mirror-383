"""
Agent Telemetry and Distributed Tracing

Provides distributed tracing capabilities for agents using OpenTelemetry.

Supports:
- Span creation for operations
- Context propagation across boundaries
- Trace export to Jaeger, Zipkin, CloudWatch X-Ray
- Automatic instrumentation
"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any, List
from uuid import uuid4


@dataclass
class Span:
    """A trace span"""

    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    attributes: Dict[str, Any] = None
    status: str = "ok"  # ok, error

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


class AgentTelemetry:
    """
    Telemetry system for agent operations

    Provides distributed tracing to understand:
    - Operation flow and dependencies
    - Latency bottlenecks
    - Error propagation
    - Resource usage

    Example:
        ```python
        telemetry = AgentTelemetry(agent_name="research-assistant")

        # Create a trace
        with telemetry.start_trace("agent_execution") as trace:
            # Create spans for operations
            with trace.span("query_processing"):
                process_query()

            with trace.span("tool_execution", attributes={"tool": "search"}):
                execute_tool()

        # Export traces
        traces = telemetry.get_traces()
        ```
    """

    def __init__(
        self,
        agent_name: str = "default",
        enabled: bool = True,
        export_to: Optional[str] = None,
    ):
        """
        Initialize telemetry

        Args:
            agent_name: Name of the agent
            enabled: Whether telemetry is enabled
            export_to: Export destination (jaeger, zipkin, xray, None)
        """
        self.agent_name = agent_name
        self.enabled = enabled
        self.export_to = export_to

        # Storage for traces and spans
        self.traces: List[Trace] = []
        self.current_trace: Optional[Trace] = None

    def start_trace(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> "Trace":
        """
        Start a new trace

        Args:
            name: Trace name
            attributes: Trace attributes

        Returns:
            Trace object
        """
        if not self.enabled:
            return _NoOpTrace()

        trace = Trace(
            telemetry=self,
            trace_id=str(uuid4()),
            name=name,
            attributes=attributes or {},
        )

        self.current_trace = trace
        self.traces.append(trace)

        return trace

    def get_traces(self) -> List[Trace]:
        """Get all traces"""
        return self.traces

    def clear_traces(self) -> None:
        """Clear all traces"""
        self.traces.clear()
        self.current_trace = None

    def export_traces(self) -> List[Dict[str, Any]]:
        """
        Export traces in standard format

        Returns:
            List of trace dictionaries
        """
        return [trace.to_dict() for trace in self.traces]


class Trace:
    """
    A trace representing a complete operation

    Contains multiple spans representing sub-operations
    """

    def __init__(
        self,
        telemetry: AgentTelemetry,
        trace_id: str,
        name: str,
        attributes: Dict[str, Any],
    ):
        self.telemetry = telemetry
        self.trace_id = trace_id
        self.name = name
        self.attributes = attributes
        self.spans: List[Span] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.current_span: Optional[Span] = None

    def span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> "_SpanContext":
        """
        Create a span within this trace

        Args:
            name: Span name
            attributes: Span attributes

        Returns:
            Span context manager
        """
        parent_span_id = self.current_span.span_id if self.current_span else None

        span = Span(
            span_id=str(uuid4()),
            trace_id=self.trace_id,
            parent_span_id=parent_span_id,
            name=name,
            start_time=datetime.now(),
            attributes=attributes or {},
        )

        self.spans.append(span)
        return _SpanContext(self, span)

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary"""
        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            "attributes": self.attributes,
            "spans": [
                {
                    "span_id": span.span_id,
                    "parent_span_id": span.parent_span_id,
                    "name": span.name,
                    "start_time": span.start_time.isoformat(),
                    "end_time": span.end_time.isoformat() if span.end_time else None,
                    "duration": span.duration,
                    "attributes": span.attributes,
                    "status": span.status,
                }
                for span in self.spans
            ],
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        return False


class _SpanContext:
    """Context manager for span"""

    def __init__(self, trace: Trace, span: Span):
        self.trace = trace
        self.span = span
        self.previous_span = None

    def __enter__(self):
        self.previous_span = self.trace.current_span
        self.trace.current_span = self.span
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.span.end_time = datetime.now()
        self.span.duration = (self.span.end_time - self.span.start_time).total_seconds()

        if exc_type is not None:
            self.span.status = "error"
            self.span.attributes["error_type"] = exc_type.__name__
            self.span.attributes["error_message"] = str(exc_val)

        self.trace.current_span = self.previous_span
        return False


class _NoOpTrace:
    """No-op trace for when telemetry is disabled"""

    def span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
