# flake8: noqa: E501

import socket
import platform
import os
import time
import psutil
import getpass
import uuid
import locale
import shutil

host_details = {
    # Basic Info
    'Hostname': socket.gethostname(),
    'FQDN': socket.getfqdn(),
    'IP Address': socket.gethostbyname(socket.gethostname()),
    'MAC Address': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1]),
    'OS': platform.platform(),
    'OS Version': platform.version(),
    'OS Release': platform.release(),
    'System': platform.system(),
    'Machine': platform.machine(),
    'Architecture': platform.architecture()[0],
    'Processor': platform.processor(),
    'CPU Model': platform.uname().processor,
    'CPU Count (Logical)': os.cpu_count(),
    'CPU Count (Physical)': psutil.cpu_count(logical=False),
    'CPU Frequency (MHz)': psutil.cpu_freq().max if psutil.cpu_freq() else None,
    'RAM Total (GB)': round(psutil.virtual_memory().total / (1024**3), 2),
    'RAM Available (GB)': round(psutil.virtual_memory().available / (1024**3), 2),
    'Swap Memory (GB)': round(psutil.swap_memory().total / (1024**3), 2),

    # Storage
    'Disk Total (GB)': round(shutil.disk_usage("/").total / (1024**3), 2),
    'Disk Used (GB)': round(shutil.disk_usage("/").used / (1024**3), 2),
    'Disk Free (GB)': round(shutil.disk_usage("/").free / (1024**3), 2),
    'Mounted Filesystems': {part.mountpoint: shutil.disk_usage(part.mountpoint)._asdict() for part in psutil.disk_partitions()},

    # Network
    'Network Interfaces': psutil.net_if_addrs(),
    'Network Stats': psutil.net_if_stats(),
    'Default Gateway': psutil.net_if_addrs().get(psutil.net_if_stats().keys().__iter__().__next__(), [{}])[0].address,
    'Active Connections': [conn._asdict() for conn in psutil.net_connections()],

    # Users and Environment
    'Current User': getpass.getuser(),
    'Logged In Users': [u._asdict() for u in psutil.users()],
    'Environment Variables': dict(os.environ),
    'Working Directory': os.getcwd(),

    # Python
    'Python Version': platform.python_version(),
    'Python Build': platform.python_build(),
    'Python Compiler': platform.python_compiler(),
    'Python Implementation': platform.python_implementation(),

    # System Uptime
    'Uptime (minutes)': int(time.time() - psutil.boot_time()) // 60,
    'Uptime (days)': round((time.time() - psutil.boot_time()) / (60 * 60 * 24), 2),

    # Locale and Time
    'Locale': locale.getdefaultlocale(),
    'Time Zone': time.tzname,
    'Current Time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),

    # UUID
    'System UUID': str(uuid.uuid1()),
}
