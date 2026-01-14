import os
import json
from app.models.problem import Problem
from app.utils.db import get_session

def load_problems(app):
    session = get_session()
    problems_dir = os.path.join(os.path.dirname(__file__), 'problems_data')
    
    if not os.path.exists(problems_dir):
        os.makedirs(problems_dir)
        return

    try:
        # Walk through subdirectories
        for entry in os.scandir(problems_dir):
            if entry.is_dir():
                problem_dir = entry.path
                config_path = os.path.join(problem_dir, 'config.json')
                
                if not os.path.exists(config_path):
                    continue
                    
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Load description
                desc_path = os.path.join(problem_dir, 'description.txt')
                description = ""
                if os.path.exists(desc_path):
                    with open(desc_path, 'r') as f:
                        description = f.read()
                
                # Load templates
                templates = {}
                templates_dir = os.path.join(problem_dir, 'templates')
                if os.path.exists(templates_dir):
                     for file in os.listdir(templates_dir):
                        lang = file.split('.')[0] # e.g. python.py -> python
                        with open(os.path.join(templates_dir, file), 'r') as f:
                            templates[lang] = f.read()

                # Load drivers
                drivers = {}
                drivers_dir = os.path.join(problem_dir, 'drivers')
                if os.path.exists(drivers_dir):
                     for file in os.listdir(drivers_dir):
                        lang = file.split('.')[0]
                        with open(os.path.join(drivers_dir, file), 'r') as f:
                            drivers[lang] = f.read()

                # Load test cases
                test_cases = []
                tests_dir = os.path.join(problem_dir, 'tests')
                if os.path.exists(tests_dir):
                    # Find all .in files
                    files = [f for f in os.listdir(tests_dir) if f.endswith('.in')]
                    # Sort by test number (test1.in, test2.in ...)
                    # Assuming format testN.in
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


                # Prepare strings for DB
                test_cases_str = json.dumps(test_cases)
                templates_str = json.dumps(templates)
                drivers_str = json.dumps(drivers)
                time_limits_str = json.dumps(config.get('time_limits', {}))
                
                # Check if problem exists
                existing = session.query(Problem).filter_by(title=config['title']).first()
                
                if not existing:
                    problem = Problem(
                        title=config['title'],
                        description=description,
                        difficulty=config['difficulty'],
                        tags=config['tags'],
                        test_cases=test_cases_str,
                        templates=templates_str,
                        drivers=drivers_str,
                        time_limits=time_limits_str
                    )
                    session.add(problem)
                    print(f"Added problem: {config['title']}")
                else:
                    existing.description = description
                    existing.difficulty = config['difficulty']
                    existing.tags = config['tags']
                    existing.test_cases = test_cases_str
                    existing.templates = templates_str
                    existing.drivers = drivers_str
                    existing.time_limits = time_limits_str
                    print(f"Updated problem: {config['title']}")
        
        session.commit()
    except Exception as e:
        print(f"Error loading problems: {e}")
        session.rollback()
    finally:
        session.close()
