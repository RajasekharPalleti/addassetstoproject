import time
import requests

from create_farmer import create_farmer
from create_asset import create_asset
from GetAuthtoken import get_access_token
from getUsers import get_users_data
from utils import append_ca_ids_to_excel

# Constants
users = [1401]
PROJECT_ID = 1501
# variety_id = 334502
# sowing_date = "2025-08-01T00:00:00.000Z"
MAX_CA_IDS = 2500
BATCH_SIZE = 100
TENANT_CODE = "auxoaidriscolls"
MOBILE = "9148981108"
PASSWORD = "cropin@123"
ENVIRONMENT = "prod1"


# Main function to generate and validate assets

def main():
    print("🔑 Getting Auth token...")
    token = get_access_token(TENANT_CODE, MOBILE, PASSWORD, ENVIRONMENT)
    if not token:
        print("❌ Failed to retrieve token.")
        return

    print("📥 Fetching assigned user details...")
    user_ids = users
    assigned_users = get_users_data(token, user_ids)

    total_ca_ids = []

    while len(total_ca_ids) < MAX_CA_IDS:
        print("👨 Creating farmer...")
        farmer_id = create_farmer(token, assigned_users)

        asset_ids = []
        for _ in range(BATCH_SIZE):
            asset_id = create_asset(token, farmer_id)
            asset_ids.append(asset_id)
            time.sleep(0.5)  # Sleep to avoid hitting API limits

        print(f"🗂️ Total assets mapped before: {len(total_ca_ids)}")
        print(f"📦 Mapping {len(asset_ids)} assets to project...")
        map_url = f"https://cloud.cropin.in/services/farm/api/projects/{PROJECT_ID}/probable-assets"
        headers = {"Authorization": f"Bearer {token}",
                   "Content-Type": "application/json"
                   }

        map_payload = asset_ids
        map_response = requests.post(map_url, headers=headers, json=map_payload)
        map_response.raise_for_status()
        mapped_asset_ids = map_response.json().get("projectAssetIds", [])

        print("✅ Mapped asset IDs:", mapped_asset_ids)

        validate_url = f"https://cloud.cropin.in/services/farm/api/projects/{PROJECT_ID}/self-validate-project-assets?cloneFlag=false"
        validate_response = requests.post(validate_url, headers=headers, json=mapped_asset_ids)
        validate_response.raise_for_status()
        ca_ids = validate_response.json().get("croppableAreaIds", [])

        print(f"✅ {len(ca_ids)} Croppable Area is assigned to project and IDs Gathered.")

        # #Adding variety and sowing date to CAs
        # bulk_url = "https://cloud.cropin.in/services/farm/api/croppable-areas/bulk"
        # bulk_payload = {"sowingDate":sowing_date,
        #                 "croppableArea":None,
        #                 "varietyId":variety_id,
        #                 "ids":ca_ids
        #                 }
        # print("⏳ Waiting for CA bulk update response...")
        # response_bulk = requests.put(bulk_url, headers=headers, json=bulk_payload)
        # response_bulk.raise_for_status()
        #
        # print("🔁 Bulk update response:", response_bulk.json())
        time.sleep(3)

        total_ca_ids.extend(ca_ids)
        append_ca_ids_to_excel(ca_ids)

        print(f"📊 Total CA IDs collected: {len(total_ca_ids)}\n")
        time.sleep(2)

    print(f"🎉 Finished collecting {MAX_CA_IDS} CA IDs.")

if __name__ == "__main__":
    main()
