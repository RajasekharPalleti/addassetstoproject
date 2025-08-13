import requests

def get_users_data(token, user_ids):
    users_data = []
    base_url = "https://cloud.cropin.in/services/user/api/users"

    for user_id in user_ids:
        url = f"{base_url}/{user_id}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            users_data.append(response.json())
        else:
            print(f"Failed to fetch data for user ID {user_id}: {response.status_code}")

    return users_data