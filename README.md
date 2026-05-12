# Asynchronous Document Management API

A high-performance, Domain-Driven Design (DDD) REST API for secure, non-blocking document storage. This system is engineered to handle large file uploads without starving web workers, featuring strict Role-Based Access Control (RBAC), real-time WebSocket notifications, and robust audit logging.

## 🚀 Tech Stack

- **Language/Framework:** Python 3.13, Django 5.x, Django REST Framework (DRF)
- **Package Manager:** `uv`
- **Asynchronous Task Queue:** Celery & Redis
- **Object Storage:** MinIO (S3-compatible API)
- **Database:** PostgreSQL (with SQLite for local fallback)
- **Web Server:** Gunicorn with Uvicorn workers (ASGI) + Nginx Reverse Proxy
- **Real-time Comms:** Django Channels (WebSockets)
- **Infrastructure:** Docker & Docker Compose

## 🏗️ Architecture & Core Patterns

This application strictly avoids "fat models" and "fat views", relying on clean decoupling:

1. **Domain-Driven Design (DDD):** Business logic is entirely isolated within the `services/` directory (e.g., `document_services.py`, `audit_log_services.py`). Serializers are strictly for data validation, and Views orchestrate HTTP requests. The Service layer has zero knowledge of the HTTP context or Celery.
2. **"Store & Forward" (Non-Blocking Uploads):** Incoming files are immediately spooled to a local NVMe/SSD staging volume via `documents/storage.py`. The API instantly returns `202 Accepted`. A background Celery worker picks up the file and handles the slow network transfer to MinIO.
3. **Transactional Audit Logging:** Every document creation or state change generates an audit log. To guarantee data integrity, the logger execution is bound to Django's `transaction.on_commit()` hook.
4. **Real-Time ASGI Notifications:** Upon successful MinIO upload by the Celery worker, the Audit log triggers a WebSocket broadcast via the `notifications/` app to alert the client in real-time.
5. **Optimized API Caching:** List endpoints utilize a custom decorator (`decorators.py`) that caches the raw JSON dictionary directly via Django's low-level cache API, bypassing DRF serialization overhead and pickling errors.

## 📂 Project Structure

```text
.
├── accounts/                   # User management, Authentication, and RBAC
│   ├── permissions.py          # Custom role-based DRF permissions
│   ├── serializers.py          
│   └── views.py                
├── config/                     # Django project configuration
│   ├── asgi.py                 # ASGI entrypoint for WebSockets & Uvicorn
│   ├── celery.py               # Celery application configuration
│   └── settings.py             
├── documents/                  # Core Domain: Document Management
│   ├── models/                 # DB Schemas split by domain
│   │   ├── audit_log.py        
│   │   └── document.py         
│   ├── services/               # The "Brain" (Pure domain logic)
│   │   ├── audit_log_services.py 
│   │   └── document_services.py  
│   ├── decorators.py           # Custom caching implementations
│   ├── permissions.py          # Document-specific access control
│   ├── serializers.py          # Input/Output validation (Write-only files)
│   ├── storage.py              # Local spooling storage definition
│   ├── tasks.py                # Celery background workers
│   └── views.py                # Orchestration and HTTP Responses
├── nginx/                      # Nginx reverse proxy configuration
│   ├── Dockerfile
│   └── nginx.conf
├── notifications/              # Django Channels / WebSocket integration
│   ├── consumers.py            # Async WebSocket consumers
│   ├── middleware.py           # Token authentication for WebSockets
│   └── routing.py              # WebSocket URL routing
├── docker-compose.yaml         # Full infrastructure stack definition
├── Dockerfile                  # Django application image
├── entrypoint.sh               # Dynamic setup script (Migrations/Static)
├── pyproject.toml / uv.lock    # Python dependencies (uv)
└── test_ws.html                # Simple client for testing WebSockets

```

## 🛠️ Local Development Setup

### Prerequisites

- Docker & Docker Compose
- `uv` (Fast Python Package Installer)

### 1. Environment Configuration

Create an `.env` file in the root directory based on your environment needs.

```bash
# Ensure DB credentials, Celery broker URLs, and MinIO keys are set

```

### 2. Launch the Infrastructure

The application relies on external services. Spin up the datastores and storage first:

```bash
docker compose up -d postgres redis minio

```

### 3. Launch the Application Stack

Start the Django API, Celery Worker, and Nginx proxy.
*Note: The `entrypoint.sh` will automatically wait for the database, run migrations, and collect static files.*

```bash
docker compose up -d web celery nginx

```

### 4. Accessing the Services

- **API Endpoints:** `http://localhost:8000/` (or via Nginx proxy)
- **MinIO Console:** `http://localhost:9001/`

## 🧪 Testing Strategy

The test suite validates the Domain Logic, API Contracts, and RBAC implementation without relying on external infrastructure.

- **Isolated Environments:** Django's cache backend is dynamically overridden during tests to bypass Redis.
- **Mocking:** Celery tasks (`.delay()`), MinIO network operations, and Channel layer broadcasts are heavily mocked using `unittest.mock.patch` to ensure tests execute in milliseconds.

**To run the tests locally:**

```bash
uv run python manage.py test

```

## 🔮 Future Improvements

- **Direct-to-S3 Presigned URLs:** For massive files (>500MB), shift the bandwidth away from the server entirely by having the API generate a MinIO Presigned URL for the frontend.
- **Dead Letter Queue (DLQ):** Implement a DLQ to capture and flag tasks that fail their maximum retry attempts (e.g., if MinIO experiences an extended outage).
- **Automated CI/CD Pipeline:** Implement GitHub Actions for automated linting (Ruff), test execution, and Docker image publishing.

