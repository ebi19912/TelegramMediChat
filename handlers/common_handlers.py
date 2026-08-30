"""
Common handlers and global error handler for TelegramMediChat.
"""

import logging
import traceback
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a gentle notification to the user."""
    logger.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__ if context.error else None
    )
    tb_string = "".join(tb_list)
    logger.error(f"Traceback:\n{tb_string}")

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ An unexpected system error occurred while processing your request. "
                "The issue has been logged. Please try again shortly.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")
