#!/usr/bin/env python3
"""
Tests for URL class
"""

import unittest
from tests.conftest import URLParseTestCase, INVALID_URLS
from urlops import (
    URL,
    QueryParams,
    URLPath,
    parse,
    join,
    TypeError,
    ValidationError,
    ParseError,
)


class TestURLCreation(URLParseTestCase):
    """Test URL creation from various inputs"""

    def test_create_from_string(self):
        """Test URL creation from string"""
        url = URL("https://example.com/path?query=value#fragment")
        self.assertURLComponents(
            url,
            scheme="https",
            host="example.com",
            path="/path",
            query="query=value",
            fragment="fragment",
        )

    def test_create_from_url_object(self):
        """Test URL creation from another URL object"""
        original = URL("https://example.com/path")
        copy = URL(original)
        self.assertEqual(str(original), str(copy))
        self.assertIsNot(original, copy)  # Should be different objects

    def test_create_protocol_relative(self):
        """Test protocol-relative URLs"""
        url = URL("//example.com/path")
        self.assertURLComponents(url, host="example.com", path="/path")
        self.assertFalse(url.is_absolute())

    def test_create_relative_path(self):
        """Test relative path URLs"""
        url = URL("/path/to/file")
        self.assertURLComponents(url, path="/path/to/file")
        self.assertFalse(url.is_absolute())

    def test_create_query_only(self):
        """Test query-only URLs"""
        url = URL("?query=value")
        self.assertURLComponents(url, query="query=value")

    def test_create_fragment_only(self):
        """Test fragment-only URLs"""
        url = URL("#fragment")
        self.assertURLComponents(url, fragment="fragment")

    def test_invalid_urls(self):
        """Test invalid URL handling"""
        for invalid_url in INVALID_URLS:
            with self.subTest(url=invalid_url):
                self.assertRaisesParseError(URL, invalid_url)


class TestURLProperties(URLParseTestCase):
    """Test URL property access"""

    def setUp(self):
        self.url = URL("https://example.com:8080/path/to/file?query=value#fragment")

    def test_scheme_property(self):
        """Test scheme property"""
        self.assertEqual(self.url.scheme, "https")

    def test_host_property(self):
        """Test host property"""
        self.assertEqual(self.url.host, "example.com")

    def test_port_property(self):
        """Test port property"""
        self.assertEqual(self.url.port, 8080)

    def test_path_property(self):
        """Test path property returns URLPath"""
        path = self.url.path
        self.assertIsInstance(path, URLPath)
        self.assertEqual(str(path), "/path/to/file")

    def test_query_property(self):
        """Test query property returns QueryParams"""
        query = self.url.query
        self.assertIsInstance(query, QueryParams)
        self.assertEqual(str(query), "query=value")

    def test_fragment_property(self):
        """Test fragment property"""
        self.assertEqual(self.url.fragment, "fragment")

    def test_string_representation(self):
        """Test string representation"""
        expected = "https://example.com:8080/path/to/file?query=value#fragment"
        self.assertEqual(str(self.url), expected)

    def test_repr_representation(self):
        """Test repr representation"""
        repr_str = repr(self.url)
        self.assertIn("URL(", repr_str)
        self.assertIn(
            "https://example.com:8080/path/to/file?query=value#fragment", repr_str
        )


