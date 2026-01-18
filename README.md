# Dead Man's Switch API

A Zero-Knowledge Dead Man's Switch backend built with FastAPI, PostgreSQL, and Celery.

## Features

- **User Authentication**: JWT-based authentication with password hashing using Argon2
- **Timer Management**: Automatic timer creation on user registration with configurable timeout
- **Heartbeat System**: POST endpoint to update check-in and recalculate deadline
- **Vault Storage**: CRUD operations for encrypted data (zero-knowledge architecture)
- **Beneficiary Management**: Store beneficiary information for emergency contacts
- **Automated Trigger**: Celery worker checks for expired timers hourly and sends notifications

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy (Async)
- **Migrations**: Alembic
- **Task Queue**: Celery with Redis
- **Authentication**: JWT with passlib[argon2]

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and session
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database CRUD operations
│   ├── dependencies.py      # Auth dependencies
│   ├── worker.py            # Celery worker and tasks
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── heartbeat.py     # Heartbeat endpoint
│       └── vault.py         # Vault CRUD endpoints
├── alembic/                 # Database migrations
├── docker-compose.yml       # Docker services configuration
├── Dockerfile               # Docker image definition
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Using Docker Compose

1. Clone the repository and navigate to the project directory

2. Create a `.env` file (optional, defaults are in docker-compose.yml):
   ```env
   DATABASE_URL=postgresql+asyncpg://safekeep_user:safekeep_password@db:5432/safekeep_db
   REDIS_URL=redis://redis:6379/0
   SECRET_KEY=your-secret-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. Start all services:
   ```bash
   docker-compose up -d
   ```

4. Run database migrations:
   ```bash
   docker-compose exec web alembic upgrade head
   ```

5. Access the API:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env` file

3. Start PostgreSQL and Redis (or use Docker Compose for just these services)

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Start Celery worker (in a separate terminal):
   ```bash
   celery -A app.worker.celery_app worker --loglevel=info
   ```

7. Start Celery beat (in another terminal):
   ```bash
   celery -A app.worker.celery_app beat --loglevel=info
   ```

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user (automatically creates a Timer)
- `POST /auth/login` - Login and get JWT token

### Heartbeat

- `POST /heartbeat` - Update last check-in and recalculate deadline (requires authentication)

### Vault

- `POST /vault` - Create vault for encrypted data
- `GET /vault` - Get vault data
- `PUT /vault` - Update vault data
- `DELETE /vault` - Delete vault data

All vault endpoints require authentication.

## Database Models

### User
- `id` (UUID): Primary key
- `email`: Unique email address
- `hashed_password`: Argon2 hashed password
- `is_active`: Active status

### Timer
- `user_id` (UUID): Foreign key to User (primary key)
- `status`: Enum (ACTIVE, TRIGGERED)
- `timeout_days`: Number of days for timeout
- `last_checkin`: Last heartbeat timestamp
- `deadline`: Calculated deadline

### Vault
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User (unique)
- `encrypted_data`: Encrypted data (Text)
- `client_salt`: Client-side salt

### Beneficiary
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User
- `email`: Beneficiary email
- `name`: Beneficiary name

## Celery Worker

The Celery worker runs a periodic task every hour that:
1. Queries for expired timers (deadline < now AND status != TRIGGERED)
2. For each expired timer:
   - Retrieves user's beneficiaries
   - Retrieves user's vault data
   - Logs: "Sending Email to [Beneficiary_Email] with data [Encrypted_Data]"
   - Updates timer status to TRIGGERED

## Security Notes

- Passwords are hashed using Argon2
- JWT tokens are used for authentication
- The server stores encrypted data but never decrypts it (zero-knowledge architecture)
- Change the `SECRET_KEY` in production
- Configure CORS appropriately for production

## License

MIT
