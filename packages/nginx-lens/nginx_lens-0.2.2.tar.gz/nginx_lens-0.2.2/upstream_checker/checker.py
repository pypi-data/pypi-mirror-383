# upstream_checker/checker.py

import socket
import time
import http.client
from typing import Dict, List


def check_tcp(address: str, timeout: float, retries: int) -> bool:
    """Проверка доступности сервера по TCP"""
    host, port = address.split(":")
    port = int(port)
    for _ in range(retries):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            time.sleep(0.2)
    return False


def check_http(address: str, timeout: float, retries: int) -> bool:
    """Проверка доступности сервера по HTTP (GET /)"""
    host, port = address.split(":")
    port = int(port)
    for _ in range(retries):
        try:
            conn = http.client.HTTPConnection(host, port, timeout=timeout)
            conn.request("GET", "/")
            resp = conn.getresponse()
            healthy = resp.status < 500
            conn.close()
            if healthy:
                return True
        except Exception:
            time.sleep(0.2)
            continue
    return False


def check_upstreams(upstreams: Dict[str, List[str]], timeout=2.0, retries=1, mode="tcp") -> Dict[str, List[dict]]:
    """
    Проверяет доступность upstream-серверов.
    mode: "tcp" (по умолчанию) или "http"
    Возвращает:
    {
        "backend": [
            {"address": "127.0.0.1:8080", "healthy": True},
            ...
        ]
    }
    """
    results = {}
    for name, servers in upstreams.items():
        results[name] = []
        for srv in servers:
            if mode.lower() == "http":
                healthy = check_http(srv, timeout, retries)
            else:
                healthy = check_tcp(srv, timeout, retries)
            results[name].append({"address": srv, "healthy": healthy})
    return results
