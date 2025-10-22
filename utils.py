import json
import math
import os
import random
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

EXCEL_FILE_NAME = "PRCAs2.xlsx"
SHEET_NAME = "croppable_area_ids"
COLUMN_NAME = "croppable area ids"
google_api_key = "AIzaSyAwy--7hbQ9x-_rFT2lCi52o0rF0JvbA7E"


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
        # {"lat_range": (24.0, 49.0), "long_range": (-125.0, -66.0)},  # USA
        # {"lat_range": (-35.0, 37.0), "long_range": (-17.0, 51.0)},  # Africa
        # {"lat_range": (14.0, 33.0), "long_range": (-118.0, -86.0)},  # Mexico
        # {"lat_range": (51.3, 51.7), "long_range": (-0.5, 0.3)},  # London
        # {"lat_range": (36.0, 71.0), "long_range": (-10.0, 40.0)}  # Europe
    ]
    country = random.choice(countries)
    lat = round(random.uniform(*country["lat_range"]), 6)
    long = round(random.uniform(*country["long_range"]), 6)
    return lat, long



def get_random_location(region):
    # Define safe bounding boxes for each Indian state
    state_bounds = {
        "karnataka": (11.5, 18.5, 74.0, 78.5),
        "andhra pradesh": (13.0, 19.5, 77.0, 85.0),
        "telangana": (15.5, 19.0, 77.0, 81.5),
        "tamil nadu": (8.0, 13.5, 76.0, 80.5),
        "kerala": (8.0, 12.9, 74.8, 77.5),
        "west bengal": (21.5, 27.5, 85.8, 89.9),
        "uttar pradesh": (24.0, 29.5, 77.0, 84.5),
        "bihar": (24.3, 27.5, 83.0, 88.0),
        "maharashtra": (15.6, 22.0, 72.5, 80.9),
        "gujarat": (20.0, 24.7, 68.0, 74.5),
        "rajasthan": (23.0, 29.9, 69.3, 78.0),
        "madhya pradesh": (21.0, 26.8, 74.0, 82.0),
        "odisha": (18.5, 22.8, 81.5, 87.5),
        "punjab": (29.5, 32.5, 73.8, 76.9)
    }

    region = region.lower().strip()

    # ✅ If region = "india", randomly choose one of the states
    if region == "india":
        region = random.choice(list(state_bounds.keys()))

    if region not in state_bounds:
        raise ValueError(f"❌ Unknown region '{region}'. Valid options are: {list(state_bounds.keys()) + ['india']}")

    lat_min, lat_max, lon_min, lon_max = state_bounds[region]
    latitude = round(random.uniform(lat_min, lat_max), 6)
    longitude = round(random.uniform(lon_min, lon_max), 6)

    return {
        "place": region,
        "latitude": latitude,
        "longitude": longitude
    }


# Helper to write CA IDs to Excel
def append_ca_ids_to_excel(ca_ids):
    file_path = r"C:\Users\rajasekhar.palleti\Downloads\\" + EXCEL_FILE_NAME
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
    else:
        df = pd.DataFrame(columns=[COLUMN_NAME])

    new_df = pd.DataFrame(ca_ids, columns=[COLUMN_NAME])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_excel(file_path, index=False, sheet_name=SHEET_NAME)

def get_excel_path():
    """
    Return the full Excel file path and sheet name.
    """
    full_path = os.path.join(r"C:\Users\rajasekhar.palleti\Downloads", EXCEL_FILE_NAME)
    return full_path, SHEET_NAME


# -----------------------------------------------------------------------------
# Utility: random_sowing_date
# Returns a random date string between 2025-08-01 (inclusive) and today (UTC)
# Format: YYYY-MM-DDT00:00:00.000Z
# -----------------------------------------------------------------------------

def random_sowing_date(start_date_str: str = "2025-08-01") -> str:

    # Parse start date
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    # Use UTC today
    end_date = datetime.now(timezone.utc).date()

    if end_date < start_date:
        raise ValueError(f"End date ({end_date}) is before start date ({start_date}).")

    total_days = (end_date - start_date).days
    # Pick random offset in days (0..total_days)
    offset = random.randint(0, total_days)
    chosen = start_date + timedelta(days=offset)

    # Return formatted string with zeroed time and milliseconds as .000Z
    return chosen.strftime("%Y-%m-%dT00:00:00.000Z")

