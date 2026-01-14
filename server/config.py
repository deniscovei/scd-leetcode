import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
# SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-123'
SECRET_KEY = 'super-secret-key-fixed'

# Internal URL for container-to-container communication
# Using host.docker.internal to match the Frontend URL (localhost:8081) and avoid issuer mismatch
KEYCLOAK_SERVER_URL = os.environ.get('KEYCLOAK_SERVER_URL', 'http://host.docker.internal:8081/')
KEYCLOAK_REALM_NAME = os.environ.get('KEYCLOAK_REALM_NAME', 'scd-leetcode')
KEYCLOAK_CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID', 'scd-leetcode-backend')
KEYCLOAK_CLIENT_SECRET = os.environ.get('KEYCLOAK_CLIENT_SECRET', 'J0j1tbTScYVCWBV8epMUsW6NH55HjxWH')
