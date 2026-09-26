"""Single chokepoint for every outbound HTTP request the app makes.

Every fetch of a user- or remote-page-supplied URL must go through
safe_get() instead of calling requests.get() directly, so the SSRF
checks below can't be bypassed by adding a new caller later.
"""

import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests

ALLOWED_SCHEMES = {"http", "https"}
MAX_REDIRECTS = 5


class UnsafeURLError(Exception):
    """Raised when a URL points at a disallowed scheme or destination."""


def _is_public_ip(ip_str):
    ip = ipaddress.ip_address(ip_str)
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def assert_safe_url(url):
    """Raise UnsafeURLError unless url is http(s) and resolves only to public IPs."""
    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise UnsafeURLError(f"Scheme '{parsed.scheme}' is not allowed")

    hostname = parsed.hostname
    if not hostname:
        raise UnsafeURLError("URL has no hostname")

    try:
        addr_infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise UnsafeURLError(f"Could not resolve host '{hostname}'")

    for *_, sockaddr in addr_infos:
        ip_str = sockaddr[0]
        if not _is_public_ip(ip_str):
            raise UnsafeURLError(
                f"Host '{hostname}' resolves to non-public address {ip_str}"
            )


def safe_get(url, **kwargs):
    """A drop-in replacement for requests.get() that blocks SSRF.

    Validates the URL, then follows redirects manually (re-validating
    each hop) instead of letting requests follow them automatically and
    unchecked.
    """
    kwargs.setdefault("timeout", 10)
    kwargs["allow_redirects"] = False

    current_url = url
    for _ in range(MAX_REDIRECTS):
        assert_safe_url(current_url)
        response = requests.get(current_url, **kwargs)

        if response.is_redirect or response.is_permanent_redirect:
            location = response.headers.get("Location")
            if not location:
                return response
            current_url = urljoin(current_url, location)
            continue

        return response

    raise UnsafeURLError("Too many redirects")
