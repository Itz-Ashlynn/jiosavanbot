"""
Utility functions for the JioSaavn bot.
"""
import logging
import time
from typing import Dict, Optional
from pyrogram.types import Message, InputMediaPhoto
from pyrogram.errors import MessageNotModified

logger = logging.getLogger(__name__)

# Simple in-memory cache for artist names to avoid callback data size limits
class ArtistCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self._cache: Dict[str, Dict] = {}
        self._max_size = max_size
        self._ttl = ttl
    
    def set(self, artist_id: str, artist_name: str) -> None:
        """Store artist name with timestamp"""
        # Clean old entries if cache is full
        if len(self._cache) >= self._max_size:
            self._cleanup()
        
        self._cache[artist_id] = {
            'name': artist_name,
            'timestamp': time.time()
        }
    
    def get(self, artist_id: str) -> Optional[str]:
        """Get artist name if exists and not expired"""
        entry = self._cache.get(artist_id)
        if not entry:
            return None
        
        # Check if expired
        if time.time() - entry['timestamp'] > self._ttl:
            del self._cache[artist_id]
            return None
        
        return entry['name']
    
    def _cleanup(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self._cache.items() 
            if current_time - value['timestamp'] > self._ttl
        ]
        for key in expired_keys:
            del self._cache[key]
        
        # If still too big, remove oldest entries
        if len(self._cache) >= self._max_size:
            # Sort by timestamp and remove oldest
            sorted_items = sorted(
                self._cache.items(), 
                key=lambda x: x[1]['timestamp']
            )
            # Remove oldest 20% of entries
            remove_count = max(1, len(sorted_items) // 5)
            for key, _ in sorted_items[:remove_count]:
                del self._cache[key]

# Global artist cache instance
artist_cache = ArtistCache()

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
