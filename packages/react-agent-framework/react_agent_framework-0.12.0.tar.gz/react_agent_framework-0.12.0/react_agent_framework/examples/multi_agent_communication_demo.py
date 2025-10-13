"""
Demo: Multi-Agent Communication System

Demonstrates message passing, protocols, and channels for agent communication.

Run: python -m react_agent_framework.examples.multi_agent_communication_demo
"""

import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from react_agent_framework.multi_agent.communication import (
    Message,
    MessageType,
    MessagePriority,
    MessageBus,
    ACLProtocol,
    DirectChannel,
    BroadcastChannel,
    MulticastChannel,
)

console = Console()


def print_section(title: str):
    """Print section header."""
    console.print(f"\n[bold cyan]{'=' * 70}[/bold cyan]")
    console.print(f"[bold yellow]{title}[/bold yellow]")
    console.print(f"[bold cyan]{'=' * 70}[/bold cyan]\n")


def demo_1_direct_messaging():
    """Demo 1: Direct Point-to-Point Messaging"""
    print_section("Demo 1: Direct Point-to-Point Messaging")

    # Create message bus and register agents
    bus = MessageBus()
    bus.register_agent("agent-1")
    bus.register_agent("agent-2")

    console.print("[bold]Registered agents:[/bold] agent-1, agent-2\n")

    # Send message from agent-1 to agent-2
    console.print("[cyan]agent-1 → agent-2:[/cyan] 'Hello, Agent 2!'")
    msg = Message(
        sender="agent-1",
        receiver="agent-2",
        message_type=MessageType.INFORM,
        content="Hello, Agent 2!"
    )
    bus.send(msg)

    # Receive message
    messages = bus.receive("agent-2")
    console.print(f"[green]✓ agent-2 received:[/green] '{messages[0].content}'\n")

    # Send reply
    console.print("[cyan]agent-2 → agent-1:[/cyan] 'Hello back, Agent 1!'")
    reply = messages[0].create_reply(
        sender="agent-2",
        content="Hello back, Agent 1!"
    )
    bus.send(reply)

    # Receive reply
    messages = bus.receive("agent-1")
    console.print(f"[green]✓ agent-1 received reply:[/green] '{messages[0].content}'\n")

    # Show stats
    stats = bus.get_stats()
    console.print(f"[bold]Messages sent:[/bold] {stats['total_sent']}")
    console.print(f"[bold]Messages received:[/bold] {stats['total_received']}")


def demo_2_broadcast():
    """Demo 2: Broadcast Communication"""
    print_section("Demo 2: Broadcast Communication")

    # Create bus and broadcast channel
    bus = MessageBus()
    channel = BroadcastChannel(bus)

    # Register multiple agents
    agents = ["controller", "worker-1", "worker-2", "worker-3"]
    for agent_id in agents:
        bus.register_agent(agent_id)

    console.print(f"[bold]Registered agents:[/bold] {', '.join(agents)}\n")

    # Broadcast from controller
    console.print("[cyan]controller → * (broadcast):[/cyan] 'Start processing task-123'")
    channel.broadcast(
        sender="controller",
        content={"command": "start", "task_id": "task-123"},
        priority=MessagePriority.HIGH
    )

    # Workers receive
    console.print("\n[bold]Workers receiving broadcast:[/bold]")
    for worker in ["worker-1", "worker-2", "worker-3"]:
        messages = channel.receive(worker, max_messages=1)
        if messages:
            content = messages[0].content
            console.print(f"  [green]✓ {worker}:[/green] Received {content}")

    # Show queue sizes
    console.print("\n[bold]Queue sizes after broadcast:[/bold]")
    for agent_id in agents:
        size = bus.get_queue_size(agent_id)
        console.print(f"  {agent_id}: {size} messages")


