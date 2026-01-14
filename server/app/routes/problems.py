from flask import Blueprint, request, jsonify, g
from app.utils.keycloak_auth import token_required
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
        return jsonify([problem.to_dict() for problem in problems]), 200
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
    code = data.get('code')
    language = data.get('language')
    
    if not code or not language:
        return jsonify({'error': 'Missing code or language'}), 400

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
    code = data.get('code')
    language = data.get('language')
    input_data = data.get('input')
    
    if not code or not language or input_data is None:
        return jsonify({'error': 'Missing code, language or input'}), 400

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

@problems_bp.route('/', methods=['POST'])
@token_required
def create_problem():
    session = get_session()
    current_user_id = g.user_id
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        difficulty = data.get('difficulty')
        tags = data.get('tags')
        
        # Expect dictionaries/lists for these, we will dump them to JSON
        test_cases = data.get('test_cases', []) 
        templates = data.get('templates', {})
        drivers = data.get('drivers', {})
        time_limits = data.get('time_limits', {})
        
        if not title or not description or not difficulty:
             return jsonify({'error': 'Missing required fields'}), 400

        new_problem = Problem(
            title=title,
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
                'title': title,
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
            
        # Check ownership
        if problem.owner_id != current_user_id:
             return jsonify({'error': 'Unauthorized'}), 403

        original_title = problem.title
        data = request.get_json()
        
        if 'title' in data: problem.title = data['title']
        if 'description' in data: problem.description = data['description']
        if 'difficulty' in data: problem.difficulty = data['difficulty']
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
            
        if problem.owner_id != current_user_id:
             return jsonify({'error': 'Unauthorized'}), 403

        title = problem.title
        
        # Delete submissions first (foreign key constraint usually handles this if cascading, but let's be safe)
        session.query(Submission).filter_by(problem_id=problem_id).delete()
        
        session.delete(problem)
        session.commit()
        
        # Delete from disk
        try:
            delete_problem_from_disk(title)
        except Exception as e:
            print(f"Error deleting problem from disk: {e}")

        return jsonify({'message': 'Problem deleted'}), 200
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
