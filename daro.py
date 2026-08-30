"""
Legacy entrypoint wrapper for TelegramMediChat.
Redirects execution to modern bot.py entrypoint.
"""

from bot import main

if __name__ == "__main__":
    print("[INFO] Starting TelegramMediChat via modern bot.py engine...")
    main()