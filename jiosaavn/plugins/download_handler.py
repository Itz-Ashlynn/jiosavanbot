import os
import html
import time
import shutil
import logging

from jiosaavn.bot import Bot
from jiosaavn.utils import safe_edit
from api.jiosaavn import Jiosaavn

import aiohttp
import aiofiles
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ChatAction

logger = logging.getLogger(__name__)

@Bot.on_callback_query(filters.regex(r"^upload#"))
@Bot.on_message(filters.regex(r"http.*") & filters.private & filters.incoming)
async def download(client: Bot, message: Message|CallbackQuery):
    if isinstance(message, CallbackQuery):
        _, item_id, search_type = message.data.split("#")
        msg = await safe_edit(message.message, "**Processing...**")
    else:
        msg = await message.reply("**Processing...**", quote=True)
        msg.reply_to_message = message
        query = message.text
        item_id = query.rsplit("/", 1)[1]
        if "song" in query:
            search_type = "song"
        elif "album" in query:
            search_type = "album"
        elif "featured" in query:
            search_type = "playlist"
        elif "artist" in query:
            search_type = "artist"

    if search_type == "song":
        await download_tool(client, message, msg, item_id)
    elif search_type in ("album", "playlist", "artist"):
        page_no = 1
        album_id = item_id if search_type == "album" else None
        playlist_id = item_id if search_type == "playlist" else None
        artist_id = item_id if search_type == "artist" else None
        
        # Get original URL for fallback API
        original_url = None
        if isinstance(message, Message):
            original_url = message.text

        # Get playlist/album/artist data
        try:
            jiosaavn = Jiosaavn()
            
            if search_type == "artist":
                response = await jiosaavn.get_artist(artist_id=artist_id, page_no=page_no)
                if response and response.get("topSongs"):
                    # Convert artist response to common format
                    response = {
                        "list": response["topSongs"],
                        "title": response.get("name", "Unknown Artist"),
                        "list_count": response.get("count", len(response["topSongs"]))
                    }
            else:
                response = await jiosaavn.get_playlist_or_album(
                    album_id=album_id, 
                    playlist_id=playlist_id, 
                    page_no=page_no,
                    original_url=original_url
                )
            
            if not response or not response.get("list"):
                await safe_edit(msg, f"**No songs found in this {search_type}.**\n\nThis might be due to:\n• Invalid {search_type} ID\n• {search_type.title()} removed from JioSaavn\n• Temporary API issues")
                return
            
            # Download all songs from the playlist/album/artist
            songs = response["list"]
            total_songs = len(songs)
            
            if total_songs == 0:
                await safe_edit(msg, f"**This {search_type} is empty.**")
                return
            
            # Limit to a reasonable number to prevent overwhelming
            MAX_SONGS = 50
            if total_songs > MAX_SONGS:
                songs = songs[:MAX_SONGS]
                total_songs = MAX_SONGS
                await safe_edit(msg, f"**Found {response.get('list_count', 'many')} songs, downloading first {MAX_SONGS}...**")
            else:
                await safe_edit(msg, f"**Found {total_songs} songs. Starting download...**")
            
            download_success = 0
            download_failed = 0
            
            for i, song in enumerate(songs, 1):
                # Try to get song ID from multiple possible fields
                song_id = song.get("id")
                if not song_id:
                    song_url = song.get("perma_url", "")
                    if song_url and "/" in song_url:
                        song_id = song_url.rsplit("/", 1)[-1]
                
                if not song_id:
                    logger.warning(f"Could not extract song ID from song: {song}")
                    download_failed += 1
                    continue
                
                # Update progress
                progress_msg = f"**Downloading song {i}/{total_songs}...**"
                try:
                    await safe_edit(msg, progress_msg)
                except:
                    pass  # Continue if edit fails
                
                try:
                    await download_tool(client, message, msg, song_id)
                    download_success += 1
                except Exception as e:
                    logger.error(f"Failed to download song {song_id}: {e}")
                    download_failed += 1
                    continue
            
            # Final status message
            if download_success > 0:
                status_msg = f"**✅ Download complete!**\n\n**Downloaded:** {download_success} songs"
                if download_failed > 0:
                    status_msg += f"\n**Failed:** {download_failed} songs"
                await safe_edit(msg, status_msg)
            else:
                await safe_edit(msg, f"**❌ Failed to download any songs from this {search_type}.**")
                
        except Exception as e:
            logger.error(f"Error processing {search_type}: {e}")
            await safe_edit(msg, f"**❌ Error processing {search_type}: {str(e)}**")
    else:
        await safe_edit(msg, "Podcast upload not supported.")
        return

