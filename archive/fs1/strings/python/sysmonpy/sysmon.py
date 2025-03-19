import psutil
import time
import datetime

def get_system_usage():
    """
    Retrieves and returns current CPU, memory, RAM, network, and disk usage.

    Returns:
        tuple: (cpu_usage, mem_usage, ram_total, ram_available, bytes_sent, bytes_recv, disk_total, disk_used, disk_free)
            cpu_usage (float): Current CPU usage as a percentage.
            mem_usage (float): Current memory usage as a percentage.
            ram_total (float): Total RAM in GB.
            ram_available (float): Available RAM in GB.
            bytes_sent (float): Bytes sent in the last second.
            bytes_recv (float): Bytes received in the last second.
            disk_total (float): Total disk space in GB.
            disk_used (float): Used disk space in GB.
            disk_free (float): Free disk space in GB.

            If an error occurs, returns (None,)*9.  This means it will return 9 None values.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        mem_usage = mem.percent
        ram_total = mem.total / (1024 ** 3)
        ram_available = mem.available / (1024 ** 3)

        net_io_counters = psutil.net_io_counters()
        bytes_sent = net_io_counters.bytes_sent
        bytes_recv = net_io_counters.bytes_recv
        # Get initial values for bytes sent and received
        time.sleep(1) 
        net_io_counters_after = psutil.net_io_counters()
        bytes_sent_rate = net_io_counters_after.bytes_sent - bytes_sent
        bytes_recv_rate = net_io_counters_after.bytes_recv - bytes_recv

        disk = psutil.disk_usage('/') # disc drive location
        disk_total = disk.total / (1024 ** 3)  # Convert to GB
        disk_used = disk.used / (1024 ** 3)    # Convert to GB
        disk_free = disk.free / (1024 ** 3)    # Convert to GB
        disk_usage_percent = disk.percent

        return (cpu_usage, mem_usage, ram_total, ram_available, bytes_sent_rate, bytes_recv_rate,
                disk_total, disk_used, disk_free)
    except Exception as e:
        print(f"Error getting system usage: {e}")
        return None, None, None, None, None, None, None, None, None

def log_system_usage(log_file="system_usage.log"):
    """
    Logs system usage (CPU, memory, RAM, network, and disk) to a file with a timestamp.
    Creates the log file if it doesn't exist, or appends to it if it does.

    Args:
        log_file (str, optional): The name of the log file.
            Defaults to "system_usage.log".
    """
    (cpu_usage, mem_usage, ram_total, ram_available, bytes_sent, bytes_recv,
     disk_total, disk_used, disk_free) = get_system_usage()
    if cpu_usage is not None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
	    f"----------------------------------------------------------------------\n"
            f"{timestamp}\n"
	    f"hardware monitoring:\n"
	    f"		--  CPU usage: {cpu_usage}%\n"
            f"          --  mem usage: {mem_usage}%\n"
            f"          --  total RAM: {ram_total:.2f} GB\n"
            f"          --  available RAM: {ram_available:.2f} GB\n"
	    f"network activity\n"
            f"          --  bytes sent/received: {bytes_sent}/{bytes_recv}\n"
	    f"disc space\n"
            f"          --  total space: {disk_total:.2f} GB\n"
            f"          --  used/free space: {disk_used:.2f}/{disk_free:.2f}GB\n\n"
        )
        try:
            with open(log_file, "a") as f:
                f.write(log_entry)
            print(f"system resource logged at:\n{log_entry}")  # print with added newlines
        except Exception as e:
            print(f"can't write to log file: {e}")
    else:
        print("unable to retrieve system info. aborted.")

def monitor_system(interval=60, log_file="system_usage.log"):
    """
    Monitors system performance at a specified interval and logs the data.

    Args:
        interval (int, optional): The time interval (in seconds) between logging.
            Defaults to 60 seconds.
        log_file (str, optional): The name of the log file.
            Defaults to "system_usage.log".
    """
    print(f"""
	sysmon v001. 
	monitoring system performance every {interval} seconds. Logging to {log_file}...
	might take approx. additional 1-2 seconds.
	""")
    try:
        while True:
            log_system_usage(log_file)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"An error occurred during monitoring: {e}")

if __name__ == "__main__":
    monitor_system(interval=8, log_file="sysmon_log.txt")
