import shlex
from typing import TextIO

import pytest
import requests

from localcurl.cli import _SID_COOKIE_NAME, _is_binary_response, _main_impl


def generate_test_parameters(localaddr: str, curl_command: str):
    """
    Generate test parameters for the main function, accounting for the 3 different ways
    the curl command can be passed to the program:
    - From the command line
    - From stdin
    - From the clipboard
    """
    return (
        pytest.param(
            localaddr,
            shlex.split(curl_command),  # curl command split into arguments
            "",  # stdin content
            "",  # clipboard content
            id="curl_from_command_line",
        ),
        pytest.param(
            localaddr,
            None,
            curl_command,
            "",
            id="curl_from_stdin",
        ),
        pytest.param(
            localaddr,
            None,
            "",
            curl_command,
            id="curl_from_clipboard",
        ),
    )


@pytest.mark.parametrize(
    ["local_addr", "curl_command", "stdin_value", "clipboard_value"],
    generate_test_parameters(
        localaddr="http://localhost:8080/", curl_command="curl https://example.com"
    ),
)
def test_get_url(local_addr, curl_command, stdin_value, clipboard_value, fake_session):
    """Test the CLI interface for a simple GET request."""
    _main_impl(
        local_addr=local_addr,
        curl_command=curl_command,
        stdin=FakeStdin(stdin_value),
        clipboard=FakeClipboard(clipboard_value),
        session_factory=lambda: fake_session,
    )
    assert fake_session.sent_request.url == "http://localhost:8080/"
    assert fake_session.sent_request.method == "GET"


@pytest.mark.parametrize(
    ["local_addr", "curl_command", "stdin_value", "clipboard_value"],
    generate_test_parameters(
        localaddr="http://localhost:8080/",
        curl_command="curl -b '__Host-foo=abc123' -H 'Cookie: __Host-bar=def456' https://example.com",
    ),
)
def test_strip_host_cookie_prefix_by_default(
    local_addr,
    curl_command,
    stdin_value,
    clipboard_value,
    fake_session,
):
    """Test that __Host- prefix is stripped by default."""
    _main_impl(
        local_addr=local_addr,
        curl_command=curl_command,
        stdin=FakeStdin(stdin_value),
        clipboard=FakeClipboard(clipboard_value),
        session_factory=lambda: fake_session,
    )

    assert fake_session.sent_request.url == "http://localhost:8080/"
    assert "foo" in fake_session.sent_request._cookies
    assert "bar" in fake_session.sent_request._cookies
    assert "__Host-foo" not in fake_session.sent_request._cookies
    assert "__Host-bar" not in fake_session.sent_request._cookies


@pytest.mark.parametrize(
    ["local_addr", "curl_command", "stdin_value", "clipboard_value"],
    generate_test_parameters(
        localaddr="http://localhost:8080/",
        curl_command="curl -b '__Host-foo=abc123' -H 'Cookie: __Host-bar=def456' https://example.com",
    ),
)
def test_keep_host_cookie_prefix(
    local_addr,
    curl_command,
    stdin_value,
    clipboard_value,
    fake_session,
):
    """Test that __Host- prefix is kept when --keep-host-cookie-prefix is passed."""
    _main_impl(
        local_addr=local_addr,
        curl_command=curl_command,
        keep_host_cookie_prefix=True,
        stdin=FakeStdin(stdin_value),
        clipboard=FakeClipboard(clipboard_value),
        session_factory=lambda: fake_session,
    )

    assert fake_session.sent_request.url == "http://localhost:8080/"
    assert "__Host-foo" in fake_session.sent_request._cookies
    assert "__Host-bar" in fake_session.sent_request._cookies


def test_handle_lines_curl_args_line_breaks_from_stdin(fake_session):
    """Test that the main function handles curl arguments with line breaks from stdin."""
    curl_command_with_line_breaks = r"""curl \
  -H 'Content-Type: application/json' \
  -d '{"key": "value"}' \
  https://example.com"""

    _main_impl(
        local_addr="http://localhost:8080/",
        curl_command=None,
        stdin=FakeStdin(curl_command_with_line_breaks),
        clipboard=FakeClipboard(),
        session_factory=lambda: fake_session,
    )

    assert fake_session.sent_request.url == "http://localhost:8080/"


