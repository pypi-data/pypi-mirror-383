#!/usr/bin/env python3
"""
Integration tests for urlops
"""

import unittest
from tests.conftest import URLParseTestCase
from urlops import QueryParams, parse, join
from urlops.exceptions import ParseError, ValidationError


class TestURLIntegration(URLParseTestCase):
    """Test URL integration scenarios"""

    def test_complete_url_workflow(self):
        """Test complete URL parsing and manipulation workflow"""
        # Start with a basic URL
        url = parse("https://example.com")

        # Add path
        url = url.with_path("/api/v1")

        # Add query parameters
        url = url.with_query({"format": "json", "version": "1.0"})

        # Add fragment
        url = url.with_fragment("docs")

        # Verify final URL
        expected = "https://example.com/api/v1?format=json&version=1.0#docs"
        self.assertEqual(str(url), expected)

        # Verify components
        self.assertURLComponents(
            url,
            scheme="https",
            host="example.com",
            path="/api/v1",
            query="format=json&version=1.0",
            fragment="docs",
        )

    def test_url_building_chain(self):
        """Test URL building with method chaining"""
        url = (
            parse("https://example.com")
            .with_path("/api")
            .with_query({"version": "v1"})
            .with_fragment("authentication")
            / "users"
            / "123"
        )

        self.assertURLComponents(
            url,
            scheme="https",
            host="example.com",
            path="/api/users/123",
            query="version=v1",
            fragment="authentication",
        )

    def test_query_parameter_manipulation(self):
        """Test query parameter manipulation"""
        url = parse("https://api.example.com/users?page=1&limit=10")

        # Get query parameters
        query = url.query
        self.assertEqual(query.get("page"), "1")
        self.assertEqual(query.get("limit"), "10")

        # Modify query parameters
        new_query = query.set("page", "2").add("sort", "name")
        new_url = url.with_query(new_query)

        self.assertURLComponents(
            new_url,
            scheme="https",
            host="api.example.com",
            path="/users",
            query="limit=10&page=2&sort=name",
        )

    def test_path_manipulation(self):
        """Test path manipulation"""
        url = parse("https://example.com/path/to/file.txt")

        # Get path components
        path = url.path
        self.assertEqual(path.name, "file.txt")
        self.assertEqual(path.stem, "file")
        self.assertEqual(path.suffix, ".txt")
        self.assertEqual(str(path.parent), "/path/to")

        # Modify path
        new_path = path.with_name("newfile.py")
        new_url = url.with_path(new_path)

        self.assertURLComponents(
            new_url, scheme="https", host="example.com", path="/path/to/newfile.py"
        )

    def test_protocol_relative_urls(self):
        """Test protocol-relative URLs"""
        # Protocol-relative URL
        url = parse("//cdn.example.com/assets/style.css")
        self.assertURLComponents(
            url, scheme="", host="cdn.example.com", path="/assets/style.css"
        )
        self.assertFalse(url.is_absolute())

        # Convert to absolute
        absolute_url = url.with_scheme("https")
        self.assertTrue(absolute_url.is_absolute())
        self.assertEqual(str(absolute_url), "https://cdn.example.com/assets/style.css")

    def test_relative_path_urls(self):
        """Test relative path URLs"""
        url = parse("/api/v1/users")
        self.assertURLComponents(url, path="/api/v1/users")
        self.assertFalse(url.is_absolute())

        # Convert to absolute
        absolute_url = url.with_scheme("https").with_host("api.example.com")
        self.assertTrue(absolute_url.is_absolute())
        self.assertEqual(str(absolute_url), "https://api.example.com/api/v1/users")


class TestErrorHandlingIntegration(URLParseTestCase):
    """Test error handling in integration scenarios"""

    def test_invalid_url_parsing(self):
        """Test invalid URL parsing"""
        invalid_urls = [
            "",  # Empty URL
            "123invalid://example.com",  # Invalid scheme
            "https://example.com:99999",  # Invalid port
            "https://example.com//path",  # Double slash in path
        ]

        for invalid_url in invalid_urls:
            with self.subTest(url=invalid_url):
                with self.assertRaises((ParseError, ValidationError, ValueError)):
                    parse(invalid_url)

    def test_invalid_modifications(self):
        """Test invalid modifications"""
        url = parse("https://example.com")

        # Invalid scheme
        with self.assertRaises(ValidationError):
            url.with_scheme("123invalid")

        # Invalid port
        with self.assertRaises(ValidationError):
            url.with_port(99999)

        # Invalid path
        with self.assertRaises(ValidationError):
            url.with_path("//invalid")

    def test_invalid_query_parameters(self):
        """Test invalid query parameters"""
        # Empty key
        with self.assertRaises(ValidationError):
            QueryParams("=value")

        # Invalid modification
        query = QueryParams("key=value")
        with self.assertRaises(ValidationError):
            query.add("", "value")


