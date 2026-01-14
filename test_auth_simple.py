import requests
import sys

BASE_URL = "http://localhost:5001/api"

def test_workflow():
    session = requests.Session()
    
    # 1. Register new user
    username = "testuser_v2"
    password = "password123"
    print(f"Registering {username}...")
    try:
        resp = session.post(f"{BASE_URL}/auth/register", json={
            "username": username,
            "email": "test2@example.com",
            "password": password
        })
        if resp.status_code == 201:
            print("Registration success")
        elif resp.status_code == 400 and "already exists" in resp.text:
            print("User already exists, proceeding to login")
        else:
            print(f"Registration failed: {resp.status_code} {resp.text}")
            return
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # 2. Login
    print("Logging in...")
    resp = session.post(f"{BASE_URL}/auth/login", json={
        "username": username,
        "password": password
    })
    
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code} {resp.text}")
        return
        
    token = resp.json().get('access_token')
    print(f"Got token: {token[:20]}...")
    
    # 3. Access Protected Route (Run Code)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try running a simple python code
    payload = {
        "language": "python",
        "code": "class Solution:\n    def twoSum(self, nums, target):\n        return [0, 1]",
        "input": "[2,7,11,15]\n9"
    }
    
    print("Attempting to run code...")
    resp = requests.post(f"{BASE_URL}/problems/2/run", json=payload, headers=headers)
    
    if resp.status_code == 200:
        print("Run Code Success!")
        print(resp.json())
    else:
        print(f"Run Code Failed: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    test_workflow()
