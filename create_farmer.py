import requests
import json
from utils import generate_timestamp_millis, generate_random_mobile, random_lat_long


def create_farmer(token, assigned_users):
    url = "https://cloud.cropin.in/services/farm/api/farmers"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    timestamp = generate_timestamp_millis()
    mobile_number = generate_random_mobile()
    lat, long = random_lat_long()

    payload = {
        "status": "DISABLE",
        "data": {
            "mobileNumber": mobile_number,
            "countryCode": "+91"
            # "tags": [289201, 13251]
        },
        "images": {},
        "declaredArea": {
            "enableConversion": "true",
            "unit": "HECTARE",
        },
        "firstName": f"Raja_Bulk_API_Farmer_{timestamp}",
        "farmerCode": timestamp,
        "assignedTo": assigned_users,
        "address": {
            "country": "India",
            "formattedAddress": "BTM 2nd Stage, BTM Layout, Bengaluru, Karnataka, India",
            "houseNo": "",
            "buildingName": "",
            "administrativeAreaLevel1": "Karnataka",
            "locality": "Bengaluru",
            "administrativeAreaLevel2": "Bangalore Division",
            "sublocalityLevel1": "BTM Layout",
            "sublocalityLevel2": "BTM 2nd Stage",
            "landmark": "",
            "postalCode": "",
            "placeId": "ChIJ4b8AQvwUrjsRtShU44e_fpg",
            "latitude": lat,
            "longitude": long
        },
        # "isGDPRCompliant": True
    }
    # print(payload)

    # Convert to multipart format for API
    multipart_data = {
        "dto": (None, json.dumps(payload), "application/json")
    }

    try:
        print(f"📤 Sending request for farmer: {payload['firstName']}")
        response = requests.post(url, headers=headers, files=multipart_data)
        if response.status_code == 201:
            farmer_id = response.json().get("id")
            print(f"✅ Farmer created successfully with ID: {farmer_id}")
            return farmer_id
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return None