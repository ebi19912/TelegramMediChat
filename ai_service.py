"""
AI Service module for TelegramMediChat.
Handles async communication with OpenRouter, OpenAI, and other compatible LLM providers.
Supports dynamic model switching, reasoning payload toggles, and strict quota management.
"""

import time
import aiohttp
from typing import Dict, Any, List, Optional
from database import db
from utils.prompts import DEFAULT_SYSTEM_PROMPT, MEDICATION_ASSISTANT_PROMPT


class QuotaExceededError(Exception):
    """Raised when the global request limit is reached."""
    pass


class AIConfigurationError(Exception):
    """Raised when API key or URL is misconfigured."""
    pass


class AIServiceError(Exception):
    """Raised when the external AI API fails or returns an error."""
    pass


class AIService:
    @staticmethod
    def _format_patient_context(profile: Dict[str, Any]) -> str:
        """Format patient health profile for system context injection."""
        return (
            "\n### Patient Health Profile (For Clinical Context):\n"
            f"- **Age**: {profile.get('age', 'Not specified')}\n"
            f"- **Gender**: {profile.get('gender', 'Not specified')}\n"
            f"- **Weight**: {profile.get('weight', 'Not specified')}\n"
            f"- **Known Allergies**: {profile.get('allergies', 'None reported')}\n"
            f"- **Medical Conditions**: {profile.get('conditions', 'None reported')}\n"
            f"- **Current Medications**: {profile.get('medications', 'None reported')}\n"
        )

    async def generate_response(
        self,
        user_id: int,
        user_message: str,
        is_medication_mode: bool = False,
    ) -> str:
        """
        Generate AI medical consultation response.
        Enforces quotas, retrieves context, and formats the request.
        """
        settings = await db.get_all_settings()
        api_key = settings.get("api_key", "").strip()
        api_url = settings.get("api_url", "https://openrouter.ai/api/v1/chat/completions").strip()
        model_name = settings.get("model_name", "openrouter/free").strip()
        enable_reasoning = settings.get("enable_reasoning", True)
        max_requests = settings.get("max_requests", 50)
        used_requests = settings.get("used_requests", 0)

        # 1. Quota Enforcement
        if max_requests > 0 and used_requests >= max_requests:
            raise QuotaExceededError(
                f"Quota limit reached ({used_requests}/{max_requests} requests used). "
                "Please contact the administrator to expand the quota."
            )

        # 2. Check API Key
        if not api_key:
            raise AIConfigurationError(
                "AI API Key is not configured. An administrator must set the API key in /admin."
            )

        # 3. Retrieve Context & History
        profile = await db.get_health_profile(user_id)
        history = await db.get_recent_messages(user_id, limit=8)

        base_prompt = (
            MEDICATION_ASSISTANT_PROMPT
            if is_medication_mode
            else settings.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
        )
        system_content = base_prompt + self._format_patient_context(profile)

        # Build message history
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_content}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        # 4. Construct Request Payload
        payload: Dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.3,
        }

        # OpenRouter reasoning parameter
        if enable_reasoning:
            payload["reasoning"] = {"enabled": True}

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/TelegramMediChat",
            "X-Title": "TelegramMediChat Bot",
        }

        # 5. Call API
        try:
            timeout = aiohttp.ClientTimeout(total=90)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(api_url, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise AIServiceError(
                            f"API Error (HTTP {resp.status}): {error_text[:300]}"
                        )

                    data = await resp.json()

                    if "choices" not in data or not data["choices"]:
                        raise AIServiceError("Invalid API response format (no choices returned).")

                    choice = data["choices"][0]
                    reply_text = choice.get("message", {}).get("content", "").strip()

                    if not reply_text:
                        # Fallback for some reasoning models that return thinking or empty content
                        reply_text = choice.get("text", "").strip() or "No response generated."

                    # 6. Increment Quotas & Save to History
                    await db.increment_used_requests(user_id)
                    await db.add_message(user_id, "user", user_message)
                    await db.add_message(user_id, "assistant", reply_text)

                    return reply_text

        except aiohttp.ClientConnectorError as e:
            raise AIServiceError(f"Connection error to AI endpoint: {str(e)}")
        except aiohttp.ClientResponseError as e:
            raise AIServiceError(f"HTTP Response error: {str(e)}")
        except TimeoutError:
            raise AIServiceError("AI request timed out. Please try again in a moment.")
        except Exception as e:
            if isinstance(e, (QuotaExceededError, AIConfigurationError, AIServiceError)):
                raise e
            raise AIServiceError(f"Unexpected AI error: {str(e)}")

    async def test_connection(self) -> Dict[str, Any]:
        """
        Admin connection test to verify current provider, model, and API key.
        """
        settings = await db.get_all_settings()
        api_key = settings.get("api_key", "").strip()
        api_url = settings.get("api_url", "").strip()
        model_name = settings.get("model_name", "").strip()
        provider_name = settings.get("provider_name", "OpenRouter")
        enable_reasoning = settings.get("enable_reasoning", True)

        if not api_key:
            return {
                "success": False,
                "error": "API Key is missing. Please set your API Key first in /admin.",
                "provider": provider_name,
                "model": model_name,
            }

        start_time = time.time()
        payload: Dict[str, Any] = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": "Respond with: 'OK: MediChat AI connection verified successfully.' and state your model name.",
                }
            ],
            "max_tokens": 100,
        }

        if enable_reasoning:
            payload["reasoning"] = {"enabled": True}

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/TelegramMediChat",
            "X-Title": "TelegramMediChat Admin Test",
        }

        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(api_url, json=payload, headers=headers) as resp:
                    latency = round((time.time() - start_time) * 1000, 1)
                    if resp.status == 200:
                        data = await resp.json()
                        content = (
                            data.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", "Success")
                        )
                        return {
                            "success": True,
                            "latency_ms": latency,
                            "provider": provider_name,
                            "model": model_name,
                            "sample_response": content[:200],
                            "reasoning_enabled": enable_reasoning,
                        }
                    else:
                        err_msg = await resp.text()
                        return {
                            "success": False,
                            "status_code": resp.status,
                            "error": err_msg[:300],
                            "provider": provider_name,
                            "model": model_name,
                            "latency_ms": latency,
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": provider_name,
                "model": model_name,
            }


# Singleton instance
ai_service = AIService()
