import jwt
import datetime

payload = {
    "email": "student@example.com",
    "preferred_username": "student_user",
    "realm_access": {
        "roles": ["student"]
    },
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}

token = jwt.encode(payload, "secret", algorithm="HS256")
print(token)
