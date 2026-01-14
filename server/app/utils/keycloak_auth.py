from functools import wraps
from flask import request, jsonify, g
from keycloak import KeycloakOpenID
from app.models.user import User
from app.utils.db import get_session
import config
import sys

# Initialize Keycloak Client
# Ensure these match your Keycloak setup
keycloak_openid = KeycloakOpenID(
    server_url=config.KEYCLOAK_SERVER_URL,
    client_id=config.KEYCLOAK_CLIENT_ID,
    realm_name=config.KEYCLOAK_REALM_NAME,
    client_secret_key=config.KEYCLOAK_CLIENT_SECRET
)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                 token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
            
        try:
            # Verify token using introspection endpoint
            token_info = keycloak_openid.introspect(token)

            if not token_info.get('active'):
                 return jsonify({'message': 'Token is expired or invalid'}), 401
                 
            # Sync user with local DB
            username = token_info.get('preferred_username')
            if not username:
                 username = token_info.get('sub') # Fallback to sub
                 
            email = token_info.get('email')
            
            session = get_session()
            try:
                user = session.query(User).filter_by(username=username).first()
                if not user:
                    user = User(
                        username=username,
                        email=email if email else f"{username}@example.com",
                        password="keycloak_managed" # Dummy
                    )
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                
                g.user_id = user.id
                g.current_user_name = user.username
            finally:
                session.close()
                
        except Exception as e:
            print(f"Keycloak Auth Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return jsonify({'message': 'Authentication failed'}), 401
            
        return f(*args, **kwargs)
    return decorated
