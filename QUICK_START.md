# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Git installed

## Steps

### 1. Clone and Navigate

```bash
git clone https://github.com/phamvanphung/safekeep-backend.git
cd safekeep-backend
```

### 2. Start Services

```bash
docker compose up -d
```

### 3. Run Database Migration

```bash
# If you get "column vaults.name does not exist" error, run:
docker compose exec db psql -U safekeep_user -d safekeep_db <<EOF
ALTER TABLE vaults ADD COLUMN IF NOT EXISTS name VARCHAR NOT NULL DEFAULT 'default_vault';
ALTER TABLE vaults DROP CONSTRAINT IF EXISTS vaults_user_id_key;
ALTER TABLE vaults ALTER COLUMN name DROP DEFAULT;
EOF

# Then run migrations
docker compose exec web alembic upgrade head
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Open in browser
# API Docs: http://localhost:8000/docs
```

### 5. Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### 6. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword123"
```

Copy the `access_token` from the response.

### 7. Use the API

Replace `{token}` with your access token:

```bash
# Get timer
curl -X GET "http://localhost:8000/timer" \
  -H "Authorization: Bearer {token}"

# Create vault
curl -X POST "http://localhost:8000/vaults" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Vault",
    "encrypted_data": "encrypted_data_here",
    "client_salt": "salt_here"
  }'

# Send heartbeat
curl -X POST "http://localhost:8000/heartbeat" \
  -H "Authorization: Bearer {token}"
```

## Common Commands

```bash
# View logs
docker compose logs -f web

# Restart services
docker compose restart

# Stop services
docker compose down

# Update from GitHub
git pull origin main
docker compose build --no-cache
docker compose up -d
```

## Next Steps

- Read [API_GUIDE.md](API_GUIDE.md) for detailed API usage
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Check [README.md](README.md) for complete documentation

## Troubleshooting

**Service not running?**
```bash
docker compose logs web --tail=50
docker compose restart web
```

**Database errors?**
```bash
docker compose exec db psql -U safekeep_user -d safekeep_db -c "\dt"
```

**Port already in use?**
Change port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

## Need Help?

- Check the logs: `docker compose logs`
- Read the full [README.md](README.md)
- Open an issue on GitHub
