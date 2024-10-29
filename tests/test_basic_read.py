import unittest
from pathlib import Path

from csvy.readers import basic_read


class TestBasicRead(unittest.TestCase):
    def test_basic_read(self):
        # Sample CSVY content for testing
        test_file = Path("test_basic_read.csvy")

        # Call basic_read and capture the output
        result, metadata = basic_read(test_file)

        # Expected values based on sample.csvy content
        expected_columns = ["col1", "col2", "col3"]
        expected_data = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]

        # Assertions to verify the output
        self.assertEqual(result["columns"], expected_columns)
        self.assertEqual(result["data"], expected_data)
        self.assertIn("title", metadata)
        self.assertIn("author", metadata)


if __name__ == "__main__":
    unittest.main()
