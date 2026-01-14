import requests
import json

BASE_URL = 'http://localhost:5001/api'

def test_run():
    # 1. Register/Login
    username = "testuser" + str(id(object())) # unique per run
    password = "password"
    
    # Register
    requests.post(f'{BASE_URL}/auth/register', json={
        'username': username,
        'email': f'{username}@example.com',
        'password': password
    })
    
    # Login
    resp = requests.post(f'{BASE_URL}/auth/login', json={
        'username': username,
        'password': password
    })
    
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return

    print(f"Login Response: {resp.json()}")
    token = resp.json().get('token')
    if not token:
        token = resp.json().get('access_token') # Flask-JWT-Extended usually returns access_token
    
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Run Code
    code = """
class Solution:
    def twoSum(self, nums, target):
        lookup = {}
        for i, num in enumerate(nums):
            if target - num in lookup:
                return [lookup[target - num], i]
            lookup[num] = i
        return []
"""
    lang = "python"
    inp = "[2,7,11,15]\n9"
    
    payload = {
        "code": code,
        "language": lang,
        "input": inp
    }
    
    print("Sending run request...")
    resp = requests.post(f'{BASE_URL}/problems/1/run', json=payload, headers=headers)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    test_run()
