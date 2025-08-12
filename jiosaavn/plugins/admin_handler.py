import asyncio
import datetime
import logging

from jiosaavn.bot import Bot
from jiosaavn.config.settings import OWNER_ID

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

logger = logging.getLogger(__name__)

def is_owner(func):
    """Decorator to check if the user is the owner."""
    async def wrapper(client: Bot, message: Message):
        if OWNER_ID == 0:
            await message.reply_text(
                "⚠️ **Owner ID Not Set**\n\n"
                "The bot owner has not configured the `OWNER_ID` environment variable. "
                "Please contact the bot administrator to set up admin access."
            )
            return
        
        if message.from_user.id != OWNER_ID:
            user_info = f"{message.from_user.first_name}"
            if message.from_user.username:
                user_info += f" (@{message.from_user.username})"
            
            await message.reply_text(
                f"⚠️ **Access Denied**\n\n"
                f"Hi {user_info}, this command is restricted to the bot owner only.\n\n"
                f"**Your ID:** `{message.from_user.id}`\n"
                f"**Required ID:** `{OWNER_ID}`\n\n"
                f"If you believe this is an error, please contact the bot administrator."
            )
            logger.warning(f"Unauthorized access attempt by user {message.from_user.id} ({user_info}) for command: {message.text}")
            return
        return await func(client, message)
    return wrapper

