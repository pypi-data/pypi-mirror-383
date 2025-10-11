"""CLI for system information collection."""

import json
import sys
from typing import Dict, Any

try:
    import click
except ImportError as e:
    raise ImportError("Required package not installed. Run: pip install click") from e

from ..logger import init_logging, logger
from ..core.system import (
    get_cpu_info,
    get_memory_info,
    get_disk_info,
    get_battery_info,
    get_network_info,
    get_system_info,
)


def _format_bytes(bytes_value: float) -> str:
    """Format bytes into human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def _print_cpu_info(cpu_info: Dict[str, Any]) -> None:
    """Print formatted CPU information."""
    click.echo("CPU Information:")
    click.echo(f"  Physical cores: {cpu_info['physical_cores']}")
    click.echo(f"  Logical cores: {cpu_info['logical_cores']}")

    if cpu_info["max_frequency"] > 0:
        click.echo(f"  Max frequency: {cpu_info['max_frequency']:.0f} MHz")
        click.echo(f"  Current frequency: {cpu_info['current_frequency']:.0f} MHz")

    click.echo(f"  Usage: {cpu_info['usage_percent']:.1f}%")

    if cpu_info["usage_per_core"]:
        core_usage = ", ".join(f"{usage:.1f}%" for usage in cpu_info["usage_per_core"])
        click.echo(f"  Per-core usage: {core_usage}")


def _print_memory_info(memory_info: Dict[str, Any]) -> None:
    """Print formatted memory information."""
    click.echo("\nMemory Information:")
    click.echo(f"  Total: {_format_bytes(memory_info['total'])}")
    click.echo(f"  Available: {_format_bytes(memory_info['available'])}")
    click.echo(
        f"  Used: {_format_bytes(memory_info['used'])} ({memory_info['percent']:.1f}%)"
    )
    click.echo(f"  Free: {_format_bytes(memory_info['free'])}")

    if memory_info["swap_total"] > 0:
        click.echo(f"  Swap total: {_format_bytes(memory_info['swap_total'])}")
        click.echo(
            f"  Swap used: {_format_bytes(memory_info['swap_used'])} ({memory_info['swap_percent']:.1f}%)"
        )


def _print_disk_info(disk_info: Dict[str, Any]) -> None:
    """Print formatted disk information."""
    click.echo("\nDisk Information:")

    for device, info in disk_info.items():
        if device == "io_stats":
            continue

        click.echo(f"  {device} ({info['filesystem']}):")
        click.echo(f"    Mountpoint: {info['mountpoint']}")
        click.echo(f"    Total: {_format_bytes(info['total'])}")
        click.echo(f"    Used: {_format_bytes(info['used'])} ({info['percent']:.1f}%)")
        click.echo(f"    Free: {_format_bytes(info['free'])}")

    if "io_stats" in disk_info:
        io = disk_info["io_stats"]
        click.echo("  I/O Statistics:")
        click.echo(
            f"    Read: {io['read_count']} ops, {_format_bytes(io['read_bytes'])}"
        )
        click.echo(
            f"    Write: {io['write_count']} ops, {_format_bytes(io['write_bytes'])}"
        )


def _print_battery_info(battery_info: Dict[str, Any]) -> None:
    """Print formatted battery information."""
    click.echo("\nBattery Information:")

    if not battery_info["present"]:
        click.echo("  No battery detected")
        return

    click.echo(f"  Charge: {battery_info['percent']:.1f}%")
    click.echo(f"  Power plugged: {'Yes' if battery_info['power_plugged'] else 'No'}")

    if battery_info["seconds_left"] is not None:
        hours = battery_info["seconds_left"] // 3600
        minutes = (battery_info["seconds_left"] % 3600) // 60
        click.echo(f"  Time remaining: {hours}h {minutes}m")


def _print_network_info(network_info: Dict[str, Any]) -> None:
    """Print formatted network information."""
    click.echo("\nNetwork Information:")

    for interface, info in network_info.items():
        if interface == "io_stats":
            continue

        click.echo(f"  {interface}:")
        click.echo(f"    Status: {'Up' if info['is_up'] else 'Down'}")

        if info["speed"] > 0:
            click.echo(f"    Speed: {info['speed']} Mbps")

        click.echo(f"    MTU: {info['mtu']}")

        for addr in info["addresses"]:
            if (
                addr["address"]
                and addr["address"] != "::1"
                and addr["address"] != "127.0.0.1"
            ):
                click.echo(f"    Address: {addr['address']}")

    if "io_stats" in network_info:
        io = network_info["io_stats"]
        click.echo("  I/O Statistics:")
        click.echo(
            f"    Sent: {io['packets_sent']} packets, {_format_bytes(io['bytes_sent'])}"
        )
        click.echo(
            f"    Received: {io['packets_recv']} packets, {_format_bytes(io['bytes_recv'])}"
        )


@click.command()
@click.option(
    "--category",
    "-c",
    type=click.Choice(["cpu", "memory", "disk", "battery", "network", "all"]),
    default="all",
    help="Information category to display",
)
@click.option("--json", "-j", "json_output", is_flag=True, help="Output in JSON format")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(category: str, json_output: bool, verbose: bool) -> None:
    """Display system information (CPU, memory, disk, battery, network)."""

    # Initialize logging
    init_logging(level=20 if verbose else 30)  # DEBUG if verbose, else WARNING

    try:
        # Get system information
        if category == "all":
            system_info = get_system_info()
        else:
            system_info = {
                "cpu": get_cpu_info() if category == "cpu" else {},
                "memory": get_memory_info() if category == "memory" else {},
                "disk": get_disk_info() if category == "disk" else {},
                "battery": get_battery_info() if category == "battery" else {},
                "network": get_network_info() if category == "network" else {},
            }
            # Keep only the requested category
            system_info = {k: v for k, v in system_info.items() if v}

        # Output format
        if json_output:
            import json as json_module

            click.echo(json_module.dumps(system_info, indent=2, default=str))
        else:
            # Human-readable format
            if "cpu" in system_info and system_info["cpu"]:
                _print_cpu_info(system_info["cpu"])

            if "memory" in system_info and system_info["memory"]:
                _print_memory_info(system_info["memory"])

            if "disk" in system_info and system_info["disk"]:
                _print_disk_info(system_info["disk"])

            if "battery" in system_info and system_info["battery"]:
                _print_battery_info(system_info["battery"])

            if "network" in system_info and system_info["network"]:
                _print_network_info(system_info["network"])

    except Exception as e:
        logger.exception("Unexpected error occurred")
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
