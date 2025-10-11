#!/usr/bin/env python3
"""
Tests for URLPath class
"""

import unittest
from tests.conftest import URLParseTestCase, INVALID_PATHS
from urlops import URLPath
from urlops.exceptions import ValidationError, TypeError


class TestURLPathCreation(URLParseTestCase):
    """Test URLPath creation from various inputs"""

    def test_create_from_string(self):
        """Test URLPath creation from string"""
        path = URLPath("/path/to/file")
        self.assertPathComponents(path, ["path", "to", "file"], is_absolute=True)

    def test_create_from_urlpath_object(self):
        """Test URLPath creation from another URLPath object"""
        original = URLPath("/path/to/file")
        copy = URLPath(original)
        self.assertEqual(str(original), str(copy))
        self.assertIsNot(original, copy)  # Should be different objects

    def test_create_absolute_path(self):
        """Test absolute path creation"""
        path = URLPath("/absolute/path")
        self.assertPathComponents(path, ["absolute", "path"], is_absolute=True)
        self.assertTrue(path.is_absolute())
        self.assertFalse(path.is_relative())

    def test_create_relative_path(self):
        """Test relative path creation"""
        path = URLPath("relative/path")
        self.assertPathComponents(path, ["relative", "path"], is_absolute=False)
        self.assertFalse(path.is_absolute())
        self.assertTrue(path.is_relative())

    def test_create_root_path(self):
        """Test root path creation"""
        path = URLPath("/")
        self.assertPathComponents(path, [], is_absolute=True)
        self.assertTrue(path.is_absolute())

    def test_create_empty_path(self):
        """Test empty path creation"""
        # Empty string
        path = URLPath("")
        self.assertPathComponents(path, [], is_absolute=False)
        self.assertFalse(path.is_absolute())
        self.assertTrue(path.is_relative())

    def test_create_single_segment(self):
        """Test single segment path creation"""
        path = URLPath("file.txt")
        self.assertPathComponents(path, ["file.txt"], is_absolute=False)

    def test_invalid_paths(self):
        """Test invalid path handling"""
        for invalid_path in INVALID_PATHS:
            with self.subTest(path=invalid_path):
                with self.assertRaises(ValidationError):
                    URLPath(invalid_path)

    def test_invalid_path_types(self):
        """Test invalid path types"""
        # Non-string, non-URLPath types should raise TypeError
        with self.assertRaises(TypeError):
            URLPath(123)

        with self.assertRaises(TypeError):
            URLPath(None)

        with self.assertRaises(TypeError):
            URLPath(object())

        with self.assertRaises(TypeError):
            URLPath([])

        with self.assertRaises(TypeError):
            URLPath({})

        with self.assertRaises(TypeError):
            URLPath(set())


class TestURLPathProperties(URLParseTestCase):
    """Test URLPath property access"""

    def test_name_property(self):
        """Test name property"""
        path = URLPath("/path/to/file.txt")
        self.assertEqual(path.name, "file.txt")

        path2 = URLPath("/path/to/directory/")
        self.assertEqual(path2.name, "directory")

        path3 = URLPath("/")
        self.assertEqual(path3.name, "")

        path4 = URLPath("")
        self.assertEqual(path4.name, "")

    def test_stem_property(self):
        """Test stem property"""
        path = URLPath("/path/to/file.txt")
        self.assertEqual(path.stem, "file")

        path2 = URLPath("/path/to/file.tar.gz")
        self.assertEqual(path2.stem, "file.tar")

        path3 = URLPath("/path/to/file")
        self.assertEqual(path3.stem, "file")

        path4 = URLPath("/path/to/.hidden")
        self.assertEqual(path4.stem, ".hidden")

    def test_suffix_property(self):
        """Test suffix property"""
        path = URLPath("/path/to/file.txt")
        self.assertEqual(path.suffix, ".txt")

        path2 = URLPath("/path/to/file.tar.gz")
        self.assertEqual(path2.suffix, ".gz")

        path3 = URLPath("/path/to/file")
        self.assertEqual(path3.suffix, "")

        path4 = URLPath("/path/to/.hidden")
        self.assertEqual(path4.suffix, "")

    def test_hidden_file_stem_suffix(self):
        """Test stem and suffix for hidden files with multiple dots"""
        # Hidden files with multiple dots
        path = URLPath("/path/.hidden.txt")
        self.assertEqual(path.stem, ".hidden")
        self.assertEqual(path.suffix, ".txt")

        # Hidden files with no extension
        path = URLPath("/path/.hidden")
        self.assertEqual(path.stem, ".hidden")
        self.assertEqual(path.suffix, "")

        # Hidden files with multiple extensions
        path = URLPath("/path/.hidden.tar.gz")
        self.assertEqual(path.stem, ".hidden.tar")
        self.assertEqual(path.suffix, ".gz")

    def test_parent_property(self):
        """Test parent property"""
        path = URLPath("/path/to/file.txt")
        parent = path.parent
        self.assertPathComponents(parent, ["path", "to"], is_absolute=True)

        path2 = URLPath("/path/to/")
        parent2 = path2.parent
        self.assertPathComponents(parent2, ["path"], is_absolute=True)

        path3 = URLPath("/")
        parent3 = path3.parent
        self.assertPathComponents(parent3, [], is_absolute=True)

        path4 = URLPath("file.txt")
        parent4 = path4.parent
        self.assertPathComponents(parent4, [], is_absolute=False)


