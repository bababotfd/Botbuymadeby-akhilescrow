import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import Database
from utils.keyboards import back_to_main

logger = logging.getLogger(__name__)


async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    stats = await Database.get_stats()

    total_users  = stats.get("total_users",  0)
    total_orders = stats.get("total_orders", 0)
    total_usd    = stats.get("total_usd",    0.0)
    successful   = stats.get("successful",   0)
    pending      = stats.get("pending",      0)
    rejected     = stats.get("rejected",     0)

    text = (
        f"📊 *Bot Statistics*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users:          *{total_users:,}*\n"
        f"📦 Total Orders:         *{total_orders:,}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 Total Volume:         *${total_usd:,.2f}*\n"
        f"✅ Successful Payments:  *{successful:,}*\n"
        f"⏳ Pending Payments:     *{pending:,}*\n"
        f"❌ Rejected Payments:    *{rejected:,}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 Powered by Crypto Buy Bot"
    )

    try:
        await query.message.delete()
    except Exception:
        pass

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=back_to_main(),
    )


def get_handlers():
    return [
        CallbackQueryHandler(stats_callback, pattern="^stats$"),
    ]
