import os
import requests
from keycloak import KeycloakOpenID

# Config matching environment
KEYCLOAK_URL = os.environ.get('KEYCLOAK_INTERNAL_URL', 'http://keycloak:8080/')
REALM_NAME = "scd-leetcode"
USER_CLIENT_ID = "scd-leetcode-client"
USER_USERNAME = "student"
# USER_PASSWORD = "student" 
# Wait, I initialized the user with password "student" in init_keycloak.py?
# Let's check init_keycloak.py content for user creation.

def get_user_token():
    keycloak_user_client = KeycloakOpenID(
        server_url=KEYCLOAK_URL,
        client_id=USER_CLIENT_ID,
        realm_name=REALM_NAME,
        verify=False
    )
    # Password set in init_keycloak.py was "student"
    # Connect to Keycloak via Host Gateway to simulate external access
    keycloak_user_client = KeycloakOpenID(
        server_url="http://host.docker.internal:8081/",
        client_id=USER_CLIENT_ID,
        realm_name=REALM_NAME,
        verify=False
    )
    return keycloak_user_client.token("student", "student")['access_token']

def test_run_endpoint():
    try:
        print("1. Getting Token...")
        token = get_user_token()
        print(f"   Token: {token[:20]}...")
    except Exception as e:
        print(f"   Failed to get token: {e}")
        return

    print("2. Calling API...")
    headers = {"Authorization": f"Bearer {token}"}
    # Flask is running on port 5001 in container? 
    # From docker-compose, server ports: "5001:5001". Inside container runs on 5001.
    # If I run this script inside server container, I use localhost:5001.
    url = "http://localhost:5001/api/problems/1/run"
    
    # Payload for run? Need to check what it expects.
    # Usually code and language.
    payload = {
        "code": "print('hello')",
        "language": "python"
    }

    resp = requests.post(url, json=payload, headers=headers)
    print(f"   Response Status: {resp.status_code}")
    print(f"   Response Body: {resp.text}")

if __name__ == "__main__":
    test_run_endpoint()
