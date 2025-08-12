# JioSaavn Telegram Bot

A powerful Python Telegram bot leveraging the Pyrofork library to search and upload songs, albums, playlists, and artists from JioSaavn. This bot utilizes hidden APIs from JioSaavn to provide a seamless music experience on Telegram with advanced admin features and a beautiful web interface.

[![GitHub](https://badgen.net/badge/Open%20Source%20%3F/Yes/yellow?icon=github)](https://github.com/Itz-Ashlynn/jiosavanbot)
[![Creator](https://badgen.net/badge/Creator/Ashlynn/purple)](https://t.me/Ashlynn_Repository)


## Features

### Core Features
- **Search** for songs, albums, playlists, and artists on JioSaavn
- **Upload** songs directly to Telegram in multiple quality options (48kbps, 96kbps, 160kbps, 320kbps)
- **Download** entire playlists and albums with batch processing
- **Smart search** with advanced filtering and result management
- **User preferences** for quality settings and download types

### Admin Features ⚡
- **Broadcasting** system to send messages to all users
- **Real-time statistics** with detailed user analytics
- **User management** with ban/unban functionality
- **Quality distribution** tracking and analysis
- **Admin-only commands** for bot management

### Web Interface 🌐
- **Professional dashboard** with dark theme and smooth animations
- **Real-time statistics** display with live updates
- **Responsive design** that works on all devices
- **Interactive charts** showing user preferences and activity
- **Modern UI/UX** with beautiful transitions and effects

## Usage

1. **Start the Bot**: Send the `/start` command.
2. **Search**: Send a query to search for a song, album, playlist, or artist.
3. **Select**: Choose the desired result from the search list.
4. **Upload**: Select the upload option to upload the song to Telegram.

## Commands

### User Commands
- `/start` - Initialize the bot and check its status
- `/settings` - Configure and manage bot settings
- `/help` - Get information on how to use the bot
- `/about` - Learn more about the bot and its features

### Admin Commands (Owner Only)
- `/broadcast` - Send a message to all users (reply to a message with this command)
- `/stats` - Get detailed bot statistics with real-time data

### Web Interface
- Access the web dashboard at your bot's hosting URL
- View real-time statistics at `/api/stats`
- Beautiful responsive interface in the `/statis/` folder

## Installation

### 🐳 Docker Deployment (Recommended)

1. **Quick Start with Docker:**
   ```sh
   git clone https://github.com/Itz-Ashlynn/jiosavanbot.git
   cd jiosavanbot
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Manual Docker Setup:**
   ```sh
   # Copy environment template
   cp .env.example .env
   # Edit .env with your values
   
   # Deploy
   docker-compose up -d --build
   ```

### 📦 Manual Installation

1. **Clone the Repository**: 
   ```sh
   git clone https://github.com/Itz-Ashlynn/jiosavanbot.git
   cd jiosavanbot
   ```
2. **Install Dependencies**:
   ```sh
   pip3 install -r requirements.txt
   ```
3. **Configure Environment**:
   ```sh
   export API_ID=your_api_id
   export API_HASH=your_api_hash
   export BOT_TOKEN=your_bot_token
   export OWNER_ID=your_telegram_user_id
   export DATABASE_URL=your_mongodb_url
   ```
4. **Run the Bot**:
   ```sh
   python3 -m jiosaavn
   ```

## Running Methods

### 🐳 Docker (Recommended)
- **Production**: `docker-compose up -d --build`
- **Development**: `docker-compose --profile local up -d --build`
- **Automated**: `./deploy.sh` (interactive script)

### ☁️ Cloud Deployment

1. **Deploy to Render**:
   - Connect your GitHub fork
   - Set environment variables in dashboard
   - Deploy automatically

2. **Deploy to Railway**:
   - Connect repository
   - Configure environment variables
   - One-click deployment

3. **Deploy to Koyeb**:
   [![](https://img.shields.io/badge/Deploy_to_Koyeb-blue)](https://app.koyeb.com/deploy?type=git&builder=buildpack&repository=https://github.com/Itz-Ashlynn/jiosavanbot&branch=main&name=jiosaavn-bot&run_command=python3%20-m%20jiosaavn&env[DATABASE_URL]=your_database_url&env[BOT_TOKEN]=your_bot_token&env[API_HASH]=your_api_hash&env[API_ID]=your_api_id&env[OWNER_ID]=your_telegram_user_id)

### 💻 Local Development
- Follow manual installation steps above
- Ensure you have Python 3.11+ and pip installed

## Dependencies

- [Pyrofork](https://pyrofork.mayuri.my.id/main/)
- Custom JioSaavn API

## How to Deploy

1. Click the **Deploy to Koyeb** button below.
2. On the Koyeb UI, you'll be asked to fill in the environment variables.

   The required environment variables are:
   - `DATABASE_URL`: Your MongoDB database connection URL
   - `BOT_TOKEN`: Your bot token from @BotFather
   - `API_HASH`: Your API hash from my.telegram.org
   - `API_ID`: Your API ID from my.telegram.org
   - `OWNER_ID`: Your Telegram user ID (for admin features)

3. Once the environment variables are set, click **Deploy** to deploy the application.

## 🐳 Docker Quick Start

For the fastest setup, use Docker:

```bash
# Clone repository
git clone https://github.com/Itz-Ashlynn/jiosavanbot.git
cd jiosavanbot

# Run deployment script
chmod +x deploy.sh
./deploy.sh
```

The script will guide you through:
- Environment configuration
- Deployment mode selection
- Service management
- Monitoring and logs

📖 **Detailed Docker Guide**: See [DOCKER.md](DOCKER.md) for comprehensive deployment instructions.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.


## Screenshots

### Web Interface Dashboard
Visit your deployed bot URL to see the beautiful dark-themed dashboard with:
- Real-time statistics and analytics
- Interactive charts and graphs
- Responsive design for all devices
- Smooth animations and modern UI

### Admin Features
- Use `/broadcast` command to send messages to all users
- Use `/stats` command to get detailed analytics
- View quality distribution and user preferences

## Credits & Acknowledgments

- **Modified by**: [Ashlynn](https://t.me/Ashlynn_Repository)
- **Channel**: [Ashlynn Repository](https://t.me/Ashlynn_Repository)
- **Original Repository**: [Ns-AnoNymouS/jiosaavn](https://github.com/Ns-AnoNymouS/jiosaavn) - Special thanks to Ns-AnoNymouS for the amazing original repository! 🙏
- **This Version**: Enhanced with admin features, broadcasting, statistics, professional web interface, and Docker deployment
- **JioSaavn API**: Hidden APIs for music streaming and downloads

### 🙏 Special Thanks

This project is a modified version of the original [JioSaavn Bot](https://github.com/Ns-AnoNymouS/jiosaavn) created by [Ns-AnoNymouS](https://github.com/Ns-AnoNymouS). The original repository provided an excellent foundation for music downloading functionality. 

**Enhancements in this version:**
- 🔐 Admin features (broadcasting, statistics)
- 🌐 Professional web interface with dark theme
- 📊 Real-time analytics dashboard
- 🐳 Docker deployment setup
- 🛡️ Enhanced security and error handling
- 📱 Mobile-responsive design
- 🚀 Production-ready configuration

## Support

If you encounter any issues or need help:
1. Join our Telegram channel: [@Ashlynn_Repository](https://t.me/Ashlynn_Repository)
2. Check the [Issues](https://github.com/Itz-Ashlynn/jiosavanbot/issues) section
3. Read the documentation in this README

## Disclaimer

This bot is for educational purposes only. Please respect the terms of service of JioSaavn and applicable copyright laws in your jurisdiction.
