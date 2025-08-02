import requests
import pandas as pd
import time
import os
from GetAuthtoken import get_access_token

EXCEL_PATH = r"C:\Users\rajasekhar.palleti\Downloads\croppable_area_ids.xlsx"
SHEET_NAME = "croppable_area_ids"
API_BASE_URL = "https://cloud.cropin.in/services/farm/api/croppable-areas"
TENANT_CODE = "qa"
MOBILE = "7382212409"
PASSWORD = "123456"
ENVIRONMENT = "prod1"

NEW_VARIETY_ID = 334502
NEW_SOWING_DATE = "2025-07-16T00:00:00.000+0000"

def update_croppable_areas():
    print("🔐 Getting access token...")
    token = get_access_token(TENANT_CODE, MOBILE, PASSWORD, ENVIRONMENT)
    if not token:
        print("❌ Failed to get token.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if not os.path.exists(EXCEL_PATH):
        print(f"❌ Excel file not found at path: {EXCEL_PATH}")
        return

    print("📄 Reading Excel for CA IDs...")
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
    df["status"] = ""
    df["message"] = ""

    index:int
    for index, row in df.iterrows():
        row_number = index + 2  # Adding 2 because Excel rows start at 1 and header is row 1
        ca_id = row.iloc[0]  # Assuming the first column contains the CA IDs

        if pd.isna(ca_id):
            print(f"🚫 Skipping empty CA ID at Excel row {row_number}")
            df.at[index, "status"] = "Skipped"
            df.at[index, "message"] = "Skipped due to empty CA ID"
            continue

        try:
            ca_id = int(ca_id)
            print(f"\n📥 Row {row_number}: Fetching CA ID: {ca_id}")
            get_url = f"{API_BASE_URL}/{ca_id}"
            response = requests.get(get_url, headers=headers)
            response.raise_for_status()

            payload = response.json()
            payload["varietyId"] = NEW_VARIETY_ID
            payload["sowingDate"] = NEW_SOWING_DATE

            print(f"🔁 Row {row_number}: Updating CA ID: {ca_id}")
            put_response = requests.put(API_BASE_URL, headers=headers, json=payload)
            put_response.raise_for_status()

            df.at[index, "status"] = "Pass"
            df.at[index, "message"] = "Updated successfully"
            print(f"✅ Row {row_number}: Successfully updated CA ID: {ca_id}")

        except Exception as e:
            df.at[index, "status"] = "Fail"
            df.at[index, "message"] = str(e)
            print(f"❌ Row {row_number}: Error for CA ID {ca_id}: {str(e)}")

        time.sleep(0.2)

    print(f"\n💾 Saving Excel back to: {EXCEL_PATH}")
    df.to_excel(EXCEL_PATH, sheet_name=SHEET_NAME, index=False)
    print("✅ Update complete and saved to Excel.")

if __name__ == "__main__":
    update_croppable_areas()