def get_address_from_latlng(lat: float, lng: float, api_key: str = None, language: str = "en") -> dict:
    # Base template
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

    if not api_key:
        # No API key provided: return the template so callers can still proceed offline.
        return addr

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"latlng": f"{lat},{lng}", "key": api_key, "language": language}

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
    except Exception as e:
        raise ValueError(f"Error calling Geocoding API: {e}")

    status = data.get("status")
    if status != "OK":
        # Propagate API errors with helpful message
        err_msg = data.get("error_message") or ""
        raise ValueError(f"Geocoding API error: {status}. {err_msg}")

    results = data.get("results", [])
    if not results:
        return addr

    # Use the most relevant result (first)
    primary = results[0]
    addr["formattedAddress"] = primary.get("formatted_address", "")
    addr["placeId"] = primary.get("place_id", "")

    # Parse address components
    for comp in primary.get("address_components", []):
        types = comp.get("types", [])
        long_name = comp.get("long_name", "")

        if "country" in types:
            addr["country"] = long_name
        if "administrative_area_level_1" in types:
            addr["administrativeAreaLevel1"] = long_name
        if "administrative_area_level_2" in types:
            addr["administrativeAreaLevel2"] = long_name
        if "locality" in types:
            addr["locality"] = long_name
        if "sublocality_level_1" in types or "sublocality" in types:
            # prefer level_1 when available
            if not addr["sublocalityLevel1"]:
                addr["sublocalityLevel1"] = long_name
        if "sublocality_level_2" in types:
            addr["sublocalityLevel2"] = long_name
        if "postal_code" in types:
            addr["postalCode"] = long_name
        if "street_number" in types:
            addr["houseNo"] = long_name
        if "route" in types:
            # route is typically the street name; store as buildingName to match payload
            if not addr["buildingName"]:
                addr["buildingName"] = long_name
        if any(t in types for t in ("premise", "establishment", "point_of_interest", "neighborhood")):
            # Use first matching as landmark if not already set
            if not addr["landmark"]:
                addr["landmark"] = long_name

    return addr

# -------------------------------
# Utility: Generate 1-acre polygon around lat/lon
# -------------------------------
def generate_polygon_near_point(lat: float, lon: float, area_acre: float = 1.0) -> dict:
    """
    Generates a roughly square polygon of given area (in acres) around the given lat/lon.
    Output is in GeoJSON MultiPolygon format.
    """
    # 1 acre = 4046.86 square meters
    side_m = math.sqrt(area_acre * 4046.86)
    half_side = side_m / 2.0

    # Convert meters to degrees (approx)
    lat_offset = half_side / 111320  # 1 deg latitude ≈ 111.32 km
    lon_offset = half_side / (111320 * math.cos(math.radians(lat)))

    # Small random variation so each area looks different
    lat += random.uniform(-0.0001, 0.0001)
    lon += random.uniform(-0.0001, 0.0001)

    # Define 4 corners of the square polygon
    coordinates = [
        [lon - lon_offset, lat - lat_offset],
        [lon + lon_offset, lat - lat_offset],
        [lon + lon_offset, lat + lat_offset],
        [lon - lon_offset, lat + lat_offset],
        [lon - lon_offset, lat - lat_offset],  # close the polygon
    ]

    geo_info = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [[coordinates]]
            },
            "properties": {}
        }]
    }
    # print (f"📐 Generated polygon coordinates: {coordinates}")
    return geo_info


# -------------------------------
# Utility: Perform Area Audit for Croppable Areas
# -------------------------------
def perform_area_audit(ca_excel_path, sheet_name, token, google_api_key):
    """
    Reads CA IDs from Excel and performs area audit by:
    1. Getting location from CropIn API
    2. Converting location to coordinates (Google API)
    3. Generating 1-acre polygon
    4. Sending PUT area-audit update
    """

    base_get_url = "https://cloud.cropin.in/services/farm/api/croppable-areas/"
    put_url = "https://cloud.cropin.in/services/farm/api/croppable-areas/area-audit"

    df = pd.read_excel(ca_excel_path, sheet_name=sheet_name)
    ca_ids = df["croppable area ids"].dropna().astype(int).tolist()

    headers = {"Authorization": f"Bearer {token}"}

    status_list = []
    message_list = []

    for ca_id in ca_ids:
        print(f"\n🔹 Processing Croppable Area ID: {ca_id}")
        try:
            # Step 1: GET CA details
            get_resp = requests.get(f"{base_get_url}{ca_id}", headers=headers, timeout=20)
            get_data = get_resp.json()
            if get_resp.status_code != 200:
                raise ValueError(f"GET failed: {get_data}")

            CA_data = get_data.get("data", {})
            location = CA_data.get("location")
            if not location:
               print(f"⚠️ Skipping CA ID {ca_id}: missing 'location' in CA data")
               status_list.append("Skipped")
               message_list.append("Missing 'location' in CA data")
               continue

            print(f"📍 Location: {location}")

            # Step 2: Get coordinates from Google API
            g_url = f"https://maps.googleapis.com/maps/api/geocode/json"
            params = {"address": location, "key": google_api_key}
            g_resp = requests.get(g_url, params=params, timeout=10)
            g_data = g_resp.json()

            if g_data.get("status") != "OK" or not g_data.get("results"):
                raise ValueError(f"Google API failed: {g_data.get('status')}")

            result = g_data["results"][0]["geometry"]["location"]
            lat, lng = result["lat"], result["lng"]
            print(f"📍 Coordinates: ({lat}, {lng})")

            # Step 3: Generate 1-acre polygon
            geo_info = generate_polygon_near_point(lat, lng)

            # Step 4: Build DTO
            audited_count = 1.0  # Always 1 acre
            if "areaAudit" not in get_data:
                get_data["areaAudit"] = None

            areaAudit = {
                "id": None,
                "geoInfo": geo_info,
                "latitude": lat,
                "longitude": lng,
                "altitude": None
            }

            auditedArea = {
                "count": audited_count,
                "unit": "Acre"
            }

            get_data["areaAudit"] = areaAudit
            get_data["latitude"] = None
            get_data["longitude"] = None
            get_data["auditedArea"] = auditedArea
            get_data["cropAudited"] = True

            # print(get_data)

            # Step 5: PUT request
            dto = get_data

            put_resp = requests.put(put_url, headers=headers, json = dto, timeout=30)
            if put_resp.status_code in (200, 201):
                print("✅ Area Audit Updated Successfully!")
                status_list.append("Success")
                message_list.append("")
            else:
                print(f"❌ Failed to update area audit: {put_resp.text}")
                status_list.append("Failed")
                message_list.append(put_resp.text)

        except Exception as e:
            print(f"⚠️ Error for CA ID {ca_id}: {e}")
            status_list.append("Error")
            message_list.append(str(e))

        # Delay between requests to avoid throttling
        time.sleep(1)

    # Step 6: Write results back to Excel
    df["status"] = status_list
    df["message"] = message_list
    df.to_excel(ca_excel_path, index=False, sheet_name=sheet_name)
    print("\n✅ Area Audit Process Completed & Results Saved to Excel.")

