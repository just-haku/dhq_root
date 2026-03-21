from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.core.database import redis_client
from app.api.auth import get_op_user
import psutil
import os
import time
from datetime import datetime, timedelta

router = APIRouter()

import subprocess
import json
import re

def _parse_pwrstat_value(line):
    """Extract the value after the dot separators in pwrstat output.
    E.g. '		State........................ Normal' -> 'Normal'
    """
    # Match: key followed by dots and spaces, then the value
    match = re.search(r'\.{2,}\s*(.+)$', line)
    return match.group(1).strip() if match else None

def get_ups_status():
    """Parse output from CyberPower pwrstat -status"""
    try:
        # User confirmed they can run this as 'haku' without sudo
        # Using absolute path for better reliability
        result = subprocess.run(['/usr/sbin/pwrstat', '-status'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return {"status": "Unavailable", "raw_error": result.stderr.strip() or "Command failed"}
            
        output = result.stdout
        data = {"status": "Connected"}
        
        field_map = {
            'Model Name': 'model',
            'Rating Voltage': 'rating_voltage',
            'Rating Power': 'rating_power',
            'State': 'state',
            'Power Supply by': 'power_supply',
            'Utility Voltage': 'utility_voltage',
            'Output Voltage': 'output_voltage',
            'Utility Frequency': 'utility_frequency',
            'Battery Capacity': 'battery_capacity',
            'Remaining Runtime': 'remaining_runtime',
            'Load': 'load',
            'Line Interaction': 'line_interaction',
            'Test Result': 'test_result',
            'Last Power Event': 'last_power_event',
        }
        
        for line in output.split('\n'):
            for key, field in field_map.items():
                if key in line:
                    val = _parse_pwrstat_value(line)
                    if val:
                        data[field] = val
                    break
        
        return data
    except Exception as e:
        return {"status": "Error", "message": str(e)}

def get_detailed_storage():
    """Get disk layout and mount points, filtering out tmpfs/virtual filesystems"""
    try:
        lsblk_res = subprocess.run(['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINTS,MODEL'], capture_output=True, text=True)
        lsblk_data = json.loads(lsblk_res.stdout)
        
        # Use -x to exclude tmpfs, devtmpfs, efivarfs
        df_res = subprocess.run(
            ['df', '-h', '-x', 'tmpfs', '-x', 'devtmpfs', '-x', 'efivarfs', '-x', 'squashfs',
             '--output=source,size,used,avail,pcent,target'],
            capture_output=True, text=True
        )
        df_lines = df_res.stdout.strip().split('\n')[1:]
        df_info = []
        for line in df_lines:
            p = line.split()
            if len(p) >= 6:
                df_info.append({
                    "fs": p[0], "size": p[1], "used": p[2], "avail": p[3], "percent": p[4], "mount": p[5]
                })
        return {"physical": lsblk_data.get("blockdevices", []), "mounts": df_info}
    except Exception as e:
        return {"error": str(e)}

@router.get("/system-health")
async def get_system_health(current_user: User = Depends(get_op_user)):
    """Get comprehensive system health metrics"""
    
    # CPU metrics - percpu=True for htop-like detail
    # We use a small interval (0.1s) to get a real instantaneous reading
    cpu_percent = psutil.cpu_percent(interval=0.1) 
    cpu_cores_percent = psutil.cpu_percent(interval=None, percpu=True)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    
    # Memory metrics
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # Old Disk metrics (for compatibility)
    disk = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()
    
    # New Hardware Details
    storage_details = get_detailed_storage()
    ups_details = get_ups_status()
    
    # Network metrics
    network = psutil.net_io_counters()
    
    # Process metrics
    dhq_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if any(name in proc.info['name'].lower() for name in ['python', 'node', 'nginx', 'mongod', 'redis']):
                dhq_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent'],
                    'memory_mb': proc.memory_info().rss / 1024 / 1024
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # System uptime
    uptime = time.time() - psutil.boot_time()
    
    # Load average
    load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": uptime,
        "uptime_formatted": format_uptime(uptime),
        "cpu": {
            "usage_percent": cpu_percent,
            "cores_percent": cpu_cores_percent,
            "core_count": cpu_count,
            "frequency_mhz": cpu_freq.current if cpu_freq else None,
            "load_average": {
                "1min": load_avg[0],
                "5min": load_avg[1],
                "15min": load_avg[2]
            }
        },
        "memory": {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "used_gb": memory.used / (1024**3),
            "usage_percent": memory.percent,
            "swap": {
                "total_gb": swap.total / (1024**3),
                "used_gb": swap.used / (1024**3),
                "usage_percent": swap.percent
            }
        },
        "storage": storage_details,
        "ups": ups_details,
        "disk": { # Keep for direct dashboard use in current UI
            "total_gb": disk.total / (1024**3),
            "used_gb": disk.used / (1024**3),
            "free_gb": disk.free / (1024**3),
            "usage_percent": (disk.used / disk.total) * 100,
            "read_mb_s": disk_io.read_bytes / (1024*1024) if disk_io else 0,
            "write_mb_s": disk_io.write_bytes / (1024*1024) if disk_io else 0
        },
        "network": {
            "bytes_sent": network.bytes_sent if network else 0,
            "bytes_recv": network.bytes_recv if network else 0,
            "packets_sent": network.packets_sent if network else 0,
            "packets_recv": network.packets_recv if network else 0
        },
        "processes": dhq_processes,
        "alerts": check_system_alerts(cpu_percent, memory.percent, (disk.used / disk.total) * 100)
    }

@router.get("/service-status")
async def get_service_status(current_user: User = Depends(get_op_user)):
    """Get status of all DHQ services"""
    
    services = {}
    
    # Check Backend (FastAPI)
    try:
        # This is the current service, so it's running
        services["backend"] = {
            "status": "running",
            "port": 8000,
            "uptime": "unknown", # Would need external monitoring
            "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
        }
    except Exception as e:
        services["backend"] = {"status": "error", "error": str(e)}
    
    # Check Socket.IO
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 8001))
        sock.close()
        
        services["socketio"] = {
            "status": "running" if result == 0 else "stopped",
            "port": 8001
        }
    except Exception as e:
        services["socketio"] = {"status": "error", "error": str(e)}
    
    # Check Frontend development server
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 3000))
        sock.close()
        
        services["frontend"] = {
            "status": "running" if result == 0 else "stopped",
            "port": 3000
        }
    except Exception as e:
        services["frontend"] = {"status": "error", "error": str(e)}
    
    # Check MongoDB
    try:
        from app.core.database import connect_db
        # Try to connect and execute a simple query
        connect_db()
        user_count = User.objects.count()
        services["mongodb"] = {
            "status": "connected",
            "database": "dhq_main",
            "collections": {
                "users": user_count
            }
        }
    except Exception as e:
        services["mongodb"] = {"status": "error", "error": str(e)}
    
    # Check Redis
    try:
        await redis_client.ping()
        redis_info = await redis_client.info()
        services["redis"] = {
            "status": "connected",
            "version": redis_info.get('redis_version'),
            "used_memory": redis_info.get('used_memory_human'),
            "connected_clients": redis_info.get('connected_clients')
        }
    except Exception as e:
        services["redis"] = {"status": "error", "error": str(e)}
    
    # Check Nginx (if running)
    try:
        nginx_processes = [p for p in psutil.process_iter() if 'nginx' in p.info['name'].lower()]
        services["nginx"] = {
            "status": "running" if nginx_processes else "stopped",
            "processes": len(nginx_processes)
        }
    except Exception as e:
        services["nginx"] = {"status": "error", "error": str(e)}
    
    return services

