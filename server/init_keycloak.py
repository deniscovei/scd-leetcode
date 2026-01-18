import os
import time
from keycloak import KeycloakAdmin

KEYCLOAK_URL = os.environ.get('KEYCLOAK_INTERNAL_URL', 'http://keycloak:8080/')
USERNAME = os.environ.get('KEYCLOAK_ADMIN', 'admin')
PASSWORD = os.environ.get('KEYCLOAK_ADMIN_PASSWORD', 'admin')

def wait_for_keycloak():
    print(f"Connecting to Keycloak at {KEYCLOAK_URL}...")
    for i in range(30):
        try:
            keycloak_admin = KeycloakAdmin(server_url=KEYCLOAK_URL,
                                           username=USERNAME,
                                           password=PASSWORD,
                                           realm_name="master",
                                           verify=False)
            return keycloak_admin
        except Exception as e:
            print(f"Waiting for Keycloak... ({e})")
            time.sleep(2)
    raise Exception("Could not connect to Keycloak")

def init_keycloak():
    try:
        admin = wait_for_keycloak()
        print("Connected to Keycloak.")

        # Create Realm
        realm_name = "scd-leetcode"
        realms = admin.get_realms()
        if not any(r['realm'] == realm_name for r in realms):
            print(f"Creating realm '{realm_name}'...")
            admin.create_realm(payload={
                "realm": realm_name,
                "enabled": True,
                "registrationAllowed": True  # Enable registration
            })
        else:
            print(f"Realm '{realm_name}' already exists.")

        # Cleanup: Check if 'scd-leetcode-client' exists in master and delete it
        # This prevents confusion if it was accidentally created in master
        print("Cleaning up master realm...")
        master_clients = admin.get_clients()
        phantom_client = next((c for c in master_clients if c.get('clientId') == "scd-leetcode-client"), None)
        if phantom_client:
            print(f"Removing 'scd-leetcode-client' from master realm (clean up)...")
            admin.delete_client(phantom_client['id'])

        # Switch context to the target realm
        print(f"Switching context to {realm_name}...")
        admin.change_current_realm(realm_name)

        # Create or Update Client
        client_id = "scd-leetcode-client"
        clients = admin.get_clients()
        client = next((c for c in clients if c.get('clientId') == client_id), None)
        
        client_payload = {
            "clientId": client_id,
            "enabled": True,
            "publicClient": True,
            "directAccessGrantsEnabled": True,
            "redirectUris": ["http://localhost:3000/*", "http://localhost:3000"],
            "webOrigins": ["http://localhost:3000", "+"],
            "standardFlowEnabled": True
        }

        if not client:
            print(f"Creating client '{client_id}'...")
            admin.create_client(payload=client_payload)
        else:
            print(f"Client '{client_id}' already exists. Updating...")
            admin.update_client(client['id'], payload=client_payload)

        # Create Test User
        user_username = "student"
        users = admin.get_users({"username": user_username})
        if not users:
            print(f"Creating user '{user_username}'...")
            admin.create_user(payload={
                "username": user_username,
                "email": "student@example.com",
                "enabled": True,
                "emailVerified": True,
                "credentials": [{"type": "password", "value": "student", "temporary": False}]
            })
        else:
            print(f"User '{user_username}' already exists.")

        # Create Admin User
        admin_username = "admin"
        users = admin.get_users({"username": admin_username})
        if not users:
            print(f"Creating user '{admin_username}'...")
            admin.create_user(payload={
                "username": admin_username,
                "email": "admin@example.com",
                "enabled": True,
                "emailVerified": True,
                "credentials": [{"type": "password", "value": "admin", "temporary": False}]
            })
        else:
            print(f"User '{admin_username}' already exists.")

        # Create Denis User
        denis_username = "denis"
        users = admin.get_users({"username": denis_username})
        if not users:
            print(f"Creating user '{denis_username}'...")
            admin.create_user(payload={
                "username": denis_username,
                "email": "denis@example.com",
                "enabled": True,
                "emailVerified": True,
                "credentials": [{"type": "password", "value": "denis", "temporary": False}]
            })
        else:
            print(f"User '{denis_username}' already exists.")

        # Create confidential client for backend API (Resource Server)
        backend_client_id = "scd-leetcode-backend"
        backend_client = next((c for c in clients if c.get('clientId') == backend_client_id), None)
        
        backend_payload = {
            "clientId": backend_client_id,
            "enabled": True,
            "publicClient": False, # Confidential
            "standardFlowEnabled": False, # Backend doesn't do user login flows usually
            "serviceAccountsEnabled": True, # Allow service account
            "directAccessGrantsEnabled": False,
            "authorizationServicesEnabled": True # It is a resource server
        }

        if not backend_client:
            print(f"Creating backend client '{backend_client_id}'...")
            admin.create_client(payload=backend_payload)
            # Fetch the client to get the ID for secret regeneration
            clients = admin.get_clients()
            backend_client = next((c for c in clients if c.get('clientId') == backend_client_id), None)
        else:
            print(f"Backend client '{backend_client_id}' already exists. Updating...")
            admin.update_client(backend_client['id'], payload=backend_payload)
        
        # Get Client Secret
        secret = admin.get_client_secrets(backend_client['id'])
        print(f"Backend Client Secret: {secret.get('value')}")
        
        # Write secret to a file so the app can pick it up (or we just print it and manually set it for now)
        # For this environment, let's write to a .env file or similar if we can, 
        # but since we are inside the container, we might just update the config code or similar.
        # Ideally, we should restart the server with the new secret in env vars.

    except Exception as e:
        print(f"Failed to initialize Keycloak: {e}")

if __name__ == "__main__":
    init_keycloak()
