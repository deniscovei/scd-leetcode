#!/usr/bin/env python3
"""
Problem Synchronization Script
This script syncs problems between the database and the problems_data folder.

Usage:
    python sync_problems.py --db-to-files   # Export problems from DB to files
    python sync_problems.py --files-to-db   # Import problems from files to DB
    python sync_problems.py --status        # Show sync status
"""

import os
import sys
import json
import argparse
import re

# Add the parent directory to the path to import from app
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models.problem import Problem
from app.models.user import User
from app.utils.db import get_session
from app.utils.file_manager import save_problem_to_disk, slugify

PROBLEMS_DIR = os.path.join(os.path.dirname(__file__), 'problems_data')


def get_db_problems(session):
    """Get all problems from the database."""
    problems = session.query(Problem).all()
    result = []
    for p in problems:
        owner = session.query(User).get(p.owner_id) if p.owner_id else None
        result.append({
            'id': p.id,
            'title': p.title,
            'slug': slugify(p.title),
            'description': p.description,
            'difficulty': p.difficulty,
            'tags': p.tags,
            'test_cases': json.loads(p.test_cases) if p.test_cases else [],
            'templates': json.loads(p.templates) if p.templates else {},
            'drivers': json.loads(p.drivers) if p.drivers else {},
            'time_limits': json.loads(p.time_limits) if p.time_limits else {},
            'owner_username': owner.username if owner else 'admin',
            'owner_id': p.owner_id
        })
    return result


def get_file_problems():
    """Get all problems from the problems_data folder."""
    if not os.path.exists(PROBLEMS_DIR):
        return []
    
    result = []
    for entry in os.scandir(PROBLEMS_DIR):
        if entry.is_dir():
            config_path = os.path.join(entry.path, 'config.json')
            if not os.path.exists(config_path):
                continue
                
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Load description
            desc_path = os.path.join(entry.path, 'description.txt')
            description = ""
            if os.path.exists(desc_path):
                with open(desc_path, 'r') as f:
                    description = f.read()
            
            # Load templates
            templates = {}
            templates_dir = os.path.join(entry.path, 'templates')
            if os.path.exists(templates_dir):
                for file in os.listdir(templates_dir):
                    lang = file.split('.')[0]
                    with open(os.path.join(templates_dir, file), 'r') as f:
                        templates[lang] = f.read()

            # Load drivers
            drivers = {}
            drivers_dir = os.path.join(entry.path, 'drivers')
            if os.path.exists(drivers_dir):
                for file in os.listdir(drivers_dir):
                    lang = file.split('.')[0]
                    with open(os.path.join(drivers_dir, file), 'r') as f:
                        drivers[lang] = f.read()

            # Load test cases
            test_cases = []
            tests_dir = os.path.join(entry.path, 'tests')
            if os.path.exists(tests_dir):
                files = [f for f in os.listdir(tests_dir) if f.endswith('.in')]
                try:
                    files.sort(key=lambda x: int(x.replace('test', '').replace('.in', '')))
                except:
                    files.sort()
                    
                for file in files:
                    test_name = file.replace('.in', '')
                    input_path = os.path.join(tests_dir, file)
                    output_path = os.path.join(tests_dir, f"{test_name}.ref")
                    
                    if os.path.exists(output_path):
                        with open(input_path, 'r') as f:
                            inp = f.read().strip()
                        with open(output_path, 'r') as f:
                            out = f.read().strip()
                        test_cases.append({'input': inp, 'output': out})

            result.append({
                'folder_name': entry.name,
                'title': config.get('title'),
                'slug': entry.name,
                'description': description,
                'difficulty': config.get('difficulty'),
                'tags': config.get('tags'),
                'test_cases': test_cases,
                'templates': templates,
                'drivers': drivers,
                'time_limits': config.get('time_limits', {})
            })
    
    return result


