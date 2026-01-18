# Dead Man's Switch API

A Zero-Knowledge Dead Man's Switch backend built with FastAPI, PostgreSQL, and Celery.

## Features

- **User Authentication**: JWT-based authentication with password hashing using Argon2
- **Timer Management**: Automatic timer creation on user registration with configurable timeout
- **Heartbeat System**: POST endpoint to update check-in and recalculate deadline
- **Vault Storage**: CRUD operations for encrypted data (zero-knowledge architecture) - **Multiple vaults per user**
- **Beneficiary Management**: Store beneficiary information for emergency contacts
- **Automated Trigger**: Celery worker checks for expired timers hourly and sends notifications

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
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
│       ├── timer.py          # Timer management endpoints
│       ├── vault.py          # Vault CRUD endpoints
│       └── beneficiary.py   # Beneficiary CRUD endpoints
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

1. **Clone the repository:**
   ```bash
   git clone https://github.com/phamvanphung/safekeep-backend.git
   cd safekeep-backend
   ```

2. **Create a `.env` file** (optional, defaults are in docker-compose.yml):
   ```env
   DATABASE_URL=postgresql+asyncpg://safekeep_user:safekeep_password@db:5432/safekeep_db
   REDIS_URL=redis://redis:6379/0
   SECRET_KEY=your-secret-key-change-in-production-use-a-long-random-string
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Start all services:**
   ```bash
   docker compose up -d
   ```

4. **Run database migrations:**
   ```bash
   docker compose exec web alembic upgrade head
   ```

   **Note:** If you encounter a "column vaults.name does not exist" error, run:
   ```bash
   docker compose exec db psql -U safekeep_user -d safekeep_db -c "ALTER TABLE vaults ADD COLUMN IF NOT EXISTS name VARCHAR NOT NULL DEFAULT 'default_vault';"
   docker compose exec db psql -U safekeep_user -d safekeep_db -c "ALTER TABLE vaults DROP CONSTRAINT IF EXISTS vaults_user_id_key;"
   docker compose exec db psql -U safekeep_user -d safekeep_db -c "ALTER TABLE vaults ALTER COLUMN name DROP DEFAULT;"
   ```

5. **Access the API:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables** in `.env` file

3. **Start PostgreSQL and Redis** (or use Docker Compose for just these services)

4. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

5. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Start Celery worker** (in a separate terminal):
   ```bash
   celery -A app.worker.celery_app worker --loglevel=info
   ```

7. **Start Celery beat** (in another terminal):
   ```bash
   celery -A app.worker.celery_app beat --loglevel=info
   ```

## API Endpoints

### Authentication

#### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "is_active": true
}
```

**Note:** Automatically creates a Timer with 30-day default timeout.

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Timer Management

#### Get Timer
```http
GET /timer
Authorization: Bearer {token}
```

**Response:**
```json
{
  "user_id": "uuid",
  "status": "ACTIVE",
  "timeout_days": 30,
  "last_checkin": "2026-01-18T12:00:00",
  "deadline": "2026-02-17T12:00:00"
}
```

#### Update Timer
```http
PUT /timer
Authorization: Bearer {token}
Content-Type: application/json

{
  "timeout_days": 60
}
```

**Response:** Updated timer object (deadline automatically recalculated)

### Heartbeat

#### Send Heartbeat
```http
POST /heartbeat
Authorization: Bearer {token}
```

**Response:**
```json
{
  "message": "Heartbeat received successfully",
  "last_checkin": "2026-01-18T12:00:00",
  "deadline": "2026-02-17T12:00:00"
}
```

**Note:** Updates `last_checkin` and recalculates `deadline` based on `timeout_days`.

### Vault Management (Multiple Vaults Per User)

#### Create Vault
```http
POST /vaults
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "My Important Data",
  "encrypted_data": "encrypted_string_here",
  "client_salt": "salt_string_here"
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "My Important Data",
  "encrypted_data": "encrypted_string_here",
  "client_salt": "salt_string_here"
}
```

