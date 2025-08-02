import requests
import pandas as pd
import time
import os
import json
from GetAuthtoken import get_access_token
from utils import random_lat_long

EXCEL_PATH = r"C:\Users\rajasekhar.palleti\Downloads\asset_ids.xlsx"
SHEET_NAME = "results"
COLUMN_ID = 0  # Assuming the first column contains the asset IDs
API_BASE_URL = "https://cloud.cropin.in/services/farm/api/assets"
TENANT_CODE = "qa"
MOBILE = "7382212409"
PASSWORD = "123456"
ENVIRONMENT = "prod1"

def update_asset_address():
    print("🔐 Getting access token...")
    token = get_access_token(TENANT_CODE, MOBILE, PASSWORD, ENVIRONMENT)
    if not token:
        print("❌ Failed to get token.")
        return

    headers = {
        "Authorization": f"Bearer {token}"
    }

    if not os.path.exists(EXCEL_PATH):
        print(f"❌ Excel file not found at path: {EXCEL_PATH}")
        return

    print("📄 Reading Excel for asset IDs...")
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
    df["status"] = ""
    df["message"] = ""

    index:int
    for index, row in df.iterrows():
        row_number = index + 2  # Adding 2 because Excel rows start at 1 and header is row 1
        asset_id = row.iloc[COLUMN_ID]  # Assuming the first column contains the asset IDs

        if pd.isna(asset_id):
            print(f"🚫 Skipping empty asset ID at Excel row {row_number}")
            df.at[index, "status"] = "Skipped"
            df.at[index, "message"] = "Skipped due to empty asset ID"
            continue

        try:
            asset_id = int(asset_id)
            print(f"\n📥 Row {row_number}: Fetching asset ID: {asset_id}")
            get_url = f"{API_BASE_URL}/{asset_id}"
            response = requests.get(get_url, headers=headers)
            response.raise_for_status()

            asset_data = response.json()
            # Generate random lat, long, address
            lat, long= random_lat_long()
            asset_data["address"]["latitude"] = lat
            asset_data["address"]["longitude"] = long

            print(f"🔁 Row {row_number}: Updating asset ID: {asset_id}")

            # Convert to multipart format for API
            multipart_data = {
                "dto": (None, json.dumps(asset_data), "application/json")
            }

            put_response = requests.put(API_BASE_URL, headers=headers, files=multipart_data)
            put_response.raise_for_status()

            df.at[index, "status"] = "Pass"
            df.at[index, "message"] = "Updated successfully"
            print(f"✅ Row {row_number}: Successfully updated CA ID: {asset_id}")

        except Exception as e:
            df.at[index, "status"] = "Fail"
            df.at[index, "message"] = str(e)
            print(f"❌ Row {row_number}: Error for asset ID {asset_id}: {str(e)}")

        time.sleep(0.5)

    print(f"\n💾 Saving Excel back to: {EXCEL_PATH}")
    df.to_excel(EXCEL_PATH, sheet_name=SHEET_NAME, index=False)
    print("✅ Update complete and saved to Excel.")

if __name__ == "__main__":
    update_asset_address()