class TestFactoryFunctionsIntegration(URLParseTestCase):
    """Test factory functions integration"""

    def test_parse_function(self):
        """Test parse function with various inputs"""
        test_cases = [
            ("https://example.com", "https", "example.com", None, "", "", ""),
            ("https://example.com:8080", "https", "example.com", 8080, "", "", ""),
            ("https://example.com/path", "https", "example.com", None, "/path", "", ""),
            (
                "https://example.com?query=value",
                "https",
                "example.com",
                None,
                "",
                "query=value",
                "",
            ),
            (
                "https://example.com#fragment",
                "https",
                "example.com",
                None,
                "",
                "",
                "fragment",
            ),
        ]

        for url_str, scheme, host, *rest in test_cases:
            with self.subTest(url=url_str):
                url = parse(url_str)
                if len(rest) == 4:
                    port, path, query, fragment = rest
                else:
                    port = None
                    path, query, fragment = rest

                self.assertURLComponents(url, scheme, host, port, path, query, fragment)

    def test_join_function(self):
        """Test join function"""
        base = parse("https://api.example.com")

        # Join with multiple components
        joined = join(base, "v1", "users", "123")
        self.assertURLComponents(
            joined, scheme="https", host="api.example.com", path="v1/users/123"
        )

        # Join with absolute path
        joined2 = join(base, "/absolute/path")
        self.assertURLComponents(
            joined2, scheme="https", host="api.example.com", path="/absolute/path"
        )


class TestRealWorldScenarios(URLParseTestCase):
    """Test real-world URL scenarios"""

    def test_api_url_construction(self):
        """Test API URL construction"""
        base_url = parse("https://api.github.com")

        # Build user endpoint
        user_url = base_url.with_path("/users").with_query(
            {"per_page": "100", "since": "2023-01-01"}
        )

        self.assertEqual(
            str(user_url), "https://api.github.com/users?per_page=100&since=2023-01-01"
        )

        # Build specific user endpoint
        specific_user = user_url / "octocat"
        self.assertEqual(
            str(specific_user),
            "https://api.github.com/users/octocat?per_page=100&since=2023-01-01",
        )

    def test_cdn_url_construction(self):
        """Test CDN URL construction"""
        # Start with protocol-relative URL
        cdn_url = parse("//cdn.example.com")

        # Add path and query
        asset_url = (
            cdn_url.with_scheme("https")
            .with_path("/assets")
            .with_query({"v": "1.2.3", "cache": "bust"})
        )

        self.assertEqual(
            str(asset_url), "https://cdn.example.com/assets?v=1.2.3&cache=bust"
        )

    def test_web_scraping_urls(self):
        """Test web scraping URL scenarios"""
        base_url = parse("https://example.com")

        # Build pagination URLs
        page_urls = []
        for page in range(1, 4):
            page_url = base_url.with_query({"page": str(page), "limit": "20"})
            page_urls.append(page_url)

        self.assertEqual(len(page_urls), 3)
        self.assertEqual(str(page_urls[0]), "https://example.com?page=1&limit=20")
        self.assertEqual(str(page_urls[1]), "https://example.com?page=2&limit=20")
        self.assertEqual(str(page_urls[2]), "https://example.com?page=3&limit=20")

    def test_file_url_handling(self):
        """Test file URL handling"""
        file_url = parse("https://example.com/files/document.pdf")

        # Analyze file path
        path = file_url.path
        self.assertEqual(path.name, "document.pdf")
        self.assertEqual(path.stem, "document")
        self.assertEqual(path.suffix, ".pdf")

        # Change file extension
        new_url = file_url.with_path(path.with_suffix(".txt"))
        self.assertEqual(str(new_url), "https://example.com/files/document.txt")


class TestEdgeCasesIntegration(URLParseTestCase):
    """Test edge cases in integration scenarios"""

    def test_empty_components(self):
        """Test URLs with empty components"""
        url = parse("https://example.com")
        self.assertURLComponents(url, scheme="https", host="example.com")

        # Add empty path
        url = url.with_path("")
        self.assertURLComponents(url, scheme="https", host="example.com", path="")

        # Add empty query
        url = url.with_query("")
        self.assertURLComponents(
            url, scheme="https", host="example.com", path="", query=""
        )

        # Add empty fragment
        url = url.with_fragment("")
        self.assertURLComponents(
            url, scheme="https", host="example.com", path="", query="", fragment=""
        )

    def test_unicode_urls(self):
        """Test URLs with unicode characters"""
        url = parse("https://example.com/路径/文件.txt")
        self.assertURLComponents(
            url, scheme="https", host="example.com", path="/路径/文件.txt"
        )

        # Test unicode in query parameters
        url2 = parse("https://example.com?search=测试&lang=中文")
        query = url2.query
        self.assertEqual(query.get("search"), "测试")
        self.assertEqual(query.get("lang"), "中文")

    def test_special_characters(self):
        """Test URLs with special characters"""
        url = parse("https://example.com/path%20with%20spaces/file-name.txt")
        self.assertURLComponents(
            url,
            scheme="https",
            host="example.com",
            path="/path%20with%20spaces/file-name.txt",
        )

        # Test special characters in query
        url2 = parse("https://example.com?key+with+spaces=value%20encoded")
        query = url2.query
        self.assertEqual(query.get("key+with+spaces"), "value%20encoded")


if __name__ == "__main__":
    unittest.main()
