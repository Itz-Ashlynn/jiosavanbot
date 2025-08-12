import logging
from jiosaavn.bot import Bot
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex(r"^close$"))
async def close_message(client: Bot, callback: CallbackQuery):
    """Handle close button callbacks"""
    await callback.answer()
    try:
        await callback.message.delete()
        logger.debug(f"Message closed by user {callback.from_user.id}")
    except Exception as e:
        logger.debug(f"Could not delete message: {e}")
        # If deletion fails, just edit to a simple closed message
        try:
            await callback.message.edit("✅ **Closed**")
        except Exception as e2:
            logger.debug(f"Could not edit message either: {e2}")
