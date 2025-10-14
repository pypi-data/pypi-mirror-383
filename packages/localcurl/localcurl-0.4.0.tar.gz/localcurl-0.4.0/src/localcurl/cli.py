from __future__ import annotations

import os
import shlex
import sys
from typing import Any, Callable, Optional, Protocol, TextIO

import pyperclip
import requests
import typer
from requests.models import PreparedRequest, Response

from . import parsers, request_adapters

_SID_COOKIE_NAME = os.environ.get("LC_SID_COOKIE_NAME", "sessionid")
_AUTH_TOKEN_HEADER = os.environ.get("LC_AUTH_TOKEN_HEADER", "Authorization: Token")


class ClipboardInterface(Protocol):
    @staticmethod
    def paste() -> str: ...


class SessionLike(Protocol):
    verify: bool | str | None

    def __enter__(self) -> SessionLike: ...
    def __exit__(self, *args: Any) -> None: ...
    def send(self, request: PreparedRequest) -> Response: ...


def validate_cookie_format(value: str) -> str:
    """Validate that cookie follows cookie_name=value format (`=` is allowed in value
    but not in name).
    """
    try:
        _, _ = value.split("=", 1)
    except ValueError:
        raise typer.BadParameter(
            f"Cookie must be in 'cookie_name=value' format, got: {value}"
        )
    return value


def validate_header_format(value: str) -> str:
    """Validate that header follows Header-Name: value format (`:` is allowed in value
    but not in name).
    """
    try:
        _, _ = value.split(":", 1)
    except ValueError:
        raise typer.BadParameter(
            f"Header must be in 'Header-Name: value' format, got: {value}"
        )
    return value


app = typer.Typer(help="Replay remote curl requests locally")


@app.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True}
)
def main_cli(
    local_addr: str = typer.Argument(
        ...,
        metavar="addrport",
        help="The local address to send the request, e.g. http://localhost:8080",
    ),
    curl_command: list[str] = typer.Argument(
        None,
        # nargs=-1,
        help="The curl command to parse (reads from stdin if not provided)",
    ),
    no_verify: bool = typer.Option(
        False, "--no-verify", help="Disable SSL certificate verification"
    ),
    keep_host_cookie_prefix: bool = typer.Option(
        False,
        "--keep-host-cookie-prefix",
        help="Prevent stripping __Host- prefix from cookies",
    ),
    extra_cookies: Optional[list[str]] = typer.Option(
        None,
        "--cookie",
        callback=(
            lambda ctx, param, value: [validate_cookie_format(v) for v in value]
            if value
            else None
        ),
        help="Add a cookie in cookie_name=value format (can be repeated). It overrides any existing cookie with the same name.",
    ),
    extra_headers: Optional[list[str]] = typer.Option(
        None,
        "--header",
        callback=(
            lambda ctx, param, value: [validate_header_format(v) for v in value]
            if value
            else None
        ),
        help="Add a header to the request in Header-Name: value format (can be repeated). It overrides any existing header with the same name.",
    ),
    session_id: Optional[str] = typer.Option(
        None,
        "--sid",
        help="Add a sessionid cookie (shorthand for --cookie sessionid=...)",
    ),
    auth_token: Optional[str] = typer.Option(
        None,
        "--auth-token",
        help="Add an authentication token (shorthand for --header 'Authorization: Token ...')",
    ),
) -> None:
    return _main_impl(
        local_addr=local_addr,
        curl_command=curl_command,
        stdin=sys.stdin,
        clipboard=pyperclip,
        session_factory=requests.Session,
        no_verify=no_verify,
        keep_host_cookie_prefix=keep_host_cookie_prefix,
        extra_cookies=extra_cookies,
        extra_headers=extra_headers,
        session_id=session_id,
        auth_token=auth_token,
    )


def _main_impl(
    local_addr: str,
    curl_command: Optional[list[str]],
    stdin: TextIO,
    clipboard: ClipboardInterface,
    session_factory: Callable[[], SessionLike],
    no_verify: bool = False,
    keep_host_cookie_prefix: bool = False,
    extra_cookies: Optional[list[str]] = None,
    extra_headers: Optional[list[str]] = None,
    session_id: Optional[str] = None,
    auth_token: Optional[str] = None,
) -> None:
    if curl_command:
        curl_command_str = shlex.join(curl_command)
    else:
        # No curl command was provided as arguments, try to read from stdin or the
        # clipboard.
        curl_command_str = clipboard.paste() if stdin.isatty() else stdin.read()

    # If the curl command has was split across multiple lines (with trailing
    # backslashes) it ends having "\\\n" characters in it that would cause the curl
    # command parser to fail. We need to remove them.
    curl_command_str = curl_command_str.replace("\\\n", "")
    curl_command_str = curl_command_str.replace("\\\r\n", "")

    try:
        request = parsers.curl_to_request(curl_command_str)
    except parsers.CurlParsingError as e:
        typer.echo(f"Unrecognized curl command: {e}", err=True)
        raise typer.Exit(1)

    # Transform the request to use the local address
    request_adapters.preserve_original_host_as_headers(request)
    request_adapters.replace_url_address(request, local_addr)
    request_adapters.replace_header_addresses(request, local_addr)

    # Strip the __Host- prefix from cookies unless instructed otherwise.
    if not keep_host_cookie_prefix:
        request_adapters.strip_host_cookie_prefix(request)

    # Add a sessionid cookie if provided
    if session_id is not None:
        request.cookies[_SID_COOKIE_NAME] = session_id

    # Add an authentication token header if provided
    if auth_token is not None:
        key, prefix = _AUTH_TOKEN_HEADER.split(": ", 1)
        request.headers[key] = f"{prefix} {auth_token}"

    #  Add any extra cookies provided as options
    if extra_cookies:
        request.cookies.update(dict(cookie.split("=", 1) for cookie in extra_cookies))

    # Add any headers provided as options
    if extra_headers:
        request.headers.update(
            {
                key.strip(): value.strip()
                for key, value in (header.split(":", 1) for header in extra_headers)
            }
        )

    with session_factory() as session:
        session.verify = not no_verify
        response = session.send(request.prepare())

    if _is_binary_response(response):
        # For binary data, write directly to stdout buffer without newlines
        sys.stdout.buffer.write(response.content)
        sys.stdout.buffer.flush()
    else:
        sys.stdout.write(response.text)


if __name__ == "__main__":
    app()


_COMMON_TEXT_TYPES = [
    "text/",
    "application/json",
    "application/xml",
    "application/javascript",
    "application/x-javascript",
    "application/ecmascript",
    "application/x-www-form-urlencoded",
    "application/xhtml+xml",
    "application/rss+xml",
    "application/atom+xml",
    "application/soap+xml",
    "application/hal+json",
    "application/ld+json",
    "application/x-yaml",
    "application/yaml",
]


def _is_binary_response(response: Response) -> bool:
    """Determine if a response contains binary data based on Content-Type header."""
    content_type = response.headers.get("Content-Type", "").lower()

    if any(content_type.startswith(text_type) for text_type in _COMMON_TEXT_TYPES):
        return False

    # Try to decode as text as a fallback
    try:
        response.content.decode("utf-8")
        return False
    except UnicodeDecodeError:
        return True
