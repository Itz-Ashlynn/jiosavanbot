import html
import logging
import traceback

from api.jiosaavn import Jiosaavn
from jiosaavn.bot import Bot
from jiosaavn.utils import safe_edit

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


logger = logging.getLogger(__name__)

@Bot.on_callback_query(filters.regex(r"^search#"))
@Bot.on_message(
    filters.text & filters.incoming & filters.private & 
    ~filters.regex(r'^http.*') & ~filters.via_bot & 
    ~filters.command(["start", "settings", "help", "about"])
)
async def search(client: Bot, message: Message|CallbackQuery):
    if isinstance(message, Message):
        send_msg = await message.reply("__**Processing... ⏳**__", quote=True)
    else:
        await message.answer()
        send_msg = message.message

    query = message.text if isinstance(message, Message) else message.message.reply_to_message.text
    page_no = 1
    if isinstance(message, Message):
        user_data = await client.db.get_user(message.from_user.id)
        search_type = user_data['type']
    else:
        data = message.data.split('#')
        search_type = data[1]
        if len(data) == 3:
            page_no = int(data[2])

    try:
        if search_type in ('all', 'topquery'):
            response = await Jiosaavn().search_all_types(query=query)
        else:
            response = await Jiosaavn().search(query=query, search_type=search_type, page_no=page_no)
    except RuntimeError as e:
        logger.error(e)
        traceback.print_exc()
        return await safe_edit(send_msg, "Connection refused by jiosaavn api. Please try again")

    if not response:
        return await safe_edit(send_msg, f'🔎 No search result found for your query `{query}`')

    buttons = []
    if search_type == "all" or search_type == "topquery":
        # Define the mapping for button labels and callback data based on result type
        button_song_type_map = {
            "songs": (f"🎙 Songs", f"search#songs"),
            "albums": (f"📚 Albums", f"search#albums"),
            "playlists": (f"💾 Playlists", f"search#playlists"),
            "artists": (f"👨‍🎤 Artists", f"search#artists"),
            "topquery": (f"✨ Top Result", f"search#topquery"),
        }

        if search_type == 'topquery':
            sub_sorted_data = sorted(
                response.get("topquery", {}).get("data", []),
                key=lambda x: x.get("position", 0)
            )
            for data in sub_sorted_data:
                # Extract relevant information from the result
                title = data.get("title", "unkown")
                title = html.unescape(title)
                album = data.get("album")
                item_type = data.get("type")
                # Extract ID from URL or use direct ID field
                url = data.get("url", "")
                if url and "/" in url:
                    item_id = url.rsplit("/", 1)[1]
                else:
                    item_id = data.get("id", "unknown")
                type_emoji_map = {
                    "song": "🎙",
                    "album": "📚",
                    "playlist": "💾",
                    "artist": "👨‍🎤",
                }
                if item_type not in type_emoji_map:
                    continue
                emoji = type_emoji_map[item_type]
                button_text = f"{emoji} {title} from {album}" if album else f"{emoji} {title}"
                
                # For artists in topquery, store the name in cache
                if item_type == "artist":
                    from jiosaavn.utils import artist_cache
                    artist_cache.set(item_id, title)
                    callback_data = f"{item_type}#{item_id}#topquery"
                else:
                    callback_data = f"{item_type}#{item_id}#topquery"
                buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
        else:
            # Sorts the response data by position to maintain consistency with the official JioSaavn website's.
            sorted_data = sorted(response.items(), key=lambda value: value[1].get("position", 0))
            for result_type, result in sorted_data:
                # ignore if the search type is unkown
                if result_type not in button_song_type_map:
                    continue

                if result.get("data"):
                    button_label, callback_data = button_song_type_map.get(result_type, (None, None))
                    buttons.append([InlineKeyboardButton(text=button_label, callback_data=callback_data)])
        text = f"**🔍 Search Query:** {query}\n\n__Please select one catogery 👇__"
    else:
        # Get the total number of results
        total_results = response.get("total", 0)

        # Iterate over each result
        for result in response.get("results", []):
            # Extract relevant information from the result
            # For some items, use 'id' field if perma_url extraction fails
            perma_url = result.get("perma_url", "")
            if perma_url and "/" in perma_url:
                item_id = perma_url.rsplit("/", 1)[1]
            else:
                item_id = result.get("id", "unknown")
            title = result.get("title", "unknown")
            title = html.unescape(title)
            result_type = result.get("type", "unknown")
            artist = result.get("name", "unknown")
            artist = html.unescape(artist)
            more_info = result.get("more_info", {})
            album = more_info.get("album", "")

            # Define the mapping for button labels based on result type
            button_label_map = {
                "song": f"🎙 {title} from '{album}'" if album else f"🎙 {title}",
                "album": f"📚 {title}",
                "playlist": f"💾 {title}",
                "artist": f"👨‍🎤 {artist}",
            }

            # Get the button label and callback data for the current result type
            button_label = button_label_map.get(result_type)
            if button_label:
                # For artists, store the name in cache to avoid callback data size limits
                if result_type == "artist":
                    from jiosaavn.utils import artist_cache
                    artist_cache.set(item_id, artist)
                    callback_data = f"{result_type}#{item_id}"
                else:
                    callback_data = f"{result_type}#{item_id}"
                buttons.append([InlineKeyboardButton(text=button_label, callback_data=callback_data)])

        text = f"**📈 Total Results:** {total_results}\n\n**🔍 Search Query:** {query}\n\n**📜 Page No:** {page_no}"
        navigation_buttons = []
        if page_no > 1:
            navigation_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"search#{search_type}#{page_no-1}"))
        if total_results > 10 * page_no:
            navigation_buttons.append(InlineKeyboardButton("➡️", callback_data=f"search#{search_type}#{page_no+1}"))
        if navigation_buttons:
            buttons.append(navigation_buttons)


    if not buttons:
        return await safe_edit(send_msg, f'🔎 No search result found for your query `{query}`')

    buttons.append([InlineKeyboardButton('Close ❌', callback_data="close")])
    await safe_edit(send_msg, text, reply_markup=InlineKeyboardMarkup(buttons))
