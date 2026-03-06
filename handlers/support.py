import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import Database
from utils.keyboards import back_to_main

logger = logging.getLogger(__name__)


async def support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    support_username = await Database.get_setting("support_username", "@support")

    try:
        await query.message.delete()
    except Exception:
        pass

    # Build URL — works for both @username and t.me/username formats
    handle = support_username.lstrip("@")
    url    = f"https://t.me/{handle}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"🆘 *Support*\n\n"
            f"Need help? Contact our support team:\n"
            f"👤 {support_username}\n\n"
            f"We typically respond within a few minutes!"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💬 Chat with Support", url=url)],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
        ]),
    )


def get_handlers():
    return [
        CallbackQueryHandler(support_callback, pattern="^support$"),
    ]