@Bot.on_message(filters.command('stats') & filters.private & filters.incoming)
@is_owner
async def stats_handler(client: Bot, message: Message):
    """Handle the stats command."""
    try:
        # Get statistics from database
        total_users = await client.db.get_total_users()
        banned_users = await client.db.get_banned_users_count()
        active_users = total_users - banned_users
        
        # Get users by quality
        quality_320 = await client.db.get_users_by_quality('320kbps')
        quality_160 = await client.db.get_users_by_quality('160kbps')
        quality_96 = await client.db.get_users_by_quality('96kbps')
        quality_48 = await client.db.get_users_by_quality('48kbps')
        
        # Get users by type
        type_all = await client.db.get_users_by_type('all')
        type_song = await client.db.get_users_by_type('song')
        
        # Get today's new users
        today = datetime.date.today().isoformat()
        today_users = await client.db.get_users_by_date(today)
        
        # Create stats message
        stats_text = f"""
📊 **Bot Statistics**

👥 **User Statistics:**
├ Total Users: `{total_users:,}`
├ Active Users: `{active_users:,}`
├ Banned Users: `{banned_users:,}`
└ New Users Today: `{today_users:,}`

🎵 **Quality Preferences:**
├ 320kbps: `{quality_320:,}` users
├ 160kbps: `{quality_160:,}` users
├ 96kbps: `{quality_96:,}` users
└ 48kbps: `{quality_48:,}` users

📁 **Type Preferences:**
├ All (Songs + Albums): `{type_all:,}` users
└ Songs Only: `{type_song:,}` users

📅 **Date:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC`
        """
        
        buttons = [[
            InlineKeyboardButton('🔄 Refresh', callback_data='refresh_stats'),
            InlineKeyboardButton('❌ Close', callback_data='close_stats')
        ]]
        
        await message.reply_text(
            stats_text, 
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.reply_text(f"❌ Error getting statistics: {str(e)}")

@Bot.on_callback_query(filters.regex('^refresh_stats$'))
async def refresh_stats_callback(client: Bot, callback):
    """Handle refresh stats callback."""
    if callback.from_user.id != OWNER_ID:
        await callback.answer("⚠️ Only owner can use this.", show_alert=True)
        return
    
    try:
        # Get fresh statistics
        total_users = await client.db.get_total_users()
        banned_users = await client.db.get_banned_users_count()
        active_users = total_users - banned_users
        
        quality_320 = await client.db.get_users_by_quality('320kbps')
        quality_160 = await client.db.get_users_by_quality('160kbps')
        quality_96 = await client.db.get_users_by_quality('96kbps')
        quality_48 = await client.db.get_users_by_quality('48kbps')
        
        type_all = await client.db.get_users_by_type('all')
        type_song = await client.db.get_users_by_type('song')
        
        today = datetime.date.today().isoformat()
        today_users = await client.db.get_users_by_date(today)
        
        stats_text = f"""
📊 **Bot Statistics**

👥 **User Statistics:**
├ Total Users: `{total_users:,}`
├ Active Users: `{active_users:,}`
├ Banned Users: `{banned_users:,}`
└ New Users Today: `{today_users:,}`

🎵 **Quality Preferences:**
├ 320kbps: `{quality_320:,}` users
├ 160kbps: `{quality_160:,}` users
├ 96kbps: `{quality_96:,}` users
└ 48kbps: `{quality_48:,}` users

📁 **Type Preferences:**
├ All (Songs + Albums): `{type_all:,}` users
└ Songs Only: `{type_song:,}` users

📅 **Date:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC`
        """
        
        buttons = [[
            InlineKeyboardButton('🔄 Refresh', callback_data='refresh_stats'),
            InlineKeyboardButton('❌ Close', callback_data='close_stats')
        ]]
        
        await callback.message.edit_text(
            stats_text, 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await callback.answer("✅ Statistics refreshed!")
        
    except Exception as e:
        logger.error(f"Error refreshing stats: {e}")
        await callback.answer(f"❌ Error: {str(e)}", show_alert=True)

@Bot.on_callback_query(filters.regex('^close_stats$'))
async def close_stats_callback(client: Bot, callback):
    """Handle close stats callback."""
    if callback.from_user.id != OWNER_ID:
        await callback.answer("⚠️ Only owner can use this.", show_alert=True)
        return
    
    await callback.message.delete()
    await callback.answer()

@Bot.on_message(filters.command('broadcast') & filters.private & filters.incoming)
@is_owner
async def broadcast_handler(client: Bot, message: Message):
    """Handle the broadcast command."""
    if not message.reply_to_message:
        await message.reply_text(
            "📢 **Broadcast Usage:**\n\n"
            "Reply to a message with `/broadcast` to send it to all users.\n\n"
            "**Supported message types:**\n"
            "• Text messages\n"
            "• Photos\n"
            "• Videos\n"
            "• Documents\n"
            "• Audio files\n"
            "• Voice messages\n"
            "• Stickers\n"
            "• Animations/GIFs"
        )
        return
    
    # Get the message to broadcast
    broadcast_message = message.reply_to_message
    
    # Start broadcasting immediately without confirmation
    total_users = await client.db.get_total_users()
    status_msg = await message.reply_text(
        f"📢 **Broadcasting...**\n\n"
        f"Starting broadcast to **{total_users:,}** users...\n"
        f"**Message Preview:** {broadcast_message.text[:50] if broadcast_message.text else '[Media Message]'}{'...' if broadcast_message.text and len(broadcast_message.text) > 50 else ''}",
        quote=True
    )
    
    # Initialize counters
    success_count = 0
    failed_count = 0
    blocked_count = 0
    deleted_count = 0
    
    start_time = datetime.datetime.now()
    
    try:
        # Get all users and broadcast
        async for user in client.db.get_all_users():
            try:
                user_id = user['id']
                
                # Send the message based on type
                if broadcast_message.text:
                    await client.send_message(
                        chat_id=user_id,
                        text=broadcast_message.text,
                        entities=broadcast_message.entities,
                        disable_web_page_preview=True
                    )
                elif broadcast_message.photo:
                    await client.send_photo(
                        chat_id=user_id,
                        photo=broadcast_message.photo.file_id,
                        caption=broadcast_message.caption,
                        caption_entities=broadcast_message.caption_entities
                    )
                elif broadcast_message.video:
                    await client.send_video(
                        chat_id=user_id,
                        video=broadcast_message.video.file_id,
                        caption=broadcast_message.caption,
                        caption_entities=broadcast_message.caption_entities
                    )
                elif broadcast_message.document:
                    await client.send_document(
                        chat_id=user_id,
                        document=broadcast_message.document.file_id,
                        caption=broadcast_message.caption,
                        caption_entities=broadcast_message.caption_entities
                    )
                elif broadcast_message.audio:
                    await client.send_audio(
                        chat_id=user_id,
                        audio=broadcast_message.audio.file_id,
                        caption=broadcast_message.caption,
                        caption_entities=broadcast_message.caption_entities
                    )
                elif broadcast_message.voice:
                    await client.send_voice(
                        chat_id=user_id,
                        voice=broadcast_message.voice.file_id,
                        caption=broadcast_message.caption,
                        caption_entities=broadcast_message.caption_entities
                    )
                elif broadcast_message.sticker:
                    await client.send_sticker(
                        chat_id=user_id,
                        sticker=broadcast_message.sticker.file_id
                    )
                elif broadcast_message.animation:
                    await client.send_animation(
                        chat_id=user_id,
                        animation=broadcast_message.animation.file_id,
                        caption=broadcast_message.caption,
                        caption_entities=broadcast_message.caption_entities
                    )
                
                success_count += 1
                
                # Update progress every 50 successful sends
                if success_count % 50 == 0:
                    await status_msg.edit_text(
                        f"📢 **Broadcasting...**\n\n"
                        f"✅ Sent: {success_count:,}\n"
                        f"❌ Failed: {failed_count:,}\n"
                        f"🚫 Blocked: {blocked_count:,}\n"
                        f"👻 Deleted: {deleted_count:,}"
                    )
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
                failed_count += 1
            except UserIsBlocked:
                blocked_count += 1
            except InputUserDeactivated:
                deleted_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"Error broadcasting to user {user.get('id', 'unknown')}: {e}")
            
            # Small delay to avoid flooding
            await asyncio.sleep(0.03)
    
    except Exception as e:
        logger.error(f"Error during broadcast: {e}")
        await status_msg.edit_text(f"❌ **Broadcast Failed**\n\nError: {str(e)}")
        return
    
    # Calculate broadcast duration
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    
    # Final broadcast report
    total_sent = success_count + failed_count + blocked_count + deleted_count
    final_text = f"""
📢 **Broadcast Completed!**

📊 **Final Statistics:**
├ Total Users: `{total_sent:,}`
├ ✅ Successfully Sent: `{success_count:,}`
├ ❌ Failed: `{failed_count:,}`
├ 🚫 Blocked Bot: `{blocked_count:,}`
└ 👻 Deleted Account: `{deleted_count:,}`

⏱️ **Duration:** `{str(duration).split('.')[0]}`
📅 **Completed:** `{end_time.strftime('%Y-%m-%d %H:%M:%S')} UTC`
    """
    
    await status_msg.edit_text(final_text)

# Additional callback handlers for new user notifications

@Bot.on_callback_query(filters.regex('^admin_broadcast_help$'))
async def admin_broadcast_help_callback(client: Bot, callback):
    """Handle broadcast help button from new user notification."""
    if callback.from_user.id != OWNER_ID:
        await callback.answer("⚠️ Only owner can use this.", show_alert=True)
        return
    
    help_text = """
📢 **How to Broadcast Messages**

1. **Send or forward** any message to the bot
2. **Reply** to that message with `/broadcast`
3. The message will be sent to all users immediately

**Supported message types:**
• Text messages (with formatting)
• Photos with captions
• Videos with captions
• Documents with captions
• Audio files with captions
• Voice messages
• Stickers
• Animations/GIFs

**Example:**
1. Send: "Hello everyone! 🎵"
2. Reply with: `/broadcast`
3. Done! ✅

You'll get real-time progress updates during broadcasting.
    """
    
    await callback.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="admin_back"),
            InlineKeyboardButton("❌ Close", callback_data="close_admin")
        ]])
    )
    await callback.answer()

@Bot.on_callback_query(filters.regex('^admin_back$'))
async def admin_back_callback(client: Bot, callback):
    """Handle back button in admin help."""
    if callback.from_user.id != OWNER_ID:
        await callback.answer("⚠️ Only owner can use this.", show_alert=True)
        return
    
    # Go back to the original new user notification
    await callback.message.edit_text(
        "📱 **Admin Panel**\n\nSelect an option:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Bot Stats", callback_data="refresh_stats"),
                InlineKeyboardButton("📢 Broadcast Help", callback_data="admin_broadcast_help")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close_admin")
            ]
        ])
    )
    await callback.answer()

@Bot.on_callback_query(filters.regex('^close_admin$'))
async def close_admin_callback(client: Bot, callback):
    """Handle close admin panel."""
    if callback.from_user.id != OWNER_ID:
        await callback.answer("⚠️ Only owner can use this.", show_alert=True)
        return
    
    await callback.message.delete()
    await callback.answer()
