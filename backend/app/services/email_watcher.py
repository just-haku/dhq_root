import asyncio
import logging
import ssl
from aioimaplib import aioimaplib
from app.models.user import User
from app.services.email_service import email_service
from app.services.ai_pipeline_service import ai_pipeline

logger = logging.getLogger(__name__)

class EmailWatcherService:
    def __init__(self):
        self.watchers = {}  # {username: Task}
        self.running = False

    async def start_all_watchers(self):
        """Scan all users and start watchers for those with credentials"""
        self.running = True
        logger.info("Initializing Email Watchers for all users...")
        # Get all users who have email credentials
        users = User.objects()
        for user in users:
            if user.email_creds and user.email_creds.get('email') and user.email_creds.get('password'):
                self.start_user_watcher(user)

    def start_user_watcher(self, user: User):
        """Start or restart a watcher task for a specific user"""
        if user.username in self.watchers:
            self.watchers[user.username].cancel()
            logger.info(f"Restarting watcher for {user.username}")
        
        task = asyncio.create_task(self._watcher_loop(user))
        self.watchers[user.username] = task
        logger.info(f"Started real-time Email IDLE watcher for {user.username}")

    async def stop_all_watchers(self):
        self.running = False
        for username, task in self.watchers.items():
            task.cancel()
        logger.info("Stopped all email watchers.")

    async def _watcher_loop(self, user: User):
        """The main IDLE loop for a single user"""
        username = user.username
        while self.running:
            client = None
            try:
                imap_host = "imap.gmail.com"
                imap_port = 993
                email_addr = user.email_creds['email']
                password = user.email_creds['password']

                client = aioimaplib.IMAP4_SSL(host=imap_host, port=imap_port)
                await client.wait_hello_from_server()
                
                # Login
                login_resp = await client.login(email_addr, password)
                if login_resp.result != 'OK':
                    logger.error(f"Watcher Login failed for {username}: {login_resp}")
                    await asyncio.sleep(300) # Wait 5 mins on auth error
                    continue

                await client.select("INBOX")
                logger.info(f"IMAP IDLE: Connection established for {username}")

                while self.running:
                    # Start IDLE mode
                    idle_task = await client.idle_start()
                    
                    # Heartbeat Logic: Re-login/Noop every 20 minutes to prevent timeout
                    # or wait for server push (new mail)
                    try:
                        # Wait for either a server push (new message) or a 20-minute timeout
                        done, pending = await asyncio.wait(
                            [client.wait_server_push(), asyncio.sleep(1200)],
                            return_when=asyncio.FIRST_COMPLETED
                        )
                        
                        for p in pending:
                            p.cancel()

                        # Stop IDLE to allow processing or heartbeat
                        client.idle_done()
                        await idle_task
                        
                        # Check for new signals
                        # If a push was received, it usually means 'EXISTS' or 'RECENT'
                        # We'll trigger the standard fetch logic
                        logger.info(f"IMAP IDLE: Signal received or heartbeat for {username}")
                        
                        # Trigger fetch logic (this also checks for duplicates in DB)
                        new_emails = email_service.fetch_emails(user, limit=5)
                        if new_emails:
                            logger.info(f"IMAP IDLE: Found {len(new_emails)} new emails for {username}")
                            for em in new_emails:
                                # Run AI classification
                                await ai_pipeline.process_email(user, em)
                        
                    except Exception as loop_error:
                        logger.error(f"IDLE internal loop error for {username}: {str(loop_error)}")
                        break # Reconnect

            except asyncio.CancelledError:
                logger.info(f"Watcher for {username} was cancelled.")
                break
            except Exception as e:
                logger.error(f"Watcher connection failed for {username}: {str(e)}")
                # Reconnection delay (internet flicker handling)
                await asyncio.sleep(60)
            finally:
                if client:
                    try:
                        await client.logout()
                    except:
                        pass

email_watcher = EmailWatcherService()
