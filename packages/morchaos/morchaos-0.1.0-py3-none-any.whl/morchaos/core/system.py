"""System information collection utilities."""
# --------------------------------------------------------------------
# Design concept
# --------------------------------------------------------------------
# 1. *Single‑responsibility helpers* –  Each public function (`get_cpu_info`,
#    `get_memory_info`, `get_disk_info`, `get_battery_info`, `get_network_info`)
#    gathers one specific category of system metrics and returns a plain
#    dictionary.  This keeps the API composable: callers can combine only
#    the parts they need, and the functions can be unit‑tested in isolation.
#
# 2. *Graceful degradation* –  Where a metric is unavailable (e.g. no
#    battery, or a read operation fails), the function logs the problem
#    and returns a sane default.  The rest of the system can continue to
#    operate without raising unexpected exceptions.
#
# 3. *Use of `psutil`* –  The optional dependency is imported at the
#    module level.  If it is missing we raise an informative `ImportError`
#    with a clear pip‑install suggestion, preventing the module from
#    silently failing at runtime.
#
# 4. *Minimal side‑effects* –  All functions simply read data and return
#    it.  They never write to disk or modify the system, which makes them
#    safe to call from anywhere (including cron jobs, monitoring agents,
#    or interactive sessions).
#
# 5. *Consistent return shape* –  Each dictionary contains the same
#    structure for common metrics (e.g., `total`, `used`, `percent`), so
#    callers can process the results without having to branch on missing
#    keys.  Optional fields are added only when the underlying data is
#    available (e.g., `io_stats`, `present` for battery).
# --------------------------------------------------------------------

import logging
from typing import Any, Dict, Optional

# Optional third‑party dependency: psutil
try:
    import psutil
except ImportError as e:
    raise ImportError("Required package not installed. Run: pip install psutil") from e

# Local logger – configured by the application that imports this module
logger = logging.getLogger(__name__)


def get_cpu_info() -> Dict[str, Any]:
    """Get CPU information.

    The routine collects physical/logical core counts, CPU frequency
    statistics (when supported), and current utilization percentages.
    It performs two successive calls to ``psutil.cpu_percent`` – one
    for the aggregate usage and another for per‑core usage – to obtain
    fresh measurements.
    """
    try:
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "max_frequency": 0.0,
            "min_frequency": 0.0,
            "current_frequency": 0.0,
            "usage_percent": psutil.cpu_percent(interval=1),
            "usage_per_core": psutil.cpu_percent(interval=1, percpu=True),
        }
        # Get CPU frequency info if available
        try:
            freq_info = psutil.cpu_freq()
            if freq_info:
                cpu_info.update(
                    {
                        "max_frequency": freq_info.max,
                        "min_frequency": freq_info.min,
                        "current_frequency": freq_info.current,
                    }
                )
        except (AttributeError, OSError):
            logger.warning("CPU frequency information not available")
        return cpu_info
    except Exception as e:
        # In the unlikely event of a crash we return a zeroed dictionary
        # so callers can still rely on a predictable return type.
        logger.error(f"Failed to get CPU info: {e}")
        return {
            "physical_cores": 0,
            "logical_cores": 0,
            "max_frequency": 0.0,
            "min_frequency": 0.0,
            "current_frequency": 0.0,
            "usage_percent": 0.0,
            "usage_per_core": [],
        }


def get_memory_info() -> Dict[str, Any]:
    """Get memory information.

    Retrieves both physical RAM and swap usage statistics via
    ``psutil.virtual_memory`` and ``psutil.swap_memory``.  All values
    are returned as integers or floats so the caller can safely format
    them (e.g., converting bytes to megabytes).
    """
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "free": memory.free,
            "percent": memory.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_free": swap.free,
            "swap_percent": swap.percent,
        }
    except Exception as e:
        logger.error(f"Failed to get memory info: {e}")
        return {
            "total": 0,
            "available": 0,
            "used": 0,
            "free": 0,
            "percent": 0.0,
            "swap_total": 0,
            "swap_used": 0,
            "swap_free": 0,
            "swap_percent": 0.0,
        }