@router.get("/performance-metrics")
async def get_performance_metrics(
    hours: int = 24,
    current_user: User = Depends(get_op_user)
):
    """Get performance metrics over time"""
    
    # This would typically query a time-series database
    # For now, we'll return recent metrics
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    # Generate sample data points (in production, this would come from monitoring system)
    metrics = []
    current_time = start_time
    
    while current_time <= end_time:
        # Sample metrics with some variation
        cpu_usage = 20 + (hash(str(current_time)) % 30)  # 20-50%
        memory_usage = 40 + (hash(str(current_time) + 1) % 20)  # 40-60%
        
        metrics.append({
            "timestamp": current_time.isoformat(),
            "cpu_percent": cpu_usage,
            "memory_percent": memory_usage,
            "active_users": 5 + (hash(str(current_time) + 2) % 10),
            "requests_per_minute": 10 + (hash(str(current_time) + 3) % 20)
        })
        
        current_time += timedelta(minutes=30)  # Every 30 minutes
    
    return {
        "time_range": f"Last {hours} hours",
        "metrics": metrics,
        "summary": {
            "avg_cpu": round(sum(m["cpu_percent"] for m in metrics) / len(metrics), 2),
            "avg_memory": round(sum(m["memory_percent"] for m in metrics) / len(metrics), 2),
            "peak_cpu": max(m["cpu_percent"] for m in metrics),
            "peak_memory": max(m["memory_percent"] for m in metrics),
            "total_requests": sum(m["requests_per_minute"] for m in metrics)
        }
    }

