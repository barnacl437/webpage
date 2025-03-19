#!/usr/bin/env python3
"""clisysmtr-py: system information and monitoring tool

a command-line tool to display system information and monitor resources.
"""

import socket
import argparse
import time
import psutil
import datetime
import sys

def get_local_ip():
    """
    retrieves the local machine's ip address.

    returns:
        str: the ip address, or none if an error occurs.
    """
    try:
        s = socket.socket(socket.af_inet, socket.sock_dgram)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except socket.error as e:
        print(f"error getting local ip: {e}")
        return None
    except Exception as e:
        print(f"an unexpected error occurred: {e}")
        return None

def get_cpu_usage():
    """
    retrieves the current cpu usage.

    returns:
        float: the cpu usage percentage, or none on error.
    """
    try:
        return psutil.cpu_percent(interval=1)
    except Exception as e:
        print(f"error getting cpu usage: {e}")
        return None

def get_cpu_clock():
    """
    retrieves the current cpu clock speed.

    returns:
        float: the cpu clock speed in mhz, or none on error or if not supported.
    """
    try:
        if hasattr(psutil, "cpu_freq"):
            return psutil.cpu_freq().current
        else:
            return None  # cpu clock speed not supported on this system
    except Exception as e:
        print(f"error getting cpu clock speed: {e}")
        return None

def get_cpu_name():
    """
    Retrieves the CPU name.

    Returns:
        str: The CPU name, or None on error.
    """
    try:
        return psutil.cpu_info()[0].model  # Access the CPU model
    except Exception as e:
        print(f"Error getting CPU name: {e}")
        return None

def get_ram_usage():
    """
    retrieves the current ram usage.

    returns:
        tuple: (total, used, percent) in gb and percentage, or (none,)*3 on error.
    """
    try:
        mem = psutil.virtual_memory()
        total = mem.total / (1024 ** 3)
        used = mem.used / (1024 ** 3)
        percent = mem.percent
        return total, used, percent
    except Exception as e:
        print(f"error getting ram usage: {e}")
        return None, None, None

def get_disk_usage(path="/"):
    """
    retrieves the current disk usage for the specified path.

    args:
        path (str): the path to the disk or partition to check.  defaults to "/".

    returns:
        tuple: (device, total, used, percent) in gb and percentage, or (none,)*4 on error.
    """
    try:
        disk = psutil.disk_usage(path)
        total = disk.total / (1024 ** 3)
        used = disk.used / (1024 ** 3)
        percent = disk.percent
        device = disk.device
        return device, total, used, percent
    except Exception as e:
        print(f"error getting disk usage for {path}: {e}")
        return None, None, None, None

def get_network_activity():
    """
    retrieves the current network activity.

    returns:
        tuple: (bytes_sent_per_sec, bytes_recv_per_sec) or (none, none) on error.
    """
    try:
        net_io_counters = psutil.net_io_counters()
        bytes_sent = net_io_counters.bytes_sent
        bytes_recv = net_io_counters.bytes_recv
        time.sleep(1)  # get bytes sent/received over 1 second
        net_io_counters_after = psutil.net_io_counters()
        bytes_sent_rate = net_io_counters_after.bytes_sent - bytes_sent
        bytes_recv_rate = net_io_counters_after.bytes_recv - bytes_recv
        return bytes_sent_rate, bytes_recv_rate
    except Exception as e:
        print(f"error getting network activity: {e}")
        return None, None

def display_system_info(args):
    """
    displays the system information.

    args:
        args: the parsed command-line arguments.
    """
    ip_address = get_local_ip()
    cpu_usage = get_cpu_usage()
    cpu_clock = get_cpu_clock()
    cpu_name = get_cpu_name()
    ram_total, ram_used, ram_percent = get_ram_usage()
    disk_device, disk_total, disk_used, disk_percent = get_disk_usage()
    bytes_sent, bytes_recv = get_network_activity()

    if ip_address:
        print(f"local ip address: {ip_address}")
    else:
        print("failed to retrieve local ip address.")

    if cpu_name:
        print(f"cpu name: {cpu_name}")
    else:
        print("failed to retrieve cpu name.")

    if cpu_usage is not None:
        print(f"cpu usage: {cpu_usage}%")
    else:
        print("failed to retrieve cpu usage.")

    if cpu_clock is not None:
        print(f"cpu clock speed: {cpu_clock:.2f} mhz")
    else:
        print("cpu clock speed: not supported or failed to retrieve.")

    if ram_total is not None and ram_used is not None and ram_percent is not None:
        print(f"ram: {ram_used:.2f} gb / {ram_total:.2f} gb ({ram_percent:.2f}%)")
    else:
        print("failed to retrieve ram usage.")

    if disk_device and disk_total and disk_used and disk_percent:
        print(f"disk drive ({disk_device}): {disk_used:.2f} gb / {disk_total:.2f} gb ({disk_percent:.2f}%)")
    else:
        print("failed to retrieve disk usage.")

    if bytes_sent is not None and bytes_recv is not None:
        print(f"network activity: sent: {bytes_sent} bytes/s, received: {bytes_recv} bytes/s")
    else:
        print("failed to retrieve network activity.")

    if args.log:
        timestamp = datetime.datetime.now().strftime("%y%m%d-%h%m%s")
        log_entry = (
            f"{timestamp}, ip: {ip_address}, cpu_name: {cpu_name}, cpu_usage: {cpu_usage}%, "
            f"cpu_clock: {cpu_clock}, ram_total: {ram_total:.2f}gb, ram_used: {ram_used:.2f}gb, "
            f"ram_percent: {ram_percent:.2f}%, disk_device: {disk_device}, "
            f"disk_total: {disk_total:.2f}gb, disk_used: {disk_used:.2f}gb, "
            f"disk_percent: {disk_percent:.2f}%, bytes_sent: {bytes_sent}, bytes_recv: {bytes_recv}\n"
        )
        try:
            with open(args.log, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"error writing to log file: {e}")

def main():
    """
    main function to parse arguments and display system information.
    """
    # create an argument parser
    parser = argparse.ArgumentParser(  # Corrected from argument_parser to ArgumentParser
        description="display system information and monitor resources."
    )

    # add version argument
    parser.add_argument(
        "--version",
        action="version",
        version="clisysmtr-py version 001",
        help="show program's version number and exit",
    )

    # add interval argument
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=1,
        help="time interval in seconds for updating information",
    )

    # add log argument
    parser.add_argument(
        "-l",
        "--log",
        type=str,
        help="log system information to the specified file",
    )

    # add one-time display argument
    parser.add_argument(
        "-n",
        "--no-loop",
        action="store_true",
        help="do not loop, display once and exit",
    )
    # add help argument
    # parser.add_argument(  # Removed the explicit help argument
    #     "-h",
    #     "--help",
    #     action="help",
    #     help="show this help message and exit",
    # )

    # parse the arguments
    args = parser.parse_args()
    if args.no_loop:
        display_system_info(args)
    else:

        # display system information in a loop with the specified interval
        try:
            while True:
                display_system_info(args)
                time.sleep(args.interval)
                if args.log:
                    print(f"logged to {args.log}")
        except KeyboardInterrupt:
            print("\nmonitoring stopped by user.")
        except Exception as e:
            print(f"an unexpected error occurred: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
