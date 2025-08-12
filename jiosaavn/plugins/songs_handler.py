import os
import html
import logging
import traceback

from jiosaavn.bot import Bot
from jiosaavn.utils import safe_edit, safe_edit_media
from api.jiosaavn import Jiosaavn
from jiosaavn.config.settings import HOST, PORT

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

logger = logging.getLogger(__name__)

@Bot.on_callback_query(filters.regex(r"^song#"))
async def handle_song_callback(client: Bot, callback: CallbackQuery):
    msg = callback.message
    await callback.answer()
    
    data = callback.data.split("#")
    song_id = data[1]
    item_id, search_type, back_type = (None, "songs", None)
    if len(data) == 3:
        search_type = data[2]
    elif len(data) >= 4:
        item_id, search_type = (data[2], data[3])
        if len(data) == 5:
            back_type = data[4]

    try:
        response = await Jiosaavn().get_song(song_id=song_id)
        if not response or not response.get("songs"):
            return await safe_edit(msg, "**The requested song could not be found.**")
    except RuntimeError as e:
        logger.error(e)
        traceback.print_exc()
        return await safe_edit(msg, "Connection refused by jiosaavn api. Please try again")

    song_data = response["songs"][0]

    title = song_data.get("title", "Unknown")
    title = html.unescape(title)
    formatted_title = title.replace(" ", "-")
    language = song_data.get("language", "Unknown")
    play_count = song_data.get("play_count", "0")
    play_count = int(play_count) if play_count else 0
    more_info = song_data.get("more_info", {})
    # Extract album info - handle both formats
    album = more_info.get("album", "Unknown")
    if isinstance(album, dict):
        album = album.get("name", "Unknown")
    elif not isinstance(album, str):
        album = "Unknown"
    
    # Extract album URL - handle both formats
    album_url = more_info.get("album_url", "")
    if not album_url and isinstance(album, str) and album != "Unknown":
        # Fallback: construct album URL if not provided
        album_url = f"https://jiosaavn.com/album/{album.lower().replace(' ', '-')}"
    
    # Extract artists - handle both formats
    artists = []
    if more_info.get("artistMap", {}).get("artists"):
        # Official API format
        artists = more_info["artistMap"]["artists"]
    elif song_data.get("artists"):
        # Fallback API format
        artists_data = song_data["artists"]
        if isinstance(artists_data, list):
            artists = artists_data
        elif isinstance(artists_data, dict):
            # Artists is a dict - convert to list format
            if "primary_artists" in artists_data:
                artists = artists_data.get("primary_artists", [])
            elif "all" in artists_data:
                artists = artists_data.get("all", [])
            else:
                # Fallback: treat the dict as a single artist entry
                artists = [artists_data]
    
    # Ensure artists is always a list
    if not isinstance(artists, list):
        artists = []

    def get_artist_by_role(role: str) -> str:
        artist_names = []
        for artist in artists:
            if isinstance(artist, dict) and artist.get("role") == role:
                name = artist.get("name", "")
                if name:
                    artist_names.append(name)
        return ", ".join(artist_names)
    
    # Extract performers/singers - handle both formats
    music = more_info.get("music") or get_artist_by_role("music")
    
    # Extract singers - prioritize singer role, then primary_artists
    singers = get_artist_by_role("singer")
    if not singers:
        # Try primary_artists if no specific singers found
        primary_artists = []
        for artist in artists:
            if isinstance(artist, dict) and artist.get("role") == "primary_artists":
                name = artist.get("name", "")
                if name:
                    primary_artists.append(name)
        if primary_artists:
            singers = ", ".join(primary_artists)
    
    # Final fallback: use first few artists if still no singers
    if not singers and artists:
        artist_names = []
        for artist in artists[:3]:  # Limit to first 3
            if isinstance(artist, dict):
                name = artist.get("name", "")
                if name:
                    artist_names.append(name)
            elif isinstance(artist, str):
                artist_names.append(artist)
        singers = ", ".join(artist_names)
    
    lyricists = get_artist_by_role("lyricist")
    actors = get_artist_by_role("starring")
    # Extract release info - handle both formats
    release_date = more_info.get("release_date") or song_data.get("releaseDate")
    release_year = song_data.get("year") or (release_date.split("-")[0] if release_date else "")
    album_url = more_info.get("album_url", "")
    
    # Handle image URL - different formats between APIs
    image_url = ""
    image_data = song_data.get("image", "")
    if isinstance(image_data, str):
        # Official API format - direct string
        image_url = image_data.replace("150x150", "500x500") if image_data else ""
    elif isinstance(image_data, list) and len(image_data) > 0:
        # Fallback API format - list of image objects
        # Get the highest quality image (usually the last one)
        image_url = image_data[-1].get("url", "") if image_data[-1] else ""
    elif isinstance(image_data, dict):
        # Some APIs return image as dict
        image_url = image_data.get("url", "")
    
    song_url = song_data.get('perma_url', f"https://jiosaavn.com/songs/{formatted_title}/{song_id}")

    text_data = [
        f"**🎧 Song:** [{title}]({song_url})" if title else '',
        f"**📚 Album:** [{album}]({album_url})" if album and album_url else f"**📚 Album:** {album}" if album else '',
        f"**🎵 Music:** {music}" if music else '',
        f"**▶️ Plays:** {play_count:,}" if play_count else '',
        f"**👨‍🎤 Singers:** {singers}" if singers else '',
        f"**✍️ Lyricist:** {lyricists}" if lyricists else '',
        f"**👫 Actors:** {actors}" if actors else '',
        f"**📰 Language:** {language}" if language else '',
        f"**📆 Release Date:** __{release_date}__" if release_date else '',
        f"**📆 Release Year:** __{release_year}__" if not release_date and release_year else '',
    ]
    text = "\n\n".join(filter(None, text_data))

    if item_id:
        back_button_callback_data = f"{search_type}#{item_id}"
        if back_type:
            back_button_callback_data += f"#{back_type}"
    else:
        back_button_callback_data = f"search#{search_type}"

    buttons = [[
        InlineKeyboardButton('Upload to TG 📤', callback_data=f'upload#{song_id}#song')
    ], [
        InlineKeyboardButton('🔙', callback_data=back_button_callback_data)
    ], [
        InlineKeyboardButton('Close ❌', callback_data="close")
    ]]
    if more_info.get('has_lyrics') == 'true':
        lyrics_id = song_data.get("id")
        lyrics_button_callback_data = f"lyrics#{lyrics_id}#{song_id}#{search_type}"
        if item_id:
            lyrics_button_callback_data += f"#{item_id}#{back_type}"

        buttons[0].insert(0, InlineKeyboardButton("Lyrics 📃", callback_data=lyrics_button_callback_data))

    await safe_edit_media(
        msg,
        media=InputMediaPhoto(image_url, caption=text[:1024]),  # Safety limit on caption length
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    await Jiosaavn()._request_data(url=f"http://{HOST}:{PORT}")

@Bot.on_callback_query(filters.regex(r"^lyrics#"))
async def lyrics(client: Bot, callback: CallbackQuery):
    data = callback.data.split('#')
    lyrics_id = data[1]

    response = await Jiosaavn().get_song_lyrics(lyrics_id=lyrics_id)
    lyrics = response.get("lyrics", "")
    lyrics = lyrics.replace("<br>", "\n")
    if not lyrics:
        await callback.answer("**The requested song could not be found.**", show_alert=True)
        return

    if len(lyrics) <= 4096:
        callback_data = "song#" + "#".join(data[2:])
        button = [
            [InlineKeyboardButton('🔙 Back', callback_data=callback_data)],
            [InlineKeyboardButton('Close ❌', callback_data="close")]
        ]
        try:
            await callback.answer()
            await callback.message.edit(lyrics, reply_markup=InlineKeyboardMarkup(button))
        except:
            pass
    else:
        await callback.answer("Sending a song lyrics document")
        file_location = f"{response.get('snippet')} song lyrics.txt"
        with open(file_location, 'w') as f:
            f.write(lyrics)

        await client.send_document(
            chat_id=callback.from_user.id,
            document=file_location
        )

        try:
            os.remove(file_location)
        except FileNotFoundError:
            logger.warning(f"File {file_location} was not found for deletion.")
