import logging
import datetime

from jiosaavn.bot import Bot
from jiosaavn.config.settings import OWNER_ID

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

@Bot.on_callback_query(filters.regex('^home$'))
@Bot.on_message(filters.command('start') & filters.private & filters.incoming)
async def start_handler(client: Bot, message: Message | CallbackQuery):
    # Check if it's a new user (only for Message, not CallbackQuery)
    is_new_user = False
    if isinstance(message, Message):
        is_new_user = not await client.db.is_user_exist(message.from_user.id)
        
        # Add user to database if new
        if is_new_user:
            await client.db.add_user(message.from_user.id)
            
            # Send notification to owner about new user
            if OWNER_ID and OWNER_ID != 0:
                try:
                    await send_new_user_notification(client, message.from_user)
                except Exception as e:
                    logger.error(f"Failed to send new user notification: {e}")
    
    ##### Mention user
    last_name = f' {message.from_user.last_name}' if message.from_user.last_name else ''
    mention = f"[{message.from_user.first_name}{last_name}](tg://user?id={message.from_user.id})"
    text = (
        f"**Hello {mention},**\n\n"
        "<blockquote>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴊɪᴏsᴀᴀᴠɴ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ! ᴛʜɪs ᴘᴏᴡᴇʀғᴜʟ ʙᴏᴛ ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ sᴇᴀʀᴄʜ ᴀɴᴅ ᴅᴏᴡɴʟᴏᴀᴅ sᴏɴɢs, ᴘʟᴀʏʟɪsᴛs, ᴀʟʙᴜᴍs, ᴀɴᴅ ᴀʀᴛɪsᴛs ᴅɪʀᴇᴄᴛʟʏ ғʀᴏᴍ ᴊɪᴏsᴀᴀᴠɴ.</blockquote>\n\n"
        "**With this Bot, you can:**\n\n"
        "__- Search for songs, albums, playlists, and artists__\n"
        "__- Download your favorite tracks directly to Telegram__\n"
        "__- Explore various features tailored to enhance your music experience__\n\n"
        "**Maintained By:** [Ashlynn](https://t.me/Ashlynn_Repository)"
    )

    buttons = [[
        InlineKeyboardButton('Owner 🧑', url='https://t.me/Ashlynn_Repository'),
        InlineKeyboardButton('About 📕', callback_data='about')
    ], [
        InlineKeyboardButton('Help 💡', callback_data='help'),
        InlineKeyboardButton('Settings ⚙', callback_data='settings')
        ],[
        InlineKeyboardButton('Open Source Repository 🌐', url='https://github.com/Itz-Ashlynn/jiosavanbot')
    ]]
    
    if isinstance(message, Message):
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), quote=True, disable_web_page_preview=True)
    else:
        await message.message.edit(text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)

@Bot.on_callback_query(filters.regex('^help$'))
@Bot.on_message(filters.command('help') & filters.private & filters.incoming)
async def help_handler(client: Bot, message: Message | CallbackQuery):
    text = (
        "**It's very simple to use me! 😉**\n\n"
        "1. Start by configuring your preferences using the `/settings` command.\n"
        "2. Send me the name of a song, playlist, album, or artist you want to search for.\n"
        "3. I'll handle the rest and provide you with the results!\n\n"
        "Feel free to explore and enjoy the music!"
    )

    buttons = [[
        InlineKeyboardButton('About 📕', callback_data='about'),
        InlineKeyboardButton('Settings ⚙', callback_data='settings')
        ],[
        InlineKeyboardButton('Home 🏕', callback_data='home'),
        InlineKeyboardButton('Close ❌', callback_data='close')
    ]]

    if isinstance(message, Message):
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), quote=True)
    else:
        await message.message.edit(text, reply_markup=InlineKeyboardMarkup(buttons))

@Bot.on_callback_query(filters.regex('^about$'))
@Bot.on_message(filters.command('about') & filters.private & filters.incoming)
async def about(client: Bot, message: Message|CallbackQuery):
    me = await client.get_me()

    text = (
        f"**🤖 Bot Name:** {me.mention()}\n\n"
        "**📝 Language:** [Python 3](https://www.python.org/)\n\n"
        "**🧰 Framework:** [Pyrogram](https://github.com/pyrogram/pyrogram)\n\n"
        "**👨‍💻 Developer:** [Ashlynn](https://t.me/Ashlynn_Repository)\n\n"
        "**📢 Updates Channel:** [Ashlynn Repository](https://t.me/Ashlynn_Repository)\n\n"
        "**🔗 Source Code:** [GitHub Repository](https://github.com/Itz-Ashlynn/jiosavanbot)\n\n"
    )

    buttons = [[
        InlineKeyboardButton('Help 💡', callback_data='help'),
        InlineKeyboardButton('Settings ⚙', callback_data='settings')
        ],[
        InlineKeyboardButton('Home 🏕', callback_data='home'),
        InlineKeyboardButton('Close ❌', callback_data='close')
    ]]
    if isinstance(message, Message):
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True, quote=True)
    else:
        await message.message.edit(text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)

@Bot.on_callback_query(filters.regex('^close$'))
async def close_cb(client: Bot, callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.reply_to_message.delete()

async def send_new_user_notification(client: Bot, user):
    """Send notification to owner when a new user starts the bot."""
    try:
        # Get current total users
        total_users = await client.db.get_total_users()
        
        # Prepare user information
        user_name = user.first_name
        if user.last_name:
            user_name += f" {user.last_name}"
        
        username = f"@{user.username}" if user.username else "No username"
        user_link = f"tg://user?id={user.id}"
        
        # Get user's profile photos
        try:
            photos = await client.get_chat_photos(user.id, limit=1)
            profile_photo = photos[0].file_id if photos else None
        except:
            profile_photo = None
        
        # Create notification text
        notification_text = f"""
🎉 **New User Joined!**

👤 **User Info:**
├ **Name:** [{user_name}]({user_link})
├ **Username:** {username}
├ **User ID:** `{user.id}`
└ **Language:** {user.language_code or 'Unknown'}

📊 **Bot Statistics:**
├ **Total Users:** `{total_users:,}`
├ **Join Date:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC`
└ **User Type:** {'Premium' if user.is_premium else 'Regular'}

🌟 Welcome to the JioSaavn Bot family!
        """
        
        # Create inline buttons
        buttons = [
            [
                InlineKeyboardButton("👤 View Profile", url=user_link),
                InlineKeyboardButton("📊 Bot Stats", callback_data="refresh_stats")
            ],
            [
                InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast_help")
            ]
        ]
        
        # Send notification with or without photo
        if profile_photo:
            await client.send_photo(
                chat_id=OWNER_ID,
                photo=profile_photo,
                caption=notification_text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await client.send_message(
                chat_id=OWNER_ID,
                text=notification_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )
            
        logger.info(f"New user notification sent for user {user.id} ({user_name})")
        
    except Exception as e:
        logger.error(f"Error sending new user notification: {e}")
        # Fallback: send simple text notification
        try:
            simple_text = f"🎉 New user joined!\n\nName: {user_name}\nID: {user.id}\nTotal users: {total_users:,}"
            await client.send_message(OWNER_ID, simple_text)
        except Exception as e2:
            logger.error(f"Failed to send fallback notification: {e2}")
