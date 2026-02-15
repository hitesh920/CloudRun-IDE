# CloudRun IDE — Deployment Guide

## Docker Compose (Recommended)

### Prerequisites

- Docker & Docker Compose
- Ports 80 and 8000 available
- A free [Groq API key](https://console.groq.com/keys) or [Gemini API key](https://makersuite.google.com/app/apikey)

### Deploy

```bash
# 1. Create data directory
mkdir -p data

# 2. Configure
cp backend/.env.example backend/.env
nano backend/.env
# Add: GROQ_API_KEY=gsk_...
# Set: JWT_SECRET=some-random-secret-string

# 3. Start
docker compose up -d

# 4. Verify
docker compose logs -f

# 5. Access
# http://localhost (or http://<server-ip>)
```

### Manage

```bash
docker compose ps          # Check status
docker compose logs -f     # Stream logs
docker compose restart     # Restart services
docker compose down        # Stop everything
docker compose up -d --build  # Rebuild and restart
```

## VPS Deployment (Oracle Cloud / AWS / etc.)

### 1. Install Docker

```bash
ssh ubuntu@your-server-ip

curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in

# Install Docker Compose (if not included)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Configure

```bash
git clone https://github.com/hitesh920/CloudRun.git
cd CloudRun
mkdir -p data
cp backend/.env.example backend/.env
nano backend/.env  # Add GROQ_API_KEY, set JWT_SECRET
```

### 3. Start

```bash
docker compose up -d
docker compose logs -f  # Watch startup (image pulls take 2-3 min first time)
```

### 4. Firewall

```bash
# Oracle Cloud: Add ingress rules in VCN security list for ports 80, 8000

# Ubuntu firewall
sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 8000 -j ACCEPT
```

### 5. Access

Open `http://<your-server-ip>` in a browser.

## HTTPS (Optional)

### With Certbot (requires a domain name)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo certbot renew --dry-run  # Test auto-renewal
```

## Updating

```bash
cd CloudRun
git pull
docker compose down
docker compose up -d --build
docker compose logs -f
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Groq API key (free, primary AI provider) |
| `GEMINI_API_KEY` | — | Gemini API key (fallback AI provider) |
| `JWT_SECRET` | `cloudrun-ide-secret-...` | Secret for JWT token signing (**change in production!**) |
| `DATABASE_URL` | SQLite (`data/cloudrun.db`) | Database URL. Supports PostgreSQL. |
| `DEBUG` | `false` | Debug mode |
| `MAX_EXECUTION_TIME` | `30` | Timeout per execution (seconds) |
| `MAX_MEMORY` | `256m` | Memory limit per container |
| `MAX_CPU_QUOTA` | `50000` | CPU quota per container |
| `MAX_REQUESTS_PER_MINUTE` | `30` | API rate limit |
| `PRE_PULL_IMAGES` | `false` | Pull all Docker images on startup |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |

## Troubleshooting

**Backend can't connect to Docker**
- Check Docker socket mount in `docker-compose.yml`: `/var/run/docker.sock:/var/run/docker.sock`
- Verify Docker is running: `docker ps`

**Frontend shows connection error**
- Check backend is healthy: `curl http://localhost:8000/health`
- Check Nginx proxy: `docker compose logs frontend`

**AI assistant not working**
- Verify API key: `curl http://localhost:8000/api/ai/status`
- Check backend logs for API errors: `docker compose logs backend | grep AI`

**Auth not working**
- Check database initialized: `docker compose logs backend | grep Database`
- Verify data directory is mounted: `docker compose exec backend ls /app/data/`

**Ubuntu containers can't access network**
- Ubuntu containers have `network_disabled=False` by default
- Other languages have network disabled for security

**Port 80 already in use**
- Change in `docker-compose.yml`: `"8080:80"` instead of `"80:80"`

## Monitoring

```bash
docker stats                    # Live resource usage
docker compose ps               # Service status
curl http://localhost:8000/api/status  # Full system status JSON
```
