import requests

from utils import get_random_location

def get_address_from_latlng(lat: float, lng: float, api_key: str, language: str = "en") -> dict:
    """
    Fetch detailed address info from latitude and longitude using Google Maps Geocoding API.

    Args:
        lat (float): Latitude
        lng (float): Longitude
        api_key (str): Google Maps API Key
        language (str): Response language (default 'en')

    Returns:
        dict: Address details with fields populated from the API response
    """

    # Initialize address structure
    addr = {
        "country": "",
        "formattedAddress": "",
        "administrativeAreaLevel1": "",
        "locality": "",
        "administrativeAreaLevel2": "",
        "sublocalityLevel1": "",
        "sublocalityLevel2": "",
        "landmark": "",
        "postalCode": "",
        "houseNo": "",
        "buildingName": "",
        "placeId": "",
        "latitude": lat,
        "longitude": lng,
    }

    # Construct API URL
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{lat},{lng}",
        "key": api_key,
        "language": language,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK" or not data.get("results"):
            print(f"⚠️ No valid address found for ({lat}, {lng}). Status: {data.get('status')}")
            return addr

        # Take the first (most relevant) result
        primary_result = data["results"][0]

        addr["formattedAddress"] = primary_result.get("formatted_address", "")
        addr["placeId"] = primary_result.get("place_id", "")

        # Parse address components
        for comp in primary_result.get("address_components", []):
            types = comp.get("types", [])
            long_name = comp.get("long_name", "")

            if "country" in types:
                addr["country"] = long_name
            elif "administrative_area_level_1" in types:
                addr["administrativeAreaLevel1"] = long_name
            elif "administrative_area_level_2" in types:
                addr["administrativeAreaLevel2"] = long_name
            elif "locality" in types:
                addr["locality"] = long_name
            elif "sublocality_level_1" in types or "sublocality" in types:
                if not addr["sublocalityLevel1"]:
                    addr["sublocalityLevel1"] = long_name
            elif "sublocality_level_2" in types:
                addr["sublocalityLevel2"] = long_name
            elif "postal_code" in types:
                addr["postalCode"] = long_name
            elif "street_number" in types:
                addr["houseNo"] = long_name
            elif "route" in types:
                if not addr["buildingName"]:
                    addr["buildingName"] = long_name
            elif any(t in types for t in ["premise", "establishment", "point_of_interest", "neighborhood"]):
                if not addr["landmark"]:
                    addr["landmark"] = long_name

        print(f"✅ Address fetched successfully for ({lat}, {lng})")
        return addr

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request failed: {e}")
        return addr
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        return addr


# Example usage
if __name__ == "__main__":
    api_key = "AIzaSyAwy--7hbQ9x-_rFT2lCi52o0rF0JvbA7E"  # Replace with your valid key
    loc_details = get_random_location("india")
    place = loc_details["place"]
    lat = loc_details["latitude"]
    lng = loc_details["longitude"]

    print(f"🌍 Random Location: {place} ({lat}, {lng})")
    address_data = get_address_from_latlng(lat, lng, api_key)
    print("📍 Address Details:")
    for key, value in address_data.items():
        print(f"{key}: {value}")