def demo_3_pub_sub_topics():
    """Demo 3: Pub/Sub with Topics (Multicast)"""
    print_section("Demo 3: Pub/Sub with Topics (Multicast)")

    # Create bus and multicast channel
    bus = MessageBus()
    channel = MulticastChannel(bus)

    # Register agents
    agents = ["publisher", "sub-1", "sub-2", "sub-3"]
    for agent_id in agents:
        bus.register_agent(agent_id)

    console.print(f"[bold]Registered agents:[/bold] {', '.join(agents)}\n")

    # Subscribe to topics
    console.print("[bold]Subscriptions:[/bold]")
    channel.subscribe("sub-1", "updates")
    channel.subscribe("sub-2", "updates")
    channel.subscribe("sub-3", "alerts")
    console.print("  sub-1 → 'updates'")
    console.print("  sub-2 → 'updates'")
    console.print("  sub-3 → 'alerts'\n")

    # Publish to 'updates' topic
    console.print("[cyan]publisher → topic 'updates':[/cyan] 'New version released'")
    channel.publish(
        sender="publisher",
        topic="updates",
        content="New version released"
    )

    # Check who received
    console.print("\n[bold]Messages received:[/bold]")
    for sub in ["sub-1", "sub-2", "sub-3"]:
        messages = channel.receive(sub)
        if messages:
            console.print(f"  [green]✓ {sub}:[/green] '{messages[0].content}'")
        else:
            console.print(f"  [dim]{sub}: (no messages)[/dim]")

    # Publish to 'alerts' topic
    console.print("\n[cyan]publisher → topic 'alerts':[/cyan] 'System maintenance at 2am'")
    channel.publish(
        sender="publisher",
        topic="alerts",
        content="System maintenance at 2am"
    )

    # Check who received
    console.print("\n[bold]Messages received:[/bold]")
    for sub in ["sub-1", "sub-2", "sub-3"]:
        messages = channel.receive(sub)
        if messages:
            console.print(f"  [green]✓ {sub}:[/green] '{messages[0].content}'")
        else:
            console.print(f"  [dim]{sub}: (no messages)[/dim]")


def demo_4_acl_protocol():
    """Demo 4: ACL Protocol Communication"""
    print_section("Demo 4: ACL Protocol Communication")

    # Create bus and protocol
    bus = MessageBus()
    protocol = ACLProtocol()

    # Register agents
    bus.register_agent("requester")
    bus.register_agent("provider")

    console.print("[bold]Registered agents:[/bold] requester, provider\n")

    # 1. REQUEST
    console.print("[cyan]1. requester → provider:[/cyan] REQUEST 'search'")
    request_msg = protocol.request(
        sender="requester",
        receiver="provider",
        action="search",
        params={"query": "multi-agent systems"}
    )
    bus.send(request_msg)

    # Provider receives and agrees
    messages = bus.receive("provider")
    console.print(f"[green]✓ provider received:[/green] {messages[0].metadata['performative']}\n")

    # 2. AGREE
    console.print("[cyan]2. provider → requester:[/cyan] AGREE to perform search")
    agree_msg = protocol.agree(
        sender="provider",
        receiver="requester",
        action="search",
        reply_to=request_msg.message_id
    )
    bus.send(agree_msg)

    messages = bus.receive("requester")
    console.print(f"[green]✓ requester received:[/green] {messages[0].metadata['performative']}\n")

    # 3. INFORM (result)
    console.print("[cyan]3. provider → requester:[/cyan] INFORM search results")
    inform_msg = protocol.inform(
        sender="provider",
        receiver="requester",
        proposition={
            "results": ["Paper 1", "Paper 2", "Paper 3"],
            "count": 3
        },
        reply_to=request_msg.message_id
    )
    bus.send(inform_msg)

    messages = bus.receive("requester")
    console.print(f"[green]✓ requester received:[/green] {messages[0].content['proposition']}")