#### List All Vaults
```http
GET /vaults
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "name": "My Important Data",
    "encrypted_data": "encrypted_string_here",
    "client_salt": "salt_string_here"
  }
]
```

#### Get Specific Vault
```http
GET /vaults/{vault_id}
Authorization: Bearer {token}
```

#### Update Vault
```http
PUT /vaults/{vault_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Name",
  "encrypted_data": "new_encrypted_data",
  "client_salt": "new_salt"
}
```

#### Delete Vault
```http
DELETE /vaults/{vault_id}
Authorization: Bearer {token}
```

### Beneficiary Management

#### Create Beneficiary
```http
POST /beneficiaries
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "beneficiary@example.com",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "email": "beneficiary@example.com",
  "name": "John Doe"
}
```

#### List All Beneficiaries
```http
GET /beneficiaries
Authorization: Bearer {token}
```

#### Get Specific Beneficiary
```http
GET /beneficiaries/{beneficiary_id}
Authorization: Bearer {token}
```

#### Update Beneficiary
```http
PUT /beneficiaries/{beneficiary_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "newemail@example.com",
  "name": "Jane Doe"
}
```

#### Delete Beneficiary
```http
DELETE /beneficiaries/{beneficiary_id}
Authorization: Bearer {token}
```

## Database Models

### User
- `id` (UUID): Primary key
- `email` (String): Unique email address
- `hashed_password` (String): Argon2 hashed password
- `is_active` (Boolean): Active status

### Timer
- `user_id` (UUID): Foreign key to User (primary key)
- `status` (Enum): ACTIVE or TRIGGERED
- `timeout_days` (Integer): Number of days for timeout
- `last_checkin` (DateTime): Last heartbeat timestamp
- `deadline` (DateTime): Calculated deadline

### Vault
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User
- `name` (String): Vault name/identifier
- `encrypted_data` (Text): Encrypted data (zero-knowledge)
- `client_salt` (String): Client-side salt

### Beneficiary
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User
- `email` (String): Beneficiary email
- `name` (String): Beneficiary name

## Celery Worker

The Celery worker runs a periodic task every hour that:

1. Queries for expired timers (`deadline < now AND status != TRIGGERED`)
2. For each expired timer:
   - Retrieves user's beneficiaries
   - Retrieves all user's vaults
   - Logs: `"Sending Email to [Beneficiary_Email] with vaults data: [vault_data]"`
   - Updates timer status to `TRIGGERED`

**Note:** Currently simulates email sending via console logs. Integrate with an email service (SMTP, SendGrid, etc.) for production.

## Security Notes

- **Passwords**: Hashed using Argon2 (industry-standard)
- **Authentication**: JWT tokens with configurable expiration
- **Zero-Knowledge**: Server stores encrypted data but never decrypts it
- **CORS**: Currently allows all origins - configure appropriately for production
- **SECRET_KEY**: Change the default secret key in production
- **HTTPS**: Use HTTPS in production

## Troubleshooting

### Service Not Running

```bash
# Check logs
docker compose logs web --tail=50

# Restart service
docker compose restart web

# Rebuild and restart
docker compose build web
docker compose up -d web
```

### Database Migration Issues

```bash
# Check migration status
docker compose exec web alembic current

# Create new migration
docker compose exec web alembic revision --autogenerate -m "description"

# Apply migrations
docker compose exec web alembic upgrade head
```

### Update from GitHub

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker compose build --no-cache

# Restart services
docker compose down
docker compose up -d

# Run migrations if needed
docker compose exec web alembic upgrade head
```

## Development Scripts

- `update.sh` / `update.ps1` / `update.bat` - Update and restart project
- `migrate_vaults.sh` - Migration helper script
- `migrate_vaults.sql` - Manual SQL migration

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub.
