import time
import random
import os
import pandas as pd

EXCEL_FILE = "croppable_area_ids17000.xlsx"
SHEET_NAME = "croppable_area_ids"
COLUMN_NAME = "croppable area ids"

# Generates a unique timestamp in milliseconds
def generate_timestamp_millis():
    return str(int(time.time() * 1000))

# Generates a valid 10-digit mobile number (starts with 6-9)
def generate_random_mobile():
    return str(random.choice(range(6, 10))) + ''.join(random.choices("0123456789", k=9))

# Generates a random latitude and longitude within India and the USA
def random_lat_long():
    countries = [
        {"lat_range": (8.0, 37.0), "long_range": (68.0, 97.0)},  # India
        {"lat_range": (24.0, 49.0), "long_range": (-125.0, -66.0)},  # USA
        {"lat_range": (-35.0, 37.0), "long_range": (-17.0, 51.0)},  # Africa
        {"lat_range": (14.0, 33.0), "long_range": (-118.0, -86.0)},  # Mexico
        {"lat_range": (51.3, 51.7), "long_range": (-0.5, 0.3)},  # London
        {"lat_range": (36.0, 71.0), "long_range": (-10.0, 40.0)},  # Europe
    ]
    country = random.choice(countries)
    lat = round(random.uniform(*country["lat_range"]), 6)
    long = round(random.uniform(*country["long_range"]), 6)
    return lat, long

# Helper to write CA IDs to Excel
def append_ca_ids_to_excel(ca_ids):
    file_path = r'C:\Users\rajasekhar.palleti\Downloads\\' + EXCEL_FILE
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
    else:
        df = pd.DataFrame(columns=[COLUMN_NAME])

    new_df = pd.DataFrame(ca_ids, columns=[COLUMN_NAME])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_excel(file_path, index=False, sheet_name=SHEET_NAME)