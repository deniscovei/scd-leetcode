from flask import Blueprint, request, jsonify, g
from app.utils.keycloak_auth import token_required, get_user_from_request
from sqlalchemy import desc
from app.models.problem import Problem
from app.models.submission import Submission
from app.utils.db import get_session
from app.services.code_execution import execute_code
from app.utils.file_manager import save_problem_to_disk, delete_problem_from_disk
import json

problems_bp = Blueprint('problems', __name__)

@problems_bp.route('/', methods=['GET'])
def get_problems():
    session = get_session()
    try:
        problems = session.query(Problem).all()
        problems_list = [problem.to_dict() for problem in problems]

        # Check for optional user auth to populate status
        user_id, _ = get_user_from_request()
        if user_id:
            # Get all submissions for this user
            submissions = session.query(Submission).filter_by(user_id=user_id).all()
            
            # Determine status for each problem
            # If ANY submission is 'Accepted', status is 'Solved'
            # Else if there are submissions, status is 'Attempted'
            solved_problem_ids = set()
            attempted_problem_ids = set()
            
            for sub in submissions:
                if sub.status == 'Accepted':
                    solved_problem_ids.add(sub.problem_id)
                else:
                    attempted_problem_ids.add(sub.problem_id)
            
            for p in problems_list:
                p_id = p['id']
                if p_id in solved_problem_ids:
                    p['status'] = 'Solved'
                elif p_id in attempted_problem_ids:
                    p['status'] = 'Attempted'
                else:
                    p['status'] = 'Todo'
        else:
             for p in problems_list:
                p['status'] = 'Todo'

        return jsonify(problems_list), 200
    finally:
        session.close()

@problems_bp.route('/<int:problem_id>', methods=['GET'])
def get_problem(problem_id):
    session = get_session()
    try:
        problem = session.query(Problem).get(problem_id)
        if not problem:
            return jsonify({'error': 'Problem not found'}), 404
        return jsonify(problem.to_dict()), 200
    finally:
        session.close()

