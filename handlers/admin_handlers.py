"""
Admin handlers for TelegramMediChat.
Provides dynamic in-bot configuration for AI Provider, Model, API URL, API Key,
Advanced Reasoning toggle, Quotas & Limits, User Statistics, Connection Testing, and Broadcast.
"""

import asyncio
from typing import Dict, Any
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

import config
from database import db
from ai_service import ai_service
from keyboards import (
    get_admin_main_keyboard,
    get_admin_ai_settings_keyboard,
    get_admin_models_keyboard,
    get_admin_quota_keyboard,
    get_cancel_inline_keyboard,
)

# Admin Conversation States
(
    ADMIN_INPUT_PROVIDER,
    ADMIN_INPUT_MODEL,
    ADMIN_INPUT_URL,
    ADMIN_INPUT_KEY,
    ADMIN_INPUT_MAX_REQ,
    ADMIN_INPUT_BROADCAST,
    ADMIN_INPUT_PROMPT,
) = range(100, 107)


def is_admin(user_id: int) -> bool:
    """Check if a Telegram user ID is authorized as an administrator."""
    return user_id in config.ADMIN_IDS


async def get_admin_dashboard_text() -> str:
    """Render main administrative dashboard text."""
    settings = await db.get_all_settings()
    quota = await db.get_quota_status()
    stats = await db.get_user_stats()

    key_display = (
        f"`{settings['api_key'][:8]}••••••••`"
        if len(settings.get("api_key", "")) > 10
        else "⚠️ _Not Configured_"
    )
    reasoning_text = "Enabled ✅" if settings["enable_reasoning"] else "Disabled ❌"

    return (
        "👑 **MediChat Administration Control Panel**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 **Current AI Engine Configuration:**\n"
        f"• **Provider Name**: `{settings['provider_name']}`\n"
        f"• **Model Name**: `{settings['model_name']}`\n"
        f"• **API URL**: `{settings['api_url']}`\n"
        f"• **API Key**: {key_display}\n"
        f"• **Advanced Reasoning**: `{reasoning_text}`\n"
        "\n"
        "📊 **Quotas & Cost Protection:**\n"
        f"• **Max Requests Limit**: `{quota['max_requests'] if quota['max_requests'] > 0 else 'Unlimited (0)'}`\n"
        f"• **Used Requests**: `{quota['used_requests']}`\n"
        f"• **Remaining**: `{quota['remaining'] if quota['remaining'] >= 0 else 'Unlimited'}`\n"
        f"• **Status**: `{'⛔ Quota Exceeded' if quota['is_exceeded'] else '🟢 Active'}`\n"
        "\n"
        "👥 **System Statistics:**\n"
        f"• **Total Users**: `{stats['total_users']}`\n"
        f"• **Active Users (24h)**: `{stats['active_24h']}`\n"
        f"• **Total Queries Handled**: `{stats['total_user_queries']}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Select an option below to manage settings:"
    )


async def get_ai_settings_text() -> str:
    """Render AI settings submenu text."""
    settings = await db.get_all_settings()
    key_display = (
        f"`{settings['api_key'][:8]}••••••••`"
        if len(settings.get("api_key", "")) > 10
        else "⚠️ _Not Set_"
    )
    reasoning_text = "Enabled ✅ (`{'reasoning': {'enabled': true}}`)" if settings["enable_reasoning"] else "Disabled ❌"

    return (
        "🤖 **AI Provider & Model Settings**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"• **Provider Name**: `{settings['provider_name']}`\n"
        f"• **Model Name**: `{settings['model_name']}`\n"
        f"• **API URL**: `{settings['api_url']}`\n"
        f"• **API Key (Bearer Token)**: {key_display}\n"
        f"• **Advanced Reasoning**: {reasoning_text}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Choose an attribute to modify or test connection:"
    )