async def download_tool(client: Bot, message: Message|CallbackQuery, msg: Message, song_id: str):
    is_exist = await client.db.is_song_id_exist(song_id)
    user = await client.db.get_user(message.from_user.id)
    quality = user['quality']
    bitrate = 320 if quality == "320kbps" else 160

    if is_exist:
        song = (await client.db.get_song(song_id)).get(quality)
        if song:
            try:
                song_msg = await client.get_messages(chat_id=int(song.get('chat_id')), message_ids=int(song.get('message_id')))
                if not song_msg.empty:
                    is_sent = await song_msg.copy(message.from_user.id, reply_to_message_id=msg.reply_to_message.id)
                    if is_sent:
                        # Delete temp message after successful copy
                        try:
                            await msg.delete()
                        except Exception as e:
                            logger.debug(f"Could not delete temp message: {e}")
                        return
            except Exception as e:
                logger.debug(f"Could not copy existing song: {e}")
                # Continue with download if copy fails

    # Extract song data
    song_response = await Jiosaavn().get_song(song_id=song_id)
    
    # Handle different response formats
    if not song_response:
        raise ValueError(f"No response received for song ID: {song_id}")
    
    # Check if songs is a list or object
    songs = song_response.get("songs")
    if isinstance(songs, list) and len(songs) > 0:
        song_data = songs[0]
    elif isinstance(songs, dict):
        song_data = songs
    else:
        raise ValueError(f"Invalid song response format for ID: {song_id}. Response: {song_response}")

    # Extract metadata - handle both official API and fallback API formats
    title = song_data.get("title") or song_data.get("name", "Unknown")
    title = html.unescape(str(title))
    formatted_title = title.replace(" ", "-")
    
    # Handle language field
    language = song_data.get("language", "Unknown")
    
    # Handle different API response formats
    more_info = song_data.get("more_info", {})
    
    # Extract album info - fallback API has direct album field
    album = more_info.get("album") or song_data.get("album", {})
    if isinstance(album, dict):
        album = album.get("name", "Unknown")
    elif not isinstance(album, str):
        album = "Unknown"
    
    # Extract artists - handle both formats
    artists = []
    if more_info.get("artistMap", {}).get("artists"):
        # Official API format
        artists = more_info["artistMap"]["artists"]
    elif song_data.get("artists"):
        # Fallback API format
        artists = song_data["artists"]
    
    def get_artist_by_role(role: str) -> str:
        return ", ".join(artist.get("name") for artist in artists if artist.get("role") == role)
    
    # Extract performers/singers
    singers = get_artist_by_role("singer") or get_artist_by_role("primary_artists")
    if not singers and artists:
        # Fallback: use first artist or all artists
        singers = ", ".join(artist.get("name", "") for artist in artists[:3])  # Limit to first 3
    
    # Extract release info
    release_date = more_info.get("release_date") or song_data.get("releaseDate")
    release_year = song_data.get("year") or (release_date.split("-")[0] if release_date else "")
    
    # Extract duration - handle string and int formats
    duration_raw = more_info.get("duration") or song_data.get("duration", "0")
    try:
        duration = int(duration_raw) if duration_raw else 0
    except (ValueError, TypeError):
        duration = 0
    
    # Extract URLs
    album_url = more_info.get("album_url", "")
    song_url = song_data.get('perma_url') or song_data.get('url', f"https://jiosaavn.com/songs/{formatted_title}/{song_id}")
    
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

    # Create caption
    text_data = [
        f"[\u2063]({image_url})"
        f"**🎧 Song:** [{title}]({song_url})" if title else '',
        f"**📚 Album:** [{album}]({album_url})" if album else '',
        f"**📰 Language:** {language}" if language else '',
        f"**📆 Release Date:** __{release_date}__" if release_date else '',
        f"**📆 Release Year:** __{release_year}__" if not release_date and release_year else '',
    ]

    caption = "\n\n".join(filter(None, text_data))

    # Download and upload song
    download_dir = f"./download/{time.time()}{message.from_user.id}/"
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)

    file_name = f"{download_dir}{title}_{quality}.mp3"
    thumbnail_location = f"{download_dir}{title}.jpg"

    try:
        await msg.edit(f"__📥 Downloading {title}__")
    except Exception as e:
        logger.debug(f"Could not edit message during download: {e}")
        # If edit fails, send a new message instead
        msg = await client.send_message(
            chat_id=message.from_user.id,
            text=f"__📥 Downloading {title}__",
            reply_to_message_id=msg.reply_to_message.id if msg.reply_to_message else None
        )
    await client.send_chat_action(
        chat_id=message.from_user.id,
        action=ChatAction.RECORD_AUDIO
    )

    async with aiohttp.ClientSession() as session: 
        async with session.get(image_url) as response:
            async with aiofiles.open(thumbnail_location, "wb") as file:
                await file.write(await response.read())

    try:
        # Try to get download URL from song data
        download_url = None
        
        # Check if song has downloadUrl field (fallback API format)
        if song_data.get("downloadUrl"):
            download_urls = song_data["downloadUrl"]
            if isinstance(download_urls, list):
                # Find the appropriate quality
                for url_obj in download_urls:
                    if str(bitrate) in url_obj.get("quality", ""):
                        download_url = url_obj.get("url")
                        break
                # Fallback to highest quality if exact bitrate not found
                if not download_url and download_urls:
                    download_url = download_urls[-1].get("url")
        
        if download_url:
            # Direct download from URL
            logger.info(f"Direct downloading from URL for {title}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Referer': 'https://www.jiosaavn.com/',
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(download_url) as response:
                    response.raise_for_status()
                    async with aiofiles.open(file_name, "wb") as file:
                        while True:
                            chunk = await response.content.read(4 * 1024 * 1024)  # 4 MB chunks
                            if not chunk:
                                break
                            await file.write(chunk)
            audio = file_name
        else:
            # Fallback to official API download
            logger.info(f"Using official API download for {title}")
            audio = await Jiosaavn().download_song(song_id=song_id, bitrate=bitrate, download_location=file_name)
        
        if not audio or not os.path.exists(file_name):
            await safe_edit(msg, f"Failed to download {title}")
            return
            
    except Exception as e:
        logger.error(f"Error downloading song {title}: {e}")
        await safe_edit(msg, f"Failed to download {title}: {str(e)}")
        return
    try:
        await msg.edit(f"__📤 Uploading {title}__")
    except Exception as e:
        logger.debug(f"Could not edit message during upload: {e}")
        # If edit fails, send a new message instead
        msg = await client.send_message(
            chat_id=message.from_user.id,
            text=f"__📤 Uploading {title}__",
            reply_to_message_id=msg.reply_to_message.id if msg.reply_to_message else None
        )
    await client.send_chat_action(
        chat_id=message.from_user.id,
        action=ChatAction.UPLOAD_AUDIO
    )

    try:
        # Get the reply_to_message_id safely
        reply_to_id = None
        if msg.reply_to_message:
            reply_to_id = msg.reply_to_message.id
        elif isinstance(message, Message) and message.reply_to_message:
            reply_to_id = message.reply_to_message.id
        elif isinstance(message, Message):
            reply_to_id = message.id
        
        # Validate file before uploading
        if not os.path.exists(audio):
            await safe_edit(msg, f"Audio file not found for {title}")
            return
        
        # Check file size (Telegram has 50MB limit for bots)
        file_size = os.path.getsize(audio)
        if file_size > 50 * 1024 * 1024:  # 50MB
            await safe_edit(msg, f"File too large to upload: {title} ({file_size / 1024 / 1024:.1f}MB)")
            return
        
        song_file = await client.send_audio(
            chat_id=message.from_user.id,
            audio=audio,
            caption=caption,
            duration=duration,
            title=title,
            thumb=thumbnail_location if os.path.exists(thumbnail_location) else None,
            performer=singers,
            reply_to_message_id=reply_to_id,
        )
        
        if not song_file:
            await safe_edit(msg, f"Failed to upload {title} - upload returned None")
            return
        
        # Update database
        await client.db.update_song(song_id, quality, song_file.chat.id, song_file.id)
        
        # Delete the audio file immediately after successful upload to save space
        try:
            if os.path.exists(audio):
                os.remove(audio)
                logger.debug(f"Deleted audio file: {audio}")
        except Exception as e:
            logger.debug(f"Could not delete audio file {audio}: {e}")
        
        # Delete the temporary message after successful upload
        try:
            await msg.delete()
        except Exception as e:
            logger.debug(f"Could not delete temp message: {e}")
            
    except Exception as e:
        logger.error(f"Error uploading song {title}: {e}")
        await safe_edit(msg, f"Failed to upload {title}: {str(e)}")
    finally:
        # Clean up download directory
        try:
            if os.path.exists(download_dir):
                shutil.rmtree(download_dir)
        except Exception as e:
            logger.debug(f"Could not clean up directory {download_dir}: {e}")