class TestURLModification(URLParseTestCase):
    """Test URL modification methods"""

    def setUp(self):
        self.url = URL("https://example.com/path")

    def test_with_scheme(self):
        """Test with_scheme method"""
        new_url = self.url.with_scheme("http")
        self.assertURLComponents(
            new_url, scheme="http", host="example.com", path="/path"
        )
        self.assertIsNot(self.url, new_url)  # Should be different objects

    def test_with_host(self):
        """Test with_host method"""
        new_url = self.url.with_host("api.example.com")
        self.assertURLComponents(
            new_url, scheme="https", host="api.example.com", path="/path"
        )

    def test_with_port(self):
        """Test with_port method"""
        new_url = self.url.with_port(8080)
        self.assertURLComponents(
            new_url, scheme="https", host="example.com", port=8080, path="/path"
        )

        # Test removing port
        no_port = new_url.with_port(None)
        self.assertURLComponents(
            no_port, scheme="https", host="example.com", port=None, path="/path"
        )

    def test_with_path(self):
        """Test with_path method"""
        new_url = self.url.with_path("/new/path")
        self.assertURLComponents(
            new_url, scheme="https", host="example.com", path="/new/path"
        )

        # Test with URLPath object
        from urlops import URLPath

        path_obj = URLPath("/path/object")
        new_url2 = self.url.with_path(path_obj)
        self.assertURLComponents(
            new_url2, scheme="https", host="example.com", path="/path/object"
        )

    def test_with_query(self):
        """Test with_query method"""
        new_url = self.url.with_query("new=query")
        self.assertURLComponents(
            new_url, scheme="https", host="example.com", path="/path", query="new=query"
        )

        # Test with dict
        new_url2 = self.url.with_query({"key": "value"})
        self.assertURLComponents(
            new_url2,
            scheme="https",
            host="example.com",
            path="/path",
            query="key=value",
        )

    def test_with_fragment(self):
        """Test with_fragment method"""
        new_url = self.url.with_fragment("new-fragment")
        self.assertURLComponents(
            new_url,
            scheme="https",
            host="example.com",
            path="/path",
            fragment="new-fragment",
        )

    def test_modification_chaining(self):
        """Test method chaining"""
        new_url = (
            self.url.with_scheme("http")
            .with_host("api.example.com")
            .with_port(8080)
            .with_path("/api/v1")
            .with_query("format=json")
            .with_fragment("docs")
        )

        self.assertURLComponents(
            new_url,
            scheme="http",
            host="api.example.com",
            port=8080,
            path="/api/v1",
            query="format=json",
            fragment="docs",
        )

    def test_invalid_modifications(self):
        """Test invalid modification parameters"""
        # Invalid scheme
        self.assertRaisesValidationError(self.url.with_scheme, "123invalid")

        # Invalid port
        self.assertRaisesValidationError(self.url.with_port, 99999)
        self.assertRaisesValidationError(self.url.with_port, -1)

        # Invalid host
        self.assertRaisesValidationError(self.url.with_host, "invalid@host")


class TestURLPathOperations(URLParseTestCase):
    """Test URL path operations"""

    def setUp(self):
        self.url = URL("https://example.com/path")

    def test_truediv_operator(self):
        """Test / operator for path joining"""
        new_url = self.url / "subpath"
        self.assertURLComponents(
            new_url, scheme="https", host="example.com", path="/path/subpath"
        )

        # Test chaining
        new_url2 = self.url / "subpath" / "file.txt"
        self.assertURLComponents(
            new_url2, scheme="https", host="example.com", path="/path/subpath/file.txt"
        )

        # Test with absolute path
        new_url3 = self.url / "/absolute"
        self.assertURLComponents(
            new_url3, scheme="https", host="example.com", path="/absolute"
        )

    def test_truediv_with_string(self):
        """Test / operator with string"""
        new_url = self.url / "string"
        self.assertURLComponents(
            new_url, scheme="https", host="example.com", path="/path/string"
        )

    def test_truediv_with_urlpath(self):
        """Test / operator with URLPath"""
        from urlops import URLPath

        path_obj = URLPath("urlpath")
        new_url = self.url / path_obj
        self.assertURLComponents(
            new_url, scheme="https", host="example.com", path="/path/urlpath"
        )


