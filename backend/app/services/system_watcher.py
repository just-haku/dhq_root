import asyncio
import logging
from datetime import datetime
from app.models.system import SystemConfig
from app.models.user import User
from app.api.monitoring import get_ups_status
from app.socketio_server import sio
from app.services.email_service import email_service

logger = logging.getLogger(__name__)

class SystemWatcher:
    def __init__(self):
        self.is_running = False
        self._task = None
        self.last_known_state = "Normal"
        
    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._watch_loop())
        logger.info("System Watcher started")
        
    async def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("System Watcher stopped")
        
    async def _watch_loop(self):
        # Allow system to start up before checking
        await asyncio.sleep(10)
        
        while self.is_running:
            try:
                await self._check_ups_status()
            except Exception as e:
                logger.error(f"Error in System Watcher loop: {str(e)}")
            
            # Poll every 60 seconds
            await asyncio.sleep(60)
            
    async def _check_ups_status(self):
        ups_data = get_ups_status()
        
        if ups_data.get("status") != "Connected":
            # UPS could be disconnected, we just ignore for now or handle it
            return
            
        current_state = ups_data.get("state", "Normal")
        
        # If state drastically changed from Normal to something else (e.g. Power Failure)
        if current_state != "Normal" and self.last_known_state == "Normal":
            logger.warning(f"UPS Status changed to {current_state}! Enabling Power Saver Mode.")
            await self._trigger_power_saver(True, current_state)
            
        # If state restored to Normal
        elif current_state == "Normal" and self.last_known_state != "Normal":
            logger.info("UPS Status restored to Normal! Disabling Power Saver Mode.")
            await self._trigger_power_saver(False, current_state)
            
        self.last_known_state = current_state
        
    async def _trigger_power_saver(self, enable: bool, reason: str):
        config = SystemConfig.get_config()
        new_mode = "power_saver" if enable else "normal"
        
        if config.power_mode != new_mode:
            config.power_mode = new_mode
            config.last_updated = datetime.utcnow()
            config.save()
            
            # Broadcast to all connected clients
            await sio.emit('power_mode_changed', {'mode': new_mode, 'reason': reason})
            
            # Email Operators
            ops = User.objects(role="OP")
            for op in ops:
                if op.email:
                    subject = "🚨 DHQ System Alert: Power Issue Detected" if enable else "✅ DHQ System Alert: Power Restored"
                    
                    if enable:
                        html_content = f"""
                        <html>
                          <body style="font-family: Arial, sans-serif; color: #333;">
                            <h2 style="color: #ef4444;">Power Issue Detected</h2>
                            <p>Boss, we're having a power issue. We'll tell you when it gets better.</p>
                            <p><strong>UPS State:</strong> {reason}</p>
                            <p>The system has automatically entered <strong>Power Saver</strong> mode. Heavy background tasks and specific features like Drive uploads and High-end LLMs have been restricted.</p>
                            <hr>
                            <small>Sent automatically by DHQ System Monitor.</small>
                          </body>
                        </html>
                        """
                    else:
                        html_content = f"""
                        <html>
                          <body style="font-family: Arial, sans-serif; color: #333;">
                            <h2 style="color: #10b981;">Power Restored</h2>
                            <p>Boss, the power is back to normal! All systems are functioning optimally.</p>
                            <p><strong>UPS State:</strong> {reason}</p>
                            <p>The system has returned to <strong>Normal</strong> mode. All features are fully operational.</p>
                            <hr>
                            <small>Sent automatically by DHQ System Monitor.</small>
                          </body>
                        </html>
                        """
                    
                    self._send_async_email(op.email, subject, html_content)
                    
    def _send_async_email(self, email: str, subject: str, content: str):
        # Fire and forget in asyncio event loop
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, email_service.send_system_alert, email, subject, content)

system_watcher = SystemWatcher()