def test_handle_lines_curl_args_line_breaks_from_clipboard(fake_session):
    """Test that the main function handles curl arguments with line breaks from clipboard."""
    curl_command_with_line_breaks = r"""curl \
  -H 'Content-Type: application/json' \
  -d '{"key": "value"}' \
  https://example.com"""

    _main_impl(
        local_addr="http://localhost:8080/",
        curl_command=None,
        stdin=FakeStdin(),
        clipboard=FakeClipboard(curl_command_with_line_breaks),
        session_factory=lambda: fake_session,
    )

    assert fake_session.sent_request.url == "http://localhost:8080/"


def test_no_verify_option(fake_session):
    """Test that no_verify option works correctly."""
    _main_impl(
        local_addr="http://localhost:8080/",
        curl_command=["curl", "https://example.com"],
        no_verify=True,
        keep_host_cookie_prefix=False,
        stdin=FakeStdin(),
        clipboard=FakeClipboard(),
        session_factory=lambda: fake_session,
    )

    assert fake_session.sent_request.url == "http://localhost:8080/"
    assert fake_session.verify is False


def test_cookie_option(fake_session):
    """Test that cookies passed as options are included in the request."""
    _main_impl(
        local_addr="http://localhost:8080/",
        curl_command=["curl", "https://example.com"],
        extra_cookies=["session=abc123", "user=john"],
        keep_host_cookie_prefix=False,
        stdin=FakeStdin(),
        clipboard=FakeClipboard(),
        session_factory=lambda: fake_session,
    )

    assert fake_session.sent_request.url == "http://localhost:8080/"
    assert fake_session.sent_request._cookies.get("session") == "abc123"
    assert fake_session.sent_request._cookies.get("user") == "john"


def test_session_id_option(fake_session):
    """Test that a sessionid cookie passed as option is included in the request."""
    _main_impl(
        local_addr="http://localhost:8080/",
        curl_command=["curl", "https://example.com"],
        session_id="abc123",
        keep_host_cookie_prefix=False,
        stdin=FakeStdin(),
        clipboard=FakeClipboard(),
        session_factory=lambda: fake_session,
    )

    assert fake_session.sent_request.url == "http://localhost:8080/"
    assert fake_session.sent_request._cookies.get(_SID_COOKIE_NAME) == "abc123"


def test_header_option(fake_session):
    """Test that headers passed as options are included in the request."""
    _main_impl(
        local_addr="http://localhost:8080/",
        curl_command=["curl", "https://example.com"],
        extra_headers=["X-Test-Header: testvalue", "Authorization: Bearer token123"],
        keep_host_cookie_prefix=False,
        stdin=FakeStdin(),
        clipboard=FakeClipboard(),
        session_factory=lambda: fake_session,
    )

    assert fake_session.sent_request.url == "http://localhost:8080/"
    assert fake_session.sent_request.headers.get("X-Test-Header") == "testvalue"
    assert fake_session.sent_request.headers.get("Authorization") == "Bearer token123"


def test_auth_token_option(fake_session):
    """Test that an auth token passed as option is included in the request headers."""
    _main_impl(
        local_addr="http://localhost:8080/",
        curl_command=["curl", "https://example.com"],
        auth_token="token123",
        keep_host_cookie_prefix=False,
        stdin=FakeStdin(),
        clipboard=FakeClipboard(),
        session_factory=lambda: fake_session,
    )

    assert fake_session.sent_request.url == "http://localhost:8080/"
    assert fake_session.sent_request.headers.get("Authorization") == "Token token123"


def test_different_local_addresses(fake_session):
    """Test that different local addresses work correctly."""
    _main_impl(
        local_addr="http://127.0.0.1:3000",
        curl_command=["curl", "https://api.example.com/v1/data"],
        stdin=FakeStdin(),
        clipboard=FakeClipboard(),
        session_factory=lambda: fake_session,
    )

    assert fake_session.sent_request.url == "http://127.0.0.1:3000/v1/data"


class FakeStdin(TextIO):
    """Mimics sys.stdin for testing purposes."""

    def __init__(self, initial_value: str = ""):
        self._value = initial_value

    def isatty(self) -> bool:
        return self._value == ""

    def read(self, n: int = -1) -> str:
        return self._value


