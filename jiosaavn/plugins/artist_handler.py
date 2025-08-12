import html
import logging
import traceback

from api.jiosaavn import Jiosaavn
from jiosaavn.bot import Bot
from jiosaavn.utils import safe_edit

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex(r"^artist#"))
async def artist(client: Bot, callback: CallbackQuery):
    await callback.answer()
    data = callback.data.split("#")
    artist_id = data[1]
    
    # Handle different callback data formats
    page_no = 1
    back_type = None
    artist_name = None
    
    if len(data) >= 3:
        # Check if the third parameter is a page number or a search type
        try:
            page_no = int(data[2])
            logger.debug(f"Artist handler: Using page number {page_no}")
        except ValueError:
            # If it's not a number, it's likely 'topquery' or similar
            back_type = data[2]
            page_no = 1
            logger.debug(f"Artist handler: Using back_type {back_type}, defaulting to page 1")
    
    # Get artist name from cache
    from jiosaavn.utils import artist_cache
    artist_name = artist_cache.get(artist_id)
    logger.debug(f"Retrieved artist name from cache: {artist_name}")
    
    logger.debug(f"Artist handler called with: artist_id={artist_id}, page_no={page_no}, back_type={back_type}")
    msg = callback.message

    try:
        response = await Jiosaavn().get_artist(artist_id=artist_id, artist_name=artist_name, page_no=page_no)
        if not response or not response.get("topSongs"):
            # Determine the appropriate back button based on the source
            back_callback = f"search#{back_type}" if back_type else "search#artists"
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=back_callback)]])
            return await safe_edit(
                callback.message,
                "**No songs found for this artist.**\n\n"
                "The artist might not have any songs available in the JioSaavn database, "
                "or there might be an issue with the artist ID.",
                reply_markup=reply_markup
            )
    except RuntimeError as e:
        logger.error(e)
        traceback.print_exc()
        back_callback = f"search#{back_type}" if back_type else "search#artists"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=back_callback)]])
        return await safe_edit(
            msg, 
            "Connection refused by JioSaavn API. Please try again.",
            reply_markup=reply_markup
        )

    name = response.get("name")
    songs = response.get("topSongs")
    total_results = response.get("count", 0)
    image_url = response.get("image")
    image_url = image_url.replace("150x150", "500x500") if image_url else None
    artist_url = response.get("urls", {}).get("songs")
    follower_count = int(response.get("follower_count", "0"))
    dob = response.get("dob")

    buttons = []
    for song in songs:
        try:
            # Handle different title fields between APIs
            song_title = song.get("title") or song.get("name", "")
            song_title = html.unescape(str(song_title))
            button_label = f"🎙 {song_title}" if song_title else f"🎙 Song"
            
            # Try to get song ID from multiple possible fields
            song_id = song.get("id")
            if not song_id and song.get("perma_url"):
                song_id = song.get("perma_url", "").rsplit("/", 1)[1]
            
            if song_id:
                # Create proper callback data for songs with back navigation
                if back_type:
                    callback_data = f"song#{song_id}#{artist_id}#artist#{back_type}"
                else:
                    callback_data = f"song#{song_id}#{artist_id}#artist"
                buttons.append([InlineKeyboardButton(button_label, callback_data=callback_data)])
        except (IndexError, AttributeError) as e:
            logger.debug(f"Error processing artist song: {e}")
            pass

    # Add navigation buttons only if we have multiple pages
    navigation_buttons = []
    if page_no > 1:
        navigation_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"artist#{artist_id}#{page_no-1}"))
    if total_results > 20 * page_no:
        navigation_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"artist#{artist_id}#{page_no+1}"))
    if navigation_buttons:
        buttons.append(navigation_buttons)

    # Add control buttons
    buttons.append([InlineKeyboardButton('Close ❌', callback_data="close")])
    # Determine the appropriate back button
    back_callback = f"search#{back_type}" if back_type else "search#artists"
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data=back_callback)])

    # Prepare display text with better formatting
    text_data = []
    
    # Add invisible image link if available
    if image_url:
        text_data.append(f"[\u2063]({image_url})")
    
    # Add artist information
    if name:
        if artist_url:
            text_data.append(f"**👨‍🎤 Artist:** [{name}]({artist_url})")
        else:
            text_data.append(f"**👨‍🎤 Artist:** {name}")
    
    # Add statistics
    if total_results:
        text_data.append(f"**🎵 Available Songs:** {total_results:,}")
    
    if follower_count:
        text_data.append(f"**👥 Followers:** {follower_count:,}")
    
    if dob:
        text_data.append(f"**📆 Date of Birth:** __{dob}__")
    
    # Add pagination info if needed
    if total_results > 10:
        text_data.append(f"**📜 Page:** {page_no}")
    
    # Join all text data
    text = "\n\n".join(filter(None, text_data))
    
    # Add a helpful message if no songs were found but artist exists
    if not buttons[:-1]:  # Only back button exists
        text += "\n\n⚠️ **No songs available for this artist at the moment.**"
    
    await safe_edit(msg, text, reply_markup=InlineKeyboardMarkup(buttons))
