"""
Configuration module for TelegramMediChat.
Loads environment variables and provides structured app settings.
"""

import os
from typing import Set
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# Admin IDs
def _parse_admin_ids(raw_ids: str) -> Set[int]:
    admin_ids: Set[int] = set()
    if not raw_ids:
        return admin_ids
    for item in raw_ids.split(","):
        cleaned = item.strip()
        if cleaned.isdigit():
            admin_ids.add(int(cleaned))
    return admin_ids

ADMIN_IDS: Set[int] = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))

# Default AI Settings (can be dynamically updated via Admin Panel in DB)
DEFAULT_AI_PROVIDER: str = os.getenv("AI_PROVIDER_NAME", "OpenRouter").strip()
DEFAULT_AI_MODEL: str = os.getenv("AI_MODEL_NAME", "openrouter/free").strip()
DEFAULT_AI_URL: str = os.getenv(
    "AI_API_URL", "https://openrouter.ai/api/v1/chat/completions"
).strip()
DEFAULT_AI_KEY: str = os.getenv("AI_API_KEY", "").strip()
DEFAULT_ENABLE_REASONING: bool = (
    os.getenv("AI_ENABLE_REASONING", "true").lower() in ("true", "1", "yes")
)
DEFAULT_MAX_REQUESTS: int = int(os.getenv("CHATBOT_MAX_REQUESTS", "50"))

# Database path
DB_PATH: str = os.getenv("DB_PATH", "medichat.db").strip()


def validate_config() -> None:
    """Validate core configurations on startup."""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN.startswith("123456789"):
        print(
            "[WARNING] TELEGRAM_BOT_TOKEN is not set properly in .env! Bot may fail to connect."
        )
    if not ADMIN_IDS:
        print(
            "[INFO] No ADMIN_IDS specified in .env. Admin panel (/admin) will not be accessible."
        )
    else:
        print(f"[INFO] Initialized with {len(ADMIN_IDS)} admin ID(s): {ADMIN_IDS}")
