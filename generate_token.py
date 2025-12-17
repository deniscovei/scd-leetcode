import jwt
import datetime

payload = {
    "email": "admin@example.com",
    "preferred_username": "admin_user",
    "realm_access": {
        "roles": ["admin"]
    },
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}

token = jwt.encode(payload, "secret", algorithm="HS256")
print(token)