@problems_bp.route('/<int:problem_id>/submit', methods=['POST'])
@token_required
def submit_solution(problem_id):
    session = get_session()
    current_user_id = g.user_id
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    code = data.get('code')
    language = data.get('language')
    
    # ========== DATA CONSISTENCY VALIDATION ==========
    
    # 1. Validate required fields
    if not code or not isinstance(code, str):
        return jsonify({'error': 'Code is required and must be a string'}), 400
    if not language or not isinstance(language, str):
        return jsonify({'error': 'Language is required and must be a string'}), 400
    
    # 2. Validate supported language
    allowed_languages = ['python', 'cpp', 'java']
    if language not in allowed_languages:
        return jsonify({'error': f'Language "{language}" is not supported. Allowed: {", ".join(allowed_languages)}'}), 400
    
    # 3. Validate code length (prevent spam/attacks)
    if len(code) > 100000:  # 100KB max
        return jsonify({'error': 'Code is too long (max 100KB)'}), 400
    
    if len(code.strip()) < 1:
        return jsonify({'error': 'Code cannot be empty'}), 400
    
    # ========== END VALIDATION ==========

    try:
        problem = session.query(Problem).get(problem_id)
        if not problem:
            return jsonify({'error': 'Problem not found'}), 404

        # determine timeout
        timeout = 5.0 # default
        if problem.time_limits:
            import json
            limits = json.loads(problem.time_limits)
            if language in limits:
                timeout = float(limits[language])

        # Create submission
        submission = Submission(
            user_id=current_user_id,
            problem_id=problem_id,
            code=code,
            language=language,
            status='pending'
        )
        session.add(submission)
        session.commit()
        
        # Custom code preparation logic
        drivers = json.loads(problem.drivers) if problem.drivers else {}
        driver = drivers.get(language, "")
        
        full_code = code
        if language == 'cpp':
             headers = """#include <bits/stdc++.h>
using namespace std;
"""
             full_code = headers + code + "\n" + driver
        elif language == 'java':
             headers = """import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;
import java.util.function.*;
import java.io.*;
import java.math.*;
import java.text.*;
"""
             full_code = headers + code + "\n" + driver
        else: # python
             headers = """import sys
import json
import math
import collections
import itertools
import functools
import heapq
import bisect
import random
import re
from typing import *
"""
             full_code = headers + code + "\n" + driver

        # Execute code against all test cases
        test_cases = json.loads(problem.test_cases) if problem.test_cases else []
        all_passed = True
        
        for i, test in enumerate(test_cases):
            inp = test.get('input', '')
            expected = test.get('output', '').strip()
            
            result = execute_code(language, full_code, inp, timeout=timeout)
            
            if not result['success']:
                submission.status = 'Runtime Error'
                submission.output = f"Error on test case {i+1}:\n{result.get('error')}"
                all_passed = False
                break
            
            actual = result['output'].strip()
            if actual != expected:
                submission.status = 'Wrong Answer'
                submission.output = f"Wrong Answer on test case {i+1}:\nInput:\n{inp}\n\nOutput:\n{actual}\n\nExpected:\n{expected}"
                all_passed = False
                break
                
        if all_passed:
            submission.status = 'Accepted'
            submission.output = f"All {len(test_cases)} test cases passed!"
            
        session.commit()
        
        return jsonify({
            'message': 'Submission processed',
            'status': submission.status,
            'output': submission.output
        }), 200
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@problems_bp.route('/<int:problem_id>/run', methods=['POST'])
@token_required
def run_code(problem_id):
    session = get_session()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    code = data.get('code')
    language = data.get('language')
    input_data = data.get('input')
    
    # ========== DATA CONSISTENCY VALIDATION ==========
    
    # 1. Validate required fields
    if not code or not isinstance(code, str):
        return jsonify({'error': 'Code is required and must be a string'}), 400
    if not language or not isinstance(language, str):
        return jsonify({'error': 'Language is required and must be a string'}), 400
    if input_data is None:
        return jsonify({'error': 'Input is required (can be empty string)'}), 400
    
    # 2. Validate supported language
    allowed_languages = ['python', 'cpp', 'java']
    if language not in allowed_languages:
        return jsonify({'error': f'Language "{language}" is not supported. Allowed: {", ".join(allowed_languages)}'}), 400
    
    # 3. Validate code and input length
    if len(code) > 100000:  # 100KB max
        return jsonify({'error': 'Code is too long (max 100KB)'}), 400
    if len(str(input_data)) > 10000:  # 10KB max input
        return jsonify({'error': 'Input is too long (max 10KB)'}), 400
    
    # ========== END VALIDATION ==========

    try:
        problem = session.query(Problem).get(problem_id)
        if not problem:
            return jsonify({'error': 'Problem not found'}), 404
            
        # Get driver code
        drivers = json.loads(problem.drivers) if problem.drivers else {}
        driver = drivers.get(language, "")

        # Determine timeout
        timeout = 5.0 # default
        if problem.time_limits:
            limits = json.loads(problem.time_limits)
            if language in limits:
                timeout = float(limits[language])
        
        full_code = code
        if language == 'cpp':
             headers = """#include <bits/stdc++.h>
using namespace std;
"""
             full_code = headers + code + "\n" + driver
        elif language == 'java':
             headers = """import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;
import java.util.function.*;
import java.io.*;
import java.math.*;
import java.text.*;
"""
             full_code = headers + code + "\n" + driver
        else: # python
             headers = """import sys
import json
import math
import collections
import itertools
import functools
import heapq
import bisect
import random
import re
from typing import *
"""
             full_code = headers + code + "\n" + driver

        result = execute_code(language, full_code, input_data, timeout=timeout)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@problems_bp.route('/my', methods=['GET'])
