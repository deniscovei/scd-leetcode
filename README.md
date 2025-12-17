# SCD-LeetCode

## Structura Proiectului

- `backend/`: Serviciul principal API (Python/Flask).
- `worker/`: Serviciul de execuție a codului (Python).
- `frontend/`: Interfața web (React).
- `docker/`: Fișiere de configurare Docker și Docker Swarm.

## Development Logs

### Milestone 2 - Prezentare Intermediară

#### 1. Stadiul Implementării (40%)

În această etapă, au fost implementate funcționalitățile de bază și infrastructura necesară pentru rularea aplicației într-un mediu distribuit.

**Componente Implementate:**

1.  **Backend API (Python/Flask):**
    -   Configurare conexiune bază de date (PostgreSQL).
    -   Modele de date definite: `User`, `Problem`.
    -   Endpoint-uri de bază:
        -   `GET /`: Health check.
        -   `GET /profile`: Vizualizare profil utilizator (protejat).
        -   `GET /problems`: Listare probleme.
        -   `POST /problems`: Adăugare problemă (doar Admin).
        -   `POST /submit`: Trimitere soluție pentru evaluare (Student).
    -   Integrare middleware pentru validare token JWT (Keycloak).

2.  **Worker Service (Python):**
    -   Conectare la RabbitMQ.
    -   Consumare mesaje din coada `judge_queue`.
    -   Simulare procesare (sleep) și confirmare mesaj (ACK).
    -   Configurat pentru replicare (2 replici în Docker Swarm).

3.  **Infrastructură (Docker Swarm):**
    -   **PostgreSQL:** Bază de date unică pentru aplicație și Keycloak.
    -   **Keycloak:** Server de identitate pentru autentificare/autorizare.
    -   **RabbitMQ:** Broker de mesaje pentru comunicarea asincronă.
    -   **Docker Compose:** Fișier `docker-compose.yml` complet pentru orchestrarea tuturor serviciilor.

#### 2. Integrare Docker Swarm

Toate componentele sunt containerizate și definite într-un stack Docker Swarm.

**Servicii definite:**
-   `db`: PostgreSQL 13.
-   `keycloak`: Keycloak 22.
-   `rabbitmq`: RabbitMQ 3 Management.
-   `backend`: Imagine custom `scd-backend`.
-   `worker`: Imagine custom `scd-worker` (replicat x2).

**Rețea:**
-   `scd-network`: Rețea de tip `overlay` pentru comunicarea între containere pe noduri diferite.

#### 3. Pași pentru Rulare

1.  **Build Imagini:**
    ```bash
    docker build -t scd-backend:latest ./backend
    docker build -t scd-worker:latest ./worker
    ```

2.  **Inițializare Swarm (dacă nu e deja):**
    ```bash
    docker swarm init
    ```

3.  **Deploy Stack:**
    ```bash
    docker stack deploy -c docker/docker-compose.yml scd-stack
    ```

4.  **Verificare:**
    ```bash
    docker service ls
    docker service logs scd-stack_backend
    ```

## Milestone-uri

- [x] Milestone 1: Alegerea proiectului și definirea arhitecturii.
- [x] Milestone 2: Implementare parțială (40%) și integrare Docker Swarm.
- [ ] Milestone 3: Aplicația finală.

## Testare API

Rezultatele detaliate ale testării API-ului pot fi găsite în fișierul [api_results.md](api_results.md).

Acesta include exemple de comenzi `curl` și răspunsurile serverului pentru:
- Health Check
- Inițializare Bază de Date
- Autentificare (Student/Admin)
- Management Probleme
- Submitere Soluții (Procesare Asincronă)