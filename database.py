"""
Database layer for TelegramMediChat.
Handles SQLite operations asynchronously with fallback support for standard library sqlite3.
"""

import asyncio
import sqlite3
import datetime
from typing import Dict, Any, List, Optional
import config
from utils.prompts import DEFAULT_SYSTEM_PROMPT


class Database:
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path

    def _execute_sync(self, query: str, params: tuple = ()) -> None:
        """Synchronous execute for write queries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def _fetch_one_sync(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Synchronous fetchone query."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def _fetch_all_sync(self, query: str, params: tuple = ()) -> List[tuple]:
        """Synchronous fetchall query."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def _fetch_all_dicts_sync(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Synchronous fetchall returning dicts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    async def init_db(self) -> None:
        """Initialize SQLite database tables and default configuration."""
        def _init():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 1. Settings Table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )

                # 2. Users Table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        requests_count INTEGER DEFAULT 0,
                        is_blocked INTEGER DEFAULT 0
                    )
                    """
                )

                # 3. Health Profiles Table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS health_profiles (
                        user_id INTEGER PRIMARY KEY,
                        age TEXT,
                        gender TEXT,
                        weight TEXT,
                        allergies TEXT,
                        conditions TEXT,
                        medications TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                    """
                )

                # 4. Conversation History Table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                    """
                )

                # 5. Seed default settings
                default_settings = {
                    "provider_name": config.DEFAULT_AI_PROVIDER,
                    "model_name": config.DEFAULT_AI_MODEL,
                    "api_url": config.DEFAULT_AI_URL,
                    "api_key": config.DEFAULT_AI_KEY,
                    "enable_reasoning": "true" if config.DEFAULT_ENABLE_REASONING else "false",
                    "max_requests": str(config.DEFAULT_MAX_REQUESTS),
                    "used_requests": "0",
                    "system_prompt": DEFAULT_SYSTEM_PROMPT,
                }

                for key, val in default_settings.items():
                    cursor.execute(
                        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                        (key, val),
                    )

                conn.commit()

        await asyncio.to_thread(_init)

    # --------------------------------------------------------------------------
    # Settings Operations
    # --------------------------------------------------------------------------
    async def get_setting(self, key: str, default: str = "") -> str:
        """Retrieve a specific setting by key."""
        row = await asyncio.to_thread(
            self._fetch_one_sync, "SELECT value FROM settings WHERE key = ?", (key,)
        )
        return row[0] if row else default

    async def set_setting(self, key: str, value: str) -> None:
        """Update or insert a setting."""
        await asyncio.to_thread(
            self._execute_sync,
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    async def get_all_settings(self) -> Dict[str, Any]:
        """Fetch all current settings as a dictionary."""
        rows = await asyncio.to_thread(
            self._fetch_all_sync, "SELECT key, value FROM settings"
        )
        settings_dict = {row[0]: row[1] for row in rows}

        return {
            "provider_name": settings_dict.get("provider_name", "OpenRouter"),
            "model_name": settings_dict.get("model_name", "openrouter/free"),
            "api_url": settings_dict.get(
                "api_url", "https://openrouter.ai/api/v1/chat/completions"
            ),
            "api_key": settings_dict.get("api_key", ""),
            "enable_reasoning": settings_dict.get("enable_reasoning", "true")
            .lower()
            .strip()
            == "true",
            "max_requests": int(settings_dict.get("max_requests", "50")),
            "used_requests": int(settings_dict.get("used_requests", "0")),
            "system_prompt": settings_dict.get("system_prompt", DEFAULT_SYSTEM_PROMPT),
        }

    # --------------------------------------------------------------------------
    # Quota Operations
    # --------------------------------------------------------------------------
    async def get_quota_status(self) -> Dict[str, Any]:
        """Get current quota statistics."""
        settings = await self.get_all_settings()
        max_req = settings["max_requests"]
        used_req = settings["used_requests"]
        is_exceeded = (max_req > 0) and (used_req >= max_req)
        remaining = max(0, max_req - used_req) if max_req > 0 else -1

        return {
            "max_requests": max_req,
            "used_requests": used_req,
            "remaining": remaining,
            "is_exceeded": is_exceeded,
        }

    async def increment_used_requests(self, user_id: Optional[int] = None) -> int:
        """Increment the global and per-user used requests counter."""
        def _inc():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE settings
                    SET value = CAST(CAST(value AS INTEGER) + 1 AS TEXT)
                    WHERE key = 'used_requests'
                    """
                )
                if user_id:
                    cursor.execute(
                        """
                        UPDATE users
                        SET requests_count = requests_count + 1,
                            last_active = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                        """,
                        (user_id,),
                    )
                conn.commit()
                cursor.execute("SELECT value FROM settings WHERE key = 'used_requests'")
                row = cursor.fetchone()
                return int(row[0]) if row else 0

        return await asyncio.to_thread(_inc)

    async def reset_quota(self) -> None:
        """Reset global used requests counter to 0."""
        await self.set_setting("used_requests", "0")

    # --------------------------------------------------------------------------
    # User Management
    # --------------------------------------------------------------------------
    async def register_or_update_user(
        self,
        user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
    ) -> None:
        """Register a new user or update their last active timestamp."""
        query = """
        INSERT INTO users (user_id, username, first_name, last_name, last_active)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_name = excluded.last_name,
            last_active = CURRENT_TIMESTAMP
        """
        await asyncio.to_thread(
            self._execute_sync, query, (user_id, username, first_name, last_name)
        )

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all registered users."""
        query = "SELECT * FROM users ORDER BY joined_at DESC"
        return await asyncio.to_thread(self._fetch_all_dicts_sync, query)

    async def get_user_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics for the admin dashboard."""
        def _stats():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE last_active >= datetime('now', '-1 day')"
                )
                active_24h = cursor.fetchone()[0]

                cursor.execute("SELECT SUM(requests_count) FROM users")
                row = cursor.fetchone()
                total_user_queries = row[0] if row and row[0] is not None else 0

                return total_users, active_24h, total_user_queries

        total_users, active_24h, total_user_queries = await asyncio.to_thread(_stats)
        quota = await self.get_quota_status()

        return {
            "total_users": total_users,
            "active_24h": active_24h,
            "total_user_queries": total_user_queries,
            "max_requests": quota["max_requests"],
            "used_requests": quota["used_requests"],
            "remaining_requests": quota["remaining"],
        }

    # --------------------------------------------------------------------------
    # Health Profile Operations
    # --------------------------------------------------------------------------
    async def get_health_profile(self, user_id: int) -> Dict[str, Any]:
        """Fetch the patient health profile for context injection."""
        rows = await asyncio.to_thread(
            self._fetch_all_dicts_sync,
            "SELECT * FROM health_profiles WHERE user_id = ?",
            (user_id,),
        )
        if rows:
            return rows[0]
        return {
            "age": "Not specified",
            "gender": "Not specified",
            "weight": "Not specified",
            "allergies": "None reported",
            "conditions": "None reported",
            "medications": "None reported",
        }

    async def update_health_profile(
        self,
        user_id: int,
        age: Optional[str] = None,
        gender: Optional[str] = None,
        weight: Optional[str] = None,
        allergies: Optional[str] = None,
        conditions: Optional[str] = None,
        medications: Optional[str] = None,
    ) -> None:
        """Update or insert health profile fields."""
        current = await self.get_health_profile(user_id)
        age = age if age is not None else current.get("age", "Not specified")
        gender = gender if gender is not None else current.get("gender", "Not specified")
        weight = weight if weight is not None else current.get("weight", "Not specified")
        allergies = (
            allergies if allergies is not None else current.get("allergies", "None reported")
        )
        conditions = (
            conditions
            if conditions is not None
            else current.get("conditions", "None reported")
        )
        medications = (
            medications
            if medications is not None
            else current.get("medications", "None reported")
        )

        query = """
        INSERT INTO health_profiles (user_id, age, gender, weight, allergies, conditions, medications, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            age = excluded.age,
            gender = excluded.gender,
            weight = excluded.weight,
            allergies = excluded.allergies,
            conditions = excluded.conditions,
            medications = excluded.medications,
            updated_at = CURRENT_TIMESTAMP
        """
        await asyncio.to_thread(
            self._execute_sync,
            query,
            (user_id, age, gender, weight, allergies, conditions, medications),
        )

    async def clear_health_profile(self, user_id: int) -> None:
        """Reset user health profile."""
        await asyncio.to_thread(
            self._execute_sync, "DELETE FROM health_profiles WHERE user_id = ?", (user_id,)
        )

    # --------------------------------------------------------------------------
    # Conversation History Operations
    # --------------------------------------------------------------------------
    async def add_message(self, user_id: int, role: str, content: str) -> None:
        """Record a chat message in history."""
        await asyncio.to_thread(
            self._execute_sync,
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content),
        )

    async def get_recent_messages(
        self, user_id: int, limit: int = 10
    ) -> List[Dict[str, str]]:
        """Retrieve recent conversation history for context memory."""
        query = """
        SELECT role, content FROM (
            SELECT id, role, content FROM messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        ) ORDER BY id ASC
        """
        rows = await asyncio.to_thread(self._fetch_all_dicts_sync, query, (user_id, limit))
        return [{"role": row["role"], "content": row["content"]} for row in rows]

    async def clear_user_history(self, user_id: int) -> None:
        """Clear conversation history for a user (New Consultation)."""
        await asyncio.to_thread(
            self._execute_sync, "DELETE FROM messages WHERE user_id = ?", (user_id,)
        )


# Singleton instance
db = Database()