def demo_5_message_priorities():
    """Demo 5: Message Priorities"""
    print_section("Demo 5: Message Priorities")

    # Create bus
    bus = MessageBus()
    bus.register_agent("receiver")

    console.print("[bold]Sending messages with different priorities:[/bold]\n")

    # Send low priority
    console.print("[dim]Sending LOW priority:[/dim] 'Regular update'")
    bus.send(Message(
        sender="sender",
        receiver="receiver",
        message_type=MessageType.INFORM,
        content="Regular update",
        priority=MessagePriority.LOW
    ))

    # Send normal priority
    console.print("[white]Sending NORMAL priority:[/white] 'Task completed'")
    bus.send(Message(
        sender="sender",
        receiver="receiver",
        message_type=MessageType.INFORM,
        content="Task completed",
        priority=MessagePriority.NORMAL
    ))

    # Send critical priority
    console.print("[red]Sending CRITICAL priority:[/red] 'System error!'")
    bus.send(Message(
        sender="sender",
        receiver="receiver",
        message_type=MessageType.ERROR,
        content="System error!",
        priority=MessagePriority.CRITICAL
    ))

    # Receive (critical should come first)
    console.print("\n[bold]Receiving messages (ordered by priority):[/bold]")
    messages = bus.receive("receiver", max_messages=10)

    for i, msg in enumerate(messages, 1):
        priority_name = MessagePriority(msg.priority).name
        color = {
            MessagePriority.LOW: "dim",
            MessagePriority.NORMAL: "white",
            MessagePriority.HIGH: "yellow",
            MessagePriority.URGENT: "orange1",
            MessagePriority.CRITICAL: "red"
        }.get(msg.priority, "white")

        console.print(f"  {i}. [{color}][{priority_name}][/{color}] {msg.content}")


def demo_6_message_bus_stats():
    """Demo 6: Message Bus Statistics"""
    print_section("Demo 6: Message Bus Statistics")

    # Create bus with multiple agents
    bus = MessageBus()
    agents = ["agent-1", "agent-2", "agent-3"]

    for agent_id in agents:
        bus.register_agent(agent_id)

    # Send various messages
    bus.send(Message("agent-1", "agent-2", MessageType.INFORM, "Hello"))
    bus.send(Message("agent-2", "agent-3", MessageType.REQUEST, "Data"))
    bus.send(Message("agent-1", "*", MessageType.BROADCAST, "Announcement"))
    bus.send(Message("agent-3", "agent-1", MessageType.RESPONSE, "Result"))

    # Receive some messages
    bus.receive("agent-2")
    bus.receive("agent-3")

    # Get stats
    stats = bus.get_stats()

    # Display as table
    table = Table(show_header=True, title="Message Bus Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow", justify="right")

    table.add_row("Total Sent", str(stats["total_sent"]))
    table.add_row("Total Received", str(stats["total_received"]))
    table.add_row("Registered Agents", str(stats["registered_agents"]))
    table.add_row("Total Queued", str(stats["total_queued"]))
    table.add_row("Dead Letters", str(stats["dead_letters"]))

    console.print(table)

    # Messages by type
    console.print("\n[bold]Messages by Type:[/bold]")
    for msg_type, count in stats["messages_by_type"].items():
        console.print(f"  {msg_type}: {count}")


def main():
    """Run all demos."""
    console.print(Panel.fit(
        "[bold yellow]Multi-Agent Communication System Demo[/bold yellow]\n"
        "Message passing, protocols, and channels for agent collaboration",
        border_style="cyan"
    ))

    try:
        demo_1_direct_messaging()
        time.sleep(1)

        demo_2_broadcast()
        time.sleep(1)

        demo_3_pub_sub_topics()
        time.sleep(1)

        demo_4_acl_protocol()
        time.sleep(1)

        demo_5_message_priorities()
        time.sleep(1)

        demo_6_message_bus_stats()

        console.print(Panel.fit(
            "[bold green]✓ All communication demos completed![/bold green]",
            border_style="green"
        ))

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
