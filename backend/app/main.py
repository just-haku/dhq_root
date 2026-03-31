from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from app.core.config import settings
from app.core.database import connect_db, disconnect_db
import os
import logging
from app.core.storage import storage_service

logger = logging.getLogger(__name__)

# Custom middleware to handle large file uploads
class LargeFileUploadMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Set content length limit for large uploads
        content_length = request.headers.get("content-length")
        if content_length:
            content_length = int(content_length)
            max_size = 10 * 1024 * 1024 * 1024  # 10GB
            if content_length > max_size:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=413,
                    detail=f"Request entity too large. Maximum size is {max_size // (1024*1024*1024)}GB"
                )
        
        response = await call_next(request)
        return response

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.order_center_worker import order_center_worker
    from app.services.service_cache_task import service_cache_task
    from app.services.email_watcher import email_watcher
    from app.services.system_watcher import system_watcher
    from app.api.ai_chat import start_download_cleanup_task
    await order_center_worker.start()
    await service_cache_task.start()
    await email_watcher.start_all_watchers()
    await system_watcher.start()
    start_download_cleanup_task()
    logger.info("Order Center, Service Cache, Email Watchers, System Watcher, and AI Cleanup Task started")
    yield
    await order_center_worker.stop()
    await service_cache_task.stop()
    await email_watcher.stop_all_watchers()
    await system_watcher.stop()
    logger.info("Order Center, Service Cache, Email Watchers, and System Watcher stopped")

# Create FastAPI app with custom middleware
app = FastAPI(
    title="DHQ Backend", 
    version="1.0.0",
    lifespan=lifespan
)

