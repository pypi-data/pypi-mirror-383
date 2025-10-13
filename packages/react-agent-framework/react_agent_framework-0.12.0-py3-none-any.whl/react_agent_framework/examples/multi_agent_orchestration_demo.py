"""
Demo: Multi-Agent Orchestration System

Demonstrates orchestration, workflows, task delegation, and role management.

Run: python -m react_agent_framework.examples.multi_agent_orchestration_demo
"""

import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from react_agent_framework.multi_agent.communication import MessageBus, Message, MessageType
from react_agent_framework.multi_agent.orchestration import (
    Orchestrator,
    Workflow,
    WorkflowEngine,
    WorkflowStep,
    StepType,
    TaskDelegator,
    LoadBalancingStrategy,
    RoleManager,
    Role,
)

console = Console()


def print_section(title: str):
    """Print section header."""
    console.print(f"\n[bold cyan]{'=' * 70}[/bold cyan]")
    console.print(f"[bold yellow]{title}[/bold yellow]")
    console.print(f"[bold cyan]{'=' * 70}[/bold cyan]\n")


def demo_1_orchestrator():
    """Demo 1: Central Orchestrator"""
    print_section("Demo 1: Central Orchestrator for Agent Coordination")

    bus = MessageBus()
    orchestrator = Orchestrator(bus, "orchestrator")

    # Register agents with capabilities
    console.print("[bold]Registering agents with capabilities...[/bold]")
    orchestrator.register_agent("worker-1", capabilities={"search", "process"})
    orchestrator.register_agent("worker-2", capabilities={"process", "analyze"})
    orchestrator.register_agent("worker-3", capabilities={"search"})

    console.print("✓ worker-1: [search, process]")
    console.print("✓ worker-2: [process, analyze]")
    console.print("✓ worker-3: [search]\n")

    # Find agents by capability
    console.print("[bold]Finding agents with 'search' capability:[/bold]")
    search_agents = orchestrator.get_agent_by_capability("search")
    console.print(f"  Agents: {', '.join(search_agents)}\n")

    # Show statistics
    stats = orchestrator.get_stats()
    table = Table(show_header=True, title="Orchestrator Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("Total Agents", str(stats["total_agents"]))
    table.add_row("Idle Agents", str(stats["idle_agents"]))
    table.add_row("Busy Agents", str(stats["busy_agents"]))

    console.print(table)


def demo_2_workflows():
    """Demo 2: Sequential and Parallel Workflows"""
    print_section("Demo 2: Sequential and Parallel Workflows")

    # Define workflow steps
    def fetch_data(**kwargs):
        console.print("  [cyan]→ Fetching data...[/cyan]")
        time.sleep(0.5)
        return {"data": [1, 2, 3, 4, 5]}

    def process_data(**kwargs):
        data = kwargs.get("fetch", {}).get("data", [])
        console.print(f"  [cyan]→ Processing {len(data)} items...[/cyan]")
        time.sleep(0.5)
        return {"processed": [x * 2 for x in data]}

    def save_results(**kwargs):
        processed = kwargs.get("process", {}).get("processed", [])
        console.print(f"  [cyan]→ Saving {len(processed)} results...[/cyan]")
        time.sleep(0.3)
        return {"saved": len(processed)}

    # Create workflow
    console.print("[bold]Creating sequential workflow:[/bold]")
    workflow = Workflow("data-pipeline", "Data Processing Pipeline")

    workflow.add_step(
        step_id="fetch",
        name="Fetch Data",
        action=fetch_data
    ).add_step(
        step_id="process",
        name="Process Data",
        action=process_data,
        dependencies={"fetch"}
    ).add_step(
        step_id="save",
        name="Save Results",
        action=save_results,
        dependencies={"process"}
    )

    console.print(f"✓ Created workflow with {len(workflow.steps)} steps\n")

    # Execute workflow
    console.print("[bold]Executing workflow:[/bold]")
    engine = WorkflowEngine()
    result = engine.execute(workflow)

    console.print(f"\n[green]✓ Workflow completed![/green]")
    console.print(f"  Status: {result['status']}")
    console.print(f"  Duration: {result['duration']:.2f}s")
    console.print(f"  Completed steps: {result['completed_steps']}/{result['total_steps']}")


def demo_3_task_delegation():
    """Demo 3: Task Delegation with Load Balancing"""
    print_section("Demo 3: Task Delegation with Load Balancing")

    # Create delegator with least-loaded strategy
    delegator = TaskDelegator(strategy=LoadBalancingStrategy.LEAST_LOADED)

    # Register agents
    console.print("[bold]Registering agents:[/bold]")
    delegator.register_agent("worker-1", capabilities={"search"}, max_concurrent=5)
    delegator.register_agent("worker-2", capabilities={"search"}, max_concurrent=3)
    delegator.register_agent("worker-3", capabilities={"search"}, max_concurrent=10)

    console.print("✓ worker-1: max_concurrent=5")
    console.print("✓ worker-2: max_concurrent=3")
    console.print("✓ worker-3: max_concurrent=10\n")

    # Delegate tasks
    console.print("[bold]Delegating 10 tasks (least-loaded strategy):[/bold]")

    for i in range(10):
        allocation = delegator.delegate_task(
            task_id=f"task-{i+1}",
            task_type="search",
            task_data={"query": f"query-{i+1}"},
            required_capability="search"
        )

        if allocation:
            console.print(f"  Task {i+1} → {allocation.agent_id}")

    # Show load distribution
    console.print("\n[bold]Load distribution:[/bold]")
    for agent_id in delegator.get_all_agents():
        load = delegator.get_agent_load(agent_id)
        console.print(f"  {agent_id}: {load} tasks")

    # Mark some tasks as completed
    console.print("\n[bold]Completing tasks...[/bold]")
    delegator.mark_completed("task-1", {"result": "completed"})
    delegator.mark_completed("task-2", {"result": "completed"})
    delegator.mark_completed("task-3", {"result": "completed"})

    # Show stats
    stats = delegator.get_stats()
    console.print(f"\n[green]✓ Delegator Statistics:[/green]")
    console.print(f"  Total delegated: {stats['total_delegated']}")
    console.print(f"  Completed: {stats['total_completed']}")
    console.print(f"  Active: {stats['active_allocations']}")


def demo_4_role_management():
    """Demo 4: Role Management"""
    print_section("Demo 4: Role-Based Agent Management")

    manager = RoleManager()

    # Assign roles
    console.print("[bold]Assigning roles to agents:[/bold]")

    manager.assign_role(
        "agent-1",
        Role.LEADER,
        responsibilities=["Coordinate team", "Make decisions"]
    )
    console.print("✓ agent-1 → LEADER")

    manager.assign_role(
        "agent-2",
        Role.WORKER,
        capabilities={"search", "process"}
    )
    console.print("✓ agent-2 → WORKER (search, process)")

    manager.assign_role(
        "agent-3",
        Role.WORKER,
        capabilities={"analyze"}
    )
    console.print("✓ agent-3 → WORKER (analyze)")

    manager.assign_role(
        "agent-4",
        Role.SPECIALIST,
        capabilities={"expert_analysis"}
    )
    console.print("✓ agent-4 → SPECIALIST (expert_analysis)\n")

    # Query roles
    console.print("[bold]Querying roles:[/bold]")
    leader = manager.get_agents_with_role(Role.LEADER)
    workers = manager.get_agents_with_role(Role.WORKER)
    specialists = manager.get_agents_with_role(Role.SPECIALIST)

    console.print(f"  Leaders: {leader}")
    console.print(f"  Workers: {workers}")
    console.print(f"  Specialists: {specialists}\n")

    # Query capabilities
    console.print("[bold]Finding agents with 'search' capability:[/bold]")
    search_capable = manager.get_agents_with_capability("search")
    console.print(f"  Agents: {search_capable}\n")

    # Role distribution
    distribution = manager.get_role_distribution()

    table = Table(show_header=True, title="Role Distribution")
    table.add_column("Role", style="cyan")
    table.add_column("Count", style="yellow", justify="right")

    for role, count in distribution.items():
        if count > 0:
            table.add_row(role.value, str(count))

    console.print(table)


def demo_5_integrated_orchestration():
    """Demo 5: Integrated Orchestration Example"""
    print_section("Demo 5: Integrated Multi-Agent Orchestration")

    bus = MessageBus()
    orchestrator = Orchestrator(bus, "orchestrator")
    role_manager = RoleManager()
    delegator = TaskDelegator(strategy=LoadBalancingStrategy.CAPABILITY_BASED)

    console.print("[bold]Setting up multi-agent system:[/bold]\n")

    # Setup agents with roles and capabilities
    agents_config = [
        ("coordinator", Role.LEADER, {"plan", "coordinate"}),
        ("worker-1", Role.WORKER, {"search", "fetch"}),
        ("worker-2", Role.WORKER, {"process", "transform"}),
        ("specialist", Role.SPECIALIST, {"analyze", "validate"}),
    ]

    for agent_id, role, capabilities in agents_config:
        # Register with orchestrator
        orchestrator.register_agent(agent_id, capabilities=capabilities)

        # Assign role
        role_manager.assign_role(agent_id, role, capabilities=capabilities)

        # Register with delegator
        delegator.register_agent(agent_id, capabilities=capabilities)

        console.print(f"✓ {agent_id}: {role.value} {list(capabilities)}")

    # Show system overview
    console.print("\n[bold]System Overview:[/bold]")

    orch_stats = orchestrator.get_stats()
    role_stats = role_manager.get_stats()
    deleg_stats = delegator.get_stats()

    table = Table(show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Metric", style="white")
    table.add_column("Value", style="yellow", justify="right")

    table.add_row("Orchestrator", "Total Agents", str(orch_stats["total_agents"]))
    table.add_row("", "Idle Agents", str(orch_stats["idle_agents"]))

    table.add_row("Role Manager", "Total Agents", str(role_stats["total_agents"]))
    table.add_row("", "Active Roles", str(role_stats["total_active_roles"]))

    table.add_row("Delegator", "Registered Agents", str(deleg_stats["registered_agents"]))
    table.add_row("", "Total Load", str(deleg_stats["total_load"]))

    console.print(table)

    console.print("\n[green]✓ Multi-agent system ready for orchestration![/green]")


def main():
    """Run all demos."""
    console.print(Panel.fit(
        "[bold yellow]Multi-Agent Orchestration System Demo[/bold yellow]\n"
        "Orchestrators, workflows, task delegation, and role management",
        border_style="cyan"
    ))

    try:
        demo_1_orchestrator()
        time.sleep(1)

        demo_2_workflows()
        time.sleep(1)

        demo_3_task_delegation()
        time.sleep(1)

        demo_4_role_management()
        time.sleep(1)

        demo_5_integrated_orchestration()

        console.print(Panel.fit(
            "[bold green]✓ All orchestration demos completed![/bold green]",
            border_style="green"
        ))

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
