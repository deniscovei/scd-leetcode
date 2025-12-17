# API Test Results

Acest document conține rezultatele testării manuale a API-ului folosind `curl`.

## 1. Health Check
Verificăm dacă serviciul API este activ.

**Comandă:**
```bash
curl -v http://127.0.0.1:5000/
```

**Rezultat:**
```http
*   Trying 127.0.0.1:5000...
* Connected to 127.0.0.1 (127.0.0.1) port 5000
> GET / HTTP/1.1
> Host: 127.0.0.1:5000
> User-Agent: curl/8.5.0
> Accept: */*
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.1.4 Python/3.9.25
< Date: Wed, 17 Dec 2025 02:41:16 GMT
< Content-Type: application/json
< Content-Length: 43
< Connection: close
< 
{"message":"SCD-LeetCode API is running!"}
```

---

## 2. Inițializare Bază de Date
Inițializăm tabelele în baza de date PostgreSQL.

**Comandă:**
```bash
curl -v http://127.0.0.1:5000/init-db
```

**Rezultat:**
```http
*   Trying 127.0.0.1:5000...
* Connected to 127.0.0.1 (127.0.0.1) port 5000
> GET /init-db HTTP/1.1
> Host: 127.0.0.1:5000
> User-Agent: curl/8.5.0
> Accept: */*
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.1.4 Python/3.9.25
< Date: Wed, 17 Dec 2025 02:41:16 GMT
< Content-Type: application/json
< Content-Length: 36
< Connection: close
< 
{"message":"Database initialized!"}
```

---

## 3. Listare Probleme
Obținem lista de probleme disponibile (momentan goală).

**Comandă:**
```bash
curl -v http://127.0.0.1:5000/problems
```

**Rezultat:**
```http
*   Trying 127.0.0.1:5000...
* Connected to 127.0.0.1 (127.0.0.1) port 5000
> GET /problems HTTP/1.1
> Host: 127.0.0.1:5000
> User-Agent: curl/8.5.0
> Accept: */*
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.1.4 Python/3.9.25
< Date: Wed, 17 Dec 2025 02:41:16 GMT
< Content-Type: application/json
< Content-Length: 3
< Connection: close
< 
[]
```

---

## 4. Profil Utilizator (Fără Autentificare)
Încercăm să accesăm un endpoint protejat fără token JWT.

**Comandă:**
```bash
curl -v http://127.0.0.1:5000/profile
```

**Rezultat:**
```http
*   Trying 127.0.0.1:5000...
* Connected to 127.0.0.1 (127.0.0.1) port 5000
> GET /profile HTTP/1.1
> Host: 127.0.0.1:5000
> User-Agent: curl/8.5.0
> Accept: */*
> 
< HTTP/1.1 401 UNAUTHORIZED
< Server: Werkzeug/3.1.4 Python/3.9.25
< Date: Wed, 17 Dec 2025 02:41:16 GMT
< Content-Type: application/json
< Content-Length: 32
< Connection: close
< 
{"message":"Token is missing!"}
```

---

## 5. Profil Utilizator (Cu Autentificare)
Accesăm endpoint-ul protejat folosind un token JWT valid (simulat).

**Generare Token (Python):**
```python
import jwt
# ... payload cu email="student@example.com", role="student" ...
token = jwt.encode(payload, "secret", algorithm="HS256")
```

**Comandă:**
```bash
curl -v -H "Authorization: Bearer <TOKEN>" http://127.0.0.1:5000/profile
```

**Rezultat:**
```http
*   Trying 127.0.0.1:5000...
* Connected to 127.0.0.1 (127.0.0.1) port 5000
> GET /profile HTTP/1.1
> Host: 127.0.0.1:5000
> User-Agent: curl/8.5.0
> Accept: */*
> Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.1.4 Python/3.9.25
< Date: Wed, 17 Dec 2025 02:42:38 GMT
< Content-Type: application/json
< Content-Length: 119
< Connection: close
< 
{"email":"student@example.com","id":"fcd292cf-ac6f-4cc2-add9-d7b30a49d347","role":"student","username":"student_user"}
```

---

## 6. Adăugare Problemă (Admin)
Adăugăm o problemă nouă folosind un token de administrator.

**Generare Token Admin (Python):**
```python
import jwt
# ... payload cu email="admin@example.com", role="admin" ...
token = jwt.encode(payload, "secret", algorithm="HS256")
```

**Comandă:**
```bash
curl -v -H "Authorization: Bearer <ADMIN_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"title": "Sum of Two Numbers", "description": "Write a function that adds two numbers."}' \
     http://127.0.0.1:5000/problems
```

**Rezultat:**
```http
*   Trying 127.0.0.1:5000...
* Connected to 127.0.0.1 (127.0.0.1) port 5000
> POST /problems HTTP/1.1
> Host: 127.0.0.1:5000
> User-Agent: curl/8.5.0
> Accept: */*
> Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
> Content-Type: application/json
> Content-Length: 89
> 
< HTTP/1.1 201 CREATED
< Server: Werkzeug/3.1.4 Python/3.9.25
< Date: Wed, 17 Dec 2025 02:54:22 GMT
< Content-Type: application/json
< Content-Length: 94
< Connection: close
< 
{"description":"Write a function that adds two numbers.","id":1,"title":"Sum of Two Numbers"}
```

---

## 7. Verificare Adăugare Problemă
Listăm din nou problemele pentru a confirma că cea nouă a fost adăugată.

**Comandă:**
```bash
curl -v http://127.0.0.1:5000/problems
```

**Rezultat:**
```http
*   Trying 127.0.0.1:5000...
* Connected to 127.0.0.1 (127.0.0.1) port 5000
> GET /problems HTTP/1.1
> Host: 127.0.0.1:5000
> User-Agent: curl/8.5.0
> Accept: */*
> 
< HTTP/1.1 200 OK
< Server: Werkzeug/3.1.4 Python/3.9.25
< Date: Wed, 17 Dec 2025 02:54:22 GMT
< Content-Type: application/json
< Content-Length: 96
< Connection: close
< 
[{"description":"Write a function that adds two numbers.","id":1,"title":"Sum of Two Numbers"}]
```
