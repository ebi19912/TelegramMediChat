"""
Main entry point for TelegramMediChat.
Initializes the Telegram bot, database, commands menu, and all message handlers.
"""

import sys
import asyncio
import logging
from telegram import BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

import config
from database import db
from handlers.admin_handlers import (
    get_admin_conversation_handler,
    admin_command,
    admin_callback_handler,
)
from handlers.user_handlers import (
    get_profile_conversation_handler,
    start_command,
    help_command,
    consult_command,
    profile_command,
    drugs_command,
    emergency_command,
    tips_command,
    reset_command,
    status_command,
    handle_user_text_message,
    profile_callback_handler,
)
from handlers.common_handlers import global_error_handler

# Configure logging
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("TelegramMediChat")


async def post_init(application) -> None:
    """Initialize DB and configure Telegram commands menu on startup."""
    logger.info("Initializing SQLite database...")
    await db.init_db()
    logger.info("Database initialized successfully.")

    # Configure Telegram bot command suggestions
    commands = [
        BotCommand("start", "Start or restart MediChat"),
        BotCommand("consult", "Begin a medical consultation"),
        BotCommand("profile", "View & edit health profile"),
        BotCommand("drugs", "Medication & interaction checker"),
        BotCommand("emergency", "Emergency guide & red flags"),
        BotCommand("tips", "Daily wellness & health advice"),
        BotCommand("reset", "Clear conversation memory"),
        BotCommand("status", "Check consultation quota"),
        BotCommand("help", "Help & usage guide"),
        BotCommand("admin", "Admin Control Panel"),
    ]
    try:
        await application.bot.set_my_commands(commands)
        logger.info("Telegram command menu configured.")
    except Exception as e:
        logger.warning(f"Could not register bot commands menu: {e}")


def main() -> None:
    """Build and run the Telegram bot application."""
    config.validate_config()

    if not config.TELEGRAM_BOT_TOKEN:
        logger.error(
            "TELEGRAM_BOT_TOKEN is not set! Please configure it in .env before running."
        )
        sys.exit(1)

    logger.info("Building Telegram application...")
    application = (
        ApplicationBuilder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # 1. Admin Conversation & Callbacks
    application.add_handler(get_admin_conversation_handler())
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(
        CallbackQueryHandler(admin_callback_handler, pattern="^admin:")
    )

    # 2. Health Profile Conversation & Callbacks
    application.add_handler(get_profile_conversation_handler())
    application.add_handler(
        CallbackQueryHandler(profile_callback_handler, pattern="^(profile:|user:)")
    )

    # 3. User Command Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("consult", consult_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("drugs", drugs_command))
    application.add_handler(CommandHandler("emergency", emergency_command))
    application.add_handler(CommandHandler("tips", tips_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("status", status_command))

    # 4. Natural Text & Reply Keyboard Message Handler
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text_message)
    )

    # 5. Global Error Handler
    application.add_error_handler(global_error_handler)

    # 6. Start Polling
    logger.info("Starting TelegramMediChat bot polling...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
