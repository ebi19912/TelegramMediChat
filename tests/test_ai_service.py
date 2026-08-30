"""
Unit tests for AI service payload formatting, reasoning toggle, and quota checking.
"""

import sys
import os
import unittest
from unittest.mock import patch, AsyncMock

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_service import AIService, QuotaExceededError, AIConfigurationError


class TestAIService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ai = AIService()

    def test_patient_context_formatting(self):
        profile = {
            "age": "45",
            "gender": "Female",
            "weight": "65 kg",
            "allergies": "Sulfa drugs",
            "conditions": "Type 2 Diabetes",
            "medications": "Metformin 850mg",
        }
        context_str = self.ai._format_patient_context(profile)
        self.assertIn("Age**: 45", context_str)
        self.assertIn("Sulfa drugs", context_str)
        self.assertIn("Metformin 850mg", context_str)

    @patch("ai_service.db.get_all_settings")
    async def test_quota_exceeded_check(self, mock_settings):
        mock_settings.return_value = {
            "api_key": "test-key",
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
            "model_name": "openrouter/free",
            "enable_reasoning": True,
            "max_requests": 10,
            "used_requests": 10,
        }
        with self.assertRaises(QuotaExceededError):
            await self.ai.generate_response(user_id=123, user_message="Hello")

    @patch("ai_service.db.get_all_settings")
    async def test_missing_api_key_check(self, mock_settings):
        mock_settings.return_value = {
            "api_key": "",
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
            "model_name": "openrouter/free",
            "enable_reasoning": True,
            "max_requests": 50,
            "used_requests": 0,
        }
        with self.assertRaises(AIConfigurationError):
            await self.ai.generate_response(user_id=123, user_message="Hello")


if __name__ == "__main__":
    unittest.main()
