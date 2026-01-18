# Problem Synchronization Guide

This document explains how to sync problems between the database and the `problems_data` folder.

## Overview

Problems in SCD.Code can exist in two places:
1. **Database (PostgreSQL)** - The primary source for the running application
2. **File System (`problems_data/`)** - Useful for version control, backup, and manual editing

## Sync Commands

All commands should be run from inside the server container:

```bash
# Enter the server container
docker-compose exec server bash
```

### Check Sync Status

See which problems exist in DB vs files:

```bash
python sync_problems.py --status
```

Output example:
```
============================================================
PROBLEM SYNC STATUS
============================================================

📊 Database: 4 problems
📁 Files: 4 problems

✅ Synced (4):
    - Sum of Three Numbers (owner: denis)
    - Sum of Two Numbers (owner: admin)
    - Two Sum (owner: admin)
    - Added Problem (owner: admin)

🎉 All problems are synced!
```

### Export DB → Files

Export all problems from the database to the `problems_data` folder:

```bash
python sync_problems.py --db-to-files
```

This will:
- Create/update folders in `problems_data/` for each problem
- Generate `config.json`, `description.txt`, templates, drivers, and tests

### Import Files → DB

Import all problems from `problems_data/` into the database:

```bash
python sync_problems.py --files-to-db
```

This will:
- Add new problems that exist only in files
- Update existing problems with file contents
- New problems are assigned to the `admin` user by default

## Quick Reference

| Command | Description |
|---------|-------------|
| `python sync_problems.py --status` | Check sync status |
| `python sync_problems.py --db-to-files` | Export DB to files |
| `python sync_problems.py --files-to-db` | Import files to DB |

## One-liner from Host

Run sync from your host machine without entering the container:

```bash
# Check status
docker-compose exec server python sync_problems.py --status

# Export DB to files
docker-compose exec server python sync_problems.py --db-to-files

# Import files to DB
docker-compose exec server python sync_problems.py --files-to-db
```

## Problem File Structure

Each problem folder in `problems_data/` should have:

```
problems_data/
└── problem_slug/
    ├── config.json       # Problem metadata (title, difficulty, tags)
    ├── description.txt   # Problem description
    ├── templates/
    │   ├── python.py     # Python starter code
    │   ├── cpp.cpp       # C++ starter code
    │   └── java.java     # Java starter code
    ├── drivers/
    │   ├── python.py     # Python driver (test harness)
    │   ├── cpp.cpp       # C++ driver
    │   └── java.java     # Java driver
    └── tests/
        ├── test1.in      # Test 1 input
        ├── test1.ref     # Test 1 expected output
        ├── test2.in      # Test 2 input
        └── test2.ref     # Test 2 expected output
```

### config.json Example

```json
{
    "title": "Two Sum",
    "difficulty": "Easy",
    "tags": "Array, Hash Table",
    "time_limits": {
        "python": 5,
        "cpp": 2,
        "java": 3
    }
}
```

## Adding Problems Manually

### Method 1: Via Frontend
1. Log in as admin or any user
2. Click "Add Problem" in the navbar
3. Fill in the form and submit
4. Problem is saved to both DB and files automatically

### Method 2: Via Files
1. Create a new folder in `problems_data/` with the problem slug
2. Add all required files (config.json, description.txt, templates/, drivers/, tests/)
3. Run `python sync_problems.py --files-to-db` to import to DB

### Method 3: Via API
```bash
curl -X POST http://localhost:5001/api/problems/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Problem",
    "description": "Problem description...",
    "difficulty": "Medium",
    "tags": "Array",
    "test_cases": [{"input": "1 2", "output": "3"}],
    "templates": {"python": "class Solution:\n    pass"},
    "drivers": {"python": "# driver code"}
  }'
```

## Deleting Problems

### Via Frontend
1. Go to the Problems list (home page)
2. Click the red "Delete" button next to a problem
3. Confirm deletion
4. Problem is deleted from both DB and files

### Via API
```bash
curl -X DELETE http://localhost:5001/api/problems/<problem_id> \
  -H "Authorization: Bearer <token>"
```

## Troubleshooting

### Problem not appearing after file sync
- Ensure `config.json` exists and has a valid `title` field
- Check that the folder name matches the slug format (lowercase, underscores)
- Run `--status` to verify the sync state

### Permission denied
- Make sure you're inside the container: `docker-compose exec server bash`
- Or use the one-liner format from host

### Problem deleted but folder remains
- The delete endpoint removes both DB entry and folder
- If folder persists, manually remove it: `rm -rf problems_data/<slug>`
