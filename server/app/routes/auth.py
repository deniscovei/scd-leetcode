from flask import Blueprint, jsonify, g
from app.utils.keycloak_auth import token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/me', methods=['GET'])
@token_required
def me():
    return jsonify({
        'id': g.user_id,
        'username': g.current_user_name
    })

# Legacy routes removed or deprecated
@auth_bp.route('/register', methods=['POST'])
def register():
    return jsonify({'error': 'Use Keycloak for registration'}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
     return jsonify({'error': 'Use Keycloak for login'}), 400

