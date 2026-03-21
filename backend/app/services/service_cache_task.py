import asyncio
import logging
import json
from datetime import datetime
from app.core.database import redis_client
from app.models.api_server import APIServer
from app.services.external_api import ExternalAPIService
import httpx

logger = logging.getLogger(__name__)

class ServiceCacheTask:
    def __init__(self):
        self.running = False
        self._task = None
        self.cache_key = "external_api_services_cache"

    async def start(self):
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._cache_loop())
        logger.info("Service Cache Task started")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
        logger.info("Service Cache Task stopped")

    async def _cache_loop(self):
        while self.running:
            try:
                await self.refresh_cache()
                # Sleep for 24 hours
                await asyncio.sleep(24 * 3600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in Service Cache Task: {e}")
                await asyncio.sleep(300) # Retry in 5m on error

    async def refresh_cache(self):
        """Fetch services from all active external APIs and cache them"""
        logger.info("Refreshing external API services cache...")
        
        # In this simplified version, we'll fetch from the default external API 
        # or all active servers marked as external.
        external_servers = APIServer.objects(is_external=True, is_active=True)
        
        all_services = []
        
        for server in external_servers:
            try:
                # We need an API key. For global caching, we might use a system key or OP's key.
                # Since we don't have a clean 'system key', let's just use the mock if enabled or skip auth for services if allowed.
                # SMM panels usually require 'key' even for services list.
                
                payload = {
                    "key": server.api_key or "SYSTEM_CACHE_KEY",
                    "action": "services"
                }
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post( # Adding explicit timeout to avoid SMM scraping hangs
                        f"{server.base_url.rstrip('/')}/api/v2",
                        data=payload
                    )
                    if response.status_code == 200:
                        data = response.json()
                        # Handle both direct list and {"services": [...]} formats
                        if isinstance(data, list):
                            services = data
                        elif isinstance(data, dict):
                            services = data.get("services", [])
                        else:
                            logger.warning(f"Unexpected response format from {server.display_name}: {type(data)}")
                            continue
                            
                        # Add server info to each service for frontend grouping
                        for s in services:
                            s["server_id"] = str(server.id)
                            s["server_name"] = server.display_name
                        all_services.extend(services)
            except httpx.TimeoutException as e:
                logger.error(f"Timeout while fetching services from {server.display_name}: {e}")
            except httpx.RequestError as e:
                logger.error(f"Request error fetching services from {server.display_name}: {e}")
            except Exception as e:
                logger.error(f"Failed to fetch services from {server.display_name}: {e}")

        if all_services:
            await redis_client.set(self.cache_key, json.dumps(all_services))
            await redis_client.set(f"{self.cache_key}:updated_at", datetime.utcnow().isoformat())
            logger.info(f"Cached {len(all_services)} services")

    async def get_balance(self, api_server_id: str = None):
        """Get balance for a server with read-through cache logic"""
        # Multi-server support: ExternalAPIService.check_balance handles internal cache
        # We need an API key. For operators, we'll try to find an active key.
        # However, for simplicity and as per instructions, we often use the mock or a system key.
        # Here we'll just proxy to ExternalAPIService.check_balance with a placeholder key
        # in a real system, we'd fetch the User's API key for that server.
        from app.models.api_server import UserAPIKey
        
        # In this context, we might not have a user_id easily. 
        # For the Order Creation page, the frontend will call an endpoint that provides user context.
        # So I'll move some logic to the API endpoint itself.
        pass

    async def get_cached_services(self, force_refresh: bool = False):
        """Get cached services, optionally checking for 24h expiration"""
        updated_at_str = await redis_client.get(f"{self.cache_key}:updated_at")
        
        should_refresh = force_refresh
        if not updated_at_str:
            should_refresh = True
        else:
            updated_at = datetime.fromisoformat(updated_at_str.decode())
            if (datetime.utcnow() - updated_at).total_seconds() > 24 * 3600:
                should_refresh = True
        
        if should_refresh:
            await self.refresh_cache()
            
        cached = await redis_client.get(self.cache_key)
        if cached:
            return json.loads(cached)
        return []

# Global instance
service_cache_task = ServiceCacheTask()
