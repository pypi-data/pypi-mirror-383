"""
Demo: Human-in-the-Loop System

Demonstrates approval workflows, intervention mechanisms, and feedback collection.

Run: python -m react_agent_framework.examples.infrastructure_human_loop_demo
"""

import time
import threading
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from react_agent_framework.infrastructure.human_loop import (
    # Approval
    ApprovalManager,
    ApprovalPolicy,
    ApprovalStatus,
    # Intervention
    InterventionManager,
    InterventionAction,
    InterventionType,
    # Feedback
    FeedbackCollector,
    FeedbackType,
    FeedbackRating,
)

console = Console()


def print_section(title: str):
    """Print section header."""
    console.print(f"\n[bold cyan]{'=' * 70}[/bold cyan]")
    console.print(f"[bold yellow]{title}[/bold yellow]")
    console.print(f"[bold cyan]{'=' * 70}[/bold cyan]\n")


def demo_1_approval_workflows():
    """Demo 1: Approval Workflows"""
    print_section("Demo 1: Approval Workflows")

    manager = ApprovalManager(default_timeout=60)

    # Configure policies
    console.print("[bold]Configuring approval policies...[/bold]")
    manager.register_policy("delete_file", ApprovalPolicy.ALWAYS)
    manager.register_policy("read_file", ApprovalPolicy.NEVER)
    manager.register_policy("api_call", ApprovalPolicy.COST_THRESHOLD)
    console.print("✓ Policies configured\n")

    # Request approvals
    console.print("[bold]Requesting approvals...[/bold]")

    # 1. Always require approval (delete_file)
    req1 = manager.request_approval(
        operation="delete_file",
        description="Delete important_data.txt",
        requester="agent-1"
    )
    console.print(f"Request 1: {req1.operation} - Status: [yellow]{req1.status}[/yellow]")

    # 2. Never require approval (read_file) - auto-approved
    req2 = manager.request_approval(
        operation="read_file",
        description="Read config.json",
        requester="agent-1"
    )
    console.print(f"Request 2: {req2.operation} - Status: [green]{req2.status}[/green]")

    # 3. Cost threshold policy
    req3 = manager.request_approval(
        operation="api_call",
        description="Call GPT-4 API",
        requester="agent-1",
        metadata={"cost": 0.5, "cost_threshold": 1.0}
    )
    console.print(f"Request 3: {req3.operation} - Status: [green]{req3.status}[/green] (below threshold)")

    req4 = manager.request_approval(
        operation="api_call",
        description="Call GPT-4 API (expensive)",
        requester="agent-1",
        metadata={"cost": 5.0, "cost_threshold": 1.0}
    )
    console.print(f"Request 4: {req4.operation} - Status: [yellow]{req4.status}[/yellow] (above threshold)\n")

    # Simulate human approval in background thread
    def approve_in_background():
        time.sleep(1)
        manager.approve(req1.request_id, "admin", "Verified safe deletion")
        console.print("\n[green]✓ Request 1 approved by admin[/green]")

    thread = threading.Thread(target=approve_in_background, daemon=True)
    thread.start()

    # Wait for approval (blocking)
    console.print(f"[bold]Waiting for approval of request 1...[/bold]")
    if manager.wait_for_approval(req1.request_id, timeout=5):
        console.print("[green]✓ Operation approved! Proceeding...[/green]")
    else:
        console.print("[red]✗ Operation not approved[/red]")

    thread.join()

    # Show statistics
    console.print("\n[bold]Approval Statistics:[/bold]")
    stats = manager.get_stats()
    table = Table(show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")

    for key, value in stats.items():
        if isinstance(value, float):
            table.add_row(key, f"{value:.2%}")
        else:
            table.add_row(key, str(value))

    console.print(table)


def demo_2_intervention_mechanisms():
    """Demo 2: Intervention Mechanisms"""
    print_section("Demo 2: Intervention Mechanisms")

    manager = InterventionManager()

    # Enable interventions
    console.print("[bold]Configuring intervention points...[/bold]")
    manager.enable_intervention(InterventionAction.TOOL_EXECUTION, auto_pause=True)
    manager.enable_intervention(InterventionAction.FILE_OPERATION)
    console.print("✓ Interventions configured\n")

    # Simulate agent execution with intervention points
    console.print("[bold]Simulating agent execution...[/bold]")

    # Point 1: Tool execution (auto-pause)
    point1 = manager.register_point(
        action=InterventionAction.TOOL_EXECUTION,
        description="About to execute search tool",
        agent_id="agent-1",
        metadata={"tool": "search", "query": "test query"}
    )
    console.print(f"Point 1: {point1.description}")
    console.print(f"Status: [yellow]{point1.status}[/yellow] (auto-paused)\n")

    # Simulate human decision in background
    def intervene_in_background():
        time.sleep(1)
        # Modify query before execution
        manager.modify_point(
            point1.point_id,
            "user-1",
            {"query": "modified query"}
        )
        console.print("\n[blue]→ Human modified query to 'modified query'[/blue]")

    thread = threading.Thread(target=intervene_in_background, daemon=True)
    thread.start()

    # Wait for intervention decision
    console.print("[bold]Waiting for human decision...[/bold]")
    result = manager.wait_for_decision(point1.point_id, timeout=5)
    console.print(f"Decision: [cyan]{result['type']}[/cyan]")
    if result.get("data"):
        console.print(f"Modified data: {result['data']}")

    thread.join()

    # Point 2: File operation (no auto-pause)
    console.print("\n[bold]Next operation...[/bold]")
    point2 = manager.register_point(
        action=InterventionAction.FILE_OPERATION,
        description="Writing to file",
        agent_id="agent-1",
        metadata={"file": "output.txt"}
    )
    console.print(f"Point 2: {point2.description}")
    console.print(f"Status: [green]{point2.status}[/green] (auto-continued)\n")

    # Enable step mode
    console.print("[bold]Enabling step-by-step mode...[/bold]")
    manager.enable_step_mode()
    console.print("✓ Step mode enabled\n")

    # Now all operations will pause
    point3 = manager.register_point(
        action=InterventionAction.API_CALL,
        description="Calling external API",
        agent_id="agent-1",
        metadata={"api": "openai"}
    )
    console.print(f"Point 3: {point3.description}")
    console.print(f"Status: [yellow]{point3.status}[/yellow] (paused by step mode)\n")

    # Continue manually
    manager.continue_point(point3.point_id, "user-1")
    console.print("[green]✓ Continued by user[/green]\n")

    # Show statistics
    console.print("[bold]Intervention Statistics:[/bold]")
    stats = manager.get_stats()
    table = Table(show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")

    for key, value in stats.items():
        table.add_row(key, str(value))

    console.print(table)


def demo_3_feedback_collection():
    """Demo 3: Feedback Collection"""
    print_section("Demo 3: Feedback Collection")

    collector = FeedbackCollector()

    # Submit different types of feedback
    console.print("[bold]Submitting feedback...[/bold]\n")

    # 1. Ratings
    console.print("[cyan]1. Rating Feedback:[/cyan]")
    collector.submit_rating(
        agent_id="agent-1",
        user="user-1",
        rating=5,
        operation="search",
        comment="Excellent results!"
    )
    collector.submit_rating(
        agent_id="agent-1",
        user="user-2",
        rating=4,
        operation="search"
    )
    collector.submit_rating(
        agent_id="agent-1",
        user="user-3",
        rating=5,
        operation="summarize",
        comment="Very helpful summary"
    )
    console.print("✓ Submitted 3 ratings\n")

    # 2. Thumbs up/down
    console.print("[cyan]2. Thumbs Feedback:[/cyan]")
    collector.submit_thumbs(
        agent_id="agent-1",
        user="user-1",
        thumbs_up=True,
        operation="translate"
    )
    collector.submit_thumbs(
        agent_id="agent-1",
        user="user-2",
        thumbs_up=True,
        operation="translate"
    )
    collector.submit_thumbs(
        agent_id="agent-1",
        user="user-3",
        thumbs_up=False,
        operation="translate",
        comment="Translation was inaccurate"
    )
    console.print("✓ Submitted 3 thumbs (2 up, 1 down)\n")

    # 3. Corrections
    console.print("[cyan]3. Correction Feedback:[/cyan]")
    collector.submit_correction(
        agent_id="agent-1",
        user="user-1",
        original_output="The capital of France is Paris",
        corrected_output="The capital of France is Paris (population: ~2.2M)",
        operation="fact_check",
        comment="Added population info"
    )
    console.print("✓ Submitted 1 correction\n")

    # 4. Bug reports
    console.print("[cyan]4. Bug Report:[/cyan]")
    feedback_bug = collector.submit_bug_report(
        agent_id="agent-1",
        user="user-2",
        description="Agent crashes when input is too long",
        operation="process_text",
        metadata={"error": "IndexError", "input_length": 10000}
    )
    console.print(f"✓ Submitted bug report (ID: {feedback_bug.feedback_id})\n")

    # 5. Feature requests
    console.print("[cyan]5. Feature Request:[/cyan]")
    collector.submit_feature_request(
        agent_id="agent-1",
        user="user-3",
        description="Add support for PDF file processing",
        metadata={"priority": "high"}
    )
    console.print("✓ Submitted 1 feature request\n")

    # Acknowledge bug report
    console.print("[bold]Acknowledging bug report...[/bold]")
    collector.acknowledge_feedback(
        feedback_bug.feedback_id,
        "developer-1",
        "Thanks! We'll fix this in the next release."
    )
    console.print("✓ Bug acknowledged\n")

    # Show statistics
    console.print("[bold]Feedback Statistics:[/bold]")
    stats = collector.get_stats(agent_id="agent-1")

    table = Table(show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("Total Feedbacks", str(stats["total_feedbacks"]))
    table.add_row("Average Rating", f"{stats['average_rating']:.2f}/5.0")
    table.add_row("Thumbs Up", str(stats["thumbs_stats"]["thumbs_up"]))
    table.add_row("Thumbs Down", str(stats["thumbs_stats"]["thumbs_down"]))
    table.add_row("Thumbs Up Rate", f"{stats['thumbs_stats']['thumbs_up_rate']:.1%}")
    table.add_row("Acknowledgment Rate", f"{stats['acknowledgment_rate']:.1%}")

    console.print(table)

    # Show feedback by type
    console.print("\n[bold]Feedback by Type:[/bold]")
    type_table = Table(show_header=True)
    type_table.add_column("Type", style="cyan")
    type_table.add_column("Count", style="yellow")

    for feedback_type, count in stats["by_type"].items():
        type_table.add_row(feedback_type, str(count))

    console.print(type_table)


def demo_4_integrated_workflow():
    """Demo 4: Integrated Workflow"""
    print_section("Demo 4: Integrated Human-in-the-Loop Workflow")

    # Setup all components
    approval_mgr = ApprovalManager()
    intervention_mgr = InterventionManager()
    feedback_collector = FeedbackCollector()

    console.print("[bold]Simulating complete agent workflow with human oversight...[/bold]\n")

    # Step 1: Request approval for sensitive operation
    console.print("[cyan]Step 1: Request Approval[/cyan]")
    approval_mgr.register_policy("sensitive_operation", ApprovalPolicy.ALWAYS)

    request = approval_mgr.request_approval(
        operation="sensitive_operation",
        description="Delete user data",
        requester="agent-1",
        metadata={"user_id": "12345", "data_type": "personal"}
    )
    console.print(f"Approval request: {request.description}")
    console.print(f"Status: [yellow]{request.status}[/yellow]\n")

    # Simulate approval
    approval_mgr.approve(request.request_id, "admin", "Verified with user consent")
    console.print("[green]✓ Operation approved[/green]\n")

    # Step 2: Execute with intervention points
    console.print("[cyan]Step 2: Execute with Intervention[/cyan]")
    intervention_mgr.enable_intervention(InterventionAction.TOOL_EXECUTION, auto_pause=True)

    point = intervention_mgr.register_point(
        action=InterventionAction.TOOL_EXECUTION,
        description="Executing delete_user_data tool",
        agent_id="agent-1",
        metadata={"user_id": "12345"}
    )
    console.print(f"Intervention point: {point.description}")
    console.print(f"Status: [yellow]{point.status}[/yellow] (paused for review)\n")

    # Continue after review
    intervention_mgr.continue_point(point.point_id, "admin")
    console.print("[green]✓ Operation continued[/green]\n")

    # Step 3: Collect feedback
    console.print("[cyan]Step 3: Collect Feedback[/cyan]")
    feedback = feedback_collector.submit_rating(
        agent_id="agent-1",
        user="admin",
        rating=5,
        operation="sensitive_operation",
        comment="Operation completed successfully with proper oversight"
    )
    console.print(f"Feedback: {feedback.comment}")
    console.print(f"Rating: [green]{feedback.rating}/5[/green]\n")

    # Show summary
    console.print("[bold]Workflow Summary:[/bold]")

    summary = Table(show_header=True)
    summary.add_column("Component", style="cyan")
    summary.add_column("Status", style="yellow")
    summary.add_column("Details", style="white")

    summary.add_row(
        "Approval",
        "[green]Approved[/green]",
        f"By: {request.approved_by}"
    )
    summary.add_row(
        "Intervention",
        "[green]Continued[/green]",
        f"Points: {len(intervention_mgr.get_history())}"
    )
    summary.add_row(
        "Feedback",
        "[green]Collected[/green]",
        f"Rating: {feedback.rating}/5"
    )

    console.print(summary)


def demo_5_async_approval():
    """Demo 5: Async Approval with Callbacks"""
    print_section("Demo 5: Async Approval with Callbacks")

    manager = ApprovalManager()

    console.print("[bold]Demonstrating async approval with callbacks...[/bold]\n")

    # Register callback
    def on_approval_response(response):
        console.print(f"\n[bold blue]→ Callback triggered![/bold blue]")
        console.print(f"Request: {response.request_id}")
        console.print(f"Status: [cyan]{response.status}[/cyan]")
        console.print(f"Approver: {response.approver}")
        if response.reason:
            console.print(f"Reason: {response.reason}")

    # Request approval
    request = manager.request_approval(
        operation="deploy_model",
        description="Deploy model to production",
        requester="agent-1"
    )

    console.print(f"Request ID: {request.request_id}")
    console.print(f"Status: [yellow]{request.status}[/yellow]")

    # Register callback
    manager.on_response(request.request_id, on_approval_response)
    console.print("✓ Callback registered\n")

    # Simulate async approval
    def approve_async():
        time.sleep(2)
        manager.approve(
            request.request_id,
            "lead-engineer",
            "Tests passed, ready for production"
        )

    thread = threading.Thread(target=approve_async, daemon=True)
    thread.start()

    console.print("[bold]Waiting for approval (callback will fire)...[/bold]")
    thread.join(timeout=3)

    time.sleep(0.5)  # Let callback execute
    console.print("\n[green]✓ Async approval complete[/green]")


def main():
    """Run all demos."""
    console.print(Panel.fit(
        "[bold yellow]Human-in-the-Loop System Demo[/bold yellow]\n"
        "Approval workflows, intervention mechanisms, and feedback collection",
        border_style="cyan"
    ))

    try:
        demo_1_approval_workflows()
        time.sleep(1)

        demo_2_intervention_mechanisms()
        time.sleep(1)

        demo_3_feedback_collection()
        time.sleep(1)

        demo_4_integrated_workflow()
        time.sleep(1)

        demo_5_async_approval()

        console.print(Panel.fit(
            "[bold green]✓ All Human-in-the-Loop demos completed![/bold green]",
            border_style="green"
        ))

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