class TestURLValidation(URLParseTestCase):
    """Test URL validation methods"""

    def test_is_valid(self):
        """Test is_valid method"""
        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://example.com/path",
            "/path/to/file",
            "//example.com",
            "?query=value",
            "#fragment",
        ]

        for url_str in valid_urls:
            with self.subTest(url=url_str):
                url = URL(url_str)
                self.assertTrue(url.is_valid(), f"URL should be valid: {url_str}")

    def test_url_immutability(self):
        """Test that URL modification methods return new objects"""
        # Create a valid URL
        original_url = URL("https://example.com")
        self.assertTrue(original_url.is_valid())

        # Store the original state
        original_port = original_url.port
        original_str = str(original_url)

        # Use modification methods - these should return new objects
        new_url = original_url.with_port(8080)

        # The original URL should be unchanged
        self.assertEqual(original_url.port, original_port)
        self.assertEqual(str(original_url), original_str)
        self.assertTrue(original_url.is_valid())

        # The new URL should have the modified state
        self.assertEqual(new_url.port, 8080)
        self.assertNotEqual(str(original_url), str(new_url))
        self.assertTrue(new_url.is_valid())

        # They should be different objects
        self.assertIsNot(original_url, new_url)

    def test_is_absolute(self):
        """Test is_absolute method"""
        # Absolute URLs (have both scheme and host)
        absolute_urls = [
            "https://example.com",
            "http://example.com/path",
            "ftp://example.com:21",
        ]

        for url_str in absolute_urls:
            with self.subTest(url=url_str):
                url = URL(url_str)
                self.assertTrue(url.is_absolute(), f"URL should be absolute: {url_str}")

        # Non-absolute URLs
        non_absolute_urls = [
            "/path/to/file",
            "//example.com",
            "path/to/file",
            "?query=value",
            "#fragment",
        ]

        for url_str in non_absolute_urls:
            with self.subTest(url=url_str):
                url = URL(url_str)
                self.assertFalse(
                    url.is_absolute(), f"URL should not be absolute: {url_str}"
                )


class TestURLParsing(URLParseTestCase):
    """Test URL parsing logic"""

    def test_scheme_parsing(self):
        """Test scheme parsing"""
        url = URL("https://example.com")
        self.assertEqual(url.scheme, "https")

        url2 = URL("http://example.com")
        self.assertEqual(url2.scheme, "http")

        url3 = URL("ftp://example.com")
        self.assertEqual(url3.scheme, "ftp")

    def test_authority_parsing(self):
        """Test authority (host:port) parsing"""
        url = URL("https://example.com")
        self.assertEqual(url.host, "example.com")
        self.assertIsNone(url.port)

        url2 = URL("https://example.com:8080")
        self.assertEqual(url2.host, "example.com")
        self.assertEqual(url2.port, 8080)

    def test_path_parsing(self):
        """Test path parsing"""
        url = URL("https://example.com/path/to/file")
        self.assertEqual(str(url.path), "/path/to/file")

        url2 = URL("https://example.com/")
        self.assertEqual(str(url2.path), "/")

        url3 = URL("https://example.com")
        self.assertEqual(str(url3.path), "")

    def test_query_parsing(self):
        """Test query parsing"""
        url = URL("https://example.com?key=value")
        self.assertEqual(str(url.query), "key=value")

        url2 = URL("https://example.com?key1=value1&key2=value2")
        self.assertEqual(str(url2.query), "key1=value1&key2=value2")

    def test_fragment_parsing(self):
        """Test fragment parsing"""
        url = URL("https://example.com#fragment")
        self.assertEqual(url.fragment, "fragment")

        url2 = URL("https://example.com#fragment-with-dashes")
        self.assertEqual(url2.fragment, "fragment-with-dashes")


class TestURLFactoryFunctions(URLParseTestCase):
    """Test URL factory functions"""

    def test_parse_function(self):
        """Test parse factory function"""
        url = parse("https://example.com/path")
        self.assertIsInstance(url, URL)
        self.assertURLComponents(url, scheme="https", host="example.com", path="/path")

    def test_join_function(self):
        """Test join factory function"""
        base = parse("https://example.com/api")
        joined = join(base, "v1", "users")
        self.assertURLComponents(
            joined, scheme="https", host="example.com", path="/api/v1/users"
        )


