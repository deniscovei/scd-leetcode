# SCD.Code - LeetCode Clone

A full-stack coding platform inspired by LeetCode, built with React, Flask, PostgreSQL, Keycloak, Redis, and Docker. The application allows users to solve coding problems, submit solutions in multiple languages (Python, C++, Java), and track their progress with a ranking system.

## Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Ports available: 3000, 5001, 5433, 6379, 8081, 8888

### Installation & Running (Docker Compose - Development)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd scd-leetcode
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```
   
   **Expected Output:**
   ```
   Creating network "scd-leetcode_default" with the default driver
   Creating scd-leetcode_redis_1    ... done
   Creating scd-leetcode_db_1       ... done
   Creating scd-leetcode_traefik_1  ... done
   Creating scd-leetcode_keycloak_1 ... done
   Creating scd-leetcode_server_1   ... done
   Creating scd-leetcode_runner_1   ... done
   Creating scd-leetcode_runner_2   ... done
   Creating scd-leetcode_client_1   ... done
   ```

3. **Initialize Keycloak and Problems** (first time only)
   ```bash
   # Wait for all services to start (about 30 seconds)
   docker-compose exec server python init_keycloak.py
   docker-compose exec server python init_problems.py
   ```
   
   **Expected Output (init_keycloak.py):**
   ```
   Initializing Keycloak...
   Creating realm 'scd-leetcode'...
   Creating client 'scd-leetcode-client'...
   Creating user 'admin'...
   Creating user 'student'...
   Creating user 'denis'...
   Keycloak initialization complete!
   ```

4. **Verify services are running**
   ```bash
   docker-compose ps
   ```
   
   **Expected Output:**
   ```
            Name                        Command               State                        Ports
   -------------------------------------------------------------------------------------------------------------------
   scd-leetcode_client_1     docker-entrypoint.sh npm start   Up      0.0.0.0:3000->3000/tcp
   scd-leetcode_db_1         docker-entrypoint.sh postgres    Up      0.0.0.0:5433->5432/tcp
   scd-leetcode_keycloak_1   /opt/keycloak/bin/kc.sh st ...   Up      0.0.0.0:8081->8080/tcp
   scd-leetcode_redis_1      docker-entrypoint.sh redis ...   Up      0.0.0.0:6379->6379/tcp
   scd-leetcode_runner_1     python app.py                    Up      5000/tcp
   scd-leetcode_runner_2     python app.py                    Up      5000/tcp
   scd-leetcode_server_1     python run.py                    Up      0.0.0.0:5001->5001/tcp
   scd-leetcode_traefik_1    /entrypoint.sh --api.insec ...   Up      0.0.0.0:80->80/tcp, 0.0.0.0:8888->8080/tcp
   ```

5. **Access the application**
   - **Frontend**: http://localhost:3000
   - **API**: http://localhost:5001
   - **Keycloak Admin**: http://localhost:8081 (admin/admin)
   - **Traefik Dashboard**: http://localhost:8888

### Stopping the Application (Docker Compose)

```bash
# Stop all services (keeps data)
docker-compose down
```

**Expected Output:**
```
Stopping scd-leetcode_client_1   ... done
Stopping scd-leetcode_runner_2   ... done
Stopping scd-leetcode_runner_1   ... done
Stopping scd-leetcode_server_1   ... done
Stopping scd-leetcode_keycloak_1 ... done
Stopping scd-leetcode_traefik_1  ... done
Stopping scd-leetcode_db_1       ... done
Stopping scd-leetcode_redis_1    ... done
Removing scd-leetcode_client_1   ... done
Removing scd-leetcode_runner_2   ... done
Removing scd-leetcode_runner_1   ... done
Removing scd-leetcode_server_1   ... done
Removing scd-leetcode_keycloak_1 ... done
Removing scd-leetcode_traefik_1  ... done
Removing scd-leetcode_db_1       ... done
Removing scd-leetcode_redis_1    ... done
Removing network scd-leetcode_default
```

```bash
# Stop and DELETE ALL DATA (removes volumes)
docker-compose down -v
```

---

## Docker Swarm Deployment (Production)

### Prerequisites
- Docker with Swarm mode enabled
- Images built locally or available in registry

### Starting the Swarm Stack

1. **Initialize Docker Swarm** (if not already done)
   ```bash
   docker swarm init
   ```
   
   **Expected Output:**
   ```
   Swarm initialized: current node (xxxxx) is now a manager.
   To add a worker to this swarm, run the following command:
       docker swarm join --token SWMTKN-1-xxxxx <ip>:2377
   ```

2. **Build the images** (if not already built)
   ```bash
   docker-compose build
   ```

3. **Deploy the stack**
   ```bash
   docker stack deploy -c docker-stack.yml leetcode
   ```
   
   **Expected Output:**
   ```
   Creating network leetcode_leetcode-network
   Creating service leetcode_traefik
   Creating service leetcode_redis
   Creating service leetcode_db
   Creating service leetcode_server
   Creating service leetcode_runner
   Creating service leetcode_keycloak
   Creating service leetcode_client
   ```

4. **Create keycloak database** (first time only)
   ```bash
   # Find the db container
   docker ps --filter name=leetcode_db
   
   # Create keycloak database
   docker exec <db_container_id> psql -U user -d leetcode_db -c "CREATE DATABASE keycloak"
   
   # Restart keycloak to pick up the new database
   docker service update --force leetcode_keycloak
   ```

5. **Check service status**
   ```bash
   docker stack services leetcode
   ```
   
   **Expected Output:**
   ```
   ID             NAME                MODE         REPLICAS   IMAGE                              PORTS
   xxxxx          leetcode_client     replicated   1/1        scd-leetcode_client:latest
   xxxxx          leetcode_db         replicated   1/1        postgres:13
   xxxxx          leetcode_keycloak   replicated   1/1        quay.io/keycloak/keycloak:23.0.0   *:8081->8080/tcp
   xxxxx          leetcode_redis      replicated   1/1        redis:7-alpine
   xxxxx          leetcode_runner     replicated   3/3        scd-leetcode_runner:latest
   xxxxx          leetcode_server     replicated   1/1        scd-leetcode_server:latest
   xxxxx          leetcode_traefik    replicated   1/1        traefik:v2.10                      *:80->80/tcp, *:8888->8080/tcp
   ```

6. **Initialize Keycloak** (first time only)
   ```bash
   docker exec $(docker ps -q -f name=leetcode_server) python init_keycloak.py
   docker exec $(docker ps -q -f name=leetcode_server) python init_problems.py
   ```

### Stopping the Swarm Stack

```bash
docker stack rm leetcode
```

**Expected Output:**
```
Removing service leetcode_client
Removing service leetcode_db
Removing service leetcode_keycloak
Removing service leetcode_redis
Removing service leetcode_runner
Removing service leetcode_server
Removing service leetcode_traefik
Removing network leetcode_leetcode-network
```

### Scaling Services in Swarm

```bash
# Scale runner workers to 5 instances
docker service scale leetcode_runner=5

