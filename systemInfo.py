"""
用于监控系统各项数据
"""
import psutil
def cpu():
    cpu = psutil.cpu_count()
    cpu_logical = psutil.cpu_count(logical=False)
    cpu_per = psutil.cpu_percent(1)
    return {'cpu': cpu, 'cpu_logical': cpu_logical, 'percent': cpu_per}
# 监控内存信息：.
def mem():
#	mem = psutil.virtual_memory()   查看内存信息；
    mem_total = psutil.virtual_memory()[0]/1024/1024/1024
    mem_used = psutil.virtual_memory()[3] / 1024 / 1024/1024
    mem_per = psutil.virtual_memory()[2]
    return {'total': mem_total, 'used': mem_used, 'percent': mem_per}
# 监控硬盘使用率：
def disk():
    total = psutil.disk_usage('F:\\录播')[0] / 1024 / 1024/1024
    used = psutil.disk_usage('F:\\录播')[1] / 1024 / 1024 / 1024
    free = psutil.disk_usage('F:\\录播')[2] / 1024 / 1024 / 1024
    percent = psutil.disk_usage('F:\\录播')[3]
    return {'total': total, 'used': used, 'free': free, 'percent': percent}
def network():
#	network = psutil.net_io_counters() #查看网络流量的信息；
    network_sent = psutil.net_io_counters()[0]/8/1024 #每秒接受的kb
    network_recv = psutil.net_io_counters()[1]/8/1024
    return {'network_sent': network_sent, 'network_recv': network_recv}

def infolist():
    return {
        "CMD": "heartbeat",
        "UUID": "ca4d9c3f-a5fe-4eb8-a8b2-43da82f94c9c",
        "name": "NGlive-1",
        "cpu": cpu(),
        "memory": mem(),
        "disk": disk(),
    }


