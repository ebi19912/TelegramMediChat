"""
User handlers for TelegramMediChat.
Manages patient interactions, medical consultation workflows, health profile editing,
drug interaction checking, emergency triage guidance, and session resets.
"""

import random
from typing import Dict, Any, Optional
from telegram import Update
from telegram.constants import ChatAction
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
from ai_service import (
    ai_service,
    QuotaExceededError,
    AIConfigurationError,
    AIServiceError,
)
from utils.prompts import EMERGENCY_GUIDE_TEXT, HEALTH_TIPS
from keyboards import (
    get_user_main_keyboard,
    get_consultation_inline_keyboard,
    get_health_profile_keyboard,
    get_cancel_inline_keyboard,
)
from handlers.admin_handlers import is_admin

# Profile Conversation States
(
    PROFILE_INPUT_AGE,
    PROFILE_INPUT_GENDER,
    PROFILE_INPUT_WEIGHT,
    PROFILE_INPUT_ALLERGIES,
    PROFILE_INPUT_CONDITIONS,
    PROFILE_INPUT_MEDICATIONS,
) = range(200, 206)


def format_health_profile_text(profile: Dict[str, Any]) -> str:
    """Format health profile summary text for the user."""
    return (
        "📋 **Your Medical Health Profile**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Providing basic health details helps MediChat deliver personalized and safer consultations.\n\n"
        f"• **Age**: `{profile.get('age', 'Not specified')}`\n"
        f"• **Gender**: `{profile.get('gender', 'Not specified')}`\n"
        f"• **Weight**: `{profile.get('weight', 'Not specified')}`\n"
        f"• **Known Allergies**: `{profile.get('allergies', 'None reported')}`\n"
        f"• **Medical Conditions**: `{profile.get('conditions', 'None reported')}`\n"
        f"• **Current Medications**: `{profile.get('medications', 'None reported')}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Tap any button below to update your information:"
    )


