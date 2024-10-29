"""
Tests for the basic_read function in the csvy library.
"""

import unittest
from pathlib import Path
from csvy.readers import basic_read

class TestBasicRead(unittest.TestCase):
    """Test case for the basic_read function."""

    def test_basic_read(self):
        """Test basic functionality of basic_read with sample CSVY content."""
        # Sample CSVY content for testing
        test_file = Path("test_basic_read.csvy")
        
        # Write sample CSVY content to the test file
        with open(test_file, "w") as f:
            f.write(
                """---
                title: Sample Dataset
                author: User
                description: This is a test CSVY file
                ---
                col1, col2, col3
                1, 2, 3
                4, 5, 6
                7, 8, 9
                """
            )
        
        # Expected values
        expected_columns = ["col1", "col2", "col3"]
        expected_data = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]
        expected_metadata = {
            "title": "Sample Dataset",
            "author": "User",
            "description": "This is a test CSVY file",
        }

        # Test basic_read function
        result, metadata = basic_read(test_file)
        
        # Assertions
        self.assertEqual(result["columns"], expected_columns)
        self.assertEqual(result["data"], expected_data)
        self.assertEqual(metadata, expected_metadata)
