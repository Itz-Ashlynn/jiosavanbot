from aiohttp.web import Application, AppRunner, TCPSite, RouteTableDef, Request, json_response, FileResponse
import os
import json
import datetime

from jiosaavn.config.settings import HOST, PORT

routes = RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request: Request):
    """ Serves the main web interface. """
    try:
        # Serve the index.html file from statis folder
        static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "statis", "index.html")
        if os.path.exists(static_path):
            return FileResponse(static_path)
        else:
            return json_response({"status": "Bot Running", "message": "Web interface not found"})
    except Exception as e:
        return json_response({"error": str(e)}, status=500)

@routes.get("/api/stats", allow_head=True) 
async def stats_api_handler(request: Request):
    """ API endpoint for bot statistics. """
    try:
        # Get bot instance from app context
        bot = request.app.get('bot')
        if not bot:
            return json_response({"error": "Bot not available"}, status=503)
        
        # Get statistics from database
        total_users = await bot.db.get_total_users()
        banned_users = await bot.db.get_banned_users_count()
        active_users = total_users - banned_users
        
        # Get today's stats
        today = datetime.date.today().isoformat()
        today_users = await bot.db.get_users_by_date(today)
        
        # Get quality distribution
        quality_stats = {
            "320kbps": await bot.db.get_users_by_quality('320kbps'),
            "160kbps": await bot.db.get_users_by_quality('160kbps'),
            "96kbps": await bot.db.get_users_by_quality('96kbps'),
            "48kbps": await bot.db.get_users_by_quality('48kbps')
        }
        
        # Get type distribution
        type_stats = {
            "all": await bot.db.get_users_by_type('all'),
            "song": await bot.db.get_users_by_type('song')
        }
        
        stats = {
            "users": {
                "total": total_users,
                "active": active_users,
                "banned": banned_users,
                "today": today_users
            },
            "quality_distribution": quality_stats,
            "type_distribution": type_stats,
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        return json_response(stats)
        
    except Exception as e:
        return json_response({"error": str(e)}, status=500)

@routes.get("/statis/{filename}", allow_head=True)
@routes.get("/{filename:styles\\.css|script\\.js}", allow_head=True)
async def static_files_handler(request: Request):
    """ Serves static files from statis folder. """
    try:
        filename = request.match_info.get('filename', '')
        
        # Security: prevent path traversal
        if '..' in filename or filename.startswith('/'):
            return json_response({"error": "Invalid file path"}, status=400)
            
        static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "statis", filename)
        
        if os.path.exists(static_path) and os.path.isfile(static_path):
            return FileResponse(static_path)
        else:
            return json_response({"error": "File not found"}, status=404)
            
    except Exception as e:
        return json_response({"error": str(e)}, status=500)

async def start_web(bot=None):
    """ Initializes and starts the web server. """

    web_app = Application()
    
    # Store bot instance in app context for API access
    if bot:
        web_app['bot'] = bot
    
    web_app.add_routes(routes)
    runner = AppRunner(web_app)
    await runner.setup()
    await TCPSite(runner, HOST, PORT).start()
    print(f"Web server started on {HOST}:{PORT}")
    return runner

async def stop_web(runner: AppRunner):
    """Stops the web server and performs cleanup."""

    print("Stopping Web Server!!")
    await runner.cleanup()