# ------------------------------------------------------------------------------
# Core User Commands
# ------------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command and register user."""
    user = update.effective_user
    if user:
        await db.register_or_update_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    admin_status = is_admin(user.id) if user else False

    welcome_text = (
        f"👋 Hello **{user.first_name if user else 'there'}**! Welcome to **MediChat AI** 🩺\n\n"
        "I am your evidence-based medical and pharmaceutical consultation assistant. "
        "I can help you understand symptoms, check medication interactions, and prepare for doctor visits.\n\n"
        "🌟 **How to get started:**\n"
        "• 🩺 **Start Consultation**: Ask any health or medical question directly.\n"
        "• 📋 **Health Profile**: Set your age, allergies, or conditions for tailored advice.\n"
        "• 💊 **Drug Checker**: Check drug interactions, side effects, and precautions.\n"
        "• 🚨 **Emergency Guide**: Instant review of life-threatening red flags.\n"
        "• 🔄 **Reset Session**: Clear chat context to discuss a new topic.\n\n"
        "_Disclaimer: MediChat provides informational guidance only and is not a substitute for clinical diagnosis._"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=get_user_main_keyboard(is_admin=admin_status),
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    user = update.effective_user
    admin_status = is_admin(user.id) if user else False

    help_text = (
        "ℹ️ **MediChat AI — Help & Commands**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• `/start` - Start or restart the bot\n"
        "• `/consult` - Begin a new medical consultation\n"
        "• `/profile` - View and edit your health profile\n"
        "• `/drugs` - Dedicated medication & interaction checker\n"
        "• `/emergency` - Emergency hotlines and critical red flags\n"
        "• `/tips` - Daily health and wellness advice\n"
        "• `/reset` - Clear conversation memory for a fresh start\n"
        "• `/status` - Check remaining consultation quota\n"
        "• `/help` - Show this help menu\n"
    )
    if admin_status:
        help_text += "• `/admin` - Open Administrator Control Panel\n"

    help_text += (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 **Tip**: You can also type any health symptom or question directly in the chat!"
    )

    await update.message.reply_text(
        help_text,
        reply_markup=get_user_main_keyboard(is_admin=admin_status),
        parse_mode="Markdown",
    )


async def consult_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt user to initiate a medical consultation."""
    text = (
        "🩺 **Medical Consultation Mode Active**\n\n"
        "Please describe your symptoms, health concerns, or medical questions in detail.\n\n"
        "For the most accurate assessment, you may mention:\n"
        "• When did symptoms start?\n"
        "• Severity (1 to 10) and exact location.\n"
        "• Any triggers or relief factors."
    )
    await update.message.reply_text(
        text, reply_markup=get_consultation_inline_keyboard(), parse_mode="Markdown"
    )


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View and manage user health profile."""
    user_id = update.effective_user.id
    profile = await db.get_health_profile(user_id)
    text = format_health_profile_text(profile)
    await update.message.reply_text(
        text, reply_markup=get_health_profile_keyboard(profile), parse_mode="Markdown"
    )


async def drugs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Medication interaction checker."""
    context.user_data["is_medication_mode"] = True
    text = (
        "💊 **Medication & Interaction Checker Active**\n\n"
        "Please list the medications, supplements, or prescriptions you want to analyze.\n\n"
        "Example:\n"
        "_\"Can I take Ibuprofen 400mg together with Lisinopril 10mg and Vitamin C?\"_"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def emergency_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display red flag emergency guide."""
    await update.message.reply_text(EMERGENCY_GUIDE_TEXT, parse_mode="Markdown")


async def tips_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a random health tip."""
    tip = random.choice(HEALTH_TIPS)
    await update.message.reply_text(f"💡 **Health & Wellness Tip**\n\n{tip}", parse_mode="Markdown")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset conversation memory."""
    user_id = update.effective_user.id
    await db.clear_user_history(user_id)
    context.user_data.pop("is_medication_mode", None)
    await update.message.reply_text(
        "🧹 **Conversation memory cleared!**\n"
        "Your previous chat context has been reset. You can now start discussing a new medical topic.",
        reply_markup=get_user_main_keyboard(is_admin=is_admin(user_id)),
        parse_mode="Markdown",
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user and system quota status."""
    user_id = update.effective_user.id
    quota = await db.get_quota_status()

    max_req_str = str(quota["max_requests"]) if quota["max_requests"] > 0 else "Unlimited"
    status_str = "⛔ Limit Reached" if quota["is_exceeded"] else "🟢 Active"

    text = (
        "📊 **Consultation Quota & Status**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"• **System Quota**: `{quota['used_requests']} / {max_req_str}`\n"
        f"• **Remaining Requests**: `{quota['remaining'] if quota['remaining'] >= 0 else 'Unlimited'}`\n"
        f"• **Status**: `{status_str}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 If you encounter quota limits, the administrator can increase the capacity."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ------------------------------------------------------------------------------
# Natural Chat & AI Handler
# ------------------------------------------------------------------------------
async def handle_user_text_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Process natural text queries and route to AI consultation."""
    user = update.effective_user
    if not user:
        return

    text = update.message.text.strip()
    if not text:
        return

    # Handle Reply Keyboard Button Text
    if text == "🩺 Start Consultation":
        await consult_command(update, context)
        return
    elif text == "📋 Health Profile":
        await profile_command(update, context)
        return
    elif text == "💊 Drug Checker":
        await drugs_command(update, context)
        return
    elif text == "🚨 Emergency Guide":
        await emergency_command(update, context)
        return
    elif text == "💡 Daily Health Tip":
        await tips_command(update, context)
        return
    elif text == "🔄 Reset Session":
        await reset_command(update, context)
        return
    elif text == "📊 My Status & Quota":
        await status_command(update, context)
        return
    elif text == "ℹ️ About & Help":
        await help_command(update, context)
        return
    elif text == "👑 Admin Panel" and is_admin(user.id):
        from handlers.admin_handlers import admin_command
        await admin_command(update, context)
        return

    # Indicate typing status
    await update.message.chat.send_action(action=ChatAction.TYPING)

    is_med_mode = context.user_data.get("is_medication_mode", False)

    try:
        reply_content = await ai_service.generate_response(
            user_id=user.id,
            user_message=text,
            is_medication_mode=is_med_mode,
        )

        try:
            await update.message.reply_text(
                reply_content,
                reply_markup=get_consultation_inline_keyboard(),
                parse_mode="Markdown",
            )
        except Exception:
            # Fallback to plain text if Markdown format contains unescaped special characters
            await update.message.reply_text(
                reply_content,
                reply_markup=get_consultation_inline_keyboard(),
            )

    except QuotaExceededError as e:
        await update.message.reply_text(
            f"⛔ **Quota Limit Exceeded**\n\n{str(e)}\n\n"
            "Please check back later or notify the bot administrator.",
            parse_mode="Markdown",
        )
    except AIConfigurationError as e:
        await update.message.reply_text(
            f"⚙️ **Configuration Notice**\n\n{str(e)}",
            parse_mode="Markdown",
        )
    except AIServiceError as e:
        await update.message.reply_text(
            f"⚠️ **AI Service Error**\n\n{str(e)}\n\nPlease try again shortly.",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ An unexpected error occurred: `{str(e)}`", parse_mode="Markdown"
        )


# ------------------------------------------------------------------------------
# Health Profile Interactive Editor (Conversation Handler)
# ------------------------------------------------------------------------------
async def profile_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[int]:
    """Handle profile inline keyboard interactions."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

    if data == "profile:clear":
        await db.clear_health_profile(user_id)
        profile = await db.get_health_profile(user_id)
        text = "🗑️ **Health profile cleared.**\n\n" + format_health_profile_text(profile)
        await query.edit_message_text(
            text, reply_markup=get_health_profile_keyboard(profile), parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "profile:done":
        profile = await db.get_health_profile(user_id)
        text = "✅ **Health profile updated!**\n\n" + format_health_profile_text(profile)
        await query.edit_message_text(
            text, reply_markup=get_health_profile_keyboard(profile), parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "user:view_profile":
        profile = await db.get_health_profile(user_id)
        text = format_health_profile_text(profile)
        await query.message.reply_text(
            text, reply_markup=get_health_profile_keyboard(profile), parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "user:reset_memory":
        await db.clear_user_history(user_id)
        await query.message.reply_text(
            "🧹 **Conversation context cleared!** Starting fresh topic.", parse_mode="Markdown"
        )
        return ConversationHandler.END

    elif data == "user:emergency":
        await query.message.reply_text(EMERGENCY_GUIDE_TEXT, parse_mode="Markdown")
        return ConversationHandler.END

    # State transitions for profile fields
    elif data == "profile:set_age":
        await query.edit_message_text(
            "🎂 **Please enter your Age** (e.g. `28`):",
            reply_markup=get_cancel_inline_keyboard("profile:done"),
            parse_mode="Markdown",
        )
        return PROFILE_INPUT_AGE

    elif data == "profile:set_gender":
        await query.edit_message_text(
            "👤 **Please enter your Biological Gender** (e.g. `Male`, `Female`):",
            reply_markup=get_cancel_inline_keyboard("profile:done"),
            parse_mode="Markdown",
        )
        return PROFILE_INPUT_GENDER

    elif data == "profile:set_weight":
        await query.edit_message_text(
            "⚖️ **Please enter your Weight** (e.g. `70 kg` or `154 lbs`):",
            reply_markup=get_cancel_inline_keyboard("profile:done"),
            parse_mode="Markdown",
        )
        return PROFILE_INPUT_WEIGHT

    elif data == "profile:set_allergies":
        await query.edit_message_text(
            "⚠️ **Please list any Known Allergies** (e.g. `Penicillin, Peanuts`, or `None`):",
            reply_markup=get_cancel_inline_keyboard("profile:done"),
            parse_mode="Markdown",
        )
        return PROFILE_INPUT_ALLERGIES

    elif data == "profile:set_conditions":
        await query.edit_message_text(
            "🩺 **Please list any Chronic Conditions** (e.g. `Hypertension, Asthma, Type 2 Diabetes`, or `None`):",
            reply_markup=get_cancel_inline_keyboard("profile:done"),
            parse_mode="Markdown",
        )
        return PROFILE_INPUT_CONDITIONS

    elif data == "profile:set_medications":
        await query.edit_message_text(
            "💊 **Please list your Current Medications & Dosages** (e.g. `Metformin 500mg daily`, or `None`):",
            reply_markup=get_cancel_inline_keyboard("profile:done"),
            parse_mode="Markdown",
        )
        return PROFILE_INPUT_MEDICATIONS

    return ConversationHandler.END


async def profile_input_age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    age_text = update.message.text.strip()
    await db.update_health_profile(user_id, age=age_text)
    profile = await db.get_health_profile(user_id)
    await update.message.reply_text(
        f"✅ Age set to `{age_text}`.\n\n" + format_health_profile_text(profile),
        reply_markup=get_health_profile_keyboard(profile),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def profile_input_gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    gender_text = update.message.text.strip()
    await db.update_health_profile(user_id, gender=gender_text)
    profile = await db.get_health_profile(user_id)
    await update.message.reply_text(
        f"✅ Gender set to `{gender_text}`.\n\n" + format_health_profile_text(profile),
        reply_markup=get_health_profile_keyboard(profile),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def profile_input_weight_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    weight_text = update.message.text.strip()
    await db.update_health_profile(user_id, weight=weight_text)
    profile = await db.get_health_profile(user_id)
    await update.message.reply_text(
        f"✅ Weight set to `{weight_text}`.\n\n" + format_health_profile_text(profile),
        reply_markup=get_health_profile_keyboard(profile),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def profile_input_allergies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    allergies_text = update.message.text.strip()
    await db.update_health_profile(user_id, allergies=allergies_text)
    profile = await db.get_health_profile(user_id)
    await update.message.reply_text(
        f"✅ Allergies updated.\n\n" + format_health_profile_text(profile),
        reply_markup=get_health_profile_keyboard(profile),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def profile_input_conditions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    conditions_text = update.message.text.strip()
    await db.update_health_profile(user_id, conditions=conditions_text)
    profile = await db.get_health_profile(user_id)
    await update.message.reply_text(
        f"✅ Chronic conditions updated.\n\n" + format_health_profile_text(profile),
        reply_markup=get_health_profile_keyboard(profile),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def profile_input_medications_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    meds_text = update.message.text.strip()
    await db.update_health_profile(user_id, medications=meds_text)
    profile = await db.get_health_profile(user_id)
    await update.message.reply_text(
        f"✅ Current medications updated.\n\n" + format_health_profile_text(profile),
        reply_markup=get_health_profile_keyboard(profile),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


def get_profile_conversation_handler() -> ConversationHandler:
    """Build the health profile conversation handler."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("profile", profile_command),
            CallbackQueryHandler(profile_callback_handler, pattern="^(profile:|user:)"),
        ],
        states={
            PROFILE_INPUT_AGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, profile_input_age_handler)
            ],
            PROFILE_INPUT_GENDER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, profile_input_gender_handler)
            ],
            PROFILE_INPUT_WEIGHT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, profile_input_weight_handler)
            ],
            PROFILE_INPUT_ALLERGIES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, profile_input_allergies_handler)
            ],
            PROFILE_INPUT_CONDITIONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, profile_input_conditions_handler)
            ],
            PROFILE_INPUT_MEDICATIONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, profile_input_medications_handler)
            ],
        },
        fallbacks=[
            CallbackQueryHandler(profile_callback_handler, pattern="^(profile:|user:)"),
            CommandHandler("profile", profile_command),
        ],
        allow_reentry=True,
    )