def get_disk_info() -> Dict[str, Any]:
    """Get disk information.

    Enumerates all mounted partitions, gathers per‑partition usage
    statistics, and aggregates global I/O counters.  Permissions
    errors on a drive are silently skipped so that a read‑only or
    inaccessible mount does not break the entire report.
    """
    try:
        disk_info = {}
        # Get disk partitions
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.device] = {
                    "mountpoint": partition.mountpoint,
                    "filesystem": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": (usage.used / usage.total) * 100
                    if usage.total > 0
                    else 0,
                }
            except (PermissionError, OSError):
                # Skip inaccessible drives
                continue
        # Get disk I/O statistics
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_info["io_stats"] = {
                    "read_count": disk_io.read_count,
                    "write_count": disk_io.write_count,
                    "read_bytes": disk_io.read_bytes,
                    "write_bytes": disk_io.write_bytes,
                    "read_time": disk_io.read_time,
                    "write_time": disk_io.write_time,
                }
        except (AttributeError, OSError):
            logger.warning("Disk I/O statistics not available")
        return disk_info
    except Exception as e:
        logger.error(f"Failed to get disk info: {e}")
        return {}


def get_battery_info() -> Dict[str, Any]:
    """Get battery information.

    Returns a minimal dictionary.  If no battery is present the function
    returns ``{"present": False}``.  Otherwise it reports the percentage,
    plug‑state, and seconds left (or ``None`` if unlimited).
    """
    try:
        battery: Optional[Any] = psutil.sensors_battery()  # type: ignore[no-untyped-call]
        if battery is None:
            return {"present": False}
        return {
            "present": True,
            "percent": battery.percent,
            "power_plugged": battery.power_plugged,
            "seconds_left": battery.secsleft
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED
            else None,
        }
    except Exception as e:
        logger.error(f"Failed to get battery info: {e}")
        return {"present": False}


def get_network_info() -> Dict[str, Any]:
    """Get network information.

    Builds a per‑interface dictionary that includes addresses,
    operational status, duplex/speed/MTU, and I/O counters.  Missing
    data is omitted rather than causing a crash, ensuring robust
    operation on headless servers or systems with restricted
    permissions.
    """
    try:
        network_info = {}
        # Get network interfaces
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for interface_name, addresses in interfaces.items():
            interface_info: Dict[str, Any] = {
                "addresses": [],
                "is_up": False,
                "duplex": "unknown",
                "speed": 0,
                "mtu": 0,
            }
            # Get interface addresses
            addresses_list = interface_info["addresses"]

            for addr in addresses:
                addresses_list.append(
                    {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast,
                    }
                )
            # Get interface statistics
            if interface_name in stats:
                stat = stats[interface_name]
                interface_info.update(
                    {
                        "is_up": stat.isup,
                        "duplex": str(stat.duplex),
                        "speed": stat.speed,
                        "mtu": stat.mtu,
                    }
                )
            network_info[interface_name] = interface_info
        # Get network I/O statistics
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                network_info["io_stats"] = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "errin": net_io.errin,
                    "errout": net_io.errout,
                    "dropin": net_io.dropin,
                    "dropout": net_io.dropout,
                }
        except (AttributeError, OSError):
            logger.warning("Network I/O statistics not available")
        return network_info
    except Exception as e:
        logger.error(f"Failed to get network info: {e}")
        return {}


def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information.

    Combines all category functions into a single dictionary.  Each
    key is a distinct subsystem – e.g., ``"cpu"``, ``"memory"``, etc. –
    making it convenient for monitoring dashboards or loggers that
    expect a nested JSON‑serialisable payload.
    """
    return {
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "battery": get_battery_info(),
        "network": get_network_info(),
    }
