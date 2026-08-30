"""
Keyboards module for TelegramMediChat.
Defines clean, modern Reply and Inline keyboards for users and administrators.
"""

from typing import Dict, Any, Optional
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def get_user_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Main persistent user reply keyboard."""
    keyboard = [
        [KeyboardButton("🩺 Start Consultation"), KeyboardButton("📋 Health Profile")],
        [KeyboardButton("💊 Drug Checker"), KeyboardButton("🚨 Emergency Guide")],
        [KeyboardButton("💡 Daily Health Tip"), KeyboardButton("🔄 Reset Session")],
        [KeyboardButton("📊 My Status & Quota"), KeyboardButton("ℹ️ About & Help")],
    ]
    if is_admin:
        keyboard.append([KeyboardButton("👑 Admin Panel")])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_consultation_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline quick actions displayed during active consultations."""
    keyboard = [
        [
            InlineKeyboardButton("🔄 New Topic (Clear Memory)", callback_data="user:reset_memory"),
            InlineKeyboardButton("📋 My Profile", callback_data="user:view_profile"),
        ],
        [
            InlineKeyboardButton("🚨 Emergency Red Flags", callback_data="user:emergency"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_health_profile_keyboard(profile: Dict[str, Any]) -> InlineKeyboardMarkup:
    """Interactive profile management inline keyboard."""
    age = profile.get("age", "Not set")
    gender = profile.get("gender", "Not set")
    weight = profile.get("weight", "Not set")
    allergies = profile.get("allergies", "None")
    conditions = profile.get("conditions", "None")
    meds = profile.get("medications", "None")

    keyboard = [
        [
            InlineKeyboardButton(f"🎂 Age: {age[:10]}", callback_data="profile:set_age"),
            InlineKeyboardButton(f"👤 Gender: {gender[:10]}", callback_data="profile:set_gender"),
        ],
        [
            InlineKeyboardButton(f"⚖️ Weight: {weight[:10]}", callback_data="profile:set_weight"),
            InlineKeyboardButton(f"⚠️ Allergies: {allergies[:10]}", callback_data="profile:set_allergies"),
        ],
        [
            InlineKeyboardButton(f"🩺 Conditions: {conditions[:10]}", callback_data="profile:set_conditions"),
        ],
        [
            InlineKeyboardButton(f"💊 Medications: {meds[:10]}", callback_data="profile:set_medications"),
        ],
        [
            InlineKeyboardButton("🗑️ Clear Profile", callback_data="profile:clear"),
            InlineKeyboardButton("✅ Done / Refresh", callback_data="profile:done"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==============================================================================
# Admin Keyboards
# ==============================================================================

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Main administrative dashboard inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("🤖 AI Connection Settings", callback_data="admin:ai_settings"),
        ],
        [
            InlineKeyboardButton("📊 Quotas & Limits", callback_data="admin:quota_settings"),
            InlineKeyboardButton("👥 User Statistics", callback_data="admin:stats"),
        ],
        [
            InlineKeyboardButton("🧪 Test AI Connection", callback_data="admin:test_ai"),
            InlineKeyboardButton("📢 Broadcast Message", callback_data="admin:broadcast"),
        ],
        [
            InlineKeyboardButton("📝 Medical System Prompt", callback_data="admin:view_prompt"),
        ],
        [
            InlineKeyboardButton("❌ Close Admin Panel", callback_data="admin:close"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_ai_settings_keyboard(settings: Dict[str, Any]) -> InlineKeyboardMarkup:
    """AI connection settings submenu."""
    provider = settings.get("provider_name", "OpenRouter")
    model = settings.get("model_name", "openrouter/free")
    reasoning = "✅ Enabled" if settings.get("enable_reasoning", True) else "❌ Disabled"
    has_key = "Configured (••••)" if settings.get("api_key") else "⚠️ Missing"

    keyboard = [
        [
            InlineKeyboardButton(f"🏷️ Provider: {provider}", callback_data="admin:set_provider"),
        ],
        [
            InlineKeyboardButton(f"🧠 Model: {model[:25]}", callback_data="admin:models_menu"),
        ],
        [
            InlineKeyboardButton("🌐 Edit API Endpoint URL", callback_data="admin:set_url"),
        ],
        [
            InlineKeyboardButton(f"🔑 API Key: {has_key}", callback_data="admin:set_key"),
        ],
        [
            InlineKeyboardButton(f"⚡ Reasoning: {reasoning}", callback_data="admin:toggle_reasoning"),
        ],
        [
            InlineKeyboardButton("🧪 Test Connection", callback_data="admin:test_ai"),
            InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin:main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_models_keyboard() -> InlineKeyboardMarkup:
    """Quick model selection presets and custom input."""
    presets = [
        ("🌟 openrouter/free", "admin:model:openrouter/free"),
        ("🧠 deepseek/deepseek-r1", "admin:model:deepseek/deepseek-r1"),
        ("⚡ meta-llama/llama-3.3-70b-instruct", "admin:model:meta-llama/llama-3.3-70b-instruct"),
        ("🎭 anthropic/claude-3.5-sonnet", "admin:model:anthropic/claude-3.5-sonnet"),
        ("🚀 openai/gpt-4o-mini", "admin:model:openai/gpt-4o-mini"),
    ]

    keyboard = []
    for label, cb in presets:
        keyboard.append([InlineKeyboardButton(label, callback_data=cb)])

    keyboard.append([InlineKeyboardButton("✏️ Custom Model (Type Name)", callback_data="admin:custom_model")])
    keyboard.append([InlineKeyboardButton("🔙 Back to AI Settings", callback_data="admin:ai_settings")])

    return InlineKeyboardMarkup(keyboard)


def get_admin_quota_keyboard(quota: Dict[str, Any]) -> InlineKeyboardMarkup:
    """Quota and limit management submenu."""
    max_req = quota.get("max_requests", 50)
    used_req = quota.get("used_requests", 0)

    keyboard = [
        [
            InlineKeyboardButton(f"🔢 Set Max Limit ({max_req})", callback_data="admin:set_max_req"),
        ],
        [
            InlineKeyboardButton("🔄 Reset Usage Counter (0)", callback_data="admin:reset_used_req"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin:main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_inline_keyboard(callback_data: str = "admin:main_menu") -> InlineKeyboardMarkup:
    """Generic cancel button for conversational input."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data=callback_data)]]
    )
