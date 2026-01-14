import os
import json
import shutil
import re

def slugify(text):
    text = text.lower()
    return re.sub(r'[\W_]+', '_', text).strip('_')

def save_problem_to_disk(problem_data, original_title=None):
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'problems_data')
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    title = problem_data.get('title')
    slug = slugify(title)
    problem_path = os.path.join(base_path, slug)

    # Handle rename if original_title is provided and different
    if original_title:
        old_slug = slugify(original_title)
        old_path = os.path.join(base_path, old_slug)
        if old_slug != slug and os.path.exists(old_path):
             # Ensure destination doesn't exist
             if not os.path.exists(problem_path):
                os.rename(old_path, problem_path)
             else:
                # If destination exists (e.g. "Two Sum" renaming to existing "Three Sum"), 
                # strictly speaking we should fail or merge. For now let's just use the new path 
                # and maybe leave the old one or overwrite? 
                # Let's simple rename logic: only rename if target doesn't exist.
                pass

    if not os.path.exists(problem_path):
        os.makedirs(problem_path)

    # 1. config.json
    config = {
        'title': title,
        'difficulty': problem_data.get('difficulty'),
        'tags': problem_data.get('tags'),
        'time_limits': problem_data.get('time_limits', {})
    }
    with open(os.path.join(problem_path, 'config.json'), 'w') as f:
        json.dump(config, f, indent=4)

    # 2. description.txt
    with open(os.path.join(problem_path, 'description.txt'), 'w') as f:
        f.write(problem_data.get('description', ''))

    # 3. templates/
    templates = problem_data.get('templates', {})
    templates_dir = os.path.join(problem_path, 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    # Clean existing templates?
    for f in os.listdir(templates_dir):
        os.remove(os.path.join(templates_dir, f))
        
    for lang, code in templates.items():
        ext = 'py' if lang == 'python' else lang # cpp, java, py
        with open(os.path.join(templates_dir, f"{lang}.{ext}"), 'w') as f:
            f.write(code)

    # 4. drivers/
    drivers = problem_data.get('drivers', {})
    drivers_dir = os.path.join(problem_path, 'drivers')
    if not os.path.exists(drivers_dir):
        os.makedirs(drivers_dir)
    for f in os.listdir(drivers_dir):
        os.remove(os.path.join(drivers_dir, f))
        
    for lang, code in drivers.items():
        ext = 'py' if lang == 'python' else lang
        with open(os.path.join(drivers_dir, f"{lang}.{ext}"), 'w') as f:
            f.write(code)

    # 5. tests/
    # problem_data['test_cases'] is a list of dicts {input, output}
    test_cases = problem_data.get('test_cases', [])
    tests_dir = os.path.join(problem_path, 'tests')
    if os.path.exists(tests_dir):
        shutil.rmtree(tests_dir)
    os.makedirs(tests_dir)

    for i, tc in enumerate(test_cases):
        # test1.in, test1.ref
        with open(os.path.join(tests_dir, f"test{i+1}.in"), 'w') as f:
            f.write(tc.get('input', ''))
        with open(os.path.join(tests_dir, f"test{i+1}.ref"), 'w') as f:
            f.write(tc.get('output', ''))

def delete_problem_from_disk(title):
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'problems_data')
    slug = slugify(title)
    problem_path = os.path.join(base_path, slug)
    if os.path.exists(problem_path):
        shutil.rmtree(problem_path)
