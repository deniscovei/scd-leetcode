#!/usr/bin/env python3
"""
Test script for concurrent submissions to the same problem.
Simulates 2 users submitting solutions at the same time.
"""

import requests
import threading
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001/api"
KEYCLOAK_URL = "http://localhost:8081"
REALM = "scd-leetcode"
CLIENT_ID = "scd-leetcode-client"

# Test users credentials (using pre-created Keycloak users)
USERS = [
    {"username": "student", "password": "student"},
    {"username": "admin", "password": "admin"}
]

PROBLEM_ID = 1  # Sum of Two Numbers

# Test code for each user
USER_CODES = {
    "student": """class Solution:
    def twoSum(self, nums, target):
        # Student's solution (brute force - O(n^2))
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []
""",
    "admin": """class Solution:
    def twoSum(self, nums, target):
        # Admin's solution (optimized with hashmap - O(n))
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
"""
}


def get_token(username, password):
    """Get access token from Keycloak"""
    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    
    data = {
        'client_id': CLIENT_ID,
        'username': username,
        'password': password,
        'grant_type': 'password'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"[ERROR] Failed to get token for {username}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"        Response: {e.response.text[:200]}")
        return None


def submit_solution(user_info, barrier, results):
    """Submit a solution for a user"""
    username = user_info['username']
    password = user_info['password']
    
    print(f"[{username}] Getting authentication token...")
    token = get_token(username, password)
    
    if not token:
        results[username] = {"success": False, "error": "Authentication failed"}
        return
    
    print(f"[{username}] Token obtained")
    
    # Wait for all threads to be ready
    print(f"[{username}] Waiting at barrier...")
    barrier.wait()
    
    # All threads start at the same time now
    start_time = time.time()
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{username}] Submitting solution at {timestamp}...")
    
    url = f"{BASE_URL}/problems/{PROBLEM_ID}/submit"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'code': USER_CODES[username],
        'language': 'python'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('status', 'unknown')
            submission_id = result.get('submission_id', 'N/A')
            
            print(f"[{username}] Submission successful!")
            print(f"         Submission ID: {submission_id}")
            print(f"         Status: {status}")
            print(f"         Response time: {elapsed:.3f}s")
            
            results[username] = {
                "success": True,
                "submission_id": submission_id,
                "status": status,
                "response_time": elapsed
            }
        else:
            error_msg = response.json().get('error', response.text)
            print(f"[{username}] Submission failed!")
            print(f"         Status code: {response.status_code}")
            print(f"         Error: {error_msg}")
            
            results[username] = {
                "success": False,
                "error": error_msg,
                "status_code": response.status_code
            }
    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[{username}] Exception occurred: {e}")
        results[username] = {
            "success": False,
            "error": str(e),
            "response_time": elapsed
        }


def main():
    print("=" * 70)
    print("CONCURRENT SUBMISSION TEST")
    print("=" * 70)
    print(f"Testing problem ID: {PROBLEM_ID}")
    print(f"Number of concurrent users: {len(USERS)}")
    print(f"Backend URL: {BASE_URL}")
    print("=" * 70)
    print()
    
    # Barrier to synchronize thread start
    barrier = threading.Barrier(len(USERS))
    results = {}
    threads = []
    
    # Create threads for each user
    for user in USERS:
        thread = threading.Thread(
            target=submit_solution,
            args=(user, barrier, results)
        )
        threads.append(thread)
    
    # Start all threads
    print("Starting concurrent submission test...\n")
    start_time = time.time()
    
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    successful = sum(1 for r in results.values() if r.get('success'))
    failed = len(results) - successful
    
    print(f"Successful submissions: {successful}/{len(USERS)}")
    print(f"Failed submissions: {failed}/{len(USERS)}")
    print(f"Total test duration: {total_time:.3f}s")
    print()
    
    for username, result in results.items():
        print(f"User: {username}")
        if result.get('success'):
            print(f"      Success")
            print(f"      Submission ID: {result['submission_id']}")
            print(f"      Status: {result['status']}")
            print(f"      Response time: {result['response_time']:.3f}s")
        else:
            print(f"      Failed")
            print(f"      Error: {result.get('error', 'Unknown error')}")
            if 'status_code' in result:
                print(f"      Status code: {result['status_code']}")
        print()
    
    print("=" * 70)
    
    # Check for race conditions - only warn if we actually have duplicate IDs (not N/A)
    if successful == len(USERS):
        submission_ids = [r['submission_id'] for r in results.values() if r.get('success') and r['submission_id'] != 'N/A']
        if submission_ids:  # Only check if we have actual IDs
            if len(submission_ids) == len(set(submission_ids)):
                print("SUCCESS: All submissions have unique IDs - No race condition detected!")
            else:
                print("WARNING: Duplicate submission IDs detected - possible race condition!")
        else:
            print("NOTE: Submission IDs not returned in response (check database for verification)")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
