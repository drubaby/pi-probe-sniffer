import os
import glob
import warnings
import datetime

warnings.simplefilter(action="ignore", category=DeprecationWarning)
import pandas as pd
from sys import argv
import json
from supabase import create_client, Client
from dotenv import load_dotenv

"""
This script parses the last day's probes into a cleaned csv of unique devices and uploads it to supabase

To run: python ~/wuds/scripts/daily_csv.py
"""

# path to raw data and output folder cleaned for data separation
usb_path = "/usb/"
cleaned_data_path = usb_path + "cleaned_data/"


def sorted_csvs_by_createdate(dir_path: str) -> list:
    list_of_files = glob.glob(dir_path + "*.csv")
    sorted_files = sorted(list_of_files, key=os.path.getctime)
    return sorted_files


def find_yesterdays_csv(sorted_csvs: list) -> str:
    """
    Finds yesterday's CSV (i.e. second-to-last csv modified in our usb)
    """
    return sorted_csvs[-2]


def remove_old_csvs(sorted_csvs: list, AGE_LIMIT=30) -> None:
    """Keep raw CSV files around for 30 days"""
    today = datetime.datetime.today()

    for file in sorted_csvs:
        create_date = datetime.datetime.fromtimestamp(os.path.getctime(file))
        age = today - create_date
        if age.days > AGE_LIMIT:
            print("Clean up old csv: ", file)
            os.remove(file)


def read_csv_to_dataframe(csv_filepath) -> pd.DataFrame:
    """
    Given the filepath of a csv file, converts that csv to a DataFrame with our preferred schema
    """
    schema = ["logtime", "rssi", "channel", "mac", "oui", "ssid"]

    schema_cols = [3, 1, 2, 4, 5, 0]
    DataFrame = pd.read_csv(
        csv_filepath,
        index_col=None,
        usecols=schema_cols,
        names=schema,
        on_bad_lines="skip",
    )
    return DataFrame


def clean_yesterdays_csv(csv_dataFrame: pd.DataFrame) -> pd.DataFrame:
    """
    Removes any duplicate MAC addresses and any invalid rows from CSV
    """
    subset = ["mac", "rssi", "channel", "oui", "ssid", "logtime"]

    csv_dataFrame.drop_duplicates(subset="mac", keep="first", inplace=True)

    # If any columns have an empty string replace that with null value
    csv_dataFrame.replace("", float("NaN"), inplace=True)

    # dropna will eleminate any rows with null value
    csv_dataFrame.dropna(subset=subset, inplace=True)

    # save cleaned to CSV
    return csv_dataFrame.sort_values(by="logtime", inplace=False, ascending=False)


def write_cleaned_csv(cleaned_csv: pd.DataFrame, file_path: str) -> None:
    """Writes cleaned csv to /usb/cleaned_data for storage"""

    filename = os.path.basename(file_path)
    # print(f"Writing to {os.path.join(cleaned_data_path, filename)}")
    cleaned_csv.to_csv(
        os.path.join(cleaned_data_path, filename), header=True, index=False
    )


def add_probes_to_raw_table(cleaned_data: pd.DataFrame, supabase: Client):
    # table columns: rssi, channel, mac, oui, ssid, logtime
    # {'logtime': '2024-03-25 23:50:47', 'rssi': '-51dBm', 'channel': 'C:05 2432Mhz', 'mac': '86:42:87:04:75:18', 'oui': 'Locally Assigned', 'ssid': 'NN23 Wifi'}
    list = []

    list = cleaned_data.to_dict(orient="records")
    data = supabase.table("csv_probes_raw").insert(list).execute()


def main():
    load_dotenv()

    RAW_CSV_AGE_LIMIT = 30
    CLEANED_CSV_AGE_LIMIT = 60

    # e.g. 03-25-2024.csv
    sorted_csvs = sorted_csvs_by_createdate(usb_path)
    yesterdays_csv_filepath: str = find_yesterdays_csv(sorted_csvs)

    csv_dataframe: pd.DataFrame = read_csv_to_dataframe(yesterdays_csv_filepath)
    cleaned: pd.DataFrame = clean_yesterdays_csv(csv_dataframe)
    write_cleaned_csv(cleaned, yesterdays_csv_filepath)

    # Remove csvs >30 days old in base path and >60 days in cleaned path
    remove_old_csvs(sorted_csvs, RAW_CSV_AGE_LIMIT)
    remove_old_csvs(sorted_csvs_by_createdate(cleaned_data_path), CLEANED_CSV_AGE_LIMIT)

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")
    supabase: Client = create_client(url, key)

    try:
        add_probes_to_raw_table(cleaned, supabase)
    except Exception as e:
        print("Something went wrong with upload, e type: ", (type(e)))
        print("exception: ", e)


if __name__ == "__main__":
    main()
