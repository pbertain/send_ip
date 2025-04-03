#!/usr/bin/env python3
"""
get_net_iface.py - Collects system IPv6 addresses and uptime,
prints them, and sends a Prowl notification.
"""

import netifaces
import socket
import os
import platform
import subprocess
from datetime import datetime, timedelta
from pyprowl import Prowl

__file_name__ = "get_net_iface.py"
__app_name__ = "Interface Sender"
__version__ = "4"

def get_active_ipv6_addresses():
    ipv6_addresses = {}
    for interface in netifaces.interfaces():
        if 'lo' in interface or interface == 'lo0':
            continue
        addresses = netifaces.ifaddresses(interface)
        ipv6_info = addresses.get(netifaces.AF_INET6)
        if ipv6_info:
            filtered_addresses = [
                addr['addr'].split('%')[0]
                for addr in ipv6_info if not addr['addr'].startswith('fe')
            ]
            if filtered_addresses:
                ipv6_addresses[interface] = filtered_addresses
    return ipv6_addresses

def get_system_uptime():
    try:
        if platform.system() == "Darwin":
            result = subprocess.run(
                ["sysctl", "-n", "kern.boottime"],
                capture_output=True,
                text=True,
                check=True,
            )
            boot_time_parts = result.stdout.strip().split(",")[0].split("=")[-1].strip()
            boot_time = datetime.fromtimestamp(int(boot_time_parts))
            uptime_seconds = (datetime.now() - boot_time).total_seconds()
        elif platform.system() == "Linux":
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
        else:
            return "System uptime is not available on this platform."
        uptime_timedelta = timedelta(seconds=uptime_seconds)
        return str(uptime_timedelta).split('.')[0]
    except Exception as e:
        return f"Error retrieving uptime: {e}"

def send_to_prowl(api_key, event, description):
    try:
        prowl = Prowl(api_key)
        prowl.add(event=event, description=description)
        print("Notification sent to Prowl successfully.\n")
    except Exception as e:
        print(f"Error sending notification to Prowl: {e}")

def collect_info():
    hostname = socket.gethostname()
    ipv6_addresses = get_active_ipv6_addresses()
    current_time = datetime.now().strftime("%a %Y-%m-%d %H:%M")
    uptime = get_system_uptime()

    ipv6_info = "\n".join(
        f"{interface}: {', '.join(addresses)}"
        for interface, addresses in ipv6_addresses.items()
    ) or "No active IPv6 addresses found."

    message = (
        f"Hostname: {hostname}\n\n"
        f"IPv6 Addresses:\n{ipv6_info}\n"
        f"\nCurrent Time: {current_time}\n"
        f"System Uptime: {uptime}\n"
    )
    return hostname, ipv6_addresses, current_time, uptime, message

def main():
    api_key = os.environ.get("PROWL_API_KEY")
    if not api_key:
        print("Environment variable 'PROWL_API_KEY' not set.")
        return

    hostname, ipv6_addresses, current_time, uptime, message = collect_info()

    print(f"\nHostname: {hostname}\n")
    for iface, addresses in ipv6_addresses.items():
        print(f"  Interface: {iface}")
        for addr in addresses:
            print(f"    IPv6 Address: {addr}")
    print(f"\nCurrent Time: {current_time}")
    print(f"System Uptime: {uptime}\n")

    send_to_prowl(api_key, event="System Info", description=message)

if __name__ == "__main__":
    main()
