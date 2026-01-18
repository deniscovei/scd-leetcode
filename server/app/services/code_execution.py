import requests
import os

RUNNER_URL = os.environ.get('RUNNER_URL', 'http://runner:5000/execute')

def execute_code(language: str, code: str, input_data: str, timeout: float = 5.0) -> dict:
    """
    Delegates code execution to the separate runner service.
    Returns result including which worker handled the job.
    """
    try:
        payload = {
            'language': language,
            'code': code,
            'input': input_data,
            'timeout': timeout
        }
        
        # Add some buffer for network latency (e.g. 2s)
        response = requests.post(RUNNER_URL, json=payload, timeout=timeout + 2) 
        
        if response.status_code == 200:
            result = response.json()
            # Log which worker handled this
            worker_id = result.get('worker_id', 'unknown')
            print(f"[Server] Code execution handled by: {worker_id}", flush=True)
            return result
        else:
            return {
                'success': False,
                'output': '',
                'error': f"Runner service unavailable or returned error: {response.status_code}",
                'worker_id': 'none'
            }
            
    except requests.exceptions.Timeout:
         return {
            'success': False,
            'output': '',
            'error': "Execution timed out (Runner service)",
            'worker_id': 'none'
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': f"Internal Server Error: {str(e)}",
            'worker_id': 'none'
        }
