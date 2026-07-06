"""SSRF / bad-scheme structural check for the fetch_url MCP tool."""

import ipaddress
import socket
import urllib.parse
from typing import Optional

ALLOWED_SCHEMES = {"http", "https"}


def _is_blocked_ip(ip_str: str) -> bool:
    ip = ipaddress.ip_address(ip_str)
    return ip.is_private or ip.is_loopback or ip.is_link_local


def check_url(url: str) -> Optional[str]:
    """Return None if *url* is safe to fetch, else a block reason.

    Resolves the hostname and inspects the resolved IP(s) rather than
    string-matching the hostname, so DNS rebinding / decimal-IP encodings /
    "localhost" aliases are all caught the same way.
    """
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        return "bad_scheme"

    hostname = parsed.hostname
    if not hostname:
        return "bad_scheme"

    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        # Unresolvable host: fail closed.
        return "ssrf_blocked"

    for family, _type, _proto, _canonname, sockaddr in infos:
        ip_str = sockaddr[0]
        if _is_blocked_ip(ip_str):
            return "ssrf_blocked"

    return None
