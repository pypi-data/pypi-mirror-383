"""Tests for url_model.py - ValidationMode, validators, and URL validation logic."""

import pytest
from pydantic import ValidationError

from path_link.url_model import (
    ValidationMode,
    LenientUrlModel,
    StrictUrlModel,
    validate_url,
)


class TestValidationMode:
    """Tests for the ValidationMode enum."""

    def test_lenient_mode_value(self):
        """Test that lenient mode has expected value."""
        assert ValidationMode.LENIENT.value == "lenient"

    def test_strict_mode_value(self):
        """Test that strict mode has expected value."""
        assert ValidationMode.STRICT.value == "strict"

    def test_lenient_from_string(self):
        """Test creating ValidationMode from string."""
        mode = ValidationMode("lenient")
        assert mode == ValidationMode.LENIENT

    def test_strict_from_string(self):
        """Test creating ValidationMode from string."""
        mode = ValidationMode("strict")
        assert mode == ValidationMode.STRICT


class TestLenientUrlModel:
    """Tests for LenientUrlModel - should accept localhost, private IPs, custom ports."""

    # Valid URLs in lenient mode
    @pytest.mark.parametrize(
        "url",
        [
            "http://localhost",
            "http://localhost:8000",
            "http://localhost:3000/api/v1",
            "http://127.0.0.1",
            "http://127.0.0.1:8080",
            "http://192.168.1.1",
            "http://192.168.1.100:5000",
            "http://10.0.0.1",
            "http://10.0.0.1:9090",
            "http://172.16.0.1",
            "http://172.31.255.255:8888",
            "https://example.com",
            "https://example.com/path/to/resource",
            "http://example.com:8080/api",
            "ftp://ftp.example.com",
            "ws://localhost:3000",
            "wss://example.com:8080",
        ],
    )
    def test_accepts_valid_urls(self, url):
        """Test lenient mode accepts localhost, private IPs, custom ports."""
        model = LenientUrlModel(url=url)
        # URL might be normalized (e.g., trailing slash added, default ports removed)
        url_str = str(model.url)
        # Just check that we got a valid URL back (not checking exact match due to normalization)
        assert url_str
        assert "://" in url_str

    # Invalid URLs that should fail even in lenient mode
    @pytest.mark.parametrize(
        "url",
        [
            "not-a-url",
            "http://",  # Missing host
            "://example.com",  # Missing scheme
            "http://example.com:not-a-port",  # Bad port
            "http://example.com:99999",  # Port out of range
            "",  # Empty string
            "   ",  # Whitespace only
        ],
    )
    def test_rejects_invalid_urls(self, url):
        """Test lenient mode rejects malformed URLs."""
        with pytest.raises(ValidationError):
            LenientUrlModel(url=url)


class TestStrictUrlModel:
    """Tests for StrictUrlModel - should only accept HTTP/HTTPS, reject localhost."""

    # Valid URLs in strict mode
    @pytest.mark.parametrize(
        "url",
        [
            "http://example.com",
            "https://example.com",
            "http://api.example.com",
            "https://api.example.com",
            "https://example.com:443",
            "http://example.com:80",
            "https://example.com/path/to/resource",
            "http://subdomain.example.co.uk",
            "https://example.com/api?key=value",
        ],
    )
    def test_accepts_valid_http_urls(self, url):
        """Test strict mode accepts RFC-compliant HTTP(S) URLs."""
        model = StrictUrlModel(url=url)
        assert str(model.url).startswith("http")

    # Invalid URLs in strict mode (localhost, private IPs, non-HTTP schemes)
    @pytest.mark.parametrize(
        "url",
        [
            "http://localhost",
            "http://localhost:8000",
            "http://127.0.0.1",
            "http://127.0.0.1:8080",
            "http://192.168.1.1",
            "http://10.0.0.1",
            "http://172.16.0.1",
            "ftp://ftp.example.com",
            "ws://example.com",
            "wss://example.com",
            "file:///etc/passwd",
        ],
    )
    def test_rejects_localhost_and_private_ips(self, url):
        """Test strict mode rejects localhost, private IPs, and non-HTTP schemes."""
        with pytest.raises(ValidationError):
            StrictUrlModel(url=url)

    # Malformed URLs
    @pytest.mark.parametrize(
        "url",
        [
            "not-a-url",
            "http://",
            "://example.com",
            "http://example.com:not-a-port",
            "http://example.com:99999",
            "",
        ],
    )
    def test_rejects_malformed_urls(self, url):
        """Test strict mode rejects malformed URLs."""
        with pytest.raises(ValidationError):
            StrictUrlModel(url=url)