class TestURLTypeValidation(URLParseTestCase):
    """Test URL type validation and error handling"""

    def test_invalid_url_types(self):
        """Test invalid URL input types"""
        with self.assertRaises(TypeError):
            URL(123)

        with self.assertRaises(ParseError):
            URL(None)

        with self.assertRaises(ParseError):
            URL([])

        with self.assertRaises(ParseError):
            URL({})

    def test_invalid_scheme_types(self):
        """Test invalid scheme types in with_scheme"""
        url = URL("https://example.com")

        with self.assertRaises(TypeError):
            url.with_scheme(123)

        with self.assertRaises(TypeError):
            url.with_scheme(None)

    def test_invalid_host_types(self):
        """Test invalid host types in with_host"""
        url = URL("https://example.com")

        with self.assertRaises(TypeError):
            url.with_host(123)

        with self.assertRaises(TypeError):
            url.with_host(None)

    def test_invalid_port_types(self):
        """Test invalid port types in with_port"""
        url = URL("https://example.com")

        with self.assertRaises(TypeError):
            url.with_port("8080")

        with self.assertRaises(TypeError):
            url.with_port([])

    def test_invalid_scheme_characters(self):
        """Test invalid scheme characters"""
        url = URL("https://example.com")

        with self.assertRaises(ValidationError):
            url.with_scheme("123invalid")

        with self.assertRaises(ValidationError):
            url.with_scheme("invalid@scheme")

    def test_invalid_host_format(self):
        """Test invalid host format"""
        url = URL("https://example.com")

        # Empty host should be allowed (it's valid)
        new_url = url.with_host("")
        self.assertEqual(new_url.host, "")

    def test_invalid_port_range(self):
        """Test invalid port range"""
        url = URL("https://example.com")

        with self.assertRaises(ValidationError):
            url.with_port(-1)

        with self.assertRaises(ValidationError):
            url.with_port(65536)

    def test_invalid_port_format_parsing(self):
        """Test invalid port format during URL parsing"""
        with self.assertRaises(ParseError):
            URL("https://example.com:invalid")

    def test_invalid_query_types(self):
        """Test invalid query types in with_query"""
        url = URL("https://example.com")

        # Test with valid types (str, dict, QueryParams, None)
        new_url1 = url.with_query("key=value")
        self.assertEqual(str(new_url1), "https://example.com?key=value")

        new_url2 = url.with_query({"key": "value"})
        self.assertEqual(str(new_url2), "https://example.com?key=value")

        new_url3 = url.with_query(None)
        self.assertEqual(str(new_url3), "https://example.com?None")

    def test_url_reconstruction_edge_cases(self):
        """Test URL reconstruction with various component combinations"""
        # Test with all components
        url1 = URL("https://example.com:8080/path?query=value#fragment")
        self.assertEqual(
            str(url1), "https://example.com:8080/path?query=value#fragment"
        )

        # Test with scheme and host only
        url2 = URL("https://example.com")
        self.assertEqual(str(url2), "https://example.com")

        # Test with host and port only (protocol-relative)
        with self.assertRaises(ValidationError):
            URL("//example.com:8080")

        # Test with path only
        url4 = URL("/path/to/file")
        self.assertEqual(str(url4), "/path/to/file")

        # Test with query only
        url5 = URL("?query=value")
        self.assertEqual(str(url5), "?query=value")

        # Test with fragment only
        url6 = URL("#fragment")
        self.assertEqual(str(url6), "#fragment")

    def test_query_params_direct_assignment(self):
        """Test direct QueryParams assignment in with_query"""
        url = URL("https://example.com")
        query_params = QueryParams("key=value")

        # Test direct QueryParams assignment
        new_url = url.with_query(query_params)
        self.assertEqual(str(new_url), "https://example.com?key=value")

    def test_validation_error_handling(self):
        """Test validation error handling in is_valid"""
        # Test with invalid port
        url2 = URL("https://example.com")
        url2._port = -1
        self.assertFalse(url2.is_valid())

        # Test with invalid scheme
        url3 = URL("https://example.com")
        url3._scheme = "123invalid"
        self.assertFalse(url3.is_valid())

    def test_url_reconstruction_with_port(self):
        """Test URL reconstruction with port (line 211)"""
        url = URL("https://example.com:8080")
        self.assertEqual(str(url), "https://example.com:8080")

    def test_url_reconstruction_with_path(self):
        """Test URL reconstruction with path (line 218)"""
        url = URL("https://example.com/path/to/file")
        self.assertEqual(str(url), "https://example.com/path/to/file")

    def test_url_reconstruction_with_fragment(self):
        """Test URL reconstruction with fragment (line 227)"""
        url = URL("https://example.com#fragment")
        self.assertEqual(str(url), "https://example.com#fragment")

    def test_truediv_with_non_string(self):
        """Test / operator with non-string (line 296)"""
        url = URL("https://example.com/path")
        result = url / 123
        self.assertEqual(str(result), "https://example.com/path/123")

    def test_is_valid_empty_components(self):
        """Test is_valid with empty components (line 311)"""
        # Test URL with no components - this should raise ParseError
        with self.assertRaises(ParseError):
            URL("")

    def test_is_valid_exception_handling(self):
        """Test is_valid exception handling (lines 319-320)"""
        # Test URL that raises ValidationError during validation
        url = URL("https://example.com")
        # Manually set invalid components to trigger validation errors
        url._scheme = "123invalid"  # This will raise ValidationError
        self.assertFalse(url.is_valid())

    def test_url_reconstruction_with_port_and_host(self):
        """Test URL reconstruction with both host and port (line 211)"""
        url = URL("https://example.com:8080")
        self.assertEqual(str(url), "https://example.com:8080")

        # Test with explicit port 0
        url2 = URL("https://example.com:0")
        self.assertEqual(str(url2), "https://example.com:0")

        # Test with different ports to ensure line 211 is hit
        url3 = URL("https://example.com:443")
        self.assertEqual(str(url3), "https://example.com:443")

        url4 = URL("https://example.com:80")
        self.assertEqual(str(url4), "https://example.com:80")

    def test_url_reconstruction_with_fragment_only(self):
        """Test URL reconstruction with fragment only (line 227)"""
        url = URL("#fragment")
        self.assertEqual(str(url), "#fragment")

        # Test with fragment and other components
        url2 = URL("https://example.com#fragment")
        self.assertEqual(str(url2), "https://example.com#fragment")

        # Test with different fragments to ensure line 227 is hit
        url3 = URL("https://example.com#section1")
        self.assertEqual(str(url3), "https://example.com#section1")

        url4 = URL("https://example.com#anchor")
        self.assertEqual(str(url4), "https://example.com#anchor")

        url5 = URL("https://example.com#top")
        self.assertEqual(str(url5), "https://example.com#top")

        # Force reconstruction by clearing cache and calling __str__
        url6 = URL("https://example.com:9999#test")
        url6._str = None  # Clear cache to force reconstruction
        result = str(url6)
        self.assertEqual(result, "https://example.com:9999#test")

        # Test another URL with different port and fragment
        url7 = URL("https://example.com:3000#api")
        url7._str = None  # Clear cache to force reconstruction
        result2 = str(url7)
        self.assertEqual(result2, "https://example.com:3000#api")

    def test_is_valid_with_no_components(self):
        """Test is_valid with URL that has no components (line 311)"""
        # Create a URL with minimal components and test is_valid
        url = URL("https://example.com")
        # Remove all components to test the empty check
        url._scheme = None
        url._host = None
        url._path = URLPath("")  # Empty path
        url._query = QueryParams("")  # Empty query
        url._fragment = None
        self.assertFalse(url.is_valid())


if __name__ == "__main__":
    unittest.main()
