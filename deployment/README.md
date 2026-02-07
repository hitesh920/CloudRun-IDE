# CloudRun IDE - Deployment Guide

## 🚀 Quick Start (Docker Compose)

### Prerequisites
- Docker & Docker Compose installed
- Port 80 available (or change in docker-compose.yml)

### Deploy

1. **Set environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your GEMINI_API_KEY
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **View logs:**
   ```bash
   docker-compose logs -f
   ```

5. **Stop services:**
   ```bash
   docker-compose down
   ```

---

## 🔧 Production Deployment (VPS)

### For Oracle Cloud (ARM64)

1. **SSH into your VPS:**
   ```bash
   ssh ubuntu@your-vps-ip
   ```

2. **Install Docker:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

3. **Install Docker Compose:**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

4. **Clone repository:**
   ```bash
   git clone <your-repo-url> cloudrun-ide
   cd cloudrun-ide
   ```

5. **Configure environment:**
   ```bash
   cp backend/.env.example backend/.env
   nano backend/.env  # Add GEMINI_API_KEY
   ```

6. **Start services:**
   ```bash
   docker-compose up -d
   ```

7. **Setup firewall (optional):**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

---

## 🔐 HTTPS Setup (Optional)

### Using Let's Encrypt with Certbot

1. **Install Certbot:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Get SSL certificate:**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Auto-renewal:**
   ```bash
   sudo certbot renew --dry-run
   ```

---

## 📊 Monitoring

### View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Check status:
```bash
docker-compose ps
```

### Restart services:
```bash
docker-compose restart
```

---

## 🛠️ Troubleshooting

### Backend can't connect to Docker
- Ensure `/var/run/docker.sock` is mounted in docker-compose.yml
- Check Docker permissions: `sudo usermod -aG docker $USER`

### Frontend can't reach backend
- Check backend is running: `docker-compose ps`
- Verify Nginx proxy configuration in `frontend/nginx.conf`

### Port already in use
- Change ports in `docker-compose.yml`:
  ```yaml
  ports:
    - "8080:80"  # Change 80 to 8080
  ```

---

## 🔄 Updates

To update the application:

```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📝 Environment Variables

### Backend (.env)
```env
GEMINI_API_KEY=your_key_here
DEBUG=False
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost,https://your-domain.com
MAX_EXECUTION_TIME=60
MAX_MEMORY=1g
RATE_LIMIT_PER_MINUTE=10
```

---

## 🎯 Performance Tips

1. **Increase container resources** (in docker-compose.yml):
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

2. **Enable caching** for faster builds
3. **Use production mode** (DEBUG=False)
4. **Monitor resource usage:**
   ```bash
   docker stats
   ```

---

## 🆘 Support

For issues, check:
- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`
- Docker status: `docker ps -a`
