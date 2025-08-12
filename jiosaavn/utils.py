"""
Utility functions for the JioSaavn bot.
"""
import logging
from pyrogram.types import Message, InputMediaPhoto
from pyrogram.errors import MessageNotModified

logger = logging.getLogger(__name__)

async def safe_edit_text(message: Message, text: str, **kwargs):
    """
    Safely edit message text, handling MessageNotModified errors.
    
    Args:
        message: Message object to edit
        text: New text content
        **kwargs: Additional arguments for edit_text
    
    Returns:
        Edited message or None if error
    """
    try:
        return await message.edit_text(text, **kwargs)
    except MessageNotModified:
        logger.debug("Message not modified - content is the same")
        return message
    except Exception as e:
        logger.error(f"Error editing message text: {e}")
        return None

async def safe_edit_media(message: Message, media: InputMediaPhoto, **kwargs):
    """
    Safely edit message media, handling MessageNotModified errors.
    
    Args:
        message: Message object to edit
        media: New media content
        **kwargs: Additional arguments for edit_media
    
    Returns:
        Edited message or None if error
    """
    try:
        return await message.edit_media(media, **kwargs)
    except MessageNotModified:
        logger.debug("Message not modified - content is the same")
        return message
    except Exception as e:
        logger.error(f"Error editing message media: {e}")
        return None

async def safe_edit(message: Message, text: str, **kwargs):
    """
    Safely edit message, handling MessageNotModified errors.
    
    Args:
        message: Message object to edit
        text: New text content
        **kwargs: Additional arguments for edit
    
    Returns:
        Edited message or None if error
    """
    try:
        return await message.edit(text, **kwargs)
    except MessageNotModified:
        logger.debug("Message not modified - content is the same")
        return message
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        return None
