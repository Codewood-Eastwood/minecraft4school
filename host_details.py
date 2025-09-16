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
import pickle
from pathlib import Path

# Cache configuration
CACHE_FILE = "host_details_cache.pkl"
CACHE_EXPIRY = 3600  # Cache expiry time in seconds (1 hour)

host_details = {}

def load_from_cache():
    """Load cached data if it exists and isn't expired."""
    if not Path(CACHE_FILE).exists():
        return None
    
    cache_time = Path(CACHE_FILE).stat().st_mtime
    if (time.time() - cache_time) > CACHE_EXPIRY:
        return None
    
    try:
        with open(CACHE_FILE, 'rb') as f:
            return pickle.load(f)
    except:
        return None

def save_to_cache(data):
    """Save data to cache file."""
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(data, f)
    except:
        pass  # Silently fail if cache can't be written

def safe_get(key, func):
    """Safely get system information, using cache when possible."""
    # Try to get from cache first
    if key in cached_data:
        host_details[key] = cached_data[key]
        return
    
    # If not in cache or cache miss, get fresh data
    try:
        host_details[key] = func()
    except Exception as e:
        host_details[key] = f"Error: {e}"
        print(f"Failed to load {key}")

# Try to load from cache
cached_data = load_from_cache() or {}

# Basic Info
safe_get('Hostname', lambda: socket.gethostname())
safe_get('FQDN', lambda: socket.getfqdn())
safe_get('IP Address', lambda: socket.gethostbyname(socket.gethostname()))
safe_get('MAC Address', lambda: ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1]))
safe_get('OS', lambda: platform.platform())
safe_get('OS Version', lambda: platform.version())
safe_get('OS Release', lambda: platform.release())
safe_get('System', lambda: platform.system())
safe_get('Machine', lambda: platform.machine())
safe_get('Architecture', lambda: platform.architecture()[0])
safe_get('Processor', lambda: platform.processor())
safe_get('CPU Model', lambda: platform.uname().processor)
safe_get('CPU Count (Logical)', lambda: os.cpu_count())
safe_get('CPU Count (Physical)', lambda: psutil.cpu_count(logical=False))
safe_get('CPU Frequency (MHz)', lambda: psutil.cpu_freq().max if psutil.cpu_freq() else None)
safe_get('RAM Total (GB)', lambda: round(psutil.virtual_memory().total / (1024**3), 2))
safe_get('RAM Available (GB)', lambda: round(psutil.virtual_memory().available / (1024**3), 2))
safe_get('Swap Memory (GB)', lambda: round(psutil.swap_memory().total / (1024**3), 2))

# Storage
safe_get('Disk Total (GB)', lambda: round(shutil.disk_usage("/").total / (1024**3), 2))
safe_get('Disk Used (GB)', lambda: round(shutil.disk_usage("/").used / (1024**3), 2))
safe_get('Disk Free (GB)', lambda: round(shutil.disk_usage("/").free / (1024**3), 2))
safe_get('Mounted Filesystems', lambda: {part.mountpoint: shutil.disk_usage(part.mountpoint)._asdict() for part in psutil.disk_partitions()})

# Network
safe_get('Network Interfaces', lambda: psutil.net_if_addrs())
safe_get('Network Stats', lambda: psutil.net_if_stats())
safe_get('Default Gateway', lambda: psutil.net_if_addrs().get(next(iter(psutil.net_if_stats().keys()), ''), [{}])[0].address if psutil.net_if_addrs().get(next(iter(psutil.net_if_stats().keys()), ''), [{}]) else None)
safe_get('Active Connections', lambda: [conn._asdict() for conn in psutil.net_connections()])

# Users and Environment
safe_get('Current User', lambda: getpass.getuser())
safe_get('Logged In Users', lambda: [u._asdict() for u in psutil.users()])
safe_get('Environment Variables', lambda: dict(os.environ))
safe_get('Working Directory', lambda: os.getcwd())

# Python
safe_get('Python Version', lambda: platform.python_version())
safe_get('Python Build', lambda: platform.python_build())
safe_get('Python Compiler', lambda: platform.python_compiler())
safe_get('Python Implementation', lambda: platform.python_implementation())

# System Uptime
safe_get('Uptime (minutes)', lambda: int(time.time() - psutil.boot_time()) // 60)
safe_get('Uptime (days)', lambda: round((time.time() - psutil.boot_time()) / (60 * 60 * 24), 2))

# Locale and Time
safe_get('Locale', lambda: locale.getdefaultlocale())
safe_get('Time Zone', lambda: time.tzname)
safe_get('Current Time', lambda: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

# UUID
safe_get('System UUID', lambda: str(uuid.uuid1()))

# Save to cache (only if we have fresh data)
if host_details and host_details != cached_data:
    save_to_cache(host_details)