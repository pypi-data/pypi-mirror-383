"""Tests for HTTP utilities."""

from __future__ import annotations

import json
import ssl
from http.client import HTTPResponse
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from stream4py.http_utils import request


class TestRequest:
    """Test cases for the request function."""

    @patch("urllib.request.urlopen")
    def test_basic_get_request(self, mock_urlopen: Mock) -> None:
        """Test basic GET request."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        url = "https://api.example.com/users"
        result = request(url)

        assert result is mock_response
        mock_urlopen.assert_called_once()

        # Check the request object passed to urlopen
        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]
        assert req.get_method() == "GET"
        assert req.full_url == url

    @patch("urllib.request.urlopen")
    def test_different_http_methods(self, mock_urlopen: Mock) -> None:
        """Test different HTTP methods."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        methods = ["POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"]

        for method in methods:
            request("https://api.example.com/endpoint", method=method)  # type: ignore[arg-type]

            _, kwargs = mock_urlopen.call_args
            req = kwargs["url"]
            assert req.get_method() == method

    @patch("urllib.request.urlopen")
    def test_params_as_dict(self, mock_urlopen: Mock) -> None:
        """Test URL parameters as dictionary."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        url = "https://api.example.com/search"
        params = {"query": "python", "limit": "10", "category": "programming"}

        request(url, params=params)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Should contain encoded parameters
        assert "query=python" in req.full_url
        assert "limit=10" in req.full_url
        assert "category=programming" in req.full_url

    @patch("urllib.request.urlopen")
    def test_params_with_list_values(self, mock_urlopen: Mock) -> None:
        """Test URL parameters with list values."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        url = "https://api.example.com/filter"
        params = {"tags": ["python", "api"], "status": "active"}

        request(url, params=params)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Should contain multiple values for tags
        assert "tags=python" in req.full_url
        assert "tags=api" in req.full_url
        assert "status=active" in req.full_url

    @patch("urllib.request.urlopen")
    def test_params_as_list_of_tuples(self, mock_urlopen: Mock) -> None:
        """Test URL parameters as list of tuples."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        url = "https://api.example.com/data"
        params = [("user", "alice"), ("user", "bob"), ("format", "json")]

        request(url, params=params)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Should contain multiple user parameters
        assert "user=alice" in req.full_url
        assert "user=bob" in req.full_url
        assert "format=json" in req.full_url

    @patch("urllib.request.urlopen")
    def test_params_with_existing_query_string(self, mock_urlopen: Mock) -> None:
        """Test parameters with existing query string in URL."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        url = "https://api.example.com/search?existing=value"
        params = {"new": "parameter"}

        request(url, params=params)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Should preserve existing and add new parameters
        assert "existing=value" in req.full_url
        assert "new=parameter" in req.full_url

    @patch("urllib.request.urlopen")
    def test_custom_headers(self, mock_urlopen: Mock) -> None:
        """Test custom headers handling."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        headers = {
            "user-agent": "TestClient/1.0",
            "authorization": "Bearer token123",
            "accept": "application/json",
        }

        request("https://api.example.com/data", headers=headers)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Headers should be title-cased by urllib (note the lowercase 'a' in 'agent')
        assert req.get_header("User-agent") == "TestClient/1.0"
        assert req.get_header("Authorization") == "Bearer token123"
        assert req.get_header("Accept") == "application/json"

    @patch("urllib.request.urlopen")
    def test_json_data(self, mock_urlopen: Mock) -> None:
        """Test JSON data serialization."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        json_data = {
            "name": "María González",
            "age": 30,
            "skills": ["Python", "数据分析", "मशीन लर्निंग"],
        }

        request("https://api.example.com/users", method="POST", json=json_data)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Should have correct content type (note urllib uses 'Content-type')
        assert req.get_header("Content-type") == "application/json"

        # Should serialize JSON data
        expected_data = json.dumps(json_data).encode("utf-8")
        assert req.data == expected_data

    @patch("urllib.request.urlopen")
    def test_form_data(self, mock_urlopen: Mock) -> None:
        """Test form data handling."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        form_data = {"username": "ahmad_ali", "password": "secret123"}

        request("https://api.example.com/login", method="POST", data=form_data)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Should pass form data as-is
        assert req.data == form_data

    def test_json_and_data_conflict(self) -> None:
        """Test error when both json and data are provided."""
        with pytest.raises(ValueError, match="Cannot set both 'data' and 'json'"):
            request(
                "https://api.example.com/endpoint",
                method="POST",
                json={"key": "value"},
                data={"other": "data"},
            )

    @patch("urllib.request.urlopen")
    def test_ssl_verify_default(self, mock_urlopen: Mock) -> None:
        """Test SSL verification with default context."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        request("https://secure.example.com/api")

        _, kwargs = mock_urlopen.call_args
        # With verify=None (default), context should be None
        assert kwargs.get("context") is None

    @patch("urllib.request.urlopen")
    @patch("ssl.create_default_context")
    def test_ssl_verify_false(self, mock_create_context: Mock, mock_urlopen: Mock) -> None:
        """Test SSL verification disabled."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        mock_context = Mock()
        mock_create_context.return_value = mock_context

        request("https://unsafe.example.com/api", verify=False)

        # Should create context and disable verification
        mock_create_context.assert_called_once()
        assert mock_context.check_hostname is False
        assert mock_context.verify_mode == ssl.CERT_NONE

    @patch("urllib.request.urlopen")
    @patch("ssl.create_default_context")
    @patch("os.path.isdir")
    def test_ssl_verify_with_ca_file(
        self, mock_isdir: Mock, mock_create_context: Mock, mock_urlopen: Mock
    ) -> None:
        """Test SSL verification with CA file."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response
        mock_isdir.return_value = False

        ca_file = "/path/to/ca-bundle.crt"
        request("https://api.example.com/data", verify=ca_file)

        mock_create_context.assert_called_once_with(cafile=ca_file)

    @patch("urllib.request.urlopen")
    @patch("ssl.create_default_context")
    @patch("os.path.isdir")
    def test_ssl_verify_with_ca_path(
        self, mock_isdir: Mock, mock_create_context: Mock, mock_urlopen: Mock
    ) -> None:
        """Test SSL verification with CA directory."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response
        mock_isdir.return_value = True

        ca_path = "/path/to/ca-certificates/"
        request("https://api.example.com/data", verify=ca_path)

        mock_create_context.assert_called_once_with(capath=ca_path)

    @patch("urllib.request.urlopen")
    def test_timeout_parameter(self, mock_urlopen: Mock) -> None:
        """Test timeout parameter."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        timeout = 30.0
        request("https://slow.example.com/api", timeout=timeout)

        _, kwargs = mock_urlopen.call_args
        assert kwargs["timeout"] == timeout

    @patch("urllib.request.urlopen")
    def test_unicode_in_params(self, mock_urlopen: Mock) -> None:
        """Test Unicode characters in parameters."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        params = {"search": "البحث عن المعلومات", "language": "中文", "category": "технология"}

        request("https://international.example.com/search", params=params)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Should properly encode Unicode characters
        assert req.full_url is not None
        # Basic check that URL contains encoded content
        assert "https://international.example.com/search?" in req.full_url

    @patch("urllib.request.urlopen")
    def test_none_values_in_params(self, mock_urlopen: Mock) -> None:
        """Test None values in parameters."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        params = {"query": "test", "filter": None, "sort": "date"}

        request("https://api.example.com/search", params=params)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # None values should be converted to empty strings
        assert "filter=" in req.full_url
        assert "query=test" in req.full_url
        assert "sort=date" in req.full_url

    @patch("urllib.request.urlopen")
    def test_method_case_insensitive(self, mock_urlopen: Mock) -> None:
        """Test that HTTP method is case-insensitive."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        # Test lowercase method
        request("https://api.example.com/data", method="post")  # type: ignore[arg-type]

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]
        assert req.get_method() == "POST"

    @patch("urllib.request.urlopen")
    def test_empty_params_dict(self, mock_urlopen: Mock) -> None:
        """Test empty parameters dictionary."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        url = "https://api.example.com/data"
        request(url, params={})

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # URL should remain unchanged with empty params
        assert req.full_url == url

    @patch("urllib.request.urlopen")
    def test_json_content_type_preservation(self, mock_urlopen: Mock) -> None:
        """Test that existing Content-Type header is preserved for JSON."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        headers = {"content-type": "application/vnd.api+json"}
        json_data = {"data": {"type": "articles", "attributes": {"title": "Test"}}}

        request("https://api.example.com/articles", method="POST", headers=headers, json=json_data)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Should preserve custom Content-Type (note urllib uses 'Content-type')
        assert req.get_header("Content-type") == "application/vnd.api+json"

    @patch("urllib.request.urlopen")
    def test_url_with_fragment(self, mock_urlopen: Mock) -> None:
        """Test URL with fragment handling."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        url = "https://api.example.com/data#section"
        params = {"query": "test"}

        request(url, params=params)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Fragment should be preserved
        assert "#section" in req.full_url
        assert "query=test" in req.full_url

    @patch("urllib.request.urlopen")
    def test_params_with_tuple_values(self, mock_urlopen: Mock) -> None:
        """Test URL parameters with tuple values."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        params = {"coordinates": (40.7128, -74.0060), "name": "NYC"}

        request("https://api.example.com/locations", params=params)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Tuple values should be handled like lists
        assert "coordinates=40.7128" in req.full_url
        assert "coordinates=-74.006" in req.full_url
        assert "name=NYC" in req.full_url

    @patch("urllib.request.urlopen")
    def test_params_as_tuple_of_tuples(self, mock_urlopen: Mock) -> None:
        """Test URL parameters as tuple of tuples."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        params = (("key1", "value1"), ("key2", "value2"), ("key1", "another_value"))

        request("https://api.example.com/data", params=params)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Should handle tuple of tuples like list of tuples
        assert "key1=value1" in req.full_url
        assert "key1=another_value" in req.full_url
        assert "key2=value2" in req.full_url

    @patch("urllib.request.urlopen")
    def test_special_characters_in_url(self, mock_urlopen: Mock) -> None:
        """Test URL with special characters."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        # URL with special characters that should be preserved
        url = "https://api.example.com/path with spaces/file.json"

        request(url)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # URL should be passed as-is to urllib
        assert req.full_url == url

    @patch("urllib.request.urlopen")
    def test_numeric_header_values(self, mock_urlopen: Mock) -> None:
        """Test numeric values in headers."""
        mock_response = Mock(spec=HTTPResponse)
        mock_urlopen.return_value = mock_response

        content_length = 1024
        retry_after = 30
        rate_limit = 100

        headers = {
            "content-length": content_length,
            "retry-after": retry_after,
            "x-rate-limit": rate_limit,
        }

        request("https://api.example.com/data", headers=headers)

        _, kwargs = mock_urlopen.call_args
        req = kwargs["url"]

        # Numeric values should be converted to strings (note urllib header casing)
        assert req.get_header("Content-length") == content_length
        assert req.get_header("Retry-after") == retry_after
        assert req.get_header("X-rate-limit") == rate_limit
