"""
Unit tests for TelegramMediChat core components:
- Database schema initialization
- Dynamic settings get/set
- Quota tracking & enforcement
- User health profiles
- Conversation memory
"""

import sys
import os
import tempfile
import unittest

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import Database


class TestCore(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Use temporary db file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db = Database(db_path=self.temp_db.name)
        await self.db.init_db()

    async def asyncTearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    async def test_default_settings_and_update(self):
        settings = await self.db.get_all_settings()
        self.assertEqual(settings["provider_name"], "OpenRouter")
        self.assertEqual(settings["model_name"], "openrouter/free")
        self.assertTrue(settings["enable_reasoning"])

        # Update settings
        await self.db.set_setting("provider_name", "DeepSeek")
        await self.db.set_setting("model_name", "deepseek/deepseek-r1")
        await self.db.set_setting("enable_reasoning", "true")

        updated = await self.db.get_all_settings()
        self.assertEqual(updated["provider_name"], "DeepSeek")
        self.assertEqual(updated["model_name"], "deepseek/deepseek-r1")

    async def test_quota_management(self):
        await self.db.set_setting("max_requests", "5")
        await self.db.set_setting("used_requests", "0")

        quota = await self.db.get_quota_status()
        self.assertEqual(quota["max_requests"], 5)
        self.assertEqual(quota["used_requests"], 0)
        self.assertEqual(quota["remaining"], 5)
        self.assertFalse(quota["is_exceeded"])

        # Increment
        for _ in range(5):
            await self.db.increment_used_requests(user_id=123)

        quota_after = await self.db.get_quota_status()
        self.assertEqual(quota_after["used_requests"], 5)
        self.assertEqual(quota_after["remaining"], 0)
        self.assertTrue(quota_after["is_exceeded"])

        # Reset
        await self.db.reset_quota()
        quota_reset = await self.db.get_quota_status()
        self.assertEqual(quota_reset["used_requests"], 0)
        self.assertFalse(quota_reset["is_exceeded"])

    async def test_user_health_profile(self):
        user_id = 999888
        await self.db.register_or_update_user(
            user_id=user_id,
            username="testuser",
            first_name="John",
            last_name="Doe",
        )

        profile = await self.db.get_health_profile(user_id)
        self.assertEqual(profile["age"], "Not specified")

        await self.db.update_health_profile(
            user_id=user_id,
            age="35",
            gender="Male",
            weight="80 kg",
            allergies="Penicillin",
            conditions="Hypertension",
            medications="Lisinopril 10mg",
        )

        updated_profile = await self.db.get_health_profile(user_id)
        self.assertEqual(updated_profile["age"], "35")
        self.assertEqual(updated_profile["gender"], "Male")
        self.assertEqual(updated_profile["allergies"], "Penicillin")

    async def test_conversation_history(self):
        user_id = 112233
        await self.db.add_message(user_id, "user", "I have a headache.")
        await self.db.add_message(user_id, "assistant", "How long has it lasted?")

        history = await self.db.get_recent_messages(user_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "I have a headache.")

        await self.db.clear_user_history(user_id)
        cleared_history = await self.db.get_recent_messages(user_id)
        self.assertEqual(len(cleared_history), 0)


if __name__ == "__main__":
    unittest.main()
