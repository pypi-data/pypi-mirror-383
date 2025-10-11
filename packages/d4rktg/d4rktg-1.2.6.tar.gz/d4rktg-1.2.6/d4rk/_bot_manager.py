"""
Bot Manager for d4rk package - Handles single or multiple bot instances using TGBase
"""

import sys
import time
import signal
import asyncio
import threading

from typing import List
from datetime import datetime
from pyrogram.errors import FloodWait

from d4rk._base import TGBase
from d4rk.Web import WebServerManager
from d4rk.Handlers import LoggerBotUtil
from d4rk.Logs import setup_logger, get_timezone_offset

logger = setup_logger("D4RK_BotManager")

online_bots = {} 
flood_waited_bots = {} 
startup_message_id = None
startup_message_chat_id = None


class D4RK_BotManager:
    def __init__(self, 
                 app_name: str = None,
                 api_id: int = None,
                 api_hash: str = None, 
                 tokens: List[str] = None,
                 max_bots_count: int = 4,
                 plugins: dict = None,
                 database_url: str = None,
                 database = None,
                 log_chat_id: int = None,
                 owner_id: int = None,
                 web_app_url: str = None,
                 web_server = None,
                 rename: bool = False,
                 logger_bot_token: str = None,
                 time_zone: str = "+5:30",
                 ) -> None:
        """
        Initialize the D4RK Bot Manager
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API Hash
            tokens: List of bot tokens to use for running bots
            max_bots_count: Maximum number of bots to run concurrently
            app_name: Application name
            plugins: Plugin configuration
            database_url: Database connection URL
            log_chat_id: Chat ID for logging
            owner_id: Owner user ID
            web_app_url: Web application URL
            rename: Whether to enable renaming functionality
            logger_bot_token: Token for the logger bot (uses python-telegram-bot library)
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.tokens = tokens or []
        self.max_bots_count = max_bots_count
        self.app_name = app_name
        self.plugins = plugins
        self.max_concurrent_bots = min(max_bots_count, len(self.tokens))
        self.database_url = database_url
        self.database = database
        self.log_chat_id = log_chat_id
        self.owner_id = owner_id
        self.web_app_url = web_app_url
        self._rename = rename
        self.logger_bot_token = logger_bot_token
        
        self.logger_bot_util = None
        if self.logger_bot_token:
            self.logger_bot_util = LoggerBotUtil()
            self.logger_bot_util.set_token(self.logger_bot_token)
        
        # Additional setup
        self.TIME_ZONE = time_zone
        self.TZ = get_timezone_offset(self.TIME_ZONE)
        self.TZ_now = datetime.now(self.TZ)
        self._stop_event = threading.Event()
        
        # Bot management
        self.bot_instances = []  # Store multiple bot instances
        self.bot_instances_copy = []  # Copy for shutdown message
        # Filter out logger bot token from available tokens
        self.available_tokens = [t for t in self.tokens if t != self.logger_bot_token] if self.logger_bot_token else self.tokens.copy()
        self.flood_waited_tokens = {}  # {token: wait_until_timestamp}
        self._running = False
        self._shutdown_initiated = False
        self._bot_counter = 0
        self._main_loop = None
        self.LOGS = self.log_chat_id
        self.web_server_manager = web_server or  WebServerManager(self)
        self._web_runner = None

    def run_bots(self):
        """
        Run multiple bots with max bot count and send status updates through logger bot.
        First sends a message that logger bot started, then edits it with bot startup info.
        """
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Create and run event loop
        try:
            self._main_loop = asyncio.get_event_loop()
        except RuntimeError:
            self._main_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._main_loop)
        
        try:
            self._main_loop.run_until_complete(self._run_async())
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping bots...")
            self._main_loop.run_until_complete(self.stop_all_bots())

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, stopping bots...")
        # Just set the stop event and let the main loop handle the shutdown
        self._running = False
        self._stop_event.set()
        logger.info("Shutdown process initiated")
        
        # If we're in the main thread, don't exit immediately
        # Let the main loop handle the shutdown
        if threading.current_thread() is threading.main_thread():
            # Don't exit immediately, let the main loop handle the shutdown
            pass
        else:
            # If called from another thread, we can exit
            sys.exit(0)

    async def _run_async(self):
        """Internal async method to run multiple bots with max bot count"""
        global startup_message_id, startup_message_chat_id
        self._running = True
            
        # Initialize database once
        await self._initialize_database()
        
        # Setup web server
        await self._setup_webserver()
        
        # Send initial logger bot startup message
        await self._send_logger_startup_message()
        
        # Start multiple bot instances with token rotation on flood wait
        bots_to_start = min(self.max_bots_count, len(self.available_tokens))
        started_bots = 0
        attempts = 0
        max_attempts = 50  # Prevent infinite loop
        
        while started_bots < bots_to_start and attempts < max_attempts and (self.available_tokens or self.flood_waited_tokens):
            attempts += 1
            
            # Check if we have available tokens
            if self.available_tokens:
                token = self.available_tokens.pop(0)
                success = await self._start_bot_instance(token)
                if success:
                    started_bots += 1
                else:
                    # If the bot failed to start, we need to decrement the bot counter
                    # since we incremented it in _start_bot_instance but the bot didn't start
                    if self._bot_counter > 0:
                        self._bot_counter -= 1
            else:
                # No available tokens, check if any flood wait tokens have expired
                current_time = time.time()
                expired_tokens = []
                for token, wait_until in self.flood_waited_tokens.items():
                    if current_time >= wait_until:
                        expired_tokens.append(token)
                
                # Move expired tokens back to available pool
                for token in expired_tokens:
                    del self.flood_waited_tokens[token]
                    self.available_tokens.append(token)
                    logger.info(f"Token {token[:10]}... is no longer flood waited")
                
                # If we moved some tokens back, continue the loop
                if expired_tokens:
                    continue
                    
                # Check if we have other tokens in the original tokens list that are not in flood wait
                # This implements actual token rotation
                for token in self.tokens:
                    if token not in self.flood_waited_tokens and token not in self.available_tokens:
                        # Check if this token is already being used by a running bot
                        token_in_use = False
                        for bot_instance in self.bot_instances:
                            if bot_instance.token == token:
                                token_in_use = True
                                break
                        if not token_in_use:
                            self.available_tokens.append(token)
                            logger.info(f"Added fresh token {token[:10]}... for rotation")
                            break
                
                # If we still don't have available tokens, wait a bit
                if not self.available_tokens:
                    logger.info("No available tokens, waiting for flood wait expiration or new tokens...")
                    await asyncio.sleep(10)
        
        logger.info(f"Attempted to start bots, {len(self.bot_instances)} bot instances successfully started")
        
        # Update startup message with online bots
        await self._update_startup_message_with_online_bots()
        
        # Monitor and manage bots
        try:
            while self._running and not self._stop_event.is_set():
                await self._manage_bots()
                await asyncio.sleep(5)  # Check every 5 seconds
        except Exception as e:
            logger.error(f"Error in bot management: {e}")
        finally:
            await self.stop_all_bots()

    async def _initialize_database(self):
        """Initialize database connection"""
        try:
            self.database.connect(name=self.app_name, DATABASE_URL=self.database_url)
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    async def _setup_webserver(self):
        """Setup web server"""
        try:
            self._web_runner = await self.web_server_manager.setup_web_server(8443)
        except Exception as e:
            logger.error(f"Failed to setup web server: {e}")

    async def _manage_bots(self):
        """Manage bots, handle flood waits, and token rotation"""
        current_time = time.time()
        
        # Check for expired flood waits
        expired_tokens = []
        for token, wait_until in self.flood_waited_tokens.items():
            if current_time >= wait_until:
                expired_tokens.append(token)
        
        # Move expired tokens back to available pool
        for token in expired_tokens:
            del self.flood_waited_tokens[token]
            self.available_tokens.append(token)
            logger.info(f"Token {token[:10]}... is no longer flood waited")
        
        # Check if we can start more bots
        while (len(self.bot_instances) < self.max_bots_count and 
               (self.available_tokens or self.flood_waited_tokens)):
            if self.available_tokens:
                # Use an available token
                token = self.available_tokens.pop(0)
                success = await self._start_bot_instance(token)
                # If failed due to flood wait, the token is already handled in _start_bot_instance
                # If successful, the bot is already added to self.bot_instances
            else:
                # No available tokens, try to add fresh tokens for rotation
                # Check if we have other tokens in the original tokens list that are not in flood wait
                for token in self.tokens:
                    if token not in self.flood_waited_tokens and token not in self.available_tokens:
                        # Check if this token is already being used by a running bot
                        token_in_use = False
                        for bot_instance in self.bot_instances:
                            if bot_instance.token == token:
                                token_in_use = True
                                break
                        if not token_in_use:
                            self.available_tokens.append(token)
                            logger.info(f"Added fresh token {token[:10]}... for rotation in manage_bots")
                            break
                
                # If we still don't have available tokens, wait a bit and check again
                if not self.available_tokens:
                    break

    async def _send_logger_startup_message(self):
        """Send initial logger bot startup message"""
        global startup_message_id, startup_message_chat_id
            
        # Only send the initial message if it hasn't been sent yet
        if startup_message_id is None and self.LOGS and self.logger_bot_util:
            try:                
                message = await self.logger_bot_util.send_log_message(
                    chat_id=self.LOGS, 
                    message=f"✨ [ {str(self.app_name).upper()} ONLINE ] ✨\n\n"
                            f"🚀 Logger Bot: ✅ Active\n"
                            f"🗄️ Database: 🟢 Connected\n"
                            f"🌐 Web Server: 🔥 Running on Port 8443\n\n"
                            f"🤖 Starting {min(self.max_bots_count, len(self.available_tokens))}",
                    parse_mode="HTML"
                )
                if message:
                    startup_message_id = message.message_id
                    startup_message_chat_id = message.chat.id
                else:
                    logger.error("Failed to send logger startup message: No message returned")
            except Exception as e:
                logger.error(f"Failed to send logger startup message: {e}")

    async def _update_startup_message_with_online_bots(self):
        """Update startup message with information about online bots"""
        global startup_message_id, startup_message_chat_id
        
        if startup_message_id and startup_message_chat_id and self.LOGS and self.logger_bot_util:
            try:
                # Get online bot information
                online_bot_count = len(self.bot_instances)
                bot_info = ""
                if online_bot_count > 0:
                    bot_info = "\n"
                    for i, bot_instance in enumerate(self.bot_instances, 1):
                        try:
                            # Get bot info to mention it properly
                            bot_me = await bot_instance.get_me()
                            bot_name = bot_me.first_name if bot_me.first_name else "Unknown Bot"
                            bot_id = bot_me.id if bot_me.id else "Unknown"
                            
                            # Store bot info for later use during shutdown
                            bot_instance._bot_name = bot_name
                            bot_instance._bot_id = bot_id
                            
                            if i == len(self.bot_instances):
                                bot_info += f"   └─ ⚡ <a href='tg://user?id={bot_id}'>{bot_name}</a>\n"
                            else:
                                bot_info += f"   ├─ ⚡ <a href='tg://user?id={bot_id}'>{bot_name}</a>\n"
                        except Exception as e:
                            # Fallback to token-based identification if we can't get bot info
                            token_suffix = bot_instance.token[-8:] if bot_instance.token else "Unknown"
                            bot_instance._bot_name = f"Bot ...{token_suffix}"
                            bot_instance._bot_id = "Unknown"
                            bot_info += f"Bot ...{token_suffix}\n"
                
                # Update the message with HTML parsing for mentions

                await self.logger_bot_util.edit_log_message(
                    chat_id=startup_message_chat_id,
                    message_id=startup_message_id,
                    message=
                            f"✨ [ {str(self.app_name).upper()} ONLINE ] ✨\n\n"  
                            f"🚀 Logger Bot: ✅ Active\n"
                            f"🗄️ Database: 🟢 Connected\n"
                            f"🌐 Web Server: 🔥 Running on Port 8443\n\n"
                            f"🤖 Active Bots: {online_bot_count}" + bot_info,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to update startup message with online bots: {e}")

    async def _start_bot_instance(self, token: str):
        """Start a bot instance with a specific token"""
        try:
            self._bot_counter += 1
            # Ensure unique bot names by using the main manager's app_name as prefix
            bot_name = f"{self.app_name}_{self._bot_counter}" if self.app_name else f"bot_{self._bot_counter}"
            
            # Create a new bot instance using TGBase
            bot_instance = TGBase(
                api_id=self.api_id,
                api_hash=self.api_hash,
                token=token,
                app_name=bot_name,
                owner_id=self.owner_id,
                plugins=self.plugins,
                database_url=self.database_url,
                log_chat_id=self.log_chat_id,
                rename=self._rename,
                logger_bot_util=self.logger_bot_util  # Pass logger bot util to each bot
            )
            
            # Mark this as a bot instance to prevent it from trying to manage other bots
            bot_instance._is_bot_instance = True
            
            # Start the bot instance
            await bot_instance._start_single_bot()
            
            # Store bot reference
            self.bot_instances.append(bot_instance)
            
            # Only log success after the bot is actually started
            logger.info(f"Started bot instance {bot_name} with token {token[:10]}...")
            
            # Return True to indicate that the bot was started successfully
            return True
            
        except FloodWait as e:
            logger.error(f"FloodWait encountered for token {token[:10]}: {e.value} seconds")
            # Add token to flood waited tokens
            self.flood_waited_tokens[token] = time.time() + e.value
            logger.info(f"Token {token[:10]} added to flood wait list, will retry later")
            # Return False to indicate that the bot was not started
            return False
            
        except Exception as e:
            logger.error(f"Failed to start bot instance with token {token[:10]}...: {e}")
            # Return False to indicate that the bot was not started
            return False

    async def stop_all_bots(self):
        """Stop all bot instances gracefully"""
        global startup_message_id, startup_message_chat_id, online_bots, flood_waited_bots
        
        # Check if already stopping to prevent duplicate calls
        if not getattr(self, '_shutdown_initiated', False):
            logger.info("Stopping all bot instances...")
            self._shutdown_initiated = True
        else:
            logger.info("Bot shutdown already initiated, skipping...")
            return
            
        self._running = False
        self._stop_event.set()
        
        # Edit startup message to show shutdown in progress with 🔄 emoji for stopping bots
        if startup_message_id and startup_message_chat_id and self.LOGS and self.logger_bot_util:
            try:
                # Create bot info with 🔄 emoji for stopping bots using saved information
                bot_info = ""
                if len(self.bot_instances) > 0:
                    bot_info = "\n"
                    for i, bot_instance in enumerate(self.bot_instances, 1):
                        
                        # Use saved bot info from when the bot was running
                        bot_name = getattr(bot_instance, '_bot_name', f"Bot ...{bot_instance.token[-8:] if bot_instance.token else 'Unknown'}")
                        bot_id = getattr(bot_instance, '_bot_id', 'Unknown')
                        if i==len(self.bot_instances):bot_info += f"   └─ 🔄 <a href='tg://user?id={bot_id}'>{bot_name}</a>\n"
                        else:bot_info += f"   ├─ 🔄 <a href='tg://user?id={bot_id}'>{bot_name}</a>\n"
                
                await self.logger_bot_util.edit_log_message(
                    chat_id=startup_message_chat_id,
                    message_id=startup_message_id,
                    message=f"✨ [ {str(self.app_name).upper()} ONLINE ] ✨\n\n"
                            f"🚀 Logger Bot: ✅ Active\n"
                            f"🗄️ Database: 🟢 Connected\n"
                            f"🌐 Web Server: 🔥 Stopping on Port 8443\n\n"
                            f"🤖 Stopping Bots: {len(self.bot_instances)}" + bot_info,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to update shutdown progress message: {e}")
        
        # Stop all bot instances
        stop_tasks = []
        for bot_instance in self.bot_instances:
            try:
                stop_tasks.append(bot_instance._stop_single_bot())
            except Exception as e:
                logger.error(f"Error preparing to stop bot instance: {e}")
        
        # Wait for all bot instances to stop
        if stop_tasks:
            try:
                await asyncio.gather(*stop_tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"Error while stopping bot instances: {e}")
        
        # Store the bot count and copy of bot instances before clearing the list
        stopped_bot_count = len(self.bot_instances)
        # Create a copy of the bot instances list before clearing it
        self.bot_instances_copy = self.bot_instances.copy()
        self.bot_instances.clear()
        
        # Edit startup message to show successful shutdown with 🛑 emoji for stopped bots
        if startup_message_id and startup_message_chat_id and self.LOGS and self.logger_bot_util:
            try:
                # Create bot info with 🛑 emoji for stopped bots using saved information
                bot_info = ""
                if stopped_bot_count > 0:
                    bot_info = "\n"
                    
                    for i, bot_instance in enumerate(self.bot_instances_copy, 1):
                        # Use saved bot info from when the bot was running
                        bot_name = getattr(bot_instance, '_bot_name', f"Bot ...{bot_instance.token[-8:] if bot_instance.token else 'Unknown'}")
                        bot_id = getattr(bot_instance, '_bot_id', 'Unknown')
                        if i==len(self.bot_instances_copy):bot_info += f"   └─ 🛑 <a href='tg://user?id={bot_id}'>{bot_name}</a>\n"
                        else:bot_info += f"   ├─ 🛑 <a href='tg://user?id={bot_id}'>{bot_name}</a>\n"
                 
                await self.logger_bot_util.edit_log_message(
                    chat_id=startup_message_chat_id,
                    message_id=startup_message_id,
                    message=f"✨ [ {self.app_name} OFFLINE ] ✨\n\n"
                            f"🚀 Logger Bot: 📛 Deactivated\n"
                            f"🗄️ Database: 📛 Disonnected\n"
                            f"🌐 Web Server: ⏸️ Stopped\n\n"
                            f"🤖 All {stopped_bot_count}" + bot_info,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to update successful shutdown message: {e}")
        
        # Clear global tracking variables
        startup_message_id = None
        startup_message_chat_id = None
        
        logger.info("All bot instances stopped successfully")

__all__ = ['D4RK_BotManager']