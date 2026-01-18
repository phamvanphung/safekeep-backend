# Deployment Guide

Complete guide for deploying the Dead Man's Switch API to production.

## Prerequisites

- Docker and Docker Compose installed
- Domain name (optional, for HTTPS)
- SSL certificate (for HTTPS)
- Email service credentials (for sending notifications)

## Production Setup

### 1. Environment Variables

Create a `.env` file with production values:

```env
DATABASE_URL=postgresql+asyncpg://safekeep_user:STRONG_PASSWORD@db:5432/safekeep_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=CHANGE-THIS-TO-A-LONG-RANDOM-STRING-IN-PRODUCTION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Security Notes:**
- Use a strong, randomly generated `SECRET_KEY` (minimum 32 characters)
- Use strong database passwords
- Never commit `.env` file to version control

### 2. Update Docker Compose for Production

Create `docker-compose.prod.yml`:

```yaml
services:
  web:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=${ALGORITHM}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
    restart: unless-stopped
    
  worker:
    restart: unless-stopped
    
  beat:
    restart: unless-stopped
```

### 3. Configure CORS

Update `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 4. Database Backup

Set up regular backups:

```bash
# Backup script
docker compose exec db pg_dump -U safekeep_user safekeep_db > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T db psql -U safekeep_user safekeep_db < backup_20260118.sql
```

### 5. SSL/HTTPS Setup

#### Using Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. Email Integration

Update `app/worker.py` to send real emails:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def send_email(to_email: str, subject: str, body: str):
    # Configure your SMTP settings
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "your-email@gmail.com"
    smtp_password = "your-app-password"
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.send_message(msg)
    server.quit()
```

### 7. Monitoring

#### Health Check Endpoint

The API includes a health check at `/health`:

```bash
curl http://localhost:8000/health
```

#### Log Monitoring

```bash
# View logs
docker compose logs -f web
docker compose logs -f worker
docker compose logs -f beat

# Log rotation (add to cron)
find /var/log/safekeep -name "*.log" -mtime +7 -delete
```

### 8. Scaling

#### Horizontal Scaling

```yaml
services:
  web:
    deploy:
      replicas: 3
    # ... other config
```

#### Database Connection Pooling

Update `app/database.py`:

```python
engine = create_async_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)
```

## Deployment Steps

1. **Clone repository:**
   ```bash
   git clone https://github.com/phamvanphung/safekeep-backend.git
   cd safekeep-backend
   ```

2. **Create production environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Build and start services:**
   ```bash
   docker compose -f docker-compose.prod.yml build
   docker compose -f docker-compose.prod.yml up -d
   ```

4. **Run migrations:**
   ```bash
   docker compose exec web alembic upgrade head
   ```

5. **Verify deployment:**
   ```bash
   curl http://localhost:8000/health
   ```

## Maintenance

### Update Application

```bash
git pull origin main
docker compose build --no-cache
docker compose down
docker compose up -d
docker compose exec web alembic upgrade head
```

### Database Migrations

```bash
# Create migration
docker compose exec web alembic revision --autogenerate -m "description"

# Review migration file
# Apply migration
docker compose exec web alembic upgrade head
```

### Backup Database

```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker compose exec -T db pg_dump -U safekeep_user safekeep_db > "$BACKUP_DIR/backup_$DATE.sql"
# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

## Security Checklist

- [ ] Changed default `SECRET_KEY`
- [ ] Using strong database passwords
- [ ] HTTPS enabled
- [ ] CORS configured for specific domains
- [ ] Database backups configured
- [ ] Logs are monitored
- [ ] Email service configured
- [ ] Firewall rules configured
- [ ] Regular security updates
- [ ] Rate limiting implemented (consider adding)

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs web

# Check database connection
docker compose exec web python -c "from app.database import engine; print('OK')"

# Restart services
docker compose restart
```

### Database Connection Issues

```bash
# Test database connection
docker compose exec db psql -U safekeep_user -d safekeep_db -c "SELECT 1;"

# Check database logs
docker compose logs db
```

### High Memory Usage

```bash
# Check container resources
docker stats

# Restart services
docker compose restart
```

## Support

For deployment issues, check:
- Docker logs: `docker compose logs`
- Application logs: Check log files
- Database logs: `docker compose logs db`
- GitHub Issues: Open an issue on the repository
