from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

import requests


def preserve_original_host_as_headers(request: requests.Request) -> None:
    """Preserve the original Host from the requested URL by copying it to
    Host/X-Forwarded-Host headers if not already set.
    """
    _, original_host, *_ = urlsplit(request.url)
    request.headers.setdefault("Host", original_host)
    request.headers.setdefault("X-Forwarded-Host", original_host)


def replace_url_address(request: requests.Request, local_addr: str) -> None:
    """Replace the scheme, host and port in the request URL with the local address ones."""
    request.url = _replace_address(request.url, local_addr)


def replace_header_addresses(request: requests.Request, local_addr: str) -> None:
    """Replace the original address in Origin and Referer headers with the local address."""
    if "Origin" in request.headers:
        request.headers["Origin"] = _replace_address(
            request.headers["Origin"], local_addr
        )
    if "Referer" in request.headers:
        request.headers["Referer"] = _replace_address(
            request.headers["Referer"], local_addr
        )


def strip_host_cookie_prefix(request: requests.Request) -> None:
    """Strip the __Host- prefix from all cookies in the request."""
    request.cookies = {
        k[len("__Host-") :] if k.startswith("__Host-") else k: v
        for k, v in request.cookies.items()
    }


def _replace_address(url: str, local_addr: str) -> str:
    """Replace the scheme, host and port in the URL with the local address ones."""
    original_parts = urlsplit(url)
    replacement_parts = urlsplit(local_addr)
    new_parts = (
        replacement_parts.scheme,
        replacement_parts.netloc,
        original_parts.path,
        original_parts.query,
        original_parts.fragment,
    )

    return urlunsplit(new_parts)
