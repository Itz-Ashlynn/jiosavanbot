from os import getenv

API_ID = getenv("API_ID")
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")
OWNER_ID = int(getenv("OWNER_ID", "0"))
BOT_COMMANDS = (
    ("start", "Initialize the bot and check its status"),
    ("settings", "Configure and manage bot settings"),
    ("help", "Get information on how to use the bot"),
    ("about", "Learn more about the bot and its features"),
    ("broadcast", "Send a message to all users (Admin Only)"),
    ("stats", "Get bot statistics (Admin Only)"),
)

DATABASE_URL = getenv("DATABASE_URL", None)
HOST = getenv("HOST", "0.0.0.0")
PORT = int(getenv("PORT", "80"))
