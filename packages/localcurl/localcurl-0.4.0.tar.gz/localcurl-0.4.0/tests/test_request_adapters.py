import pytest
import requests

from localcurl.request_adapters import (
    replace_url_address,
    replace_header_addresses,
    strip_host_cookie_prefix,
    _replace_address,
)


class TestReplaceAddress:
    """Test the _replace_address helper function."""

    @pytest.mark.parametrize(
        "original_url, local_addr, expected",
        [
            # Basic case
            (
                "https://api.github.com/repos/user/repo",
                "http://localhost:8080",
                "http://localhost:8080/repos/user/repo",
            ),
            # URL with query parameters
            (
                "https://api.github.com/search?q=test",
                "http://localhost:8080",
                "http://localhost:8080/search?q=test",
            ),
            # URL with fragment
            (
                "https://api.github.com/docs#section1",
                "http://localhost:8080",
                "http://localhost:8080/docs#section1",
            ),
            # URL with port
            (
                "https://api.github.com:443/v1/data",
                "http://localhost:8080",
                "http://localhost:8080/v1/data",
            ),
            # URL with query and fragment
            (
                "https://example.com/api?param=value#anchor",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3000/api?param=value#anchor",
            ),
            # Different scheme replacement
            (
                "http://example.com/path",
                "https://localhost:8443",
                "https://localhost:8443/path",
            ),
            # Root path
            (
                "https://example.com/",
                "http://localhost:8080",
                "http://localhost:8080/",
            ),
            # No path
            (
                "https://example.com",
                "http://localhost:8080",
                "http://localhost:8080",
            ),
        ],
    )
    def test_replace_address(self, original_url, local_addr, expected):
        """Test that only the address part is replaced in the URL."""
        assert _replace_address(original_url, local_addr) == expected


class TestReplaceUrlAddress:
    """Test the replace_url_address function."""

    def test_replace_url_address(self):
        """Test that request URL is modified in place."""
        request = requests.Request(
            method="GET",
            url="https://api.example.com/v1/users",
        )

        replace_url_address(request, "http://localhost:8080")

        assert request.url == "http://localhost:8080/v1/users"

    def test_replace_url_address_with_query_params(self):
        """Test URL replacement preserves query parameters."""
        request = requests.Request(
            method="POST",
            url="https://api.example.com/search?q=test&limit=10",
        )

        replace_url_address(request, "http://localhost:3000")

        assert request.url == "http://localhost:3000/search?q=test&limit=10"


class TestReplaceHeaderAddresses:
    """Test the replace_header_addresses function."""

    def test_replace_origin_header(self):
        """Test that Origin header is replaced when present."""
        request = requests.Request(
            method="POST",
            url="https://api.example.com/data",
            headers={"Origin": "https://app.example.com"},
        )

        replace_header_addresses(request, "http://localhost:8080")

        assert request.headers["Origin"] == "http://localhost:8080"

    def test_replace_referer_header(self):
        """Test that Referer header is replaced when present."""
        request = requests.Request(
            method="GET",
            url="https://api.example.com/data",
            headers={"Referer": "https://app.example.com/page"},
        )

        replace_header_addresses(request, "http://localhost:8080")

        assert request.headers["Referer"] == "http://localhost:8080/page"

    def test_replace_both_headers(self):
        """Test that both Origin and Referer headers are replaced when present."""
        request = requests.Request(
            method="POST",
            url="https://api.example.com/data",
            headers={
                "Origin": "https://app.example.com",
                "Referer": "https://app.example.com/login",
                "Content-Type": "application/json",
            },
        )

        replace_header_addresses(request, "http://localhost:8080")

        assert request.headers["Origin"] == "http://localhost:8080"
        assert request.headers["Referer"] == "http://localhost:8080/login"
        assert request.headers["Content-Type"] == "application/json"  # Unchanged

    def test_no_headers_to_replace(self):
        """Test that function works when no Origin/Referer headers are present."""
        request = requests.Request(
            method="GET",
            url="https://api.example.com/data",
            headers={"Content-Type": "application/json"},
        )

        replace_header_addresses(request, "http://localhost:8080")

        assert "Origin" not in request.headers
        assert "Referer" not in request.headers
        assert request.headers["Content-Type"] == "application/json"

    def test_empty_headers(self):
        """Test that function works with empty headers dict."""
        request = requests.Request(
            method="GET",
            url="https://api.example.com/data",
            headers={},
        )

        replace_header_addresses(request, "http://localhost:8080")

        assert len(request.headers) == 0


class TestStripHostCookiePrefix:
    """Test the strip_host_cookie_prefix function."""

    def test_strip_host_prefix_from_cookies(self):
        """Test that __Host- prefix is stripped from cookie names."""
        request = requests.Request(
            method="GET",
            url="https://example.com",
            cookies={
                "__Host-session": "abc123",
                "__Host-csrf": "def456",
                "regular_cookie": "value",
            },
        )

        strip_host_cookie_prefix(request)

        expected_cookies = {
            "session": "abc123",
            "csrf": "def456",
            "regular_cookie": "value",
        }
        assert dict(request.cookies) == expected_cookies

    def test_strip_mixed_cookies(self):
        """Test stripping when some cookies have prefix and others don't."""
        request = requests.Request(
            method="GET",
            url="https://example.com",
            cookies={
                "__Host-auth": "token123",
                "preferences": "dark_mode",
                "__Host-user_id": "user456",
                "analytics": "enabled",
            },
        )

        strip_host_cookie_prefix(request)

        expected_cookies = {
            "auth": "token123",
            "preferences": "dark_mode",
            "user_id": "user456",
            "analytics": "enabled",
        }
        assert dict(request.cookies) == expected_cookies

    def test_no_host_prefix_cookies(self):
        """Test that regular cookies without prefix are unchanged."""
        request = requests.Request(
            method="GET",
            url="https://example.com",
            cookies={
                "session": "abc123",
                "user_pref": "value",
                "cart": "item1,item2",
            },
        )

        original_cookies = dict(request.cookies)
        strip_host_cookie_prefix(request)

        assert dict(request.cookies) == original_cookies

    def test_empty_cookies(self):
        """Test that function works with no cookies."""
        request = requests.Request(
            method="GET",
            url="https://example.com",
            cookies={},
        )

        strip_host_cookie_prefix(request)

        assert len(request.cookies) == 0

    def test_only_host_prefix_cookies(self):
        """Test when all cookies have __Host- prefix."""
        request = requests.Request(
            method="GET",
            url="https://example.com",
            cookies={
                "__Host-session": "abc123",
                "__Host-csrf": "def456",
                "__Host-auth": "token789",
            },
        )

        strip_host_cookie_prefix(request)

        expected_cookies = {
            "session": "abc123",
            "csrf": "def456",
            "auth": "token789",
        }
        assert dict(request.cookies) == expected_cookies

    def test_preserve_cookie_values(self):
        """Test that cookie values are preserved exactly."""
        request = requests.Request(
            method="GET",
            url="https://example.com",
            cookies={
                "__Host-complex": "value=with=equals&and&ampersands",
                "__Host-empty": "",
                "__Host-special": "!@#$%^&*()_+-=[]{}|;:,.<>?",
            },
        )

        strip_host_cookie_prefix(request)

        expected_cookies = {
            "complex": "value=with=equals&and&ampersands",
            "empty": "",
            "special": "!@#$%^&*()_+-=[]{}|;:,.<>?",
        }
        assert dict(request.cookies) == expected_cookies