# Add custom middleware first
app.add_middleware(LargeFileUploadMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://localhost:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3000",
        "https://haku.io.vn",
        "http://haku.io.vn"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
connect_db()

if os.path.exists("frontend/dist"):
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

# Mount uploads directory for avatars and banners from external storage if possible
primary_storage = storage_service.storages[0]
avatar_dir = os.path.join(primary_storage, "avatars")
banner_dir = os.path.join(primary_storage, "banners")
os.makedirs(avatar_dir, exist_ok=True)
os.makedirs(banner_dir, exist_ok=True)

app.mount("/api/uploads/avatars", StaticFiles(directory=avatar_dir), name="avatars")
app.mount("/api/uploads/banners", StaticFiles(directory=banner_dir), name="banners")

@app.get("/", response_class=HTMLResponse)
async def decoy_landing():
    """Decoy landing page - innocent lifestyle blog"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>My Creative Journey</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .post { border-bottom: 1px solid #eee; padding: 20px 0; }
            .post h2 { color: #333; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>My Creative Journey</h1>
            <p>Welcome to my personal blog about creativity and growth.</p>
        </div>
        <div class="post">
            <h2>Coming Soon!</h2>
            <p>This website is currently under construction. Check back soon for amazing content!</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# @app.get(settings.REAL_LOGIN_ROUTE, response_class=HTMLResponse, include_in_schema=False)
# async def login_page():
#     return """
#     <html>
#         <head><title>DHQ Login</title></head>
#         <body style="background: #0f172a; color: white; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0;">
#             <div style="background: #1e293b; padding: 2rem; border-radius: 1rem; border: 1px solid #334155; width: 300px;">
#                 <h2 style="margin-top: 0;">DHQ Backend</h2>
#                 <p>Frontend is not reachable. This is the backend fallback login.</p>
#                 <form action="/shadow-garden/login" method="post">
#                     <div style="margin-bottom: 1rem;">
#                         <label>Username</label><br>
#                         <input name="username" style="width: 100%; padding: 0.5rem; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 0.25rem;">
#                     </div>
#                     <div style="margin-bottom: 1rem;">
#                         <label>Password</label><br>
#                         <input name="password" type="password" style="width: 100%; padding: 0.5rem; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 0.25rem;">
#                     </div>
#                     <button type="submit" style="width: 100%; padding: 0.75rem; background: #3b82f6; border: none; color: white; border-radius: 0.25rem; font-weight: bold; cursor: pointer;">Sign In</button>
#                 </form>
#             </div>
#         </body>
#     </html>
#     """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DHQ Backend"}

# Import and include routers
from app.api import auth, admin, hub, arcade, gifts, gifts_management, activity, monitoring, user_management, ordering, ordering_enhanced, organic_ordering, smart_collaboration, kpi_bonus, drive, test_api, gcode_generator, economy, order_center, mock_api, email_hub, prompt_api, virus_scan, ai_chat, system_config, vault_api, public_api
# Standard API routes
app.include_router(vault_api.router, prefix="/api", tags=["vault"])
app.include_router(virus_scan.router, prefix="/api/scan", tags=["virus-scan"])
from app.api.games import wordle, typing, memory, tictactoe, bovo, blackjack, bigtwo, common
from app.api import api_management

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(hub.router, prefix="/api/hub", tags=["hub"])
app.include_router(arcade.router, prefix="/api/arcade", tags=["arcade"])
app.include_router(economy.router, prefix="/api/economy", tags=["economy"])
app.include_router(gifts.router, prefix="/api/gifts", tags=["gifts"])
app.include_router(gifts_management.router, prefix="/api/gifts/manage", tags=["gifts-manage"])
app.include_router(activity.router, prefix="/api/activity", tags=["activity"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(user_management.router, prefix="/api/user", tags=["user-management"])
app.include_router(ordering.router, prefix="/api/ordering", tags=["ordering"])
app.include_router(ordering_enhanced.router, prefix="/api/ordering-enhanced", tags=["ordering-enhanced"])
app.include_router(order_center.router, prefix="/api/order-center", tags=["order-center"])
app.include_router(mock_api.router, prefix="/api/mock-api", tags=["mock-api"])
app.include_router(email_hub.router, prefix="/api/emails", tags=["Emails"])
app.include_router(prompt_api.router, prefix="/api/prompts", tags=["Prompts"])
app.include_router(ai_chat.router, prefix="/api/ai", tags=["ai-chat"])
app.include_router(system_config.router, prefix="/api/system", tags=["system-config"])

# Game routes
app.include_router(wordle.router, prefix="/api/games/wordle", tags=["games-wordle"])
app.include_router(typing.router, prefix="/api/games/typing", tags=["games-typing"])
app.include_router(memory.router, prefix="/api/games/memory", tags=["games-memory"])
app.include_router(tictactoe.router, prefix="/api/games/tictactoe", tags=["games-tictactoe"])
app.include_router(bovo.router, prefix="/api/games/bovo", tags=["games-bovo"])
app.include_router(blackjack.router, prefix="/api/games/blackjack", tags=["games-blackjack"])
app.include_router(bigtwo.router, prefix="/api/games/bigtwo", tags=["games-bigtwo"])
app.include_router(common.router, prefix="/api/games", tags=["games-common"])

app.include_router(organic_ordering.router, prefix="/api/organic-ordering", tags=["organic-ordering"])
app.include_router(smart_collaboration.router, prefix="/api/collaboration", tags=["collaboration"])
app.include_router(kpi_bonus.router, prefix="/api/kpi-bonus", tags=["kpi-bonus"])
app.include_router(api_management.router, prefix="/api/api-management", tags=["api-management"])
app.include_router(drive.router, prefix="/api", tags=["drive"])
app.include_router(test_api.router, prefix="/api", tags=["test-api"])
app.include_router(gcode_generator.router, prefix="/api", tags=["gcode-generator"])
app.include_router(public_api.router, prefix="/api", tags=["public"])

# Hidden routes (obfuscated)
app.include_router(auth.router, prefix=settings.REAL_LOGIN_ROUTE.replace("/login", ""), tags=["hidden-auth"])
app.include_router(auth.router, prefix=settings.REAL_REGISTER_ROUTE.replace("/apply", ""), tags=["hidden-register"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
