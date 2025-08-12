import html
import logging
import traceback

from api.jiosaavn import Jiosaavn
from jiosaavn.bot import Bot
from jiosaavn.utils import safe_edit

from humanfriendly import format_timespan
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex(r"^(playlist|album)#"))
async def playlist_or_album(client: Bot, callback: CallbackQuery):
    await callback.answer()
    
    data = callback.data.split("#")
    item_id = data[1]
    page_no = int(data[2]) if len(data) > 2 and data[2].isdigit() else 1
    back_type = data[2] if len(data) > 2 and not data[2].isdigit() else None
    search_type = "album" if data[0] == "album" else "playlist"
    album_id = item_id if search_type == "album" else None
    playlist_id = item_id if search_type == "playlist" else None
    
    try:
        response = await Jiosaavn().get_playlist_or_album(album_id=album_id, playlist_id=playlist_id, page_no=page_no)
        logger.debug(f"Playlist/Album response: {response}")
        
        if not response:
            return await safe_edit(callback.message, f"**The requested {search_type} could not be found.**\n\n"
                                             f"This might be due to:\n"
                                             f"• Invalid {search_type} ID\n"
                                             f"• {search_type.title()} removed from JioSaavn\n"
                                             f"• Temporary API issues")
        
        # Check for songs in different possible fields
        songs = response.get("list") or response.get("songs") or []
        if not songs:
            return await safe_edit(callback.message, f"**The {search_type} exists but contains no songs.**\n\n"
                                             f"The {search_type} might be empty or the songs are not available in your region.")
        
        # Ensure 'list' field exists for compatibility with rest of code
        if not response.get("list") and response.get("songs"):
            response["list"] = response["songs"]
            response["list_count"] = len(response["songs"])
    except RuntimeError as e:
        logger.error(f"RuntimeError in playlist/album handler: {e}")
        traceback.print_exc()
        return await safe_edit(callback.message, "Connection refused by JioSaavn API. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error in playlist/album handler: {e}")
        traceback.print_exc()
        return await safe_edit(callback.message, f"An unexpected error occurred while fetching the {search_type}. Please try again.")

    title = html.unescape(response.get("title", ""))
    total_results = int(response.get("list_count", 0))
    image_url = response.get("image", "").replace("150x150", "500x500")
    perma_url = response.get("perma_url", "")
    more_info = response.get("more_info", {})
    followers = int(more_info.get("follower_count", 0))
    duration = int(more_info.get("duration", 0))
    release_year = response.get("year", "")
    songs = response.get("list", [])
    
    buttons = []
    for song in songs:
        try:
            # Handle different title fields between APIs
            song_title = song.get("title") or song.get("name", "")
            song_title = html.unescape(str(song_title))
            
            # Try to get song ID from multiple possible fields
            song_id = song.get("id")
            if not song_id and song.get("perma_url"):
                song_id = song.get("perma_url", "").rsplit("/", 1)[1]
            
            if song_id and song_title:
                callback_data = f"song#{song_id}#{item_id}#{search_type}"
                if back_type:
                    callback_data += f"#{back_type}"
                buttons.append([InlineKeyboardButton(f"🎙 {song_title}", callback_data=callback_data)])
            elif song_id:
                # Fallback if no title
                callback_data = f"song#{song_id}#{item_id}#{search_type}"
                if back_type:
                    callback_data += f"#{back_type}"
                buttons.append([InlineKeyboardButton(f"🎙 Song {song_id}", callback_data=callback_data)])
        except (IndexError, AttributeError) as e:
            logger.debug(f"Error processing song: {e}")
            pass

    navigation_buttons = []
    if page_no > 1:
        navigation_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"{search_type}#{item_id}#{page_no-1}"))
    if total_results > 10 * page_no:
        navigation_buttons.append(InlineKeyboardButton("➡️", callback_data=f"{search_type}#{item_id}#{page_no+1}"))
    if navigation_buttons:
        buttons.append(navigation_buttons)

    buttons.append([InlineKeyboardButton('Upload Album 📤', callback_data=f'upload#{item_id}#{search_type}')])
    buttons.append([InlineKeyboardButton('Close ❌', callback_data="close")])
    back_callback_data = f"search#{back_type}" if back_type else f"search#{search_type}s"
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data=back_callback_data)])

    search_type_text = "💾 Playlist" if playlist_id else "📚 Album"
    text_data = (
        f"[\u2063]({image_url})"
        f"**{search_type_text}:** [{title}]({perma_url})",
        f"**📜 Page No:** {page_no}",
        f"**🕰 Duration:** {format_timespan(duration)}" if duration else "",
        f"**🔊 Total Songs:** {total_results}" if total_results else "",
        f"**👥 Followers:** {followers:,}" if followers else "",
        f"**📆 Release Year:** __{release_year}__" if release_year else ''
    )
    text = "\n\n".join(filter(None, text_data))

    await safe_edit(callback.message, text, reply_markup=InlineKeyboardMarkup(buttons))