def process_pr_for_cas(file_path: str, sheet_name: str, token: str):
    """
    Process Plot Risk (PR) for Croppable Area IDs from an Excel sheet.

    Args:
        file_path (str): Path to the Excel file containing CA IDs.
        sheet_name (str): Sheet name in the Excel file.
        token (str): CropIn API access token.

    Updates the same Excel sheet with:
        - status
        - Failed in Response
        - srPlotid
        - Plot_risk_response
    """

    if not token:
        raise ValueError("Access token is missing. Cannot proceed.")

    # Load Excel
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Ensure necessary columns exist
    columns_to_check = ["status", "Failed in Response", "srPlotid", "Plot_risk_response"]
    for col in columns_to_check:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype(str)

    # API endpoint
    plot_risk_url = "https://cloud.cropin.in/services/farm/api/croppable-areas/plot-risk/batch"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def extract_sr_plot_id(response_json):
        if "srPlotDetails" in response_json:
            for details in response_json["srPlotDetails"].values():
                return details.get("srPlotId")
        for key, value in response_json.items():
            if isinstance(value, list):
                for item in value:
                    if "srPlotId" in item:
                        return item["srPlotId"]
        return "N/A"

    # Iterate over rows
    for index, row in df.iterrows():
        try:
            croppable_area_id = str(row.iloc[0]).strip()
            print(f"🔄 Processing row {index + 1}: CroppableAreaId = {croppable_area_id}")

            # Plot Risk payload
            plot_risk_payload = [{"croppableAreaId": croppable_area_id, "farmerId": None}]

            # Call Plot Risk API
            try:
                response = requests.post(plot_risk_url, headers=headers, json=plot_risk_payload, timeout=20)
                response.raise_for_status()
                resp_json = response.json()
                time.sleep(2)

                df.at[index, "Plot_risk_response"] = json.dumps(resp_json)
                df.at[index, "srPlotid"] = extract_sr_plot_id(resp_json)
                print(f"✅ Extracted srPlotId: {df.at[index, 'srPlotid']}")

            except requests.exceptions.RequestException as req_err:
                error_msg = str(req_err)
                df.at[index, "Plot_risk_response"] = error_msg
                df.at[index, "srPlotid"] = "N/A"
                print(f"❌ Plot Risk API request failed: {error_msg}")
                df.at[index, "status"] = "❌ Failed"
                continue

            # Determine status
            sr_plot_details = resp_json.get("srPlotDetails", {})
            failed_found = False

            for key, val in sr_plot_details.items():
                if val.get("status") == "FAILED":
                    failed_found = True
                    df.at[index, "Failed in Response"] = f"❌ Failed: {val.get('message', 'No details')}"
                    print(f"❌ Status for {key}: {val['status']} - {val.get('message', 'No message')}")

            if not failed_found:
                df.at[index, "Failed in Response"] = "✅ Success"
                df.at[index, "status"] = "✅ Success"

            time.sleep(0.5)

        except Exception as e:
            df.at[index, "status"] = f"⚠️ Error: {str(e)}"
            print(f"⚠️ Error in row {index + 1}: {str(e)}")
            time.sleep(0.5)

    # Save back to Excel
    with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    print("🎯 PR Processing completed. Excel updated successfully.")