def sync_db_to_files(session):
    """Export all problems from database to files."""
    print("Syncing Database → Files...")
    db_problems = get_db_problems(session)
    
    for problem in db_problems:
        print(f"  Exporting: {problem['title']}")
        save_problem_to_disk({
            'title': problem['title'],
            'description': problem['description'],
            'difficulty': problem['difficulty'],
            'tags': problem['tags'],
            'time_limits': problem['time_limits'],
            'templates': problem['templates'],
            'drivers': problem['drivers'],
            'test_cases': problem['test_cases']
        })
    
    print(f"\n✅ Exported {len(db_problems)} problems to {PROBLEMS_DIR}")


def sync_files_to_db(session):
    """Import all problems from files to database."""
    print("Syncing Files → Database...")
    file_problems = get_file_problems()
    
    added = 0
    updated = 0
    
    for problem in file_problems:
        existing = session.query(Problem).filter_by(title=problem['title']).first()
        
        if existing:
            # Update existing problem
            existing.description = problem['description']
            existing.difficulty = problem['difficulty']
            existing.tags = problem['tags']
            existing.test_cases = json.dumps(problem['test_cases'])
            existing.templates = json.dumps(problem['templates'])
            existing.drivers = json.dumps(problem['drivers'])
            existing.time_limits = json.dumps(problem['time_limits'])
            print(f"  Updated: {problem['title']}")
            updated += 1
        else:
            # Create new problem (assign to admin by default)
            admin = session.query(User).filter_by(username='admin').first()
            owner_id = admin.id if admin else 1
            
            new_problem = Problem(
                title=problem['title'],
                description=problem['description'],
                difficulty=problem['difficulty'],
                tags=problem['tags'],
                test_cases=json.dumps(problem['test_cases']),
                templates=json.dumps(problem['templates']),
                drivers=json.dumps(problem['drivers']),
                time_limits=json.dumps(problem['time_limits']),
                owner_id=owner_id
            )
            session.add(new_problem)
            print(f"  Added: {problem['title']}")
            added += 1
    
    session.commit()
    print(f"\n✅ Synced files to database: {added} added, {updated} updated")


def show_status(session):
    """Show sync status between database and files."""
    db_problems = get_db_problems(session)
    file_problems = get_file_problems()
    
    db_titles = {p['title'] for p in db_problems}
    file_titles = {p['title'] for p in file_problems}
    
    db_slugs = {p['slug'] for p in db_problems}
    file_slugs = {p['slug'] for p in file_problems}
    
    print("=" * 60)
    print("PROBLEM SYNC STATUS")
    print("=" * 60)
    
    print(f"\n📊 Database: {len(db_problems)} problems")
    print(f"📁 Files: {len(file_problems)} problems")
    
    # Problems only in DB
    only_in_db = db_titles - file_titles
    if only_in_db:
        print(f"\n⚠️  In DB but NOT in files ({len(only_in_db)}):")
        for title in only_in_db:
            print(f"    - {title}")
    
    # Problems only in files
    only_in_files = file_titles - db_titles
    if only_in_files:
        print(f"\n⚠️  In files but NOT in DB ({len(only_in_files)}):")
        for title in only_in_files:
            print(f"    - {title}")
    
    # Problems in both
    in_both = db_titles & file_titles
    print(f"\n✅ Synced ({len(in_both)}):")
    for title in sorted(in_both):
        db_p = next(p for p in db_problems if p['title'] == title)
        print(f"    - {title} (owner: {db_p['owner_username']})")
    
    if not only_in_db and not only_in_files:
        print("\n🎉 All problems are synced!")
    else:
        print("\n💡 Run with --db-to-files or --files-to-db to sync")


def main():
    parser = argparse.ArgumentParser(description='Sync problems between database and files')
    parser.add_argument('--db-to-files', action='store_true', help='Export problems from DB to files')
    parser.add_argument('--files-to-db', action='store_true', help='Import problems from files to DB')
    parser.add_argument('--status', action='store_true', help='Show sync status')
    
    args = parser.parse_args()
    
    if not any([args.db_to_files, args.files_to_db, args.status]):
        parser.print_help()
        return
    
    # Create Flask app context
    app = create_app()
    with app.app_context():
        session = get_session()
        try:
            if args.status:
                show_status(session)
            elif args.db_to_files:
                sync_db_to_files(session)
            elif args.files_to_db:
                sync_files_to_db(session)
        finally:
            session.close()


if __name__ == '__main__':
    main()