# Expected Output:
# leetcode_runner scaled to 5
# overall progress: 5 out of 5 tasks

# Check scaling
docker service ls
```

### Viewing Swarm Logs

```bash
# View logs for a specific service
docker service logs leetcode_server --tail 50

# Follow logs in real-time
docker service logs -f leetcode_runner
```

---

### Default Users

| Username | Password | Role   |
|----------|----------|--------|
| admin    | admin    | Admin  |
| student  | student  | User   |
| denis    | denis    | User   |

## Architecture

### Docker Services Overview

The application runs 8 Docker containers orchestrated by Docker Compose:

#### 1. **traefik** (API Gateway & Load Balancer)
- **Image**: `traefik:v2.10`
- **Port**: 80 (gateway), 8888 (dashboard)
- **Purpose**: Routes requests to appropriate services, load balances runner workers
- **Features**:
  - Automatic service discovery via Docker labels
  - HTTP routing based on path prefixes
  - Round-robin load balancing for code execution workers

#### 2. **redis** (Queue & Caching)
- **Image**: `redis:7-alpine`
- **Port**: 6379
- **Purpose**: Message queue for code execution tasks, caching
- **Data**: Persisted in `redis_data` volume

#### 3. **db** (PostgreSQL Database)
- **Image**: `postgres:13`
- **Port**: 5433 (mapped from 5432)
- **Purpose**: Stores users, problems, submissions (in `leetcode_db`) and Keycloak data (in `keycloak` database)
- **Credentials**: user/password
- **Databases**: 
  - `leetcode_db` - Application data (users, problems, submissions)
  - `keycloak` - Keycloak authentication data
- **Data**: Persisted in `./data/db`
- **Init Script**: `./init-db.sh` automatically creates both databases on first run

#### 4. **server** (Flask Backend API)
- **Build**: `./server/Dockerfile`
- **Port**: 5001
- **Purpose**: Main application API
- **Features**:
  - User authentication (via Keycloak)
  - Problem CRUD operations
  - Submission handling
  - Ranking system
- **Dependencies**: db, redis, traefik
- **Routing**: `PathPrefix(/api)` → server:5001

#### 5. **runner** (Code Execution Workers - 2 replicas)
- **Build**: `./runner/Dockerfile`
- **Replicas**: 2 (scalable)
- **Purpose**: Execute user code submissions in isolated environments
- **Features**:
  - Supports Python, C++, Java
  - Timeout protection
  - Security isolation
- **Dependencies**: redis
- **Routing**: `PathPrefix(/execute)` → Load balanced across 2 workers

#### 6. **keycloak** (Authentication & Authorization)
- **Image**: `quay.io/keycloak/keycloak:23.0.0`
- **Port**: 8081
- **Purpose**: OAuth2/OpenID Connect authentication
- **Admin**: admin/admin
- **Features**:
  - User management
  - Token-based authentication
  - SSO capabilities

#### 7. **client** (React Frontend)
- **Build**: `./client/Dockerfile`
- **Port**: 3000
- **Purpose**: User interface
- **Features**:
  - Monaco Editor for code editing
  - Problem browsing and filtering
  - Real-time code execution
  - Ranking leaderboard
  - User profile management

### Network Architecture

```
Internet → Traefik (Port 80)
            ├── /api/* → Flask Server (5001)
            ├── /execute/* → Runner Workers (2x, load balanced)
            └── /* → React Client (3000)

Server → PostgreSQL (5432)
      → Redis (6379)
      → Keycloak (8081)
      → Traefik → Runners

Client → Keycloak (8081) for auth
      → Server API (via Traefik or direct 5001)
```

## Database Schema

### Table: `users`
Stores user account information.

| Column   | Type         | Constraints           | Description                    |
|----------|--------------|-----------------------|--------------------------------|
| id       | INTEGER      | PRIMARY KEY, AUTO_INC | User ID                        |
| username | VARCHAR(50)  | UNIQUE, NOT NULL      | Username (used for login)      |
| password | VARCHAR(255) | NOT NULL              | Hashed password (bcrypt)       |
| email    | VARCHAR(120) | UNIQUE, NOT NULL      | User email                     |
| role     | VARCHAR(20)  | DEFAULT 'student'     | Role: 'student' or 'admin'     |

**Relationships**:
- One-to-Many with `submissions` (user → submissions)
- One-to-Many with `problems` (user → owned problems)

### Table: `problems`
Stores coding problems.

| Column      | Type         | Constraints              | Description                           |
|-------------|--------------|--------------------------|---------------------------------------|
| id          | INTEGER      | PRIMARY KEY, AUTO_INC    | Problem ID                            |
| title       | VARCHAR(255) | NOT NULL                 | Problem title                         |
| description | TEXT         | NOT NULL                 | Problem description (Markdown)        |
| difficulty  | VARCHAR(50)  | NOT NULL                 | 'Easy', 'Medium', 'Hard'              |
| tags        | VARCHAR(255) | NULL                     | Comma-separated tags                  |
| test_cases  | TEXT         | NULL                     | JSON array of {input, output} pairs   |
| templates   | TEXT         | NULL                     | JSON object {python, cpp, java}       |
| drivers     | TEXT         | NULL                     | JSON object with driver code          |
| time_limits | TEXT         | NULL                     | JSON object {python: 5, cpp: 2, ...}  |
| owner_id    | INTEGER      | FOREIGN KEY(users.id)    | User who created the problem          |

**Relationships**:
- Many-to-One with `users` (problem → owner)
- One-to-Many with `submissions` (problem → submissions)

**JSON Field Examples**:

```json
// test_cases
[
  {"input": "1 2", "output": "3"},
  {"input": "5 7", "output": "12"}
]

// templates
{
  "python": "class Solution:\n    def solve(self, a, b):\n        pass",
  "cpp": "class Solution {\npublic:\n    int solve(int a, int b) {\n        \n    }\n};",
  "java": "class Solution {\n    public int solve(int a, int b) {\n        \n    }\n}"
}

// time_limits (seconds)
{
  "python": 5.0,
  "cpp": 2.0,
  "java": 3.0
}
```

### Table: `submissions`
Stores user code submissions.

| Column     | Type        | Constraints              | Description                           |
|------------|-------------|--------------------------|---------------------------------------|
| id         | INTEGER     | PRIMARY KEY, AUTO_INC    | Submission ID                         |
| user_id    | INTEGER     | FOREIGN KEY(users.id), NOT NULL | User who submitted              |
| problem_id | INTEGER     | FOREIGN KEY(problems.id), NOT NULL | Problem being solved          |
| code       | TEXT        | NOT NULL                 | User's submitted code                 |
| language   | VARCHAR(50) | NOT NULL                 | 'python', 'cpp', 'java'               |
| status     | VARCHAR(50) | DEFAULT 'pending'        | 'Accepted', 'Wrong Answer', 'Runtime Error', etc. |
| output     | TEXT        | NULL                     | Execution output or error message     |
| created_at | DATETIME    | DEFAULT NOW()            | Submission timestamp                  |

**Relationships**:
- Many-to-One with `users` (submission → user)
- Many-to-One with `problems` (submission → problem)

**Status Values**:
- `pending` - Submission queued
- `Accepted` - All test cases passed
- `Wrong Answer` - Output doesn't match expected
- `Runtime Error` - Code crashed during execution
- `Time Limit Exceeded` - Execution timeout

## Project Structure

```
scd-leetcode/
├── client/                      # React Frontend
│   ├── public/
│   │   └── index.html          # HTML entry point
│   ├── src/
│   │   ├── api/
│   │   │   └── index.ts        # API client functions
│   │   ├── components/
│   │   │   ├── CodeEditor.tsx  # Monaco editor with resizable panels
│   │   │   ├── Navbar.tsx      # Navigation bar with auth
│   │   │   └── ProblemDescription.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx        # Problems list with delete buttons
│   │   │   ├── ProblemPage.tsx # Problem solving interface
│   │   │   ├── Submissions.tsx # User submissions history
│   │   │   ├── MyProblems.tsx  # User's created problems
│   │   │   ├── AddProblem.tsx  # Create new problem
│   │   │   ├── MyAccount.tsx   # User profile & stats
│   │   │   └── Ranking.tsx     # Leaderboard
│   │   ├── utils/
│   │   │   └── auth.ts         # Keycloak auth utilities
│   │   ├── App.tsx             # Main app with routing
│   │   ├── index.tsx           # React entry point
│   │   └── keycloak.ts         # Keycloak configuration
│   ├── Dockerfile
│   └── package.json
│
├── server/                      # Flask Backend
│   ├── app/
│   │   ├── models/
│   │   │   ├── user.py         # User model
│   │   │   ├── problem.py      # Problem model
│   │   │   └── submission.py   # Submission model
│   │   ├── routes/
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   └── problems.py     # Problem & submission endpoints
│   │   ├── services/
│   │   │   └── code_execution.py # Code execution logic
│   │   └── utils/
│   │       ├── db.py           # Database connection
│   │       ├── keycloak_auth.py # Keycloak integration
│   │       └── file_manager.py # Problem file I/O
│   ├── problems_data/          # Problem definitions (synced with DB)
│   │   ├── two_sum/
│   │   │   ├── config.json     # Problem metadata
│   │   │   ├── description.txt # Problem description
│   │   │   ├── templates/      # Starter code
│   │   │   │   ├── python.py
│   │   │   │   ├── cpp.cpp
│   │   │   │   └── java.java
│   │   │   ├── drivers/        # Test harness code
│   │   │   │   ├── python.py
│   │   │   │   ├── cpp.cpp
│   │   │   │   └── java.java
│   │   │   └── tests/          # Test cases
│   │   │       ├── test1.in
│   │   │       ├── test1.ref
│   │   │       ├── test2.in
│   │   │       └── test2.ref
│   │   └── ...
│   ├── config.py               # Flask configuration
│   ├── run.py                  # Flask entry point
│   ├── init_keycloak.py        # Keycloak initialization script
│   ├── init_problems.py        # Load problems to DB
│   ├── sync_problems.py        # Bidirectional DB ↔ files sync
│   ├── Dockerfile
│   └── requirements.txt
│
├── runner/                      # Code Execution Worker
│   ├── app.py                  # Worker Flask app
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/
│   └── db/                     # PostgreSQL data (persisted)
│
├── docker-compose.yml          # Docker orchestration
├── README.md                   # This file
├── SYNC_PROBLEMS.md            # Problem sync guide
└── api_tests_results.md        # API documentation & tests
```

## Common Tasks

### Managing Problems

#### Check Sync Status
```bash
docker-compose exec server python sync_problems.py --status
```

**Expected Output:**
```
=== Problem Sync Status ===
Problems in database: 5
Problems on disk: 5

Database problems:
  - Two Sum (ID: 1)
  - Sum of Two Numbers (ID: 2)
  - Added Problem (ID: 3)
  - Sum of Three Numbers (ID: 4)
  - Noua problema (ID: 7)

Disk problems:
  - two_sum
  - sum_of_two_numbers
  - added_problem
  - sum_of_three_numbers
  - noua_problema
```

#### Export Problems from DB to Files
```bash
docker-compose exec server python sync_problems.py --db-to-files
```

**Expected Output:**
```
Exporting problems from database to files...
Exported: Two Sum -> two_sum/
Exported: Sum of Two Numbers -> sum_of_two_numbers/
...
Export complete! 5 problems exported.
```

#### Import Problems from Files to DB
```bash
docker-compose exec server python sync_problems.py --files-to-db
```

**Expected Output:**
```
Importing problems from files to database...
Imported: two_sum -> Two Sum (ID: 1)
Imported: sum_of_two_numbers -> Sum of Two Numbers (ID: 2)
...
Import complete! 5 problems imported.
```

See [SYNC_PROBLEMS.md](SYNC_PROBLEMS.md) for detailed documentation.

### Viewing Logs

```bash
# All services
docker-compose logs -f
```

```bash
# Specific service
docker-compose logs -f server
docker-compose logs -f runner
docker-compose logs -f client
```

```bash
# Last N lines
docker-compose logs --tail=50 server
```

**Expected Output (server logs):**
```
server_1   |  * Serving Flask app 'app'
server_1   |  * Debug mode: on
server_1   |  * Running on all addresses (0.0.0.0)
server_1   |  * Running on http://127.0.0.1:5001
server_1   | 2026-01-21 10:00:00,123 - INFO - Processing submission for problem 1
```

### Restarting Services

```bash
# All services
docker-compose restart
```

**Expected Output:**
```
Restarting scd-leetcode_client_1   ... done
Restarting scd-leetcode_runner_2   ... done
Restarting scd-leetcode_runner_1   ... done
Restarting scd-leetcode_server_1   ... done
Restarting scd-leetcode_keycloak_1 ... done
Restarting scd-leetcode_traefik_1  ... done
Restarting scd-leetcode_db_1       ... done
Restarting scd-leetcode_redis_1    ... done
```

```bash
# Specific service
docker-compose restart server
```

**Expected Output:**
```
Restarting scd-leetcode_server_1 ... done
```

### Scaling Workers

```bash
# Scale runner workers to 4 instances
docker-compose up -d --scale runner=4
```

**Expected Output:**
```
scd-leetcode_db_1 is up-to-date
scd-leetcode_redis_1 is up-to-date
scd-leetcode_traefik_1 is up-to-date
Creating scd-leetcode_runner_3 ... done
Creating scd-leetcode_runner_4 ... done
```

```bash
# Scale back to 2
docker-compose up -d --scale runner=2
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U user -d leetcode_db
```

**Expected Output:**
```
psql (13.x)
Type "help" for help.

leetcode_db=#
```

```bash
# Common queries
\dt                          # List tables
SELECT * FROM users;
SELECT * FROM problems;
SELECT * FROM submissions;
```

**Example \dt output:**
```
           List of relations
 Schema |    Name     | Type  | Owner
--------+-------------+-------+-------
 public | problems    | table | user
 public | submissions | table | user
 public | users       | table | user
(3 rows)
```

### Stopping the Application

```bash
# Stop all services
docker-compose down
```

```bash
# Stop and remove volumes (deletes all data)
docker-compose down -v
```

## Features

### For Users
- ✅ **Authentication**: Keycloak-based OAuth2/OpenID Connect
- ✅ **Problem Solving**: Browse problems, filter by difficulty
- ✅ **Code Editor**: Monaco editor with syntax highlighting
- ✅ **Multi-Language**: Python, C++, Java support
- ✅ **Real-Time Execution**: Run code with custom input
- ✅ **Submissions**: Track submission history and results
- ✅ **Ranking**: Global leaderboard based on solved problems
- ✅ **User Profile**: View stats and manage account

### For Problem Creators
- ✅ **Add Problems**: Via frontend UI or manual file creation
- ✅ **Edit Problems**: Modify description, test cases, templates
- ✅ **Delete Problems**: Remove from both DB and filesystem
- ✅ **Problem Ownership**: Track who created each problem
- ✅ **Admin Override**: Admin can edit/delete any problem

### Technical Features
- ✅ **Microservices Architecture**: Separated concerns with Docker
- ✅ **Load Balancing**: Traefik distributes execution load
- ✅ **Horizontal Scaling**: Add more runner workers as needed
- ✅ **Data Persistence**: PostgreSQL for DB, volumes for data
- ✅ **Queue System**: Redis for task management
- ✅ **Security**: Isolated code execution, JWT tokens
- ✅ **Bidirectional Sync**: DB ↔ filesystem problem sync

## Troubleshooting

### Services Not Starting
```bash
# Check if ports are in use
lsof -i :3000    # Client
lsof -i :5001    # Server
lsof -i :5433    # PostgreSQL
lsof -i :8081    # Keycloak

# Check service logs
docker-compose logs <service-name>
```

### Database Connection Issues
```bash
# Restart database
docker-compose restart db

# Recreate database container
docker-compose down
docker-compose up -d db

# Wait for DB to be ready, then initialize
sleep 10
docker-compose exec server python init_keycloak.py
docker-compose exec server python init_problems.py
```

### Keycloak Not Initializing
```bash
# Manually run initialization
docker-compose exec server python init_keycloak.py

# Check Keycloak logs
docker-compose logs keycloak

# Access Keycloak admin console
# http://localhost:8081 (admin/admin)
```

### Missing Keycloak Database
```bash
# If Keycloak fails with "database keycloak does not exist":
# 1. Create the database manually
docker-compose exec db psql -U user -d leetcode_db -c "CREATE DATABASE keycloak;"

# 2. Restart Keycloak
docker-compose restart keycloak

# 3. Initialize Keycloak realm and users
docker-compose exec server python init_keycloak.py
```

### Data Not Persisting
If your submissions or user data disappear after restart:

```bash
# Check if data directory exists and has correct permissions
ls -la ./data/db

# Verify database volumes are mounted correctly
docker-compose exec db psql -U user -d leetcode_db -c "\l"

# Check if databases exist
docker-compose exec db psql -U user -d leetcode_db -c "SELECT datname FROM pg_database;"

# If data was lost, you may need to:
# 1. Stop all services
docker-compose down

# 2. Backup any important data from ./data/db if it exists

# 3. Remove old data (THIS WILL DELETE ALL DATA)
sudo rm -rf ./data/db/*

# 4. Start fresh with automatic database creation
docker-compose up -d

# 5. Wait for services to start (30 seconds)
sleep 30

# 6. Initialize Keycloak and problems
docker-compose exec server python init_keycloak.py
docker-compose exec server python init_problems.py
```

**Note**: Users are automatically created in the PostgreSQL database when they first log in through Keycloak. The system syncs Keycloak users to the local database on their first authentication.

### Code Execution Failing
```bash
# Check runner logs
docker-compose logs runner

# Check Redis connection
docker-compose exec server redis-cli -h redis ping

# Restart runners
docker-compose restart runner
```

## API Documentation

See [api_tests_results.md](api_tests_results.md) for complete API documentation with curl examples.

### Key Endpoints

- `GET /api/problems/` - List all problems
- `GET /api/problems/<id>` - Get problem details
- `POST /api/problems/<id>/submit` - Submit solution
- `POST /api/problems/<id>/run` - Run code with custom input
- `GET /api/problems/ranking` - Get user ranking
- `POST /api/problems/` - Create problem (auth required)
- `PUT /api/problems/<id>` - Update problem (owner/admin)
- `DELETE /api/problems/<id>` - Delete problem (owner/admin)

## Security Notes

- Passwords are hashed with bcrypt
- JWT tokens expire after 1 hour
- Code execution runs in Docker containers (isolated)
- Execution timeouts prevent infinite loops
- Admin role required for sensitive operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Authors

- Denis Covei

## Acknowledgments

- Inspired by LeetCode
- Built with React, Flask, PostgreSQL, Keycloak, Redis, Traefik
- Dockerized for easy deployment