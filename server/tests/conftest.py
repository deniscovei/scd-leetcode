import pytest
from app import create_app
from app.utils.db import get_session, Base, engine
from app.models.user import User
from app.models.problem import Problem
from app.models.submission import Submission

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_auth(monkeypatch):
    # Mock the introspection to return active=True and specific user info
    def _mock_auth(user_id, username, role='student'):
        # We need to Ensure the user exists in DB first
        session = get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                user = User(username=username, email=f'{username}@example.com', role=role, password='x')
                session.add(user)
                session.commit()
                # If we want to force specific user_id, we might need to be careful if id is autoincrement 
                # but usually for legacy/test we might want to check if ID matched.
                # Here we just rely on username.
            else:
                 # Update role if needed
                 if user.role != role:
                     user.role = role
                     session.commit()
            
            real_user_id = user.id
        finally:
            session.close()

        # Mock keycloak introspect
        def mock_introspect(token):
             return {
                'active': True,
                'preferred_username': username,
                'email': f'{username}@example.com',
                'sub': f'uuid-{username}',
                'realm_access': {'roles': [role]}
            }
            
        monkeypatch.setattr('app.utils.keycloak_auth.keycloak_openid.introspect', mock_introspect)
        return real_user_id
        
    return _mock_auth