@token_required
def get_my_problems():
    session = get_session()
    current_user_id = g.user_id
    try:
        # If user is admin (id=1), return all problems
        if current_user_id == 1:
            problems = session.query(Problem).all()
        else:
            problems = session.query(Problem).filter_by(owner_id=current_user_id).all()
            
        problems_list = [problem.to_dict() for problem in problems]
        
        # Calculate status as well
        # Get all submissions for this user 
        submissions = session.query(Submission).filter_by(user_id=current_user_id).all()
        
        solved_problem_ids = set()
        attempted_problem_ids = set()
        
        for sub in submissions:
            if sub.status == 'Accepted':
                solved_problem_ids.add(sub.problem_id)
            else:
                attempted_problem_ids.add(sub.problem_id)
        
        for p in problems_list:
            p_id = p['id']
            if p_id in solved_problem_ids:
                p['status'] = 'Solved'
            elif p_id in attempted_problem_ids:
                p['status'] = 'Attempted'
            else:
                 p['status'] = 'Todo'
                 
        return jsonify(problems_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@problems_bp.route('/submissions', methods=['GET'])
@token_required
def get_all_submissions():
    session = get_session()
    current_user_id = g.user_id
    try:
        if current_user_id == 1:
            # Admin sees all submissions, ordered by date desc
            submissions = session.query(Submission).order_by(desc(Submission.created_at)).limit(100).all()
        else:
            # Regular user sees only their own
            submissions = session.query(Submission).filter_by(user_id=current_user_id).order_by(desc(Submission.created_at)).all()
            
        # We need to join with Problem title and username for display
        result = []
        for sub in submissions:
            sub_dict = sub.to_dict()
            sub_dict['problem_title'] = sub.problem.title
            sub_dict['username'] = sub.user.username
            result.append(sub_dict)
            
        return jsonify(result), 200
    finally:
        session.close()

@problems_bp.route('/ranking', methods=['GET'])
def get_ranking():
    """Get user ranking based on solved problems and total submissions."""
    from app.models.user import User
    session = get_session()
    try:
        users = session.query(User).all()
        ranking = []
        
        for user in users:
            # Count distinct solved problems (Accepted submissions)
            solved_submissions = session.query(Submission).filter_by(
                user_id=user.id, 
                status='Accepted'
            ).all()
            solved_problem_ids = set(s.problem_id for s in solved_submissions)
            
            # Count total submissions
            total_submissions = session.query(Submission).filter_by(user_id=user.id).count()
            
            ranking.append({
                'user_id': user.id,
                'username': user.username,
                'solved_problems': len(solved_problem_ids),
                'total_submissions': total_submissions,
                'acceptance_rate': round(len(solved_problem_ids) / total_submissions * 100, 1) if total_submissions > 0 else 0
            })
        
        # Sort by solved_problems desc, then by acceptance_rate desc
        ranking.sort(key=lambda x: (-x['solved_problems'], -x['acceptance_rate']))
        
        # Add rank position
        for i, r in enumerate(ranking):
            r['rank'] = i + 1
            
        return jsonify(ranking), 200
    finally:
        session.close()

@problems_bp.route('/', methods=['POST'])
@token_required
def create_problem():
    session = get_session()
    current_user_id = g.user_id
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        title = data.get('title')
        description = data.get('description')
        difficulty = data.get('difficulty')
        tags = data.get('tags')
        
        # Expect dictionaries/lists for these, we will dump them to JSON
        test_cases = data.get('test_cases', []) 
        templates = data.get('templates', {})
        drivers = data.get('drivers', {})
        time_limits = data.get('time_limits', {})
        
        # ========== DATA CONSISTENCY VALIDATION ==========
        
        # 1. Validate required fields
        if not title or not isinstance(title, str):
            return jsonify({'error': 'Title is required and must be a string'}), 400
        if not description or not isinstance(description, str):
            return jsonify({'error': 'Description is required and must be a string'}), 400
        if not difficulty or not isinstance(difficulty, str):
            return jsonify({'error': 'Difficulty is required and must be a string'}), 400
        
        # 2. Validate title length
        if len(title.strip()) < 3:
            return jsonify({'error': 'Title must be at least 3 characters long'}), 400
        if len(title) > 255:
            return jsonify({'error': 'Title must be less than 255 characters'}), 400
            
        # 3. Validate title uniqueness
        existing_problem = session.query(Problem).filter_by(title=title.strip()).first()
        if existing_problem:
            return jsonify({'error': f'A problem with title "{title}" already exists'}), 409
        
        # 4. Validate allowed difficulty values
        allowed_difficulties = ['Easy', 'Medium', 'Hard']
        if difficulty not in allowed_difficulties:
            return jsonify({'error': f'Difficulty must be one of: {", ".join(allowed_difficulties)}'}), 400
        
        # 5. Validate test_cases format
        if test_cases:
            if not isinstance(test_cases, list):
                return jsonify({'error': 'test_cases must be an array'}), 400
            for i, tc in enumerate(test_cases):
                if not isinstance(tc, dict):
                    return jsonify({'error': f'Test case {i+1} must be an object'}), 400
                if 'input' not in tc or 'output' not in tc:
                    return jsonify({'error': f'Test case {i+1} must have "input" and "output" fields'}), 400
        
        # 6. Validate templates format
        if templates:
            if not isinstance(templates, dict):
                return jsonify({'error': 'templates must be an object'}), 400
            allowed_languages = ['python', 'cpp', 'java']
            for lang in templates.keys():
                if lang not in allowed_languages:
                    return jsonify({'error': f'Template language "{lang}" is not supported. Allowed: {", ".join(allowed_languages)}'}), 400
        
        # 7. Validate time_limits format
        if time_limits:
            if not isinstance(time_limits, dict):
                return jsonify({'error': 'time_limits must be an object'}), 400
            for lang, limit in time_limits.items():
                if not isinstance(limit, (int, float)) or limit <= 0:
                    return jsonify({'error': f'Time limit for {lang} must be a positive number'}), 400
                if limit > 60:
                    return jsonify({'error': f'Time limit for {lang} cannot exceed 60 seconds'}), 400
        
        # ========== END VALIDATION ==========

        new_problem = Problem(
            title=title.strip(),
            description=description,
            difficulty=difficulty,
            tags=tags,
            test_cases=json.dumps(test_cases) if not isinstance(test_cases, str) else test_cases,
            templates=json.dumps(templates) if not isinstance(templates, str) else templates,
            drivers=json.dumps(drivers) if not isinstance(drivers, str) else drivers,
            time_limits=json.dumps(time_limits) if not isinstance(time_limits, str) else time_limits,
            owner_id=current_user_id
        )
        
        session.add(new_problem)
        session.commit()
        
        # Save to disk
        try:
            problem_data = {
                'title': title.strip(),
                'description': description,
                'difficulty': difficulty,
                'tags': tags,
                'time_limits': time_limits,
                'templates': templates,
                'drivers': drivers,
                'test_cases': test_cases
            }
            save_problem_to_disk(problem_data)
        except Exception as e:
            print(f"Error saving problem to disk: {e}")
            # Non-critical? Or should we rollback? 
            # For now log it to not break DB insertion
            pass

        return jsonify(new_problem.to_dict()), 201
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@problems_bp.route('/<int:problem_id>', methods=['PUT'])
@token_required
def update_problem(problem_id):
    session = get_session()
    current_user_id = g.user_id
    try:
        problem = session.query(Problem).get(problem_id)
        if not problem:
            return jsonify({'error': 'Problem not found'}), 404
            
        # Check ownership (admin with id=1 can also update)
        if problem.owner_id != current_user_id and current_user_id != 1:
             return jsonify({'error': 'Unauthorized - only owner or admin can update'}), 403

        original_title = problem.title
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # ========== DATA CONSISTENCY VALIDATION ==========
        
        # 1. Validate title if provided
        if 'title' in data:
            title = data['title']
            if not title or not isinstance(title, str):
                return jsonify({'error': 'Title must be a non-empty string'}), 400
            if len(title.strip()) < 3:
                return jsonify({'error': 'Title must be at least 3 characters long'}), 400
            if len(title) > 255:
                return jsonify({'error': 'Title must be less than 255 characters'}), 400
            # Check uniqueness only if title changed
            if title.strip() != original_title:
                existing = session.query(Problem).filter_by(title=title.strip()).first()
                if existing and existing.id != problem_id:
                    return jsonify({'error': f'A problem with title "{title}" already exists'}), 409
            problem.title = title.strip()
        
        # 2. Validate difficulty if provided
        if 'difficulty' in data:
            difficulty = data['difficulty']
            allowed_difficulties = ['Easy', 'Medium', 'Hard']
            if difficulty not in allowed_difficulties:
                return jsonify({'error': f'Difficulty must be one of: {", ".join(allowed_difficulties)}'}), 400
            problem.difficulty = difficulty
        
        # 3. Validate test_cases if provided
        if 'test_cases' in data:
            test_cases = data['test_cases']
            if test_cases and not isinstance(test_cases, list):
                return jsonify({'error': 'test_cases must be an array'}), 400
            for i, tc in enumerate(test_cases or []):
                if not isinstance(tc, dict) or 'input' not in tc or 'output' not in tc:
                    return jsonify({'error': f'Test case {i+1} must have "input" and "output" fields'}), 400
        
        # 4. Validate time_limits if provided
        if 'time_limits' in data:
            time_limits = data['time_limits']
            if time_limits and not isinstance(time_limits, dict):
                return jsonify({'error': 'time_limits must be an object'}), 400
            for lang, limit in (time_limits or {}).items():
                if not isinstance(limit, (int, float)) or limit <= 0 or limit > 60:
                    return jsonify({'error': f'Time limit for {lang} must be a positive number (max 60s)'}), 400
        
        # ========== END VALIDATION ==========
        
        if 'description' in data: problem.description = data['description']
        if 'tags' in data: problem.tags = data['tags']
        
        test_cases_obj = []
        if 'test_cases' in data:
            test_cases = data['test_cases']
            test_cases_obj = test_cases if not isinstance(test_cases, str) else json.loads(test_cases)
            problem.test_cases = json.dumps(test_cases) if not isinstance(test_cases, str) else test_cases
        else:
             test_cases_obj = json.loads(problem.test_cases) if problem.test_cases else []

        templates_obj = {}
        if 'templates' in data:
             templates = data['templates']
             templates_obj = templates if not isinstance(templates, str) else json.loads(templates)
             problem.templates = json.dumps(templates) if not isinstance(templates, str) else templates
        else:
             templates_obj = json.loads(problem.templates) if problem.templates else {}

        drivers_obj = {}
        if 'drivers' in data:
             drivers = data['drivers']
             drivers_obj = drivers if not isinstance(drivers, str) else json.loads(drivers)
             problem.drivers = json.dumps(drivers) if not isinstance(drivers, str) else drivers
        else:
             drivers_obj = json.loads(problem.drivers) if problem.drivers else {}

        time_limits_obj = {}
        if 'time_limits' in data:
             time_limits = data['time_limits']
             time_limits_obj = time_limits if not isinstance(time_limits, str) else json.loads(time_limits)
             problem.time_limits = json.dumps(time_limits) if not isinstance(time_limits, str) else time_limits
        else:
             time_limits_obj = json.loads(problem.time_limits) if problem.time_limits else {}

        session.commit()
        
        # Sync to disk
        try:
            problem_disk_data = {
                'title': problem.title,
                'description': problem.description,
                'difficulty': problem.difficulty,
                'tags': problem.tags,
                'test_cases': test_cases_obj,
                'templates': templates_obj,
                'drivers': drivers_obj,
                'time_limits': time_limits_obj
            }
            save_problem_to_disk(problem_disk_data, original_title=original_title)
        except Exception as e:
            print(f"Error syncing problem to disk: {e}")

        return jsonify(problem.to_dict()), 200
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@problems_bp.route('/<int:problem_id>', methods=['DELETE'])
@token_required
def delete_problem(problem_id):
    session = get_session()
    current_user_id = g.user_id
    try:
        problem = session.query(Problem).get(problem_id)
        if not problem:
            return jsonify({'error': 'Problem not found'}), 404
            
        # Allow admin (id=1) or problem owner to delete
        if problem.owner_id != current_user_id and current_user_id != 1:
             return jsonify({'error': 'Unauthorized - only owner or admin can delete'}), 403

        title = problem.title
        
        # Count submissions that will be deleted (for response info)
        submissions_count = session.query(Submission).filter_by(problem_id=problem_id).count()
        
        # Delete submissions first (foreign key constraint usually handles this if cascading, but let's be safe)
        session.query(Submission).filter_by(problem_id=problem_id).delete()
        
        session.delete(problem)
        session.commit()
        
        # Delete from disk
        try:
            delete_problem_from_disk(title)
        except Exception as e:
            print(f"Error deleting problem from disk: {e}")

        return jsonify({
            'message': 'Problem deleted successfully',
            'deleted_problem': title,
            'deleted_submissions_count': submissions_count
        }), 200
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()



@problems_bp.route('/<int:problem_id>/submissions', methods=['GET'])
@token_required
def get_submissions(problem_id):
    session = get_session()
    current_user_id = g.user_id
    try:
        submissions = session.query(Submission).filter_by(
            problem_id=problem_id, 
            user_id=current_user_id
        ).order_by(desc(Submission.created_at)).all()
        
        return jsonify([sub.to_dict() for sub in submissions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
