import httpx
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from app.core.database import redis_client
from app.models.test_api import TestAPIConfig

logger = logging.getLogger(__name__)

class ExternalAPIService:
    """Service for interacting with the external SMM API"""
    
    BASE_URL = "https://tangtuongtacre.com/api/v2"
    API_LOCK_KEY = "api_lock"
    API_LOCK_DURATION = 10  # 10 seconds cooldown
    BALANCE_CACHE_KEY = "api_balance"
    BALANCE_CACHE_DURATION = 60  # 1 minute cache
    
    @staticmethod
    async def add_order(
        api_key: str,
        service_id: str,
        link: str,
        quantity: int,
        user_id: str = None,
        api_server_id: str = None
    ) -> Tuple[bool, Dict]:
        """
        Add an order to external API
        First checks if test API interception is enabled
        Then checks if user has configured API servers and keys
        
        Returns:
            Tuple of (success, response_data)
        """
        
        # Check if test API interception is enabled
        test_config = TestAPIConfig.objects(is_enabled=True, intercept_growth_orders=True).first()
        if test_config:
            logger.info(f"Intercepting order with test API: {test_config.name}")
            return await ExternalAPIService._execute_test_order(
                test_config, service_id, link, quantity
            )
        
        # Determine API Key and Server URL
        final_api_key = api_key
        final_base_url = ExternalAPIService.BASE_URL
        
        # Check if explicit API server is requested
        if api_server_id:
            from app.models.api_server import APIServer, UserAPIKey
            import re
            
            if re.match(r"^[0-9a-fA-F]{24}$", str(api_server_id)):
                server = APIServer.objects(id=api_server_id).first()
                if server and server.is_active:
                    final_base_url = server.base_url
                    logger.info(f"Using requested API server: {server.display_name}")
                    
                    # Try to find a specific key for this user/server combo
                    if user_id:
                        user_key = UserAPIKey.objects(user_id=str(user_id), api_server_id=str(api_server_id), is_active=True).first()
                        if user_key:
                            final_api_key = user_key.api_key
                            logger.info(f"Found personal API key for server {server.display_name}")
                        elif server.api_key:
                            final_api_key = server.api_key
                            logger.info(f"Using system fallback key for server {server.display_name}")
            else:
                logger.warning(f"Invalid api_server_id: {api_server_id}")

        # Execute order
        return await ExternalAPIService._execute_order(
            final_base_url,
            final_api_key,
            service_id,
            link,
            quantity
        )
    
    @staticmethod
    async def _execute_order(
        base_url: str,
        api_key: str,
        service_id: str,
        link: str,
        quantity: int
    ) -> Tuple[bool, Dict]:
        """Execute order on specified API server"""
        
        # Check API lock
        if await ExternalAPIService._is_api_locked():
            return False, {"error": "API rate limit in effect"}
        
        # Acquire API lock
        await ExternalAPIService._set_api_lock()
        
        try:
            # INTERCEPT INTERNAL SERVER: If base_url is local or server_id matches internal_api_server
            # For now, we rely on the server_id being passed or checking the base_url
            if "localhost:8000/api" in base_url or "internal_api_server" in base_url:
                logger.info("Internal API Server request - bypassing external call")
                # For Internal Server, the key is a generated Personal API Token.
                # We can perform a local validation here if needed, but for 'add' order, 
                # let's just return a successful mock response for now as requested.
                return True, {"order": 12345, "status": "Internal Success"}

            payload = {
                "key": api_key,
                "action": "add",
                "service": service_id,
                "link": link,
                "quantity": quantity
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{base_url.rstrip('/')}/api/v2" if "api/v2" not in base_url else base_url,
                    data=payload
                )
                
                response_data = response.json()
                
                # Check if response contains an error, even with 200 status
                if isinstance(response_data, dict) and 'error' in response_data:
                    logger.error(f"Order addition failed: API returned error - {response_data}")
                    return False, response_data
                
                if response.status_code == 200:
                    logger.info(f"Order added successfully: {response_data}")
                    return True, response_data
                else:
                    logger.error(f"Order addition failed: {response.status_code} - {response_data}")
                    return False, response_data
                    
        except httpx.TimeoutException as e:
            logger.error(f"API timeout during order addition: {e}")
            return False, {"error": "API timeout - the remote server took too long to respond"}
        except httpx.RequestError as e:
            logger.error(f"Request error during order addition: {e}")
            return False, {"error": f"Request error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error during order addition: {e}")
            return False, {"error": f"Unexpected error: {str(e)}"}
        finally:
            # Release API lock after delay
            await asyncio.sleep(1)  # Small delay before releasing
            await ExternalAPIService._release_api_lock()
    
    @staticmethod
    async def check_order_status(
        api_key: str,
        order_id: str,
        api_server_id: str = None
    ) -> Tuple[bool, Dict]:
        """
        Check the status of an order
        """
        base_url = ExternalAPIService.BASE_URL
        if api_server_id:
            from app.models.api_server import APIServer
            server = APIServer.objects(id=api_server_id).first()
            if server:
                base_url = server.base_url
        
        # INTERCEPT INTERNAL SERVER
        if "localhost:8000/api" in base_url or "internal_api_server" in base_url:
            return True, {"status": "Completed", "charge": "0.00", "remains": "0"}
        
        # Check API lock
        if await ExternalAPIService._is_api_locked():
            return False, {"error": "API rate limit in effect"}
        
        # Acquire API lock
        await ExternalAPIService._set_api_lock()
        
        try:
            payload = {
                "key": api_key,
                "action": "status",
                "order": order_id
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{base_url.rstrip('/')}/api/v2",
                    data=payload
                )
                
                response_data = response.json()
                
                if response.status_code == 200:
                    logger.info(f"Order status retrieved: {order_id} - {response_data}")
                    return True, response_data
                else:
                    logger.error(f"Order status check failed: {response.status_code} - {response_data}")
                    return False, response_data
                    
        except httpx.TimeoutException as e:
            logger.error(f"Timeout checking order status: {e}")
            return False, {"error": "API timeout"}
        except httpx.RequestError as e:
            logger.error(f"Request error checking order status: {e}")
            return False, {"error": f"Request error"}
        except Exception as e:
            logger.error(f"Error checking order status: {e}")
            return False, {"error": str(e)}
        finally:
            await asyncio.sleep(1)
            await ExternalAPIService._release_api_lock()
    
    @staticmethod
    async def check_balance(api_key: str, api_server_id: str = None) -> Tuple[bool, Dict]:
        """
        Check API balance
        """
        base_url = ExternalAPIService.BASE_URL
        cache_key = ExternalAPIService.BALANCE_CACHE_KEY
        
        try:
            # Clean server_id
            if api_server_id in [None, "", "null", "undefined"]:
                api_server_id = None
                
            if api_server_id:
                from app.models.api_server import APIServer
                import re
                
                # Verify if it's a valid ObjectId string using regex to avoid bson dependency
                if not re.match(r"^[0-9a-fA-F]{24}$", str(api_server_id)):
                    logger.warning(f"Invalid server_id format: {api_server_id}, using default")
                    api_server_id = None
                else:
                    server = APIServer.objects(id=api_server_id).first()
                    if server:
                        base_url = server.base_url
                        cache_key = f"{ExternalAPIService.BALANCE_CACHE_KEY}:{api_server_id}"
            
            # Check cache first
            if redis_client:
                try:
                    cached_data = await redis_client.get(cache_key)
                    if cached_data:
                        return True, json.loads(cached_data)
                except Exception as redis_err:
                    logger.warning(f"Redis cache error in check_balance: {redis_err}")
            
            # Check API lock
            if await ExternalAPIService._is_api_locked():
                return False, {"balance": "0.00", "currency": "USD", "error": "API rate limit in effect"}
            
            # Acquire API lock
            await ExternalAPIService._set_api_lock()
            
            # INTERCEPT INTERNAL SERVER
            if "localhost:8000/api" in base_url or "internal_api_server" in base_url:
                # Return a dummy balance for internal server or implement real credit logic
                return True, {"balance": "1000.00", "currency": "USD"}

            payload = {
                "key": api_key,
                "action": "balance"
            }
            
            async with httpx.AsyncClient(timeout=45.0) as client: # Generous timeout for balance check
                response = await client.post(
                    f"{base_url.rstrip('/')}/api/v2",
                    data=payload
                )
                
                # Check for empty or non-JSON responses
                try:
                    response_data = response.json()
                except Exception:
                    response_data = {"error": f"Invalid response from API (Status {response.status_code})"}
                    return False, response_data
                
                if response.status_code == 200:
                    logger.info(f"Balance retrieved: {response_data}")
                    # Cache the balance for 5 minutes
                    if redis_client:
                        try:
                            await redis_client.set(cache_key, json.dumps(response_data), ex=300)
                        except Exception: pass
                    return True, response_data
                else:
                    logger.error(f"Balance check failed: {response.status_code} - {response_data}")
                    return False, response_data
                    
        except httpx.TimeoutException as e:
            logger.error(f"Timeout checking balance: {e}")
            return False, {"balance": "0.00", "currency": "USD", "error": "API timeout"}
        except httpx.RequestError as e:
            logger.error(f"Request error checking balance: {e}")
            return False, {"balance": "0.00", "currency": "USD", "error": f"Request error"}
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
            return False, {"balance": "0.00", "currency": "USD", "error": f"Service error: {str(e)}"}
        finally:
            # Release API lock after delay
            await asyncio.sleep(0.5)
            try:
                await ExternalAPIService._release_api_lock()
            except Exception:
                pass
    
    @staticmethod
    async def _is_api_locked() -> bool:
        """Check if API is currently locked"""
        try:
            if redis_client is None:
                logger.warning("Redis client not available, API lock disabled")
                return False
            
            lock_value = await redis_client.get(ExternalAPIService.API_LOCK_KEY)
            return lock_value is not None
        except Exception as e:
            logger.error(f"Error checking API lock: {e}")
            return False
    
    @staticmethod
    async def _set_api_lock():
        """Set API lock"""
        try:
            if redis_client is None:
                logger.warning("Redis client not available, API lock disabled")
                return
            
            await redis_client.set(
                ExternalAPIService.API_LOCK_KEY,
                "locked",
                ex=ExternalAPIService.API_LOCK_DURATION
            )
        except Exception as e:
            logger.error(f"Error setting API lock: {e}")
    
    @staticmethod
    async def _release_api_lock():
        """Release API lock"""
        try:
            if redis_client is None:
                logger.warning("Redis client not available, API lock disabled")
                return
            
            await redis_client.delete(ExternalAPIService.API_LOCK_KEY)
        except Exception as e:
            logger.error(f"Error releasing API lock: {e}")
    
    @staticmethod
    async def _get_cached_balance() -> Optional[Dict]:
        """Get cached balance"""
        try:
            cached_data = await redis_client.get(ExternalAPIService.BALANCE_CACHE_KEY)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting cached balance: {e}")
        return None
    
    @staticmethod
    async def _set_cached_balance(balance_data: Dict):
        """Set cached balance"""
        try:
            await redis_client.set(
                ExternalAPIService.BALANCE_CACHE_KEY,
                json.dumps(balance_data),
                ex=ExternalAPIService.BALANCE_CACHE_DURATION
            )
        except Exception as e:
            logger.error(f"Error setting cached balance: {e}")
    
    @staticmethod
    def is_network_error(error_data: Dict) -> bool:
        """Determine if an error is a network error (retryable)"""
        error_msg = error_data.get("error", "").lower()
        
        network_error_indicators = [
            "timeout",
            "connection",
            "network",
            "502",
            "503",
            "504",
            "unreachable"
        ]
        
        return any(indicator in error_msg for indicator in network_error_indicators)
    
    @staticmethod
    def is_fatal_error(error_data: Dict) -> bool:
        """Determine if an error is fatal (not retryable)"""
        error_msg = error_data.get("error", "").lower()
        
        fatal_error_indicators = [
            "invalid",
            "authentication",
            "forbidden",
            "not found",
            "duplicate",
            "insufficient"
        ]
        
        return any(indicator in error_msg for indicator in fatal_error_indicators)
    
    @staticmethod
    async def _execute_test_order(
        test_config: TestAPIConfig,
        service_id: str,
        link: str,
        quantity: int
    ) -> Tuple[bool, Dict]:
        """Execute order via test API endpoint"""
        try:
            # Simulate API delay
            if test_config.response_delay_ms > 0:
                await asyncio.sleep(test_config.response_delay_ms / 1000)
            
            # Simulate random failures
            import random
            if test_config.failure_rate_percent > 0:
                if random.randint(1, 100) <= test_config.failure_rate_percent:
                    logger.warning(f"Test API simulated failure for order")
                    return False, test_config.error_response
            
            # Use the success response template
            response_data = test_config.success_response.copy()
            if "order" in response_data:
                # Generate a random order ID for testing
                response_data["order"] = random.randint(100000, 999999)
            
            # Log the test API call if enabled
            if test_config.log_requests:
                from app.models.test_api import APILog
                log_entry = APILog(
                    endpoint_name=test_config.name,
                    method="POST",
                    url="/api/test-api",
                    request_body={
                        "action": "add",
                        "service_id": service_id,
                        "link": link,
                        "quantity": quantity
                    },
                    response_status=200,
                    response_body=response_data,
                    response_timestamp=datetime.utcnow(),
                    duration_ms=test_config.response_delay_ms,
                    is_test_mode=True,
                    mock_response_used=test_config.mock_responses
                )
                log_entry.save()
            
            logger.info(f"Test API order executed successfully: {response_data}")
            return True, response_data
            
        except Exception as e:
            logger.error(f"Error in test API execution: {e}")
            return False, {"error": f"Test API execution failed: {str(e)}"}