class TestURLPathOperations(URLParseTestCase):
    """Test URLPath operations"""

    def test_truediv_operator(self):
        """Test / operator for path joining"""
        path = URLPath("/path/to")
        new_path = path / "file.txt"
        self.assertPathComponents(
            new_path, ["path", "to", "file.txt"], is_absolute=True
        )

        # Test chaining
        new_path2 = path / "subdir" / "file.txt"
        self.assertPathComponents(
            new_path2, ["path", "to", "subdir", "file.txt"], is_absolute=True
        )

        # Test with absolute path (should replace)
        new_path3 = path / "/absolute"
        self.assertPathComponents(new_path3, ["absolute"], is_absolute=True)

        # Test with string
        new_path4 = path / "string"
        self.assertPathComponents(new_path4, ["path", "to", "string"], is_absolute=True)

    def test_truediv_with_relative_path(self):
        """Test / operator with relative paths"""
        path = URLPath("relative/path")
        new_path = path / "file.txt"
        self.assertPathComponents(
            new_path, ["relative", "path", "file.txt"], is_absolute=False
        )

    def test_truediv_with_non_string_types(self):
        """Test / operator with non-string types"""
        path = URLPath("path/to")

        # Test with integer (should convert to string)
        result = path / 123
        self.assertEqual(str(result), "path/to/123")

        # Test with None (should convert to string)
        result = path / None
        self.assertEqual(str(result), "path/to/None")

    def test_with_name_method(self):
        """Test with_name method"""
        path = URLPath("/path/to/file.txt")
        new_path = path.with_name("newfile.py")
        self.assertPathComponents(
            new_path, ["path", "to", "newfile.py"], is_absolute=True
        )

        # Test with empty path
        path2 = URLPath("")
        new_path2 = path2.with_name("file.txt")
        self.assertPathComponents(new_path2, ["file.txt"], is_absolute=False)

    def test_with_suffix_method(self):
        """Test with_suffix method"""
        path = URLPath("/path/to/file.txt")
        new_path = path.with_suffix(".py")
        self.assertPathComponents(new_path, ["path", "to", "file.py"], is_absolute=True)

        # Test adding suffix to file without extension
        path2 = URLPath("/path/to/file")
        new_path2 = path2.with_suffix(".txt")
        self.assertPathComponents(
            new_path2, ["path", "to", "file.txt"], is_absolute=True
        )

        # Test with empty path
        path3 = URLPath("")
        new_path3 = path3.with_suffix(".txt")
        self.assertPathComponents(new_path3, [".txt"], is_absolute=False)

    def test_invalid_modifications(self):
        """Test invalid modification parameters"""
        path = URLPath("/path/to/file")

        # Invalid name types
        with self.assertRaises(TypeError):
            path.with_name(123)

        with self.assertRaises(TypeError):
            path.with_name(None)

        # Empty name
        with self.assertRaises(ValidationError):
            path.with_name("")

        # Invalid suffix types
        with self.assertRaises(TypeError):
            path.with_suffix(123)

        # Suffix without dot
        with self.assertRaises(ValidationError):
            path.with_suffix("txt")

        with self.assertRaises(ValidationError):
            path.with_suffix("")

    def test_with_name_empty_segments(self):
        """Test with_name with empty path segments"""
        # Empty path
        empty_path = URLPath("")
        result = empty_path.with_name("file.txt")
        self.assertEqual(str(result), "file.txt")

        # Single segment path
        single_path = URLPath("file.txt")
        result = single_path.with_name("newfile.py")
        self.assertEqual(str(result), "newfile.py")

    def test_parent_empty_relative_path(self):
        """Test parent property with empty relative path"""
        # Empty relative path should return empty path
        empty_path = URLPath("")
        parent = empty_path.parent
        self.assertEqual(str(parent), "")
        self.assertFalse(parent.is_absolute())
        self.assertTrue(parent.is_relative())

    def test_truediv_with_urlpath_objects(self):
        """Test / operator with URLPath objects"""
        path1 = URLPath("/path/to")
        path2 = URLPath("file.txt")
        result = path1 / path2
        self.assertEqual(str(result), "/path/to/file.txt")

        # Test with absolute URLPath
        path3 = URLPath("/absolute/path")
        result = path1 / path3
        self.assertEqual(str(result), "/absolute/path")


