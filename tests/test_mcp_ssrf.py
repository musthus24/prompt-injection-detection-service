import socket

import pytest

from app.mcp import ssrf


def _mock_getaddrinfo(ip):
    def _fake(host, port):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))]

    return _fake


def test_bad_scheme_blocked():
    assert ssrf.check_url("ftp://example.com") == "bad_scheme"


def test_public_host_allowed(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _mock_getaddrinfo("8.8.8.8"))
    assert ssrf.check_url("https://example.com") is None


@pytest.mark.parametrize(
    "ip",
    ["127.0.0.1", "10.0.0.5", "172.16.0.1", "192.168.1.1", "169.254.169.254"],
)
def test_private_loopback_link_local_blocked(monkeypatch, ip):
    monkeypatch.setattr(socket, "getaddrinfo", _mock_getaddrinfo(ip))
    assert ssrf.check_url("http://internal.example") == "ssrf_blocked"


def test_ipv6_loopback_blocked(monkeypatch):
    def _fake(host, port):
        return [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("::1", 0, 0, 0))]

    monkeypatch.setattr(socket, "getaddrinfo", _fake)
    assert ssrf.check_url("http://internal.example") == "ssrf_blocked"


def test_unresolvable_host_fails_closed(monkeypatch):
    def _fake(host, port):
        raise socket.gaierror("unresolvable")

    monkeypatch.setattr(socket, "getaddrinfo", _fake)
    assert ssrf.check_url("http://does-not-resolve.invalid") == "ssrf_blocked"