@router.get("/alerts")
async def get_system_alerts(current_user: User = Depends(get_op_user)):
    """Get current system alerts"""
    
    alerts = []
    
    # Check system metrics for alerts
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # CPU alerts
    if cpu_percent > 80:
        alerts.append({
            "type": "critical",
            "service": "system",
            "message": f"High CPU usage: {cpu_percent}%",
            "timestamp": datetime.utcnow().isoformat()
        })
    elif cpu_percent > 60:
        alerts.append({
            "type": "warning",
            "service": "system",
            "message": f"Elevated CPU usage: {cpu_percent}%",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    # Memory alerts
    if memory.percent > 85:
        alerts.append({
            "type": "critical",
            "service": "system",
            "message": f"High memory usage: {memory.percent}%",
            "timestamp": datetime.utcnow().isoformat()
        })
    elif memory.percent > 70:
        alerts.append({
            "type": "warning",
            "service": "system",
            "message": f"Elevated memory usage: {memory.percent}%",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    # Disk alerts
    disk_usage_percent = (disk.used / disk.total) * 100
    if disk_usage_percent > 90:
        alerts.append({
            "type": "critical",
            "service": "system",
            "message": f"Low disk space: {disk_usage_percent:.1f}%",
            "timestamp": datetime.utcnow().isoformat()
        })
    elif disk_usage_percent > 80:
        alerts.append({
            "type": "warning",
            "service": "system",
            "message": f"Low disk space: {disk_usage_percent:.1f}%",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    # Check service status
    try:
        import socket
        # Check Socket.IO
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 8001))
        sock.close()
        
        if result != 0:
            alerts.append({
                "type": "critical",
                "service": "socketio",
                "message": "Socket.IO service is not responding",
                "timestamp": datetime.utcnow().isoformat()
            })
    except:
        pass
    
    # Check Redis
    try:
        redis_client.ping()
    except:
        alerts.append({
            "type": "critical",
            "service": "redis",
            "message": "Redis service is not responding",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return {
        "alerts": alerts,
        "total_count": len(alerts),
        "critical_count": len([a for a in alerts if a["type"] == "critical"]),
        "warning_count": len([a for a in alerts if a["type"] == "warning"])
    }

def format_uptime(seconds):
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def check_system_alerts(cpu_percent, memory_percent, disk_percent):
    alerts = []
    
    if cpu_percent > 80:
        alerts.append({
            "type": "critical",
            "message": f"High CPU usage: {cpu_percent}%"
        })
    elif cpu_percent > 60:
        alerts.append({
            "type": "warning",
            "message": f"Elevated CPU usage: {cpu_percent}%"
        })
    
    if memory_percent > 85:
        alerts.append({
            "type": "critical",
            "message": f"High memory usage: {memory_percent}%"
        })
    elif memory_percent > 70:
        alerts.append({
            "type": "warning",
            "message": f"Elevated memory usage: {memory_percent}%"
        })
    
    if disk_percent > 90:
        alerts.append({
            "type": "critical",
            "message": f"Low disk space: {disk_percent:.1f}%"
        })
    elif disk_percent > 80:
        alerts.append({
            "type": "warning",
            "message": f"Low disk space: {disk_percent:.1f}%"
        })
    
    return alerts
