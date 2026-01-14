from app import create_app
from init_problems import load_problems
from app.models.user import User
from app.utils.db import get_session
from werkzeug.security import generate_password_hash

app = create_app()

def init_users():
    session = get_session()
    try:
        if session.query(User).first() is None:
            print("Creating default user...")
            hashed_password = generate_password_hash('password')
            # Create user to ensure ID 1 exists
            user = User(username='admin', email='admin@example.com', password=hashed_password, role='admin')
            session.add(user)
            session.commit()
            print("Default user created (id=1, username=admin, password=password)")
    except Exception as e:
        print(f"Error creating default user: {e}")
        session.rollback()
    finally:
        session.close()

# Load initial problems and users
with app.app_context():
    init_users()
    load_problems(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

