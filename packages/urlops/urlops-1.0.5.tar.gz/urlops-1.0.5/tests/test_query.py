#!/usr/bin/env python3
"""
Tests for QueryParams class
"""

import unittest
from tests.conftest import URLParseTestCase, INVALID_QUERY_STRINGS
from urlops import QueryParams
from urlops.exceptions import ValidationError, TypeError


class TestQueryParamsCreation(URLParseTestCase):
    """Test QueryParams creation from various inputs"""

    def test_create_from_string(self):
        """Test QueryParams creation from string"""
        query = QueryParams("key1=value1&key2=value2")
        self.assertQueryParamsEqual(query, [("key1", "value1"), ("key2", "value2")])

    def test_create_from_dict(self):
        """Test QueryParams creation from dictionary"""
        query = QueryParams({"key1": "value1", "key2": "value2"})
        self.assertQueryParamsEqual(query, [("key1", "value1"), ("key2", "value2")])

    def test_create_from_dict_with_lists(self):
        """Test QueryParams creation from dict with list values"""
        query = QueryParams({"key": ["value1", "value2"]})
        self.assertQueryParamsEqual(query, [("key", "value1"), ("key", "value2")])

    def test_create_from_none(self):
        """Test QueryParams creation from None"""
        query = QueryParams(None)
        self.assertQueryParamsEqual(query, [])
        self.assertFalse(query)

    def test_create_from_empty_string(self):
        """Test QueryParams creation from empty string"""
        query = QueryParams("")
        self.assertQueryParamsEqual(query, [])
        self.assertFalse(query)

    def test_create_with_key_only(self):
        """Test QueryParams creation with keys without values"""
        query = QueryParams("key1&key2=value")
        self.assertQueryParamsEqual(query, [("key1", ""), ("key2", "value")])

    def test_create_with_iterables(self):
        """Test QueryParams creation with various iterables"""
        # List
        query1 = QueryParams({"tags": ["python", "url"]})
        self.assertQueryParamsEqual(query1, [("tags", "python"), ("tags", "url")])

        # Tuple
        query2 = QueryParams({"ids": (1, 2, 3)})
        self.assertQueryParamsEqual(query2, [("ids", "1"), ("ids", "2"), ("ids", "3")])

        # Set
        query3 = QueryParams({"values": {10, 20, 30}})
        # Order may vary with sets, so check length and content
        self.assertEqual(len(query3), 3)
        self.assertEqual(set(query3.get_all("values")), {"10", "20", "30"})

    def test_invalid_inputs(self):
        """Test invalid input handling"""
        # Invalid type
        with self.assertRaises(TypeError):
            QueryParams(123)

        with self.assertRaises(TypeError):
            QueryParams([1, 2, 3])

        # Invalid query strings
        for invalid_query in INVALID_QUERY_STRINGS:
            with self.subTest(query=invalid_query):
                with self.assertRaises(ValidationError):
                    QueryParams(invalid_query)


class TestQueryParamsAccess(URLParseTestCase):
    """Test QueryParams access methods"""

    def setUp(self):
        self.query = QueryParams("key1=value1&key2=value2&key1=value3")

    def test_get_method(self):
        """Test get method"""
        self.assertEqual(self.query.get("key1"), "value1")  # First value
        self.assertEqual(self.query.get("key2"), "value2")
        self.assertEqual(self.query.get("nonexistent"), None)
        self.assertEqual(self.query.get("nonexistent", "default"), "default")

    def test_get_all_method(self):
        """Test get_all method"""
        self.assertEqual(self.query.get_all("key1"), ["value1", "value3"])
        self.assertEqual(self.query.get_all("key2"), ["value2"])
        self.assertEqual(self.query.get_all("nonexistent"), [])

    def test_keys_method(self):
        """Test keys method"""
        keys = self.query.keys()
        self.assertEqual(set(keys), {"key1", "key2"})

    def test_values_method(self):
        """Test values method"""
        values = self.query.values()
        self.assertEqual(values, ["value1", "value2", "value3"])

    def test_items_method(self):
        """Test items method"""
        items = self.query.items()
        expected = [("key1", "value1"), ("key2", "value2"), ("key1", "value3")]
        self.assertEqual(items, expected)

    def test_len_method(self):
        """Test len method"""
        self.assertEqual(len(self.query), 3)

        empty_query = QueryParams()
        self.assertEqual(len(empty_query), 0)

    def test_bool_method(self):
        """Test bool method"""
        self.assertTrue(self.query)

        empty_query = QueryParams()
        self.assertFalse(empty_query)


