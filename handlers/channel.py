import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import Database

logger = logging.getLogger(__name__)


async def channel_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Processing approval...", show_alert=False)

    # callback_data = "ch_approve_CRB-20260306-ABC123"
    order_id = query.data[len("ch_approve_"):]
    order    = await Database.approve_order(order_id)

    if not order:
        await query.answer("❌ Order not found or already processed.", show_alert=True)
        return

    # Edit channel message to show approved status
    try:
        await query.edit_message_caption(
            caption=(
                f"✅ *APPROVED*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🆔 Order ID:  `{order_id}`\n"
                f"💰 Amount:   *${float(order['amount_usd']):,.2f}*\n"
                f"🏦 Details:  `{order.get('user_receiving_address', '—')}`\n"
                f"💳 Method:   *{order.get('payment_method', '—')}*\n"
                f"👤 User ID:  `{order['user_id']}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ Approved and user notified."
            ),
            parse_mode="Markdown",
        )
    except Exception:
        pass

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                f"✅ *Payment Approved!*\n\n"
                f"🆔 Order: `{order_id}`\n"
                f"💰 ${float(order['amount_usd']):,.2f}\n\n"
                f"Your crypto will be sent to your given details shortly. Thank you! 🙏"
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Failed to notify user on approve: {e}")


async def channel_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Processing rejection...", show_alert=False)

    order_id = query.data[len("ch_reject_"):]
    order    = await Database.reject_order(order_id)

    if not order:
        await query.answer("❌ Order not found or already processed.", show_alert=True)
        return

    # Edit channel message to show rejected status
    try:
        await query.edit_message_caption(
            caption=(
                f"❌ *REJECTED*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🆔 Order ID:  `{order_id}`\n"
                f"💰 Amount:   *${float(order['amount_usd']):,.2f}*\n"
                f"🏦 Details:  `{order.get('user_receiving_address', '—')}`\n"
                f"💳 Method:   *{order.get('payment_method', '—')}*\n"
                f"👤 User ID:  `{order['user_id']}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"❌ Rejected and user notified."
            ),
            parse_mode="Markdown",
        )
    except Exception:
        pass

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                f"❌ *Payment Rejected*\n\n"
                f"🆔 Order: `{order_id}`\n\n"
                f"Your payment could not be verified. "
                f"Please contact support for assistance."
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Failed to notify user on reject: {e}")


def get_handlers():
    return [
        CallbackQueryHandler(channel_approve, pattern=r"^ch_approve_.+"),
        CallbackQueryHandler(channel_reject,  pattern=r"^ch_reject_.+"),
    ]
