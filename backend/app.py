import os
import json
import requests
import pika
from flask import Flask, jsonify, request
from models import db, User, Problem
import jwt
from functools import wraps

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@db:5432/scd_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Keycloak Configuration
KEYCLOAK_URL = os.getenv('KEYCLOAK_URL', 'http://keycloak:8080')
REALM_NAME = os.getenv('KEYCLOAK_REALM', 'scd-realm')
CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', 'scd-client')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
QUEUE_NAME = 'judge_queue'

db.init_app(app)

def get_keycloak_public_key():
    try:
        url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('public_key')
    except Exception as e:
        print(f"Error fetching Keycloak public key: {e}")
    return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode token without verification for simplicity
            data = jwt.decode(token, options={"verify_signature": False})
            
            # Sync user to local DB if not exists
            current_user_email = data.get('email')
            current_user_name = data.get('preferred_username')
            
            # Check roles
            realm_access = data.get('realm_access', {})
            roles = realm_access.get('roles', [])
            
            user_role = 'student'
            if 'admin' in roles:
                user_role = 'admin'
                
            # Sync logic
            user = User.query.filter_by(email=current_user_email).first()
            if not user:
                user = User(username=current_user_name, email=current_user_email, role=user_role)
                db.session.add(user)
                db.session.commit()
            else:
                # Update role if changed
                if user.role != user_role:
                    user.role = user_role
                    db.session.commit()
            
            request.current_user = user

        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401

        return f(*args, **kwargs)

    return decorated

@app.route('/')
def hello():
    return jsonify({"message": "SCD-LeetCode API is running!"})

@app.route('/init-db')
def init_db():
    db.create_all()
    return jsonify({"message": "Database initialized!"})

@app.route('/profile', methods=['GET'])
@token_required
def profile():
    user = request.current_user
    return jsonify(user.to_dict())

@app.route('/problems', methods=['GET'])
def get_problems():
    problems = Problem.query.all()
    return jsonify([p.to_dict() for p in problems])

@app.route('/problems', methods=['POST'])
@token_required
def create_problem():
    user = request.current_user
    if user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_problem = Problem(title=data['title'], description=data['description'])
    db.session.add(new_problem)
    db.session.commit()
    
    return jsonify(new_problem.to_dict()), 201

@app.route('/submit', methods=['POST'])
@token_required
def submit_solution():
    user = request.current_user
    data = request.get_json()
    
    problem_id = data.get('problem_id')
    code = data.get('code')
    language = data.get('language')
    
    if not problem_id or not code:
        return jsonify({'message': 'Missing problem_id or code'}), 400

    submission = {
        'user_id': user.to_dict()['id'],
        'problem_id': problem_id,
        'code': code,
        'language': language
    }
    
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(submission),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        connection.close()
        return jsonify({'message': 'Submission received and queued for processing'}), 200
    except Exception as e:
        return jsonify({'message': 'Error queuing submission', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