@pytest.mark.parametrize(
    ["content_type", "content", "expected_is_binary", "test_id"],
    [
        # Text content types (should not be binary)
        ("text/html", b"Hello, world!", False, "text_html"),
        ("application/json", b'{"key": "value"}', False, "json"),
        ("application/xml", b'<?xml version="1.0"?><root>test</root>', False, "xml"),
        (
            "application/xhtml+xml",
            b"<!DOCTYPE html><html><body>test</body></html>",
            False,
            "xhtml",
        ),
        ("application/yaml", b"key: value\nlist:\n  - item1\n  - item2", False, "yaml"),
        ("text/plain", b"Plain text content", False, "text_plain"),
        ("application/javascript", b'console.log("hello");', False, "javascript"),
        # Binary content types (should be binary)
        ("image/png", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR", True, "png_image"),
        (
            "application/octet-stream",
            b"\x89\xff\xfe\x00",
            True,
            "octet_stream_invalid_utf8",
        ),
        ("image/jpeg", b"\xff\xd8\xff\xe0", True, "jpeg_image"),
        ("application/pdf", b"%PDF-1.4\x89\xff\xfe\x00", True, "pdf"),
        # Unknown content types with valid UTF-8 (should not be binary)
        ("application/unknown", b"Hello, world!", False, "unknown_type_valid_utf8"),
        (
            "application/mystery",
            b"Valid text content",
            False,
            "mystery_type_valid_utf8",
        ),
        # Unknown content types with invalid UTF-8 (should be binary)
        ("application/unknown", b"\x89\xff\xfe\x00", True, "unknown_type_invalid_utf8"),
        # No content type header with valid UTF-8 (should not be binary)
        ("", b"Hello, world!", False, "no_content_type_valid_utf8"),
        # No content type header with invalid UTF-8 (should be binary)
        ("", b"\x89\xff\xfe\x00", True, "no_content_type_invalid_utf8"),
    ],
)
def test_is_binary_response(content_type, content, expected_is_binary, test_id):
    """Test binary response detection for various content types and content."""
    response = requests.Response()
    response._content = content
    if content_type:
        response.headers["Content-Type"] = content_type

    assert _is_binary_response(response) == expected_is_binary


def test_binary_response_output(capfdbinary, fake_session):
    """Test that binary responses are handled without errors."""
    binary_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    fake_session = FakeSessionFactory(
        response_content=binary_content, response_headers={"Content-Type": "image/png"}
    )

    _main_impl(
        local_addr="http://localhost:8080/",
        curl_command=["curl", "https://example.com"],
        no_verify=False,
        keep_host_cookie_prefix=False,
        stdin=FakeStdin(),
        clipboard=FakeClipboard(),
        session_factory=lambda: fake_session,
    )

    assert capfdbinary.readouterr().out == binary_content


def test_text_response_output(capsys, fake_session):
    """Test that text responses are printed normally."""
    text_content = b"Hello, world!"
    fake_session = FakeSessionFactory(
        response_content=text_content, response_headers={"Content-Type": "text/plain"}
    )

    _main_impl(
        local_addr="http://localhost:8080/",
        curl_command=["curl", "https://example.com"],
        no_verify=False,
        keep_host_cookie_prefix=False,
        stdin=FakeStdin(),
        clipboard=FakeClipboard(),
        session_factory=lambda: fake_session,
    )

    captured = capsys.readouterr()
    assert captured.out == "Hello, world!"
    assert captured.err == ""


class FakeClipboard:
    """Mimics the pyperclip.paste function for testing purposes."""

    def __init__(self, initial_value: str = ""):
        self._value = initial_value

    def paste(self):
        return self._value


class FakeSessionFactory:
    """Mimics the minimal required portion of the  requests.Session interface for
    testing purposes (and it stores the last request sent through it).
    """

    verify = None

    def __init__(self, response_content=None, response_headers=None):
        self.sent_request: requests.Request = requests.Request()
        self._response_content = response_content or b"fake response"
        self._response_headers = response_headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def send(self, request: requests.Request) -> requests.Response:
        self.sent_request = request
        response = requests.Response()
        response._content = self._response_content
        response.headers.update(self._response_headers)
        response.status_code = 200
        return response


@pytest.fixture
def fake_session():
    return FakeSessionFactory()
