from flask import Flask, request, jsonify
import subprocess
import os
import uuid
import shutil
import threading
import socket
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TEMP_DIR = '/tmp/code_execution'
# Get unique worker ID - try hostname (Docker container ID) or fallback to a file-based ID
def get_worker_id():
    # In Docker, hostname is the container ID (short form)
    hostname = socket.gethostname()
    # Also try to read from /etc/hostname which has the full container ID
    try:
        with open('/etc/hostname', 'r') as f:
            container_id = f.read().strip()[:12]  # Short container ID
            return f'worker-{container_id}'
    except:
        return f'worker-{hostname}'

WORKER_ID = get_worker_id()

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def execute_code_logic(language: str, code: str, input_data: str, timeout: float = 5.0) -> dict:
    job_id = str(uuid.uuid4())
    temp_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Log which worker is handling this job
    print(f"[{WORKER_ID}] Processing job {job_id} for language: {language}", flush=True)
    
    output = ""
    error = ""
    success = False

    try:
        if language == 'python':
            file_path = os.path.join(temp_dir, f"solution.py")
            with open(file_path, 'w') as f:
                f.write(code)
            
            try:
                # Capture output
                process = subprocess.Popen(
                    ['python3', file_path], 
                    stdin=subprocess.PIPE, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
                stdout, stderr = process.communicate(input=input_data, timeout=timeout)
                output = stdout
                
                if process.returncode != 0:
                    success = False
                    error = stderr or "Runtime Error"
                else:
                    success = True
                    # stderr might contain warnings
            except subprocess.TimeoutExpired:
                process.kill()
                error = "Time Limit Exceeded"
                success = False

        elif language == 'cpp':
            file_path = os.path.join(temp_dir, "solution.cpp")
            exe_path = os.path.join(temp_dir, "solution")
            
            with open(file_path, 'w') as f:
                f.write(code)
            
            try:
                # Compile
                compile_process = subprocess.Popen(['g++', file_path, '-o', exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                c_out, c_err = compile_process.communicate(timeout=10)
                
                if compile_process.returncode != 0:
                    success = False
                    error = "Compilation Error:\n" + c_err
                else:
                    # Run
                    run_process = subprocess.Popen(
                        [exe_path], 
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True
                    )
                    stdout, stderr = run_process.communicate(input=input_data, timeout=timeout)
                    output = stdout
                    
                    if run_process.returncode != 0:
                        success = False
                        error = stderr or "Runtime Error"
                    else:
                        success = True
                        error = stderr
            except subprocess.TimeoutExpired:
                error = "Time Limit Exceeded"
                success = False

        elif language == 'java':
            file_path = os.path.join(temp_dir, "Solution.java")
            
            with open(file_path, 'w') as f:
                f.write(code)
            
            try:
                # Compile
                print(f"[{WORKER_ID}] Compiling Java code...", flush=True)
                compile_process = subprocess.Popen(['javac', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                c_out, c_err = compile_process.communicate(timeout=10)
                
                if compile_process.returncode != 0:
                    success = False
                    error = "Compilation Error:\n" + c_err
                    print(f"[{WORKER_ID}] Compilation failed: {c_err}", flush=True)
                else:
                    # Run - execute Driver class which contains the main method
                    # The code should contain both Solution and Driver classes
                    print(f"[{WORKER_ID}] Running Java Driver class...", flush=True)
                    run_process = subprocess.Popen(
                        ['java', '-cp', temp_dir, 'Driver'], 
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True
                    )
                    stdout, stderr = run_process.communicate(input=input_data, timeout=timeout)
                    output = stdout
                    
                    if run_process.returncode != 0:
                        success = False
                        error = stderr or "Runtime Error"
                        print(f"[{WORKER_ID}] Runtime error: {stderr}", flush=True)
                    else:
                        success = True
                        error = stderr
                        print(f"[{WORKER_ID}] Java execution successful", flush=True)
            except subprocess.TimeoutExpired:
                error = "Time Limit Exceeded"
                success = False
                print(f"[{WORKER_ID}] Java execution timeout", flush=True)
        else:
            return {'success': False, 'error': f"Unsupported language: {language}", 'output': ''}

    except Exception as e:
        success = False
        error = str(e)
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    return {
        'success': success,
        'output': output,
        'error': error,
        'worker_id': WORKER_ID
    }

@app.route('/execute', methods=['POST'])
def run_code():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    code = data.get('code')
    language = data.get('language')
    input_data = data.get('input', '')
    timeout = data.get('timeout', 5.0)

    if not code or not language:
        return jsonify({'error': 'Missing code or language'}), 400

    result = execute_code_logic(language, code, input_data, float(timeout))
    print(f"[{WORKER_ID}] Job completed: success={result['success']}", flush=True)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