class TestQueryParamsModification(URLParseTestCase):
    """Test QueryParams modification methods"""

    def setUp(self):
        self.query = QueryParams("key1=value1&key2=value2")

    def test_add_method(self):
        """Test add method"""
        new_query = self.query.add("key3", "value3")
        self.assertQueryParamsEqual(
            new_query, [("key1", "value1"), ("key2", "value2"), ("key3", "value3")]
        )
        self.assertIsNot(self.query, new_query)  # Should be different objects

        # Test adding duplicate key
        new_query2 = self.query.add("key1", "value4")
        self.assertQueryParamsEqual(
            new_query2, [("key1", "value1"), ("key2", "value2"), ("key1", "value4")]
        )

    def test_set_method(self):
        """Test set method"""
        new_query = self.query.set("key1", "new_value")
        self.assertQueryParamsEqual(
            new_query, [("key2", "value2"), ("key1", "new_value")]
        )

        # Test setting new key
        new_query2 = self.query.set("key3", "value3")
        self.assertQueryParamsEqual(
            new_query2, [("key1", "value1"), ("key2", "value2"), ("key3", "value3")]
        )

    def test_remove_method(self):
        """Test remove method"""
        new_query = self.query.remove("key1")
        self.assertQueryParamsEqual(new_query, [("key2", "value2")])

        # Test removing non-existent key
        new_query2 = self.query.remove("nonexistent")
        self.assertQueryParamsEqual(
            new_query2, [("key1", "value1"), ("key2", "value2")]
        )

    def test_with_method(self):
        """Test with_ method"""
        new_query = self.query.with_(key3="value3", key4="value4")
        self.assertQueryParamsEqual(
            new_query,
            [
                ("key1", "value1"),
                ("key2", "value2"),
                ("key3", "value3"),
                ("key4", "value4"),
            ],
        )

        # Test adding existing key
        new_query2 = self.query.with_(key1="new_value")
        # with_ method adds parameters, doesn't replace them
        self.assertQueryParamsEqual(
            new_query2, [("key1", "value1"), ("key2", "value2"), ("key1", "new_value")]
        )

    def test_modification_chaining(self):
        """Test method chaining"""
        new_query = (
            self.query.add("key3", "value3").set("key1", "updated").remove("key2")
        )

        self.assertQueryParamsEqual(
            new_query, [("key3", "value3"), ("key1", "updated")]
        )

    def test_invalid_modifications(self):
        """Test invalid modification parameters"""
        # Invalid key types
        with self.assertRaises(TypeError):
            self.query.add(123, "value")

        with self.assertRaises(TypeError):
            self.query.set(None, "value")

        # Invalid value types
        with self.assertRaises(TypeError):
            self.query.add("key", 123)

        # Empty key
        with self.assertRaises(ValidationError):
            self.query.add("", "value")

        with self.assertRaises(ValidationError):
            self.query.set("", "value")


class TestQueryParamsStringRepresentation(URLParseTestCase):
    """Test QueryParams string representation"""

    def test_str_representation(self):
        """Test string representation"""
        query = QueryParams("key1=value1&key2=value2")
        self.assertEqual(str(query), "key1=value1&key2=value2")

        # Test with empty values
        query2 = QueryParams("key1&key2=value")
        self.assertEqual(str(query2), "key1&key2=value")

        # Test empty query
        query3 = QueryParams()
        self.assertEqual(str(query3), "")

    def test_repr_representation(self):
        """Test repr representation"""
        query = QueryParams("key1=value1")
        repr_str = repr(query)
        self.assertIn("QueryParams(", repr_str)
        self.assertIn("key1=value1", repr_str)

    def test_string_reconstruction(self):
        """Test that string representation can be parsed back"""
        original = "key1=value1&key2=value2&key1=value3"
        query = QueryParams(original)
        reconstructed = str(query)
        self.assertEqual(reconstructed, original)


class TestQueryParamsEdgeCases(URLParseTestCase):
    """Test QueryParams edge cases"""

    def test_special_characters(self):
        """Test special characters in keys and values"""
        query = QueryParams("key%20=value%20&key+with+spaces=value+with+spaces")
        self.assertEqual(len(query), 2)
        self.assertEqual(query.get("key%20"), "value%20")
        self.assertEqual(query.get("key+with+spaces"), "value+with+spaces")

    def test_empty_values(self):
        """Test empty values"""
        query = QueryParams("key1=&key2&key3=value")
        self.assertEqual(query.get("key1"), "")
        self.assertEqual(query.get("key2"), "")
        self.assertEqual(query.get("key3"), "value")

    def test_unicode_characters(self):
        """Test unicode characters"""
        query = QueryParams("key=测试&key2=value")
        self.assertEqual(query.get("key"), "测试")
        self.assertEqual(query.get("key2"), "value")

    def test_large_query_string(self):
        """Test large query string"""
        # Create a large query string
        pairs = [f"key{i}=value{i}" for i in range(100)]
        large_query = "&".join(pairs)

        query = QueryParams(large_query)
        self.assertEqual(len(query), 100)
        self.assertEqual(query.get("key0"), "value0")
        self.assertEqual(query.get("key99"), "value99")


class TestQueryParamsOrdering(URLParseTestCase):
    """Test QueryParams ordering behavior"""

    def test_preserve_order(self):
        """Test that order is preserved"""
        query = QueryParams("z=1&a=2&m=3&z=4")
        items = list(query.items())
        expected = [("z", "1"), ("a", "2"), ("m", "3"), ("z", "4")]
        self.assertEqual(items, expected)

    def test_dict_order_preservation(self):
        """Test that dict order is preserved"""
        # Python 3.7+ preserves dict order
        query = QueryParams({"z": "1", "a": "2", "m": "3"})
        items = list(query.items())
        expected = [("z", "1"), ("a", "2"), ("m", "3")]
        self.assertEqual(items, expected)


if __name__ == "__main__":
    unittest.main()
