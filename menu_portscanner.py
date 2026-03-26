#!/usr/bin/env python3
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def banner():
    import time
    import sys

    print(CYAN + "\nBooting scanner...\n" + RESET)

    for i in range(0, 101, 10):
        sys.stdout.write(f"\rLoading: {i}%")
        sys.stdout.flush()
        time.sleep(0.2)

    print("\n")

    print(CYAN + r"""
        .-.
       (o o)
       | O \
       |   |
      /|   |\
     /_|   |_\
       /   \
      /_____\
      SYSTEM READY

╔══════════════════════════════════════╗
║      FAST PORT SCANNER TOOL         ║
║                                      ║
║      CREATED BY RAUF TIMURI         ║
╚══════════════════════════════════════╝
""" + RESET)
def resolve_target(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None

def common_ports(count):
    ports = [
        20,21,22,23,25,53,67,68,69,80,
        110,111,123,135,137,138,139,143,161,162,
        389,443,445,465,514,587,993,995,1433,1521,
        3306,3389,5432,5900,6379,8080,8443,27017,
        5000,8000,8888,1723,5060,554,179,10000,2000
    ]
    return ports[:count]

def service_name(port):
    custom = {
        143: "imap",
        587: "submission",
        1723: "pptp",
        5060: "sip",
        554: "rtsp",
    }
    if port in custom:
        return custom[port]
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"

def scan_port(host, port, timeout=1.0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((host, port)) == 0:
                return {"port": port, "service": service_name(port)}
    except Exception:
        pass
    return None

def main():
    banner()

    target = input("➤ Enter target (IP or domain): ").strip()
    ip = resolve_target(target)

    if not ip:
        print(RED + "\n[!] Invalid target." + RESET)
        sys.exit(1)

    count_input = input("➤ How many ports to scan: ").strip()

    try:
        count = int(count_input)
        if count <= 0:
            raise ValueError
    except ValueError:
        print(RED + "\n[!] Invalid number." + RESET)
        sys.exit(1)

    ports = list(range(1, count + 1))
    workers = min(100, max(1, len(ports)))

    print(YELLOW + "\n[+] Starting scan..." + RESET)
    print(YELLOW + f"[+] Target: {target} ({ip})" + RESET)
    print(YELLOW + f"[+] Total ports: {len(ports)}\n" + RESET)

    open_ports = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(scan_port, ip, port) for port in ports]

        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)
                print(GREEN + f"[OPEN] Port {result['port']} -> {result['service']}" + RESET)

    elapsed = time.time() - start_time
    open_ports.sort(key=lambda x: x["port"])

    print("\n=== RESULTS ===\n")

    if open_ports:
        for item in open_ports:
            print(f"[OPEN] Port {item['port']} -> {item['service']}")
    else:
        print("No open ports found.")

    print(f"\nTotal open ports: {len(open_ports)}")
    print(f"Scan time: {elapsed:.2f} seconds")
    print("Note: Other ports are closed or filtered.")

if __name__ == "__main__":
    main()
