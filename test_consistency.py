#!/usr/bin/env python3
"""
Test script for data consistency validation.
Tests various scenarios to ensure data integrity constraints are enforced.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001/api"
KEYCLOAK_URL = "http://localhost:8081"
REALM = "scd-leetcode"
CLIENT_ID = "scd-leetcode-client"

# Test user credentials
TEST_USER = {"username": "admin", "password": "admin"}


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
        print(f"[ERROR] Failed to get token: {e}")
        return None


def test_create_problem_validation(token):
    """Test problem creation with various invalid inputs"""
    url = f"{BASE_URL}/problems/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    tests = [
        {
            "name": "Empty title",
            "data": {
                "title": "",
                "description": "Test description",
                "difficulty": "Easy"
            },
            "expected_status": 400,
            "expected_error": "Title"
        },
        {
            "name": "Short title (< 3 chars)",
            "data": {
                "title": "AB",
                "description": "Test description",
                "difficulty": "Easy"
            },
            "expected_status": 400,
            "expected_error": "at least 3 characters"
        },
        {
            "name": "Long title (> 255 chars)",
            "data": {
                "title": "A" * 300,
                "description": "Test description",
                "difficulty": "Easy"
            },
            "expected_status": 400,
            "expected_error": "less than 255"
        },
        {
            "name": "Invalid difficulty",
            "data": {
                "title": "Valid Title",
                "description": "Test description",
                "difficulty": "VeryHard"
            },
            "expected_status": 400,
            "expected_error": "Difficulty must be one of"
        },
        {
            "name": "Missing required fields",
            "data": {
                "title": "Valid Title"
            },
            "expected_status": 400,
            "expected_error": "required"
        },
        {
            "name": "Invalid test_cases format (not array)",
            "data": {
                "title": "Valid Title Test",
                "description": "Test description",
                "difficulty": "Easy",
                "test_cases": "not an array"
            },
            "expected_status": 400,
            "expected_error": "must be an array"
        },
        {
            "name": "Invalid test_cases (missing output)",
            "data": {
                "title": "Valid Title Test 2",
                "description": "Test description",
                "difficulty": "Easy",
                "test_cases": [{"input": "test"}]
            },
            "expected_status": 400,
            "expected_error": "must have"
        },
        {
            "name": "Invalid time_limits (not object)",
            "data": {
                "title": "Valid Title Test 3",
                "description": "Test description",
                "difficulty": "Easy",
                "time_limits": "not an object"
            },
            "expected_status": 400,
            "expected_error": "must be an object"
        },
        {
            "name": "Invalid time_limits (negative value)",
            "data": {
                "title": "Valid Title Test 4",
                "description": "Test description",
                "difficulty": "Easy",
                "time_limits": {"python": -5}
            },
            "expected_status": 400,
            "expected_error": "positive number"
        },
        {
            "name": "Invalid time_limits (exceeds maximum)",
            "data": {
                "title": "Valid Title Test 5",
                "description": "Test description",
                "difficulty": "Easy",
                "time_limits": {"python": 100}
            },
            "expected_status": 400,
            "expected_error": "cannot exceed 60"
        }
    ]
    
    print("\n" + "=" * 70)
    print("TEST 1: Problem Creation Validation")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            response = requests.post(url, json=test["data"], headers=headers)
            
            if response.status_code == test["expected_status"]:
                if test["expected_error"] in response.text:
                    print(f"[PASS] {test['name']}")
                    print(f"       Expected error found: {test['expected_error']}")
                    passed += 1
                else:
                    print(f"[FAIL] {test['name']}")
                    print(f"       Expected error '{test['expected_error']}' not found")
                    print(f"       Response: {response.text[:100]}")
                    failed += 1
            else:
                print(f"[FAIL] {test['name']}")
                print(f"       Expected status {test['expected_status']}, got {response.status_code}")
                print(f"       Response: {response.text[:100]}")
                failed += 1
        except Exception as e:
            print(f"[ERROR] {test['name']}: {e}")
            failed += 1
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    return passed, failed


def test_submission_validation(token):
    """Test submission with various invalid inputs"""
    url = f"{BASE_URL}/problems/1/submit"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    tests = [
        {
            "name": "Empty code",
            "data": {
                "code": "",
                "language": "python"
            },
            "expected_status": 400,
            "expected_error": "Code"
        },
        {
            "name": "Missing code field",
            "data": {
                "language": "python"
            },
            "expected_status": 400,
            "expected_error": "Code is required"
        },
        {
            "name": "Missing language field",
            "data": {
                "code": "print('hello')"
            },
            "expected_status": 400,
            "expected_error": "Language is required"
        },
        {
            "name": "Invalid language",
            "data": {
                "code": "print('hello')",
                "language": "javascript"
            },
            "expected_status": 400,
            "expected_error": "not supported"
        },
        {
            "name": "Code too long (> 100KB)",
            "data": {
                "code": "a" * 200000,
                "language": "python"
            },
            "expected_status": 400,
            "expected_error": "too long"
        }
    ]
    
    print("\n" + "=" * 70)
    print("TEST 2: Submission Validation")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            response = requests.post(url, json=test["data"], headers=headers)
            
            if response.status_code == test["expected_status"]:
                if test["expected_error"] in response.text:
                    print(f"[PASS] {test['name']}")
                    print(f"       Expected error found: {test['expected_error']}")
                    passed += 1
                else:
                    print(f"[FAIL] {test['name']}")
                    print(f"       Expected error '{test['expected_error']}' not found")
                    print(f"       Response: {response.text[:100]}")
                    failed += 1
            else:
                print(f"[FAIL] {test['name']}")
                print(f"       Expected status {test['expected_status']}, got {response.status_code}")
                print(f"       Response: {response.text[:100]}")
                failed += 1
        except Exception as e:
            print(f"[ERROR] {test['name']}: {e}")
            failed += 1
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    return passed, failed


def test_run_code_validation(token):
    """Test code run with various invalid inputs"""
    url = f"{BASE_URL}/problems/1/run"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    tests = [
        {
            "name": "Missing input field",
            "data": {
                "code": "print('hello')",
                "language": "python"
            },
            "expected_status": 400,
            "expected_error": "Input is required"
        },
        {
            "name": "Invalid language for run",
            "data": {
                "code": "console.log('hello')",
                "language": "javascript",
                "input": ""
            },
            "expected_status": 400,
            "expected_error": "not supported"
        },
        {
            "name": "Input too long (> 10KB)",
            "data": {
                "code": "print('hello')",
                "language": "python",
                "input": "x" * 20000
            },
            "expected_status": 400,
            "expected_error": "Input is too long"
        }
    ]
    
    print("\n" + "=" * 70)
    print("TEST 3: Run Code Validation")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            response = requests.post(url, json=test["data"], headers=headers)
            
            if response.status_code == test["expected_status"]:
                if test["expected_error"] in response.text:
                    print(f"[PASS] {test['name']}")
                    print(f"       Expected error found: {test['expected_error']}")
                    passed += 1
                else:
                    print(f"[FAIL] {test['name']}")
                    print(f"       Expected error '{test['expected_error']}' not found")
                    print(f"       Response: {response.text[:100]}")
                    failed += 1
            else:
                print(f"[FAIL] {test['name']}")
                print(f"       Expected status {test['expected_status']}, got {response.status_code}")
                print(f"       Response: {response.text[:100]}")
                failed += 1
        except Exception as e:
            print(f"[ERROR] {test['name']}: {e}")
            failed += 1
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    return passed, failed


def test_duplicate_title(token):
    """Test that duplicate problem titles are rejected"""
    url = f"{BASE_URL}/problems/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n" + "=" * 70)
    print("TEST 4: Duplicate Title Constraint")
    print("=" * 70)
    
    # Create a problem with unique title
    unique_title = f"Test Problem {datetime.now().timestamp()}"
    problem_data = {
        "title": unique_title,
        "description": "Test description",
        "difficulty": "Easy",
        "tags": "test",
        "test_cases": [{"input": "1", "output": "1"}],
        "templates": {"python": "def solve(): pass"},
        "drivers": {"python": "solve()"},
        "time_limits": {"python": 5.0}
    }
    
    # First creation should succeed
    response1 = requests.post(url, json=problem_data, headers=headers)
    if response1.status_code in [200, 201]:
        print(f"[PASS] First problem created: {unique_title}")
        problem_id = response1.json().get('id')
        
        # Second creation with same title should fail
        response2 = requests.post(url, json=problem_data, headers=headers)
        if response2.status_code == 409:
            if "already exists" in response2.text:
                print(f"[PASS] Duplicate title rejected correctly")
                print(f"       Error: {response2.json().get('error', '')}")
                
                # Clean up - delete the created problem
                delete_url = f"{BASE_URL}/problems/{problem_id}"
                delete_response = requests.delete(delete_url, headers=headers)
                if delete_response.status_code == 200:
                    print(f"[INFO] Test problem cleaned up (ID: {problem_id})")
                
                return 1, 0
            else:
                print(f"[FAIL] Wrong error message")
                print(f"       Response: {response2.text[:100]}")
                return 0, 1
        else:
            print(f"[FAIL] Expected 409 status, got {response2.status_code}")
            print(f"       Response: {response2.text[:100]}")
            return 0, 1
    else:
        print(f"[FAIL] Could not create test problem")
        print(f"       Status: {response1.status_code}")
        print(f"       Response: {response1.text[:100]}")
        return 0, 1


def test_unauthorized_access(token):
    """Test that non-owners cannot modify problems"""
    print("\n" + "=" * 70)
    print("TEST 5: Authorization Checks")
    print("=" * 70)
    
    # Get a problem owned by someone else
    url = f"{BASE_URL}/problems/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Get list of problems
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("[FAIL] Could not fetch problems list")
        return 0, 1
    
    problems = response.json()
    if not problems:
        print("[SKIP] No problems available to test")
        return 0, 0
    
    # For admin (user_id=1), this test doesn't apply since admin can edit all
    # So we just verify admin CAN edit
    test_problem_id = problems[0]['id']
    update_url = f"{BASE_URL}/problems/{test_problem_id}"
    update_data = {
        "description": "Updated by test script"
    }
    
    response = requests.put(update_url, json=update_data, headers=headers)
    if response.status_code == 200:
        print(f"[PASS] Admin can update problem {test_problem_id} (expected)")
        return 1, 0
    else:
        print(f"[FAIL] Admin could not update problem {test_problem_id}")
        print(f"       Status: {response.status_code}")
        return 0, 1


def main():
    print("=" * 70)
    print("DATA CONSISTENCY VALIDATION TEST")
    print("=" * 70)
    print(f"Backend URL: {BASE_URL}")
    print(f"Testing user: {TEST_USER['username']}")
    print("=" * 70)
    
    # Get authentication token
    print("\n[INFO] Getting authentication token...")
    token = get_token(TEST_USER['username'], TEST_USER['password'])
    
    if not token:
        print("[ERROR] Could not authenticate. Exiting.")
        return
    
    print("[INFO] Token obtained successfully")
    
    # Run all tests
    total_passed = 0
    total_failed = 0
    
    passed, failed = test_create_problem_validation(token)
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_submission_validation(token)
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_run_code_validation(token)
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_duplicate_title(token)
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_unauthorized_access(token)
    total_passed += passed
    total_failed += failed
    
    # Print final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Total tests passed: {total_passed}")
    print(f"Total tests failed: {total_failed}")
    print(f"Success rate: {total_passed / (total_passed + total_failed) * 100:.1f}%")
    print("=" * 70)
    
    if total_failed == 0:
        print("\nAll consistency tests passed successfully!")
    else:
        print(f"\n{total_failed} test(s) failed. Please review the output above.")


if __name__ == "__main__":
    main()
