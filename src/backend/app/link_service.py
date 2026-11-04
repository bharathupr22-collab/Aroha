"""Link extraction and validation with SSRF protection."""
import ipaddress
import re
import socket
from urllib.parse import urlparse

import httpx

URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)
BARE_DOMAIN_RE = re.compile(r"\b(?:[a-z0-9-]+\.)+(?:com|org|net|io|in|co|shop|store|link|app|me|ly)(?:/[^\s<>\"')\]]*)?", re.I)
TIMEOUT = 8.0


def extract_urls(text: str) -> list[str]:
    found: list[str] = []
    for m in URL_RE.findall(text):
        found.append(m.rstrip(".,;:!?"))
    stripped = URL_RE.sub(" ", text)
    for m in BARE_DOMAIN_RE.findall(stripped):
        if "@" not in m:
            found.append("https://" + m.rstrip(".,;:!?"))
    seen, unique = set(), []
    for u in found:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def is_safe_host(host: str) -> bool:
    """Reject hosts resolving to private, loopback, link-local or reserved addresses."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True


def check_url(url: str) -> tuple[int | None, str, str | None]:
    """Return (status_code, result, issue). result: working|broken|redirect_loop|unsafe|invalid|unreachable."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None, "invalid", "Not a valid http(s) URL"
    if not is_safe_host(parsed.hostname):
        return None, "unreachable", "Host could not be resolved or is not a public address"
    try:
        with httpx.Client(follow_redirects=True, max_redirects=5, timeout=TIMEOUT,
                          headers={"User-Agent": "AROHA-LinkChecker/0.1"}) as client:
            resp = client.head(url)
            if resp.status_code in (403, 405, 501):
                resp = client.get(url)
            for hop in resp.history + [resp]:
                hop_host = urlparse(str(hop.url)).hostname or ""
                if not is_safe_host(hop_host):
                    return None, "unsafe", "Redirected to a non-public address"
            code = resp.status_code
            if code < 400:
                return code, "working", None
            return code, "broken", f"Server returned HTTP {code}"
    except httpx.TooManyRedirects:
        return None, "redirect_loop", "Too many redirects"
    except httpx.TimeoutException:
        return None, "unreachable", "Request timed out"
    except httpx.HTTPError as exc:
        return None, "unreachable", f"Connection failed: {type(exc).__name__}"
