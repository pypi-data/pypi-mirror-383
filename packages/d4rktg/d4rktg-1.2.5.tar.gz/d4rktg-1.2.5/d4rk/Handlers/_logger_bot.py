"""
Utility functions for working with the logger bot
"""
import logging
from typing import Optional
from telegram import Bot

logger = logging.getLogger(__name__)

class LoggerBotUtil:
    """Utility class for logger bot operations"""
    bot: Optional[Bot] = None  # class-level bot instance
    start_message = None
    start_message_id = None
    start_message_chat_id = None


    @classmethod
    def set_token(cls, token: str):
        """Initialize the bot with the given token"""
        try:
            cls.bot = Bot(token=token)
            logger.info(f"Logger bot initialized successfully with token {token[:10]}...")
        except ImportError as e:
            logger.warning("python-telegram-bot not installed. Logger bot functionality disabled.")
            logger.error(f"Import error: {e}")
            cls.bot = None
        except Exception as e:
            logger.error(f"Failed to initialize logger bot with token {token[:10]}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            cls.bot = None

    @classmethod
    async def send_start_message(cls, chat_id: int, message: str):
        if not cls.bot:
            logger.error("Logger bot is not initialized. Call set_token() first.")
            return None
        try:
            if cls.start_message is None:
                sent_message = await cls.bot.send_message(chat_id=chat_id, text=message)
                cls.start_message_id = sent_message.message_id
                cls.start_message_chat_id = sent_message.chat_id
            else:
                await cls.bot.edit_message_text(chat_id=cls.start_message_chat_id, message_id=cls.start_message_id, text=cls.start_message + "\n" + message)
            return True
        except Exception as e:
            logger.error(f"Failed to send log message: {e}")
            return None


    @classmethod
    async def send_log_message(cls, chat_id: int, message: str, parse_mode: str = None):
        if not cls.bot:
            logger.error("Logger bot is not initialized. Call set_token() first.")
            return None
        try:
            sent_message = await cls.bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)
            return sent_message
        except Exception as e:
            logger.error(f"Failed to send log message: {e}")
            return None
    
    @classmethod
    async def edit_log_message(cls, chat_id: int, message_id: int, message: str, parse_mode: str = 'HTML') -> bool:
        if not cls.bot:
            logger.error("Logger bot is not initialized. Call set_token() first.")
            return False
        try:
            await cls.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode=parse_mode)
            return True
        except Exception as e:
            logger.error(f"Failed to edit log message: {e}")
            return False
    
    @classmethod
    async def send_document(cls, chat_id: int, document_path: str, caption: str = None) -> bool:
        if not cls.bot:
            logger.error("Logger bot is not initialized. Call set_token() first.")
            return False
        try:
            with open(document_path, 'rb') as document:
                await cls.bot.send_document(chat_id=chat_id, document=document, caption=caption)
            return True
        except Exception as e:
            logger.error(f"Failed to send document: {e}")
            return False