async def get_quota_settings_text() -> str:
    """Render Quotas & Limits submenu text."""
    quota = await db.get_quota_status()
    max_req_str = str(quota["max_requests"]) if quota["max_requests"] > 0 else "Unlimited (0)"

    return (
        "📊 **Quotas & Rate Limits**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Set maximum request limits to prevent unexpected costs from AI API usage.\n\n"
        f"• **Chatbot Max Requests**: `{max_req_str}`\n"
        f"• **Used Requests**: `{quota['used_requests']}`\n"
        f"• **Remaining Requests**: `{quota['remaining'] if quota['remaining'] >= 0 else 'Unlimited'}`\n"
        f"• **Quota Exceeded**: `{'YES ⚠️' if quota['is_exceeded'] else 'NO 🟢'}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


# ------------------------------------------------------------------------------
# Entry Commands & Callbacks
# ------------------------------------------------------------------------------
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entrypoint for /admin command."""
    user = update.effective_user
    if not user or not is_admin(user.id):
        await update.message.reply_text(
            "⛔ **Access Denied**: You are not registered as an administrator in this bot.",
            parse_mode="Markdown",
        )
        return

    text = await get_admin_dashboard_text()
    await update.message.reply_text(
        text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown"
    )


async def admin_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[int]:
    """Handle administrative inline button clicks."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    if not user or not is_admin(user.id):
        await query.edit_message_text("⛔ **Access Denied**.", parse_mode="Markdown")
        return ConversationHandler.END

    data = query.data

    # Main Navigation
    if data == "admin:main_menu":
        text = await get_admin_dashboard_text()
        await query.edit_message_text(
            text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "admin:ai_settings":
        settings = await db.get_all_settings()
        text = await get_ai_settings_text()
        await query.edit_message_text(
            text, reply_markup=get_admin_ai_settings_keyboard(settings), parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "admin:quota_settings":
        quota = await db.get_quota_status()
        text = await get_quota_settings_text()
        await query.edit_message_text(
            text, reply_markup=get_admin_quota_keyboard(quota), parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "admin:stats":
        stats = await db.get_user_stats()
        text = (
            "👥 **Detailed User Statistics**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• **Registered Patients/Users**: `{stats['total_users']}`\n"
            f"• **Active in last 24h**: `{stats['active_24h']}`\n"
            f"• **Total User Inquiries**: `{stats['total_user_queries']}`\n"
            f"• **Global AI Requests Counter**: `{stats['used_requests']} / {stats['max_requests']}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await query.edit_message_text(
            text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "admin:toggle_reasoning":
        settings = await db.get_all_settings()
        new_val = "false" if settings["enable_reasoning"] else "true"
        await db.set_setting("enable_reasoning", new_val)
        updated_settings = await db.get_all_settings()
        text = await get_ai_settings_text()
        await query.edit_message_text(
            text,
            reply_markup=get_admin_ai_settings_keyboard(updated_settings),
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    elif data == "admin:models_menu":
        await query.edit_message_text(
            "🧠 **Select AI Model Preset or Custom Name**\n\n"
            "Choose a popular model below or specify a custom identifier (e.g., from OpenRouter):",
            reply_markup=get_admin_models_keyboard(),
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    elif data.startswith("admin:model:"):
        model_name = data.replace("admin:model:", "")
        await db.set_setting("model_name", model_name)
        settings = await db.get_all_settings()
        text = f"✅ Model successfully set to `{model_name}`.\n\n" + (
            await get_ai_settings_text()
        )
        await query.edit_message_text(
            text,
            reply_markup=get_admin_ai_settings_keyboard(settings),
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    elif data == "admin:reset_used_req":
        await db.reset_quota()
        quota = await db.get_quota_status()
        text = "✅ **Used Requests Counter has been reset to 0.**\n\n" + (
            await get_quota_settings_text()
        )
        await query.edit_message_text(
            text, reply_markup=get_admin_quota_keyboard(quota), parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "admin:test_ai":
        await query.edit_message_text("🧪 **Testing AI Connection...** Please wait...", parse_mode="Markdown")
        res = await ai_service.test_connection()
        if res.get("success"):
            text = (
                "✅ **AI Connection Test: SUCCESS**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Provider**: `{res.get('provider')}`\n"
                f"• **Model**: `{res.get('model')}`\n"
                f"• **Latency**: `{res.get('latency_ms')} ms`\n"
                f"• **Reasoning**: `{'Enabled ✅' if res.get('reasoning_enabled') else 'Disabled ❌'}`\n"
                f"• **Response**: _{res.get('sample_response', '')}_\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
        else:
            text = (
                "❌ **AI Connection Test: FAILED**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Provider**: `{res.get('provider')}`\n"
                f"• **Model**: `{res.get('model')}`\n"
                f"• **Error**: `{res.get('error')}`\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Please verify your API Key, Endpoint URL, or Model identifier."
            )
        await query.edit_message_text(
            text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "admin:view_prompt":
        settings = await db.get_all_settings()
        prompt_text = settings.get("system_prompt", "")
        # Truncate if too long for telegram message limits (4096)
        display_prompt = prompt_text[:3500] + ("..." if len(prompt_text) > 3500 else "")
        text = (
            "📝 **Medical System Prompt**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"```\n{display_prompt}\n```\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await query.edit_message_text(
            text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "admin:close":
        try:
            await query.message.delete()
        except Exception:
            await query.edit_message_text("Admin panel closed.")
        return ConversationHandler.END

    # State transitions for interactive text inputs
    elif data == "admin:set_provider":
        await query.edit_message_text(
            "🏷️ **Enter New Provider Name** (e.g. `OpenRouter`, `OpenAI`, `Groq`):",
            reply_markup=get_cancel_inline_keyboard("admin:ai_settings"),
            parse_mode="Markdown",
        )
        return ADMIN_INPUT_PROVIDER

    elif data == "admin:custom_model":
        await query.edit_message_text(
            "🧠 **Enter Custom Model Name** (e.g. `deepseek/deepseek-r1`, `google/gemini-2.0-flash`, `openai/gpt-4o`):",
            reply_markup=get_cancel_inline_keyboard("admin:ai_settings"),
            parse_mode="Markdown",
        )
        return ADMIN_INPUT_MODEL

    elif data == "admin:set_url":
        await query.edit_message_text(
            "🌐 **Enter Full API Endpoint URL**\n\n"
            "Default OpenRouter: `https://openrouter.ai/api/v1/chat/completions`\n"
            "Default OpenAI: `https://api.openai.com/v1/chat/completions`",
            reply_markup=get_cancel_inline_keyboard("admin:ai_settings"),
            parse_mode="Markdown",
        )
        return ADMIN_INPUT_URL

    elif data == "admin:set_key":
        await query.edit_message_text(
            "🔑 **Enter AI API Key (Bearer Token)**\n\n"
            "⚠️ _Your input message will be immediately deleted for privacy & security._",
            reply_markup=get_cancel_inline_keyboard("admin:ai_settings"),
            parse_mode="Markdown",
        )
        return ADMIN_INPUT_KEY

    elif data == "admin:set_max_req":
        await query.edit_message_text(
            "🔢 **Enter Chatbot Max Requests Quota**\n\n"
            "Enter a positive integer (e.g., `50` or `100`), or `0` for unlimited:",
            reply_markup=get_cancel_inline_keyboard("admin:quota_settings"),
            parse_mode="Markdown",
        )
        return ADMIN_INPUT_MAX_REQ

    elif data == "admin:broadcast":
        await query.edit_message_text(
            "📢 **Broadcast Announcement**\n\n"
            "Please send the message text you wish to broadcast to all bot users (supports Markdown):",
            reply_markup=get_cancel_inline_keyboard("admin:main_menu"),
            parse_mode="Markdown",
        )
        return ADMIN_INPUT_BROADCAST

    return ConversationHandler.END


# ------------------------------------------------------------------------------
# Text Input Handlers for Admin State Machine
# ------------------------------------------------------------------------------
async def admin_handle_provider_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    new_provider = update.message.text.strip()
    await db.set_setting("provider_name", new_provider)
    settings = await db.get_all_settings()
    await update.message.reply_text(
        f"✅ Provider Name updated to `{new_provider}`.\n\n" + (await get_ai_settings_text()),
        reply_markup=get_admin_ai_settings_keyboard(settings),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def admin_handle_model_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    new_model = update.message.text.strip()
    await db.set_setting("model_name", new_model)
    settings = await db.get_all_settings()
    await update.message.reply_text(
        f"✅ Model Name updated to `{new_model}`.\n\n" + (await get_ai_settings_text()),
        reply_markup=get_admin_ai_settings_keyboard(settings),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def admin_handle_url_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    new_url = update.message.text.strip()
    await db.set_setting("api_url", new_url)
    settings = await db.get_all_settings()
    await update.message.reply_text(
        f"✅ API Endpoint URL updated to `{new_url}`.\n\n" + (await get_ai_settings_text()),
        reply_markup=get_admin_ai_settings_keyboard(settings),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def admin_handle_key_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    new_key = update.message.text.strip()
    # Delete admin's message containing raw API key for security
    try:
        await update.message.delete()
    except Exception:
        pass

    await db.set_setting("api_key", new_key)
    settings = await db.get_all_settings()
    await update.effective_chat.send_message(
        "✅ **API Key securely stored!** (Input message deleted)\n\n"
        + (await get_ai_settings_text()),
        reply_markup=get_admin_ai_settings_keyboard(settings),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def admin_handle_max_req_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text(
            "⚠️ Please enter a valid number (digits only, e.g. `50`):",
            reply_markup=get_cancel_inline_keyboard("admin:quota_settings"),
            parse_mode="Markdown",
        )
        return ADMIN_INPUT_MAX_REQ

    await db.set_setting("max_requests", text)
    quota = await db.get_quota_status()
    await update.message.reply_text(
        f"✅ Chatbot Max Requests set to `{text}`.\n\n" + (await get_quota_settings_text()),
        reply_markup=get_admin_quota_keyboard(quota),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def admin_handle_broadcast_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    broadcast_text = update.message.text
    users = await db.get_all_users()
    total_users = len(users)

    progress_msg = await update.message.reply_text(
        f"📢 Broadcasting to `{total_users}` users... Please wait.", parse_mode="Markdown"
    )

    success_count = 0
    fail_count = 0

    for user in users:
        uid = user["user_id"]
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 **System Announcement**\n\n{broadcast_text}",
                parse_mode="Markdown",
            )
            success_count += 1
            await asyncio.sleep(0.05)  # Telegram rate limit compliance
        except Exception:
            fail_count += 1

    await progress_msg.edit_text(
        f"📢 **Broadcast Complete!**\n"
        f"• Delivered: `{success_count}`\n"
        f"• Failed/Blocked: `{fail_count}`\n"
        f"• Total: `{total_users}`",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def admin_cancel_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    if query:
        await query.answer()
        text = await get_admin_dashboard_text()
        await query.edit_message_text(
            text, reply_markup=get_admin_main_keyboard(), parse_mode="Markdown"
        )
    return ConversationHandler.END


def get_admin_conversation_handler() -> ConversationHandler:
    """Build the admin conversation handler."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("admin", admin_command),
            CallbackQueryHandler(admin_callback_handler, pattern="^admin:"),
        ],
        states={
            ADMIN_INPUT_PROVIDER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handle_provider_input)
            ],
            ADMIN_INPUT_MODEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handle_model_input)
            ],
            ADMIN_INPUT_URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handle_url_input)
            ],
            ADMIN_INPUT_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handle_key_input)
            ],
            ADMIN_INPUT_MAX_REQ: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handle_max_req_input)
            ],
            ADMIN_INPUT_BROADCAST: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handle_broadcast_input)
            ],
        },
        fallbacks=[
            CallbackQueryHandler(admin_cancel_input, pattern="^admin:"),
            CommandHandler("admin", admin_command),
        ],
        allow_reentry=True,
    )
