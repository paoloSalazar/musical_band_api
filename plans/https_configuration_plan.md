# HTTPS Configuration Plan for Musical Band API

## Overview

Configure HTTPS for the FastAPI application running in Docker containers.

## Current State

- Application runs on HTTP port 8000
- No TLS/SSL configuration
- No reverse proxy
- Development setup with MailHog for email testing

## Options for HTTPS

### Option 1: Let's Encrypt with Nginx Reverse Proxy (Recommended for Production)
Add an nginx container with Let's Encrypt certification.

### Option 2: Self-Signed Certificates
Generate self-signed certificates for development/testing.

### Option 3: Traefik Reverse Proxy
Use Traefik as a reverse proxy with automatic Let's Encrypt integration.

### Option 4: Cloud Provider SSL
Configure SSL at the load balancer/CDN level (AWS ACM, GCP Managed SSL, etc.).

## Recommended Approach: Nginx + Let's Encrypt

### Files to Create/Modify

1. **build/nginx.conf** - Nginx configuration
2. **build/docker-compose.yml** - Add nginx and certbot services
3. **build/certbot/** - Directory for certificate storage
4. **build/www/** - Directory for ACME challenge files

### Implementation Steps

#### Step 1: Create nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;
        
        ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### Step 2: Update docker-compose.yml

```yaml
name: musical_band

services:
  db:
    image: postgres:15-alpine
    env_file:
      - .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - musical_band_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  db-init:
    build:
      context: ..
      dockerfile: build/Dockerfile
    depends_on:
      db:
        condition: service_healthy
    command: ["python", "scripts/sync_database.py", "scripts/backup_data_20260629_InitialState.sql", "--force"]
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+pg8000://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    networks:
      - musical_band_network
    volumes:
      - ..:/app
    restart: "no"

  api:
    build:
      context: ..
      dockerfile: build/Dockerfile
    depends_on:
      db-init:
        condition: service_completed_successfully
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+pg8000://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      SMTP_HOST: mailhog
      # Trust proxy headers from nginx
      PRIVACY_LEVEL: public
    ports:
      - "8000:8000"
    volumes:
      - app_logs:/app/logs
    networks:
      - musical_band_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - certbot_etc:/etc/letsencrypt
      - certbot_var:/var/www/certbot
    depends_on:
      - api
    networks:
      - musical_band_network

  certbot:
    image: certbot/certbot
    volumes:
      - certbot_etc:/etc/letsencrypt
      - certbot_var:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do sleep 12h & wait $${!}; certbot renew --quiet --deploy-hook \"nginx -s reload\"; done &'"
    networks:
      - musical_band_network

volumes:
  postgres_data:
  app_logs:
  certbot_etc:
  certbot_var:

networks:
  musical_band_network:
    driver: bridge
```

#### Step 3: Update FastAPI CORS Settings (main.py)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Certificate Generation

#### Option A: Let's Encrypt (Production)

1. **Initial certificate request**
```bash
docker run -it --rm \
  -v "certbot_etc:/etc/letsencrypt" \
  -v "certbot_var:/var/www/certbot" \
  certbot/certbot \
  certonly --webroot -w /var/www/certbot -d your-domain.com
```

2. **Using existing certbot service**
```bash
docker-compose -f build/docker-compose.yml run --rm certbot \
  certonly --webroot -w /var/www/certbot -d your-domain.com
```

#### Option B: Self-Signed Certificate (Development)

```bash
# Create directories
mkdir -p build/certs

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout build/certs/key.pem \
  -out build/certs/cert.pem \
  -subj "/CN=localhost"

# Update nginx.conf to use local certs
# Replace certificate paths:
# ssl_certificate /etc/letsencrypt/live/localhost/cert.pem;
# ssl_certificate_key /etc/letsencrypt/live/localhost/key.pem;
```

### Environment Variables to Add (Optional)

Add to `.env.production`:

```env
# Domain configuration
DOMAIN=your-domain.com

# HTTPS settings
HTTPS_ENABLED=true

# Production JWT secret (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=generate-a-secure-secret-key-here

# Production SMTP settings
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
```

### Deployment Steps

1. **Obtain SSL certificate**
   - Let's Encrypt or self-signed

2. **Create nginx.conf** with proper domain and certificate paths

3. **Update docker-compose.yml** with nginx and certbot services

4. **Update FastAPI CORS** to allow your domain

5. **Deploy containers**
```bash
cd build
docker-compose up -d
```

6. **Verify HTTPS**
```bash
curl -I https://your-domain.com
# Should return HTTP/2 200
```

7. **Set up automatic renewal**
   - Certbot service auto-renews every 12 hours

### Cloud Provider SSL Alternative

For platforms like AWS, GCP, Azure, or Render:

1. **Request certificate** at the cloud provider level
2. **Point domain** to load balancer/CDN
3. **Minimal app changes** - just update CORS origins
4. **No nginx needed** - SSL handled by provider

### Security Headers to Add in nginx.conf

```nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Additional Production Considerations

1. **Rate Limiting** (nginx)
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
location / {
    limit_req zone=api burst=20 nodelay;
    ...
}
```

2. **HSTS for all HTTPS**
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

3. **Remove MailHog** for production
4. **Use production JWT secret**
5. **Configure proper database credentials**
6. **Set up backup strategy**

### Testing HTTPS Locally

When using self-signed certificates:

```bash
# Test with curl (skip verification for self-signed)
curl -k https://localhost

# Or add certificate to system trust store
```

### Troubleshooting

- **Certificate not renewing**: Check certbot logs
- **Nginx proxy errors**: Verify upstream api:8000 is accessible
- **Mixed content warnings**: Ensure all resources use HTTPS
- **CORS errors**: Update allow_origins in FastAPI middleware