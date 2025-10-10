""" 
Test for file_locations.py.
Author: Darren
"""
import unittest
from pathlib import Path

import dazbo_commons as dc


class TestFileLocations(unittest.TestCase):
    """ Tests for the file_locations module. """
    
    def setUp(self):
        # Create a dummy script file for testing purposes
        self.test_script_name = "dummy_script.py"
        self.test_script_path = Path(__file__).parent / self.test_script_name
        self.test_script_path.touch()

        # Define expected paths based on the test script's location
        self.expected_script_dir = self.test_script_path.parent.resolve()
        self.expected_input_dir = self.expected_script_dir / "input"
        self.expected_output_dir = self.expected_script_dir / "output"
        self.expected_input_file = self.expected_input_dir / "input.txt"

    def tearDown(self):
        # Clean up the dummy script file
        if self.test_script_path.exists():
            self.test_script_path.unlink()

    def test_get_locations_no_subfolder(self): 
        """ Test get_locations with no sub_folder. """
        locations = dc.get_locations(str(self.test_script_path))

        self.assertEqual(locations.script_name, self.test_script_name)
        self.assertEqual(locations.script_dir, self.expected_script_dir)
        self.assertEqual(locations.input_dir, self.expected_input_dir)
        self.assertEqual(locations.output_dir, self.expected_output_dir)
        self.assertEqual(locations.input_file, self.expected_input_file)

    def test_get_locations_with_subfolder(self): 
        """ Test get_locations with a sub_folder. """
        sub_folder = "my_data"
        expected_sub_folder_dir = self.expected_script_dir / sub_folder
        expected_input_dir_sub = expected_sub_folder_dir / "input"
        expected_output_dir_sub = expected_sub_folder_dir / "output"
        expected_input_file_sub = expected_input_dir_sub / "input.txt"

        locations = dc.get_locations(str(self.test_script_path), sub_folder=sub_folder)

        self.assertEqual(locations.script_name, self.test_script_name)
        self.assertEqual(locations.script_dir, expected_sub_folder_dir)
        self.assertEqual(locations.input_dir, expected_input_dir_sub)
        self.assertEqual(locations.output_dir, expected_output_dir_sub)
        self.assertEqual(locations.input_file, expected_input_file_sub)

    def test_locations_dataclass_types(self): 
        """ Test that the returned Locations object has correct types. """
        locations = dc.get_locations(str(self.test_script_path))

        self.assertIsInstance(locations.script_name, str)
        self.assertIsInstance(locations.script_dir, Path)
        self.assertIsInstance(locations.input_dir, Path)
        self.assertIsInstance(locations.output_dir, Path)
        self.assertIsInstance(locations.input_file, Path)

if __name__ == '__main__':
    unittest.main()
