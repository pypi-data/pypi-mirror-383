"""
Infrastructure Monitoring Demo

Demonstrates the new monitoring system (v0.11.0):
- AgentMetrics: Metrics collection and export
- AgentLogger: Structured logging
- AgentTelemetry: Distributed tracing

Part of Layer 4 (Agentic Infrastructure) implementation.
"""

from react_agent_framework import ReactAgent
from react_agent_framework.infrastructure.monitoring import (
    AgentMetrics,
    AgentLogger,
    AgentTelemetry,
    LogLevel,
)


def demo_1_metrics():
    """Demo 1: Metrics Collection"""
    print("=" * 80)
    print("DEMO 1: Metrics Collection")
    print("=" * 80)

    # Create metrics collector
    metrics = AgentMetrics(agent_name="demo-agent")

    # Track executions
    print("\n1. Tracking executions...")
    with metrics.track_execution():
        # Simulate agent work
        import time
        time.sleep(0.1)

    with metrics.track_execution():
        time.sleep(0.2)

    # Track tokens
    print("2. Recording token usage...")
    metrics.record_tokens(
        input_tokens=100,
        output_tokens=50,
        cost=0.001,
        model="gpt-4o-mini"
    )

    # Track tool calls
    print("3. Recording tool calls...")
    metrics.record_tool_call("search", duration=1.2, success=True)
    metrics.record_tool_call("calculator", duration=0.5, success=True)

    # Get summary
    print("\n4. Metrics Summary:")
    summary = metrics.get_summary()
    print(f"   Executions: {summary['execution']['total']}")
    print(f"   Success rate: {summary['execution']['success_rate']:.1%}")
    print(f"   Total tokens: {summary['tokens']['total']}")
    print(f"   Total cost: ${summary['cost']['total']:.4f}")

    # Export to Prometheus
    print("\n5. Prometheus Export:")
    prometheus_data = metrics.export_prometheus()
    print(prometheus_data[:300] + "...")


def demo_2_logging():
    """Demo 2: Structured Logging"""
    print("\n" + "=" * 80)
    print("DEMO 2: Structured Logging")
    print("=" * 80)

    # Create logger
    logger = AgentLogger(
        agent_name="demo-agent",
        level=LogLevel.DEBUG,
        json_format=True
    )

    # Simple logging
    print("\n1. Simple logging:")
    logger.info("Agent started successfully")
    logger.debug("Processing query", extra={"query": "What is AI?"})

    # Logging with context
    print("\n2. Contextual logging:")
    with logger.context(execution_id="exec-123", user="john"):
        logger.info("Executing task")
        logger.warn("Low token budget", tokens_remaining=10)

    # Error logging
    print("\n3. Error logging:")
    try:
        raise ValueError("Invalid input")
    except Exception as e:
        logger.error("Task failed", error=str(e), error_type=type(e).__name__)


def demo_3_telemetry():
    """Demo 3: Distributed Tracing"""
    print("\n" + "=" * 80)
    print("DEMO 3: Distributed Tracing")
    print("=" * 80)

    # Create telemetry
    telemetry = AgentTelemetry(agent_name="demo-agent")

    print("\n1. Creating trace with spans...")

    # Start trace
    with telemetry.start_trace("agent_execution") as trace:
        # Span for query processing
        with trace.span("query_processing"):
            import time
            time.sleep(0.1)

        # Span for tool execution
        with trace.span("tool_execution", attributes={"tool": "search"}):
            time.sleep(0.2)

        # Span for response generation
        with trace.span("response_generation", attributes={"model": "gpt-4"}):
            time.sleep(0.15)

    # Export traces
    print("\n2. Trace export:")
    traces = telemetry.export_traces()
    trace = traces[0]
    print(f"   Trace ID: {trace['trace_id']}")
    print(f"   Name: {trace['name']}")
    print(f"   Duration: {trace['duration']:.2f}s")
    print(f"   Spans: {len(trace['spans'])}")

    print("\n3. Span details:")
    for span in trace['spans']:
        print(f"   - {span['name']}: {span['duration']:.2f}s")


def demo_4_integrated():
    """Demo 4: Integrated Monitoring"""
    print("\n" + "=" * 80)
    print("DEMO 4: Integrated Monitoring (All Together)")
    print("=" * 80)

    # Setup monitoring
    metrics = AgentMetrics(agent_name="integrated-demo")
    logger = AgentLogger(agent_name="integrated-demo", level=LogLevel.INFO)
    telemetry = AgentTelemetry(agent_name="integrated-demo")

    # Simulated agent execution
    with telemetry.start_trace("agent_run") as trace:
        with logger.context(execution_id=trace.trace_id):
            logger.info("Starting agent execution")

            with metrics.track_execution():
                with trace.span("initialization"):
                    logger.debug("Initializing agent")

                with trace.span("processing"):
                    logger.info("Processing query")
                    metrics.record_tokens(input_tokens=50, output_tokens=30, cost=0.0005)

                with trace.span("tool_call"):
                    logger.info("Executing tool", tool="search")
                    metrics.record_tool_call("search", duration=0.5, success=True)

                logger.info("Agent execution completed")

    # Summary
    print("\n📊 Final Summary:")
    print(f"   Executions: {metrics.get_summary()['execution']['total']}")
    print(f"   Traces: {len(telemetry.get_traces())}")
    print(f"   Logs: Structured JSON format")


if __name__ == "__main__":
    print("\n🔍 Infrastructure Monitoring System Demo (v0.11.0)")
    print("="* 80)
    print("Layer 4: Agentic Infrastructure - Monitoring Component")
    print("=" * 80)

    demo_1_metrics()
    demo_2_logging()
    demo_3_telemetry()
    demo_4_integrated()

    print("\n" + "=" * 80)
    print("✅ All demos completed successfully!")
    print("=" * 80)
