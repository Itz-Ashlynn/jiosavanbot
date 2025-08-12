# Docker Deployment Guide

## 🐳 Quick Start with Docker

The JioSaavn Bot can be easily deployed using Docker. This guide covers both local development and production deployment.

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

### 📋 Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Itz-Ashlynn/jiosavanbot.git
   cd jiosavanbot
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Required Environment Variables:**
   ```env
   API_ID=your_api_id                    # From my.telegram.org
   API_HASH=your_api_hash                # From my.telegram.org
   BOT_TOKEN=your_bot_token              # From @BotFather
   OWNER_ID=your_telegram_user_id        # From @userinfobot
   DATABASE_URL=your_mongodb_url         # MongoDB connection string
   PORT=80                               # Server port (optional)
   ```

### 🚀 Deployment Options

#### Option 1: Automated Deployment (Recommended)

Use the provided deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

The script provides these options:
- **Production**: Bot only with external database
- **Development**: Bot + local MongoDB
- **Build only**: Just build the Docker image
- **Management**: Stop, restart, view logs

#### Option 2: Manual Docker Compose

**Production deployment:**
```bash
docker-compose up -d --build jiosaavn-bot
```

**Development with local MongoDB:**
```bash
docker-compose --profile local up -d --build
```

#### Option 3: Docker CLI

**Build image:**
```bash
docker build -t jiosaavn-bot .
```

**Run container:**
```bash
docker run -d \
  --name jiosaavn-bot \
  -p 80:80 \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  -e OWNER_ID=your_telegram_user_id \
  -e DATABASE_URL=your_mongodb_url \
  jiosaavn-bot
```

### 🔧 Configuration

#### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `API_ID` | ✅ | Telegram API ID | `12345678` |
| `API_HASH` | ✅ | Telegram API Hash | `abcdef123456` |
| `BOT_TOKEN` | ✅ | Bot token from @BotFather | `123:ABC-DEF` |
| `OWNER_ID` | ✅ | Admin Telegram user ID | `987654321` |
| `DATABASE_URL` | ✅ | MongoDB connection string | `mongodb://...` |
| `HOST` | ❌ | Server host | `0.0.0.0` |
| `PORT` | ❌ | Server port | `80` |

#### MongoDB Connection Strings

**MongoDB Atlas (Recommended):**
```
mongodb+srv://username:password@cluster.mongodb.net/jiosaavn
```

**Local MongoDB:**
```
mongodb://localhost:27017/jiosaavn
```

**Docker MongoDB:**
```
mongodb://admin:password@mongodb:27017/jiosaavn?authSource=admin
```

### 📊 Monitoring & Management

#### View Logs
```bash
docker-compose logs -f jiosaavn-bot
```

#### Health Check
```bash
curl http://localhost:80/
```

#### Container Stats
```bash
docker stats jiosaavn-bot
```

#### Restart Bot
```bash
docker-compose restart jiosaavn-bot
```

#### Update Bot
```bash
git pull
docker-compose up -d --build jiosaavn-bot
```

### 🌐 Web Interface

After deployment, access:
- **Main Dashboard**: `http://localhost:80`
- **API Stats**: `http://localhost:80/api/stats`
- **Health Check**: `http://localhost:80/`

### 🔧 Troubleshooting

#### Common Issues

1. **Container won't start:**
   ```bash
   docker-compose logs jiosaavn-bot
   ```

2. **Database connection failed:**
   - Check `DATABASE_URL` format
   - Ensure MongoDB is accessible
   - Verify credentials

3. **Port already in use:**
   ```bash
   # Change port in .env
   PORT=8080
   ```

4. **Permission denied:**
   ```bash
   sudo docker-compose up -d
   ```

#### Debug Mode

Run with debug logs:
```bash
docker-compose up jiosaavn-bot  # Without -d flag
```

#### Reset Everything

```bash
docker-compose down -v
docker system prune -f
```

### 🔒 Security Considerations

#### Production Security

1. **Use non-root user** (already configured in Dockerfile)
2. **Set resource limits:**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

3. **Use secrets management:**
   ```yaml
   environment:
     - BOT_TOKEN_FILE=/run/secrets/bot_token
   secrets:
     - bot_token
   ```

4. **Enable firewall:**
   ```bash
   ufw allow 80
   ufw enable
   ```

#### Network Security

- Use reverse proxy (nginx/traefik)
- Enable HTTPS with SSL certificates
- Restrict database access

### 📈 Performance Optimization

#### Resource Limits

Add to `docker-compose.yml`:
```yaml
services:
  jiosaavn-bot:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 256M
```

#### Volume Optimization

```yaml
volumes:
  - ./logs:/app/logs:rw
  - /tmp:/app/downloads:rw  # Use tmpfs for downloads
```

### 🎯 Production Deployment

#### Render.com

1. Connect GitHub repository
2. Set environment variables in dashboard
3. Deploy automatically on push

#### Railway

1. Connect repository
2. Configure environment variables
3. Deploy with one click

#### DigitalOcean App Platform

1. Create new app from GitHub
2. Configure build settings
3. Set environment variables

#### VPS Deployment

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and deploy
git clone https://github.com/Itz-Ashlynn/jiosavanbot.git
cd jiosavanbot
./deploy.sh
```

### 📝 Maintenance

#### Regular Updates

```bash
# Update codebase
git pull

# Rebuild and restart
docker-compose up -d --build jiosaavn-bot
```

#### Backup Database

```bash
# For MongoDB
mongodump --uri="$DATABASE_URL" --out=backup/
```

#### Log Rotation

Add to docker-compose.yml:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 🆘 Support

If you encounter issues:

1. Check logs: `docker-compose logs jiosaavn-bot`
2. Verify environment variables
3. Test database connectivity
4. Join: [@Ashlynn_Repository](https://t.me/Ashlynn_Repository)

---

*Created by [Ashlynn](https://t.me/Ashlynn_Repository) - [GitHub Repository](https://github.com/Itz-Ashlynn/jiosavanbot)*
