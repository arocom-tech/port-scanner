import socket
from concurrent.futures import ThreadPoolExecutor

def scan_port(target, port, timeout=0.5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((target, port))
        if result == 0:
            try:
                service = socket.getservbyport(port, "tcp")
            except OSError:
                service = "unknown"
            return {"port": port, "state": "open", "service": service}
        return {"port": port, "state": "closed", "service": "-"}
    except (socket.timeout, socket.error):
        return {"port": port, "state": "filtered/error", "service": "-"}
    finally:
        sock.close()

def scan(target, start_port, end_port):
    results = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(scan_port, target, port)
                   for port in range(start_port, end_port + 1)]
        for future in futures:
            result = future.result()
            if result["state"] == "open":
                results.append(result)
    return sorted(results, key=lambda x: x["port"])
