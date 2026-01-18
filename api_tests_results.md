# API Endpoint Tests - SCD.Code Platform

> **Test Date:** January 18, 2026  
> **Platform:** SCD LeetCode Clone with Distributed Architecture

---

## Table of Contents

1. [Service Status](#1-service-status)
2. [Authentication (Keycloak)](#2-authentication-keycloak)
3. [Problems API](#3-problems-api)
4. [Code Execution](#4-code-execution)
5. [Submissions API](#5-submissions-api)
6. [Ranking API](#6-ranking-api)
7. [Infrastructure Services](#7-infrastructure-services)
8. [Worker Load Balancing](#8-worker-load-balancing)

---

## 1. Service Status

### Check All Services

```bash
docker-compose ps
```

**Expected Output:**
```
         Name                        Command               State                        Ports
-------------------------------------------------------------------------------------------------------------------
scd-leetcode_client_1     docker-entrypoint.sh npm start   Up      0.0.0.0:3000->3000/tcp
scd-leetcode_db_1         docker-entrypoint.sh postgres    Up      0.0.0.0:5433->5432/tcp
scd-leetcode_keycloak_1   /opt/keycloak/bin/kc.sh st ...   Up      0.0.0.0:8081->8080/tcp, 8443/tcp
scd-leetcode_redis_1      docker-entrypoint.sh redis ...   Up      0.0.0.0:6379->6379/tcp
scd-leetcode_runner_1     python app.py                    Up      5000/tcp
scd-leetcode_runner_2     python app.py                    Up      5000/tcp
scd-leetcode_server_1     python run.py                    Up      0.0.0.0:5001->5001/tcp
scd-leetcode_traefik_1    /entrypoint.sh --api.insec ...   Up      0.0.0.0:80->80/tcp, 0.0.0.0:8888->8080/tcp
```

---

## 2. Authentication (Keycloak)

### 2.1 Get Access Token (Student User)

```bash
curl -s -X POST "http://localhost:8081/realms/scd-leetcode/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=scd-leetcode-client" \
  -d "username=student" \
  -d "password=student" | jq .
```

**Expected Output:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "expires_in": 300,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "not-before-policy": 0,
  "session_state": "...",
  "scope": "profile email"
}
```

### 2.2 Get Access Token (Admin User)

```bash
curl -s -X POST "http://localhost:8081/realms/scd-leetcode/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=scd-leetcode-client" \
  -d "username=admin" \
  -d "password=admin" | jq .
```

### 2.3 Get Access Token (Denis User)

```bash
curl -s -X POST "http://localhost:8081/realms/scd-leetcode/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=scd-leetcode-client" \
  -d "username=denis" \
  -d "password=denis" | jq .
```

---

## 3. Problems API

### 3.1 GET /api/problems/ - List All Problems (Public)

```bash
curl -s -X GET "http://localhost:5001/api/problems/" | jq .
```

**Expected Output:**
```json
[
  {
    "id": 1,
    "title": "Two Sum",
    "description": "Given an array of integers...",
    "difficulty": "Easy",
    "tags": "Array, Hash Table",
    "owner_id": 1,
    "owner_username": "admin",
    "status": "Todo"
  },
  {
    "id": 2,
    "title": "Sum of Two Numbers",
    "difficulty": "Easy",
    "tags": "Math, Basic",
    "owner_id": 1,
    "owner_username": "admin",
    "status": "Todo"
  },
  {
    "id": 4,
    "title": "Sum of Three Numbers",
    "difficulty": "Easy",
    "tags": "Math, Basic",
    "owner_id": 4,
    "owner_username": "denis",
    "status": "Todo"
  }
]
```

### 3.2 GET /api/problems/{id} - Get Single Problem

```bash
curl -s -X GET "http://localhost:5001/api/problems/1" | jq .
```

**Expected Output:**
```json
{
  "id": 1,
  "title": "Two Sum",
  "description": "Given an array of integers `nums`...",
  "difficulty": "Easy",
  "tags": "Array, Hash Table",
  "test_cases": "[...]",
  "templates": "{...}",
  "drivers": "{...}",
  "time_limits": "{...}",
  "owner_id": 1,
  "owner_username": "admin"
}
```

### 3.3 POST /api/problems/ - Create Problem (Auth Required)

```bash
# Get token first
TOKEN=$(curl -s -X POST "http://localhost:8081/realms/scd-leetcode/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=scd-leetcode-client&username=admin&password=admin" | jq -r .access_token)

# Create problem
curl -s -X POST "http://localhost:5001/api/problems/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Test Problem",
    "description": "This is a test problem",
    "difficulty": "Easy",
    "tags": "test",
    "test_cases": [{"input": "1", "output": "1"}],
    "templates": {"python": "class Solution:\n    pass"},
    "drivers": {"python": "pass"},
    "time_limits": {"python": 2.0}
  }' | jq .
```

### 3.4 GET /api/problems/my - Get User's Own Problems (Auth Required)

```bash
TOKEN=$(curl -s -X POST "http://localhost:8081/realms/scd-leetcode/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=scd-leetcode-client&username=denis&password=denis" | jq -r .access_token)

curl -s -X GET "http://localhost:5001/api/problems/my" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

**Expected Output:**
```json
[
  {
    "id": 4,
    "title": "Sum of Three Numbers",
    "difficulty": "Easy",
    "owner_username": "denis",
    "status": "Todo"
  }
]
```

---

## 4. Code Execution

### 4.1 POST /api/problems/{id}/run - Run Code (Auth Required)

```bash
TOKEN=$(curl -s -X POST "http://localhost:8081/realms/scd-leetcode/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=scd-leetcode-client&username=student&password=student" | jq -r .access_token)

curl -s -X POST "http://localhost:5001/api/problems/1/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "language": "python",
    "code": "class Solution:\n    def twoSum(self, nums, target):\n        lookup = {}\n        for i, num in enumerate(nums):\n            if target - num in lookup:\n                return [lookup[target - num], i]\n            lookup[num] = i\n        return []",
    "input": "[2,7,11,15]\n9"
  }' | jq .
```

**Expected Output:**
```json
{
  "success": true,
  "output": "[0, 1]\n",
  "error": "",
  "worker_id": "worker-aa52a9ffab78"
}
```

---

## 5. Submissions API

### 5.1 POST /api/problems/{id}/submit - Submit Solution (Auth Required)

```bash
TOKEN=$(curl -s -X POST "http://localhost:8081/realms/scd-leetcode/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=scd-leetcode-client&username=student&password=student" | jq -r .access_token)

curl -s -X POST "http://localhost:5001/api/problems/1/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "language": "python",
    "code": "class Solution:\n    def twoSum(self, nums, target):\n        lookup = {}\n        for i, num in enumerate(nums):\n            if target - num in lookup:\n                return [lookup[target - num], i]\n            lookup[num] = i\n        return []"
  }' | jq .
```

**Expected Output:**
```json
{
  "message": "Submission processed",
  "status": "Accepted",
  "output": "All 5 test cases passed!"
}
```

### 5.2 GET /api/problems/{id}/submissions - Get Problem Submissions

```bash
TOKEN=$(curl -s -X POST "http://localhost:8081/realms/scd-leetcode/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=scd-leetcode-client&username=student&password=student" | jq -r .access_token)

curl -s -X GET "http://localhost:5001/api/problems/1/submissions" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### 5.3 GET /api/problems/submissions - Get All Submissions (Admin sees all, users see own)

```bash
# As Admin (sees all submissions)
TOKEN=$(curl -s -X POST "http://localhost:8081/realms/scd-leetcode/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=scd-leetcode-client&username=admin&password=admin" | jq -r .access_token)

curl -s -X GET "http://localhost:5001/api/problems/submissions" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

**Expected Output:**
```json
[
  {
    "id": 6,
    "user_id": 3,
    "username": "student",
    "problem_id": 1,
    "problem_title": "Two Sum",
    "status": "Accepted",
    "language": "python",
    "created_at": "2026-01-18T16:48:33.002039"
  }
]
```

---

## 6. Ranking API

### 6.1 GET /api/problems/ranking - Get User Ranking (Public)

```bash
curl -s -X GET "http://localhost:5001/api/problems/ranking" | jq .
```

**Expected Output:**
```json
[
  {
    "rank": 1,
    "user_id": 2,
    "username": "denis",
    "solved_problems": 1,
    "total_submissions": 3,
    "acceptance_rate": 33.3
  },
  {
    "rank": 2,
    "user_id": 1,
    "username": "admin",
    "solved_problems": 1,
    "total_submissions": 2,
    "acceptance_rate": 50.0
  },
  {
    "rank": 3,
    "user_id": 3,
    "username": "student",
    "solved_problems": 0,
    "total_submissions": 2,
    "acceptance_rate": 0.0
  }
]
```

---

## 7. Infrastructure Services

### 7.1 Redis Queue - Connection Test

```bash
docker-compose exec redis redis-cli ping
```

**Expected Output:**
```
PONG
```

### 7.2 Traefik API Gateway - Access via Port 80

```bash
curl -s -X GET "http://localhost/api/problems/" | jq '.[0].title'
```

**Expected Output:**
```
"Two Sum"
```

### 7.3 Traefik Dashboard

```bash
curl -s "http://localhost:8888/api/overview" | jq .
```

---

## 8. Worker Load Balancing

### 8.1 Test Worker Distribution

```bash
TOKEN=$(curl -s -X POST "http://localhost:8081/realms/scd-leetcode/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=scd-leetcode-client&username=student&password=student" | jq -r .access_token)

echo "=== Worker Distribution Test ==="
for i in 1 2 3 4 5 6; do
  echo -n "Request $i: "
  curl -s -X POST "http://localhost:5001/api/problems/1/run" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"language": "python", "code": "print(1)", "input": ""}' | jq -r '.worker_id // "N/A"'
done
```

**Expected Output:**
```
=== Worker Distribution Test ===
Request 1: worker-aa52a9ffab78
Request 2: worker-ceef6568a562
Request 3: worker-aa52a9ffab78
Request 4: worker-ceef6568a562
Request 5: worker-aa52a9ffab78
Request 6: worker-ceef6568a562
```

### 8.2 View Worker Logs

```bash
docker-compose logs --tail=20 runner | grep "Processing"
```

**Expected Output:**
```
runner_1    | [worker-aa52a9ffab78] Processing job b5f1e3a5-... for language: python
runner_2    | [worker-ceef6568a562] Processing job e06be133-... for language: python
runner_1    | [worker-aa52a9ffab78] Processing job aee1f343-... for language: python
runner_2    | [worker-ceef6568a562] Processing job 8bc0d4f1-... for language: python
```

---

## Architecture Summary

| Service | Port | Description |
|---------|------|-------------|
| **Traefik** | 80, 8888 | API Gateway & Load Balancer |
| **Client** | 3000 | React Frontend |
| **Server** | 5001 | Flask Backend API |
| **Keycloak** | 8081 | SSO Authentication |
| **PostgreSQL** | 5433 | Database |
| **Redis** | 6379 | Queue Service |
| **Runner 1** | 5000 (internal) | Code Execution Worker |
| **Runner 2** | 5000 (internal) | Code Execution Worker |

---

## User Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin | Administrator |
| student | student | Student |
| denis | denis | Student |
