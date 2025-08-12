# JioSaavn Bot - Admin Guide

## Environment Setup

Add the following environment variable to enable admin features:

```env
OWNER_ID=your_telegram_user_id
```

**How to get your Telegram User ID:**
1. Start a chat with @userinfobot
2. Send any message
3. Copy the ID number provided

## Admin Commands

### 📊 Statistics (`/stats`)
Get detailed bot analytics including:
- Total users and active users
- New users today
- Quality preferences distribution
- User type preferences
- Interactive refresh functionality

### 📢 Broadcasting (`/broadcast`)
Send messages to all users:
1. Send or forward any message to the bot
2. Reply to that message with `/broadcast`
3. The broadcast starts immediately (no confirmation needed)
4. Real-time progress updates every 50 successful sends
5. Final statistics report with delivery success/failure rates

### 🔔 New User Notifications
Automatic notifications when new users join:
- Detailed user information (name, username, ID, language)
- User profile photo (if available)
- Current bot statistics 
- Quick access buttons for admin actions
- Real-time user count updates

**Supported message types:**
- Text messages (with formatting)
- Photos with captions
- Videos with captions
- Documents with captions
- Audio files with captions
- Voice messages
- Stickers
- Animations/GIFs

## Web Interface

Access the admin dashboard through your bot's web interface:
- **Home Page**: Professional dark-themed dashboard
- **Live Statistics**: Real-time user analytics
- **API Endpoint**: `/api/stats` for raw JSON data

## Error Handling

The bot includes robust error handling:
- **Non-owner users**: Clear access denied messages with user information
- **Missing OWNER_ID**: Helpful setup instructions
- **Download failures**: Automatic retry with exponential backoff
- **Broadcast errors**: Detailed tracking of blocked/deleted users

## Security Features

- Owner-only command access with ID verification
- Comprehensive logging of unauthorized access attempts
- Secure file serving with path traversal protection
- Rate limiting and flood protection during broadcasts

## Technical Improvements

### API Enhancements
- Proper User-Agent headers for JioSaavn compatibility
- Retry logic for failed downloads
- Better error messages and handling
- Support for HTML responses (web interface health checks)

### Performance Optimizations
- Optimized broadcast delays to prevent flooding
- Efficient database queries for statistics
- Progress updates to keep users informed
- Proper session management for downloads

## Troubleshooting

### Common Issues

1. **403 Forbidden errors**: Fixed with proper User-Agent headers
2. **CSS/JS 404 errors**: Fixed with improved static file routing
3. **JSON decode errors**: Fixed with content type detection
4. **Broadcast message not found**: Fixed by removing confirmation step

### Monitoring

- Check logs for unauthorized access attempts
- Monitor broadcast success rates
- Track user growth through statistics
- Use web interface for real-time monitoring

## Best Practices

1. **Broadcasting**: Use sparingly to avoid spam reports
2. **Monitoring**: Check statistics regularly for insights
3. **Security**: Keep OWNER_ID private and secure
4. **Performance**: Monitor server resources during large broadcasts

---

*Created by [Ashlynn](https://t.me/Ashlynn_Repository) - [GitHub Repository](https://github.com/Itz-Ashlynn/jiosavanbot)*
