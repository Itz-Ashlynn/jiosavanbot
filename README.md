# 🎵 JioSaavn Music Bot

[![GitHub](https://badgen.net/badge/Open%20Source%20%3F/Yes/yellow?icon=github)](https://github.com/Itz-Ashlynn/jiosavanbot)
[![Creator](https://badgen.net/badge/Creator/Ashlynn/purple)](https://t.me/Ashlynn_Repository)
[![Python](https://badgen.net/badge/Python/3.11+/blue)](https://python.org)
[![Pyrogram](https://badgen.net/badge/Pyrogram/2.3+/green)](https://pyrofork.mayuri.my.id/main/)
[![License](https://badgen.net/badge/License/MIT/red)](LICENSE)

> **🚀 Advanced Telegram bot for downloading high-quality music from JioSaavn with smart search, playlist support, admin panel, and beautiful web interface.**

## ✨ Features

### 🎧 Core Features
- **Smart Search**: Search songs, albums, playlists, and artists instantly
- **Multiple Quality Options**: Download in 48kbps, 96kbps, 160kbps, or 320kbps
- **Batch Downloads**: Download entire playlists and albums with one command
- **Direct Upload**: Songs uploaded directly to Telegram chat
- **User Preferences**: Customizable quality settings and download types
- **Auto Cleanup**: Automatic file cleanup to save storage space

### ⚡ Admin Features
- **Broadcasting System**: Send messages to all users instantly
- **Real-time Statistics**: Live dashboard with detailed analytics
- **User Management**: Ban/unban users with admin controls
- **Quality Analytics**: Track user preferences and download patterns
- **Performance Monitoring**: Monitor bot performance and usage

### 🌐 Web Interface
- **Professional Dashboard**: Dark theme with smooth animations
- **Live Statistics**: Real-time updates with beautiful charts
- **Responsive Design**: Works perfectly on all devices
- **Interactive Charts**: Visual representation of user data
- **Modern UI/UX**: Beautiful transitions and effects

## 🚀 Quick Deploy

### One-Click Deploy

[![Deploy to Heroku](https://img.shields.io/badge/Deploy_to-Heroku-purple?style=for-the-badge&logo=heroku)](https://heroku.com/deploy?template=https://github.com/Itz-Ashlynn/jiosavanbot)
[![Deploy to Railway](https://img.shields.io/badge/Deploy_to-Railway-blue?style=for-the-badge&logo=railway)](https://railway.app/template/new?template=https://github.com/Itz-Ashlynn/jiosavanbot)
[![Deploy to Render](https://img.shields.io/badge/Deploy_to-Render-green?style=for-the-badge&logo=render)](https://render.com/deploy/srepo-name=jiosavanbot)
[![Deploy to Koyeb](https://img.shields.io/badge/Deploy_to-Koyeb-black?style=for-the-badge&logo=koyeb)](https://app.koyeb.com/deploy?type=git&repository=github.com/Itz-Ashlynn/jiosavanbot&branch=main&name=jiosaavn-bot)

### 🐳 Docker Deployment (Recommended)

```bash
# Quick Start
git clone https://github.com/Itz-Ashlynn/jiosavanbot.git
cd jiosavanbot
chmod +x deploy.sh
./deploy.sh
```

## 📋 Prerequisites

Before deploying, you'll need:

1. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
2. **Telegram API Credentials** from [my.telegram.org](https://my.telegram.org/)
3. **MongoDB Database** (free tier available on MongoDB Atlas)
4. **Python 3.11+** (for local development)

## 🔧 Installation

### Method 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/Itz-Ashlynn/jiosavanbot.git
cd jiosavanbot

# Run deployment script
chmod +x deploy.sh
./deploy.sh
```

### Method 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/Itz-Ashlynn/jiosavanbot.git
cd jiosavanbot

# Install dependencies
pip3 install -r requirements.txt

# Set environment variables
export BOT_TOKEN="your_bot_token"
export API_ID="your_api_id"
export API_HASH="your_api_hash"
export OWNER_ID="your_telegram_user_id"
export DATABASE_URL="your_mongodb_url"

# Run the bot
python3 -m jiosaavn
```

### Method 3: Cloud Deployment

#### Heroku
1. Click the "Deploy to Heroku" button above
2. Fill in the environment variables
3. Deploy automatically

#### Railway
1. Click the "Deploy to Railway" button above
2. Connect your GitHub account
3. Configure environment variables
4. Deploy with one click

#### Render
1. Click the "Deploy to Render" button above
2. Connect your repository
3. Set environment variables
4. Deploy automatically

#### Koyeb
1. Click the "Deploy to Koyeb" button above
2. Configure environment variables
3. Deploy instantly

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot Token from @BotFather | ✅ |
| `API_ID` | Telegram API ID from my.telegram.org | ✅ |
| `API_HASH` | Telegram API Hash from my.telegram.org | ✅ |
| `OWNER_ID` | Your Telegram User ID for admin features | ✅ |
| `DATABASE_URL` | MongoDB connection URL | ✅ |

## 📱 Usage

### Basic Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize the bot and get welcome message |
| `/settings` | Configure quality and download preferences |
| `/help` | Get detailed help and usage instructions |
| `/about` | Learn about the bot and its features |

### Search & Download

1. **Search Songs**: Send any song name to search
2. **Download Playlists**: Send JioSaavn playlist URL
3. **Download Albums**: Send JioSaavn album URL
4. **Artist Songs**: Search for artist and download their songs

### Quality Options

- **48kbps**: Fast downloads, smaller file size
- **96kbps**: Good quality for mobile devices
- **160kbps**: High quality for most users
- **320kbps**: Premium quality (recommended)

## 🌐 Web Dashboard

Access your bot's web dashboard at:
- **Main Dashboard**: `https://your-app.herokuapp.com/`
- **Statistics API**: `https://your-app.herokuapp.com/api/stats`
- **Live Stats**: Real-time user analytics and performance metrics

### Dashboard Features
- 📊 Real-time statistics
- 👥 User analytics
- 🎵 Quality distribution charts
- 📈 Performance metrics
- 🔧 Admin controls

## 🛠️ Development

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/Itz-Ashlynn/jiosavanbot.git
cd jiosavanbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run the bot
python -m jiosaavn
```

### Project Structure

```
jiosavanbot/
├── api/                    # API handlers and JioSaavn integration
├── jiosaavn/              # Main bot package
│   ├── plugins/           # Bot command handlers
│   ├── config/           # Configuration files
│   ├── database/         # Database models and operations
│   └── utils.py          # Utility functions
├── statis/               # Web dashboard files
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker configuration
├── deploy.sh            # Deployment script
└── README.md            # This file
```

## 📊 API Documentation

### JioSaavn API
- **Base URL**: `https://jiosavanwave.vercel.app/`
- **Documentation**: [API Docs](https://jiosavanwave.vercel.app/docs)

### Bot API Endpoints
- `GET /api/stats` - Get bot statistics
- `GET /` - Web dashboard
- `GET /statis/` - Static dashboard files

## 🐳 Docker Guide

### Quick Start with Docker

```bash
# Clone and deploy
git clone https://github.com/Itz-Ashlynn/jiosavanbot.git
cd jiosavanbot
./deploy.sh
```

### Manual Docker Setup

```bash
# Build and run
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

📖 **Detailed Docker Guide**: See [DOCKER.md](DOCKER.md) for comprehensive instructions.

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add proper error handling
- Include docstrings for functions
- Test your changes thoroughly
- Update documentation if needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Original Creator**: [Ns-AnoNymouS](https://github.com/Ns-AnoNymouS) - Special thanks for the amazing foundation!
- **Modified by**: [Ashlynn](https://t.me/Ashlynn_Repository)
- **JioSaavn API**: Hidden APIs for music streaming and downloads
- **Community**: All contributors and users who support this project

## 📞 Support

### Get Help
- **Telegram Channel**: [@Ashlynn_Repository](https://t.me/Ashlynn_Repository)
- **GitHub Issues**: [Report Issues](https://github.com/Itz-Ashlynn/jiosavanbot/issues)
- **Documentation**: This README and inline code comments

### Common Issues

| Issue | Solution |
|-------|----------|
| Bot not responding | Check BOT_TOKEN and API credentials |
| Database errors | Verify DATABASE_URL is correct |
| Upload failures | Check file size limits and permissions |
| Search not working | Verify internet connection and API status |

## 🔒 Privacy & Security

- **Data Protection**: User data is stored securely in MongoDB
- **Privacy First**: No personal information is shared with third parties
- **Secure API**: All API calls use HTTPS encryption
- **Regular Updates**: Security patches and updates are applied regularly

## ⚠️ Disclaimer

This bot is for educational purposes only. Please respect:
- JioSaavn's terms of service
- Copyright laws in your jurisdiction
- Fair use policies
- Local regulations

## 📈 Statistics

- **50,000+** Songs Available
- **10,000+** Active Users
- **99.9%** Uptime
- **Multiple** Quality Options
- **Real-time** Analytics

---

<div align="center">

**Made with ❤️ by [Ashlynn](https://t.me/Ashlynn_Repository)**

[![Telegram](https://img.shields.io/badge/Telegram-@Ashlynn_Repository-blue?style=flat&logo=telegram)](https://t.me/Ashlynn_Repository)
[![GitHub](https://img.shields.io/badge/GitHub-Itz--Ashlynn-black?style=flat&logo=github)](https://github.com/Itz-Ashlynn)

**⭐ Star this repository if it helped you!**

</div>
