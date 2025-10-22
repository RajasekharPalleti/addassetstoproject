import requests
import json
from utils import generate_timestamp_millis, get_random_location
from utils import get_address_from_latlng

def create_asset(token, owner_id):
    url = "https://cloud.cropin.in/services/farm/api/assets"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    timestamp = generate_timestamp_millis()
    region = "india"
    # region = "world"

    loc_details = get_random_location(region)
    # place = loc_details["place"]
    lat = loc_details["latitude"]
    lng = loc_details["longitude"]

    google_api_key = "AIzaSyAwy--7hbQ9x-_rFT2lCi52o0rF0JvbA7E"
    address = get_address_from_latlng(lat, lng, api_key=google_api_key)

    payload = {
        "data": {},
        "images": {},
        "companyStatus": "ACTIVE",
        "declaredArea": {
            "enableConversion": "true",
            "unit": "HECTARE",
            "count": 5
        },
        "auditedArea": {
            "enableConversion": "true",
            "unit": "ACRE"
        },
        "name": f"Raja_Bulk_API_Asset_{timestamp}",
        "ownerId": owner_id,
        "soilType": {
            "id": 1059
        },
        "irrigationType": {
            "id": 1101
        },
        "address": address
    }

    multipart_data = {
        "dto": (None, json.dumps(payload), "application/json")
    }

    try:
        print(f"📤 Sending request to create asset for farmer ID: {owner_id}")
        response = requests.post(url, headers=headers, files=multipart_data)
        if response.status_code == 201:
            asset_id = response.json().get("id")
            print(f"✅ Asset created successfully with ID: {asset_id}")
            return asset_id
        else:
            print(f"❌ Asset creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception occurred while creating asset: {e}")
        return None