class TestURLPathStringRepresentation(URLParseTestCase):
    """Test URLPath string representation"""

    def test_str_representation(self):
        """Test string representation"""
        path = URLPath("/path/to/file.txt")
        self.assertEqual(str(path), "/path/to/file.txt")

        path2 = URLPath("relative/path")
        self.assertEqual(str(path2), "relative/path")

        path3 = URLPath("/")
        self.assertEqual(str(path3), "/")

        path4 = URLPath("")
        self.assertEqual(str(path4), "")

    def test_repr_representation(self):
        """Test repr representation"""
        path = URLPath("/path/to/file.txt")
        repr_str = repr(path)
        self.assertIn("URLPath(", repr_str)
        self.assertIn("/path/to/file.txt", repr_str)

    def test_string_reconstruction(self):
        """Test that string representation can be parsed back"""
        original = "/path/to/file.txt"
        path = URLPath(original)
        reconstructed = str(path)
        self.assertEqual(reconstructed, original)


class TestURLPathEdgeCases(URLParseTestCase):
    """Test URLPath edge cases"""

    def test_special_characters(self):
        """Test special characters in paths"""
        path = URLPath("/path with spaces/file-name.txt")
        self.assertPathComponents(
            path, ["path with spaces", "file-name.txt"], is_absolute=True
        )

        path2 = URLPath("/path%20with%20encoding/file.txt")
        self.assertPathComponents(
            path2, ["path%20with%20encoding", "file.txt"], is_absolute=True
        )

    def test_unicode_characters(self):
        """Test unicode characters"""
        path = URLPath("/路径/文件.txt")
        self.assertPathComponents(path, ["路径", "文件.txt"], is_absolute=True)

        path2 = URLPath("/тест/файл.txt")
        self.assertPathComponents(path2, ["тест", "файл.txt"], is_absolute=True)

    def test_dot_segments(self):
        """Test dot segments"""
        path = URLPath("/path/./file")
        self.assertPathComponents(path, ["path", ".", "file"], is_absolute=True)

        path2 = URLPath("/path/../file")
        self.assertPathComponents(path2, ["path", "..", "file"], is_absolute=True)

    def test_multiple_slashes_validation(self):
        """Test multiple slashes validation"""
        # These should raise ValueError
        invalid_paths = [
            "//path",
            "///path",
            "path//file",
            "path///file",
            "/path//file",
            "path//",
        ]

        for invalid_path in invalid_paths:
            with self.subTest(path=invalid_path):
                with self.assertRaises(ValidationError):
                    URLPath(invalid_path)


class TestURLPathAnalysis(URLParseTestCase):
    """Test URLPath analysis methods"""

    def test_is_absolute(self):
        """Test is_absolute method"""
        absolute_paths = ["/", "/path", "/path/to/file", "/path/to/file.txt"]

        for path_str in absolute_paths:
            with self.subTest(path=path_str):
                path = URLPath(path_str)
                self.assertTrue(
                    path.is_absolute(), f"Path should be absolute: {path_str}"
                )

    def test_is_relative(self):
        """Test is_relative method"""
        relative_paths = ["", "path", "path/to/file", "file.txt"]

        for path_str in relative_paths:
            with self.subTest(path=path_str):
                path = URLPath(path_str)
                self.assertTrue(
                    path.is_relative(), f"Path should be relative: {path_str}"
                )

    def test_empty_path_analysis(self):
        """Test analysis of empty paths"""
        empty_path = URLPath("")
        self.assertFalse(empty_path.is_absolute())
        self.assertTrue(empty_path.is_relative())
        self.assertEqual(empty_path.name, "")
        self.assertEqual(empty_path.stem, "")
        self.assertEqual(empty_path.suffix, "")

    def test_root_path_analysis(self):
        """Test analysis of root path"""
        root_path = URLPath("/")
        self.assertTrue(root_path.is_absolute())
        self.assertFalse(root_path.is_relative())
        self.assertEqual(root_path.name, "")
        self.assertEqual(root_path.stem, "")
        self.assertEqual(root_path.suffix, "")


if __name__ == "__main__":
    unittest.main()
