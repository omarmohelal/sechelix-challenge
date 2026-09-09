"""Import a user avatar from a URL they supply."""

import ipaddress
import socket
import urllib.parse
import urllib.request

MAX_BYTES = 2 * 1024 * 1024
ALLOWED_SCHEMES = {"https"}


def _is_public(host: str) -> bool:
    try:
        for family, _, _, _, sockaddr in socket.getaddrinfo(host, None):
            address = ipaddress.ip_address(sockaddr[0])
            if address.is_private or address.is_loopback or address.is_link_local:
                return False
    except socket.gaierror:
        return False
    return True


def validate(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError("only https is allowed")
    if not parsed.hostname:
        raise ValueError("missing host")
    if not _is_public(parsed.hostname):
        raise ValueError("destination is not a public address")
    return url


def import_avatar(url: str) -> bytes:
    """Fetch the image the user pointed us at."""
    safe_url = validate(url)
    with urllib.request.urlopen(safe_url, timeout=5) as response:
        if response.headers.get("Content-Type", "").split(";")[0] not in (
            "image/png", "image/jpeg", "image/webp",
        ):
            raise ValueError("not an image")
        return response.read(MAX_BYTES)
