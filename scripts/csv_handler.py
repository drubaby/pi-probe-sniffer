import os
import glob
import pandas as pd
from sys import argv

"""
This script loops through all CSV files in a directory (default: /usb)
and aggregates them into a new folder (<first_directory>/cleaned_data) for analysis.
It takes a single argument for file name

To run: python csv_handler.py /usb/$(date +%m-%d-%Y) $(date +%m-%d-%Y)
"""

# path to raw data and output folder cleaned for data separation
csvs = []
current = "/usb/"
path = current
cleaned = current + "cleaned_data"
allCSV = glob.glob(path + "*.csv")
print(allCSV)
# allCSV = glob.glob(path + "02-14-2024.csv")
# TARGET = argv[1]


old_subset = [
    "rssi",
    "channel",
    "timestamp",
    "mac",
    "vendor",
    "SSID",
]

new_subset = ["mac", "rssi", "channel", "oui", "ssid", "logtime"]

schema = ["logtime", "rssi", "channel", "mac", "oui", "ssid"]
old_schema_cols = [5, 1, 2, 5, 6, 3]
new_schema_cols = [3, 1, 2, 4, 5, 0]
# new_schema_cols = [3, 1, 2, 4, 5, 0]

# names = [os.path.basename(x) for x in glob.glob(path + "*.csv")]
# loop through allCSV and append to csvs list
# facility to expand script for tagging GPS data as N/A for earlier collections
for csv in allCSV:
    # old_schema = [
    #     "rssi", # 1
    #     "channel", # 2
    #     "timestamp", # 3
    #     "mac", # 5
    #     "vendor", # 6
    #     "SSID", # 7
    # ]
    # old schema example
    # 0         1     2               3                 4      5               6                                 7
    # PR-REQ,-79dBm,C:10 2457Mhz,2024-02-13 11:16:34,Client,40:aa:56:53:ad:6a,China Dragon Technology Limited,b'Simba2018'

    # new schema applied 03-12

    DataFrame = pd.read_csv(
        csv,
        index_col=None,
        usecols=new_schema_cols,
        names=schema,
        on_bad_lines="skip",
    )
    csvs.append(DataFrame)
# print(f"CSVS {csvs}")

# concatenate files + Aggressive filtering (Drop row if data incomplete)
DataFrame = pd.DataFrame()
# print("csvs so far: ", csvs)
DataFrame: pd.DataFrame = pd.concat(csvs, axis=0, join="outer").dropna(
    subset=new_subset
)
# print("DF so far: ", DataFrame)
# remove duplicates
DataFrame.drop_duplicates(subset="mac", keep="first", inplace=True)
# print("DF after drop dupes: ", DataFrame)
DataFrame.dropna(
    # subset=[
    #     "rssi",
    #     "channel",
    #     "timestamp",
    #     "mac",
    #     "vendor",
    #     "SSID",
    # ]
    subset=new_subset
)
# print("DF after dropna: ", DataFrame)
# save cleaned to CSV
tentative = DataFrame.sort_values(by="logtime", inplace=False, ascending=False)
print(tentative)
looks_good = input("Does this look right y/n? ")
if looks_good == "y":
    DataFrame.to_csv(os.path.join(cleaned, argv[1] + ".csv"), header=True, index=False)
