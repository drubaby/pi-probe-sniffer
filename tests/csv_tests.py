import unittest
import os
import sys
import warnings

warnings.simplefilter(action="ignore", category=DeprecationWarning)
import pandas as pd
from io import BytesIO, StringIO
from unittest.mock import patch
import datatest as dt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from scripts import daily_csv


class TestCSVHandler(unittest.TestCase):
    def setUp(self):
        # Create a sample CSV file for testing
        self.csv_filepath = "test.csv"
        self.data = {
            "logtime": [
                "2024-03-27 00:03:31",
                "2024-03-27 00:01:59",
                "1XZ%]X^ԫƛTtA!=܇",
            ],
            "rssi": ["-73dBm", "-75dBm", ""],
            "channel": ["C:01 2412Mhz", "C:02 2412Mhz", ""],
            "mac": ["bc:1c:81:4b:d1:ef", "40:aa:56:53:ad:6a", ""],
            "oui": [
                "Sichuan iLink Technology Co.",
                "China Dragon Technology Limited",
                "",
            ],
            "ssid": ["Ltd.", "WifiName", ""],
        }
        self.df = pd.DataFrame(self.data)
        # print("Self df: ", self.df)
        self.df.to_csv(self.csv_filepath, index=False)

    def tearDown(self):
        # Clean up the test CSV file
        import os

        os.remove(self.csv_filepath)

    def test_csv_to_dataframe(self):
        # Test if the CSV handler correctly converts CSV to DataFrame)
        schema = ["logtime", "rssi", "channel", "mac", "oui", "ssid"]
        expected_df = pd.read_csv(
            self.csv_filepath,
            names=schema,
        )

        actual_df = daily_csv.read_csv_to_dataframe(self.csv_filepath)
        self.assertTrue(expected_df.equals(actual_df), msg="DataFrames are not equal")

    def test_csv_to_dataframe_invalid_path(self):
        # Test for invalid file path handling
        with self.assertRaises(FileNotFoundError):
            daily_csv.read_csv_to_dataframe(
                "invalid_file.csv"
            )  # Provide a non-existent file path

    def test_clean_invalid_row(self):
        # Test that row with empty values is excluded
        actual_df = daily_csv.clean_yesterdays_csv(self.df)

        expected_df = pd.DataFrame(
            {
                "logtime": ["2024-03-27 00:03:31", "2024-03-27 00:01:59"],
                "rssi": ["-73dBm", "-75dBm"],
                "channel": ["C:01 2412Mhz", "C:02 2412Mhz"],
                "mac": ["bc:1c:81:4b:d1:ef", "40:aa:56:53:ad:6a"],
                "oui": [
                    "Sichuan iLink Technology Co.",
                    "China Dragon Technology Limited",
                ],
                "ssid": ["Ltd.", "WifiName"],
            }
        )

        self.assertEqual(len(actual_df), 2)
        self.assertTrue(expected_df.equals(actual_df))


if __name__ == "__main__":
    unittest.main()
