import requests
import json
from datetime import datetime
import time
from utils import generate_timestamp_millis
from utils import random_lat_long

def create_asset(token, owner_id):
    url = "https://cloud.cropin.in/services/farm/api/assets"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    timestamp = generate_timestamp_millis()

    lat, long = random_lat_long()

    payload = {
        "data": {},
        "images": {},
        "companyStatus": "ACTIVE",
        "declaredArea": {
            "enableConversion": "true",
            "unit": "ACRE",
            "count": 10
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
            "id": 1107
        },
        "address": {
            "country": "India",
            "formattedAddress": "Default address name given by API",
            "administrativeAreaLevel1": "",
            "locality": "Bengaluru",
            "administrativeAreaLevel2": "",
            "sublocalityLevel1": "",
            "sublocalityLevel2": "",
            "landmark": "",
            "postalCode": "",
            "houseNo": "",
            "buildingName": "",
            "placeId": "ChIJ4b8AQvwUrjsRtShU44e_fpg",
            "latitude": lat,
            "longitude": long
        }
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