class TestValidateUrlFunction:
    """Tests for the validate_url() function."""

    def test_validate_lenient_localhost(self):
        """Test validate_url accepts localhost in lenient mode."""
        result = validate_url("http://localhost:8000", ValidationMode.LENIENT)
        assert "localhost" in result
        assert "8000" in result

    def test_validate_lenient_private_ip(self):
        """Test validate_url accepts private IP in lenient mode."""
        result = validate_url("http://192.168.1.1:5000", ValidationMode.LENIENT)
        assert "192.168.1.1" in result

    def test_validate_strict_public_url(self):
        """Test validate_url accepts public URL in strict mode."""
        result = validate_url("https://example.com/api", ValidationMode.STRICT)
        assert "example.com" in result

    def test_validate_strict_rejects_localhost(self):
        """Test validate_url rejects localhost in strict mode."""
        with pytest.raises(ValidationError):
            validate_url("http://localhost:8000", ValidationMode.STRICT)

    def test_validate_strict_rejects_private_ip(self):
        """Test validate_url rejects private IP in strict mode."""
        with pytest.raises(ValidationError):
            validate_url("http://192.168.1.1", ValidationMode.STRICT)

    def test_validate_malformed_url_lenient(self):
        """Test validate_url rejects malformed URL even in lenient mode."""
        with pytest.raises(ValidationError):
            validate_url("not-a-url", ValidationMode.LENIENT)

    def test_validate_malformed_url_strict(self):
        """Test validate_url rejects malformed URL in strict mode."""
        with pytest.raises(ValidationError):
            validate_url("htp://example.com", ValidationMode.STRICT)

    def test_validate_default_mode_is_lenient(self):
        """Test validate_url defaults to lenient mode."""
        # Should accept localhost without specifying mode
        result = validate_url("http://localhost:3000")
        assert "localhost" in result

    def test_returns_string(self):
        """Test validate_url returns a string."""
        result = validate_url("https://example.com", ValidationMode.STRICT)
        assert isinstance(result, str)


class TestUnicodeAndEdgeCases:
    """Tests for unicode hosts and edge cases."""

    def test_lenient_unicode_host(self):
        """Test lenient mode with unicode host."""
        # IDN (Internationalized Domain Name)
        url = "http://例え.jp"
        model = LenientUrlModel(url=url)
        assert model.url is not None

    def test_strict_unicode_host(self):
        """Test strict mode with unicode host."""
        url = "https://例え.jp"
        model = StrictUrlModel(url=url)
        assert model.url is not None

    def test_lenient_ipv6_localhost(self):
        """Test lenient mode with IPv6 localhost."""
        url = "http://[::1]:8000"
        model = LenientUrlModel(url=url)
        assert model.url is not None

    def test_url_with_auth(self):
        """Test URL with authentication credentials."""
        url = "https://user:pass@example.com/api"
        model = StrictUrlModel(url=url)
        assert model.url is not None

    def test_url_with_fragment(self):
        """Test URL with fragment identifier."""
        url = "https://example.com/page#section"
        model = StrictUrlModel(url=url)
        assert model.url is not None

    def test_url_with_query_params(self):
        """Test URL with query parameters."""
        url = "https://api.example.com/search?q=test&limit=10"
        model = StrictUrlModel(url=url)
        assert model.url is not None
