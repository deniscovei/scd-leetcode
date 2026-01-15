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
    
    # 1. Submit solution for Problem 1
    submit_url = "http://localhost:5001/api/problems/1/submit"
    code = """
import json
class Solution:
    def twoSum(self, nums, target):
        lookup = {}
        for i, num in enumerate(nums):
            if target - num in lookup:
                return [lookup[target - num], i]
            lookup[num] = i
        return []
"""
    payload = {
        "language": "python",
        "code": code
    }
    print("   Submitting solution...")
    submit_resp = requests.post(submit_url, json=payload, headers=headers)
    print(f"   Submit Status: {submit_resp.status_code}")
    print(f"   Submit Result: {submit_resp.text}")

    # 2. Check problems list for status
    import json
    url = "http://localhost:5001/api/problems/"
    
    response = requests.get(url, headers=headers)
    print(f"List Status: {response.status_code}")
    # Find problem 1 status
    problems = response.json()
    for p in problems:
        if p['id'] == 1:
            print(f"   Problem 1 Status: {p.get('status')}")

if __name__ == "__main__":
    test_run_endpoint()
