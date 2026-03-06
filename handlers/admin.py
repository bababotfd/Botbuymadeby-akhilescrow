import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters,
)

from database import Database
from utils.keyboards import admin_home_keyboard, network_choice_keyboard, admin_cancel_keyboard
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

# ── States ─────────────────────────────────────────────────────────────────────
(
    ADMIN_HOME,
    ADMIN_AWAIT_MAIN_PHOTO,
    ADMIN_AWAIT_PAY_PHOTO,
    ADMIN_AWAIT_SUPPORT,
    ADMIN_AWAIT_CONV_MSG,
    ADMIN_CHOOSE_WALLET,
    ADMIN_AWAIT_WALLET,
    ADMIN_CHOOSE_QR,
    ADMIN_AWAIT_QR_PHOTO,
    ADMIN_AWAIT_APPROVE,
    ADMIN_AWAIT_REJECT,
    ADMIN_AWAIT_RATES,
    ADMIN_VIEW_ORDERS,
) = range(13)


# ── Guard ──────────────────────────────────────────────────────────────────────
def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def _delete(msg):
    try:
        await msg.delete()
    except Exception:
        pass


# ── Admin home ─────────────────────────────────────────────────────────────────
async def admin_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_admin(user.id):
        if update.message:
            await update.message.reply_text("⛔ You are not authorised to use this command.")
        return ConversationHandler.END

    text = (
        "⚙️ *Admin Panel*\n\n"
        "Select an option to manage the bot:"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await _delete(update.callback_query.message)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── Photo setters ──────────────────────────────────────────────────────────────
async def prompt_main_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🖼 *Send the new Main Menu photo:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_MAIN_PHOTO


async def receive_main_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    await Database.set_setting("main_menu_photo", file_id)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Main menu photo updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


async def prompt_pay_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="💳 *Send the new Payment photo:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_PAY_PHOTO


async def receive_pay_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    await Database.set_setting("payment_photo", file_id)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Payment photo updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── Support username ───────────────────────────────────────────────────────────
async def prompt_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    cur = await Database.get_setting("support_username", "@support")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📞 *Current support username:* `{cur}`\n\nSend the new username (e.g. `@mysupport`):",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_SUPPORT


async def receive_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    await Database.set_setting("support_username", val)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ Support username set to `{val}`",
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── Conversion rates message ───────────────────────────────────────────────────
async def prompt_conv_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    cur = await Database.get_setting("conversion_rate_message", "")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"💬 *Current rates popup message:*\n\n{cur}\n\n"
            f"Send the new message text (Markdown supported):"
        ),
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_CONV_MSG


async def receive_conv_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text
    await Database.set_setting("conversion_rate_message", val)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Conversion rate message updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── Wallet addresses ───────────────────────────────────────────────────────────
async def prompt_wallet_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="💼 *Select network to update wallet address:*",
        parse_mode="Markdown",
        reply_markup=network_choice_keyboard("wallet"),
    )
    return ADMIN_CHOOSE_WALLET


async def choose_wallet_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # callback_data = "wallet_bep20" etc.
    network = query.data.split("_")[1]
    context.user_data["editing_wallet_network"] = network
    cur = await Database.get_setting(f"wallet_{network}", "Not set")
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"💼 *{network.upper()} Wallet*\n\n"
            f"Current: `{cur}`\n\n"
            f"Send the new wallet address:"
        ),
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_WALLET


async def receive_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    network = context.user_data.pop("editing_wallet_network", None)
    if not network:
        await update.message.reply_text("❌ Session error. Try again.", reply_markup=admin_home_keyboard())
        return ADMIN_HOME
    val = update.message.text.strip()
    await Database.set_setting(f"wallet_{network}", val)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ {network.upper()} wallet updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── QR codes ───────────────────────────────────────────────────────────────────
async def prompt_qr_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📷 *Select network to update QR code:*",
        parse_mode="Markdown",
        reply_markup=network_choice_keyboard("qr"),
    )
    return ADMIN_CHOOSE_QR


async def choose_qr_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    network = query.data.split("_")[1]
    context.user_data["editing_qr_network"] = network
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📷 *Send the QR code photo for {network.upper()}:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_QR_PHOTO


async def receive_qr_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    network = context.user_data.pop("editing_qr_network", None)
    if not network:
        await update.message.reply_text("❌ Session error.", reply_markup=admin_home_keyboard())
        return ADMIN_HOME
    file_id = update.message.photo[-1].file_id
    await Database.set_setting(f"qr_{network}", file_id)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ QR code for {network.upper()} updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── Exchange rate tiers ────────────────────────────────────────────────────────
async def prompt_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)

    t1_min  = await Database.get_setting("rate_tier_1_min",  "10")
    t1_max  = await Database.get_setting("rate_tier_1_max",  "299")
    t1_rate = await Database.get_setting("rate_tier_1_rate", "98")
    t2_min  = await Database.get_setting("rate_tier_2_min",  "300")
    t2_max  = await Database.get_setting("rate_tier_2_max",  "1350")
    t2_rate = await Database.get_setting("rate_tier_2_rate", "97")
    t3_min  = await Database.get_setting("rate_tier_3_min",  "1351")
    t3_rate = await Database.get_setting("rate_tier_3_rate", "96")

    cur = (
        f"Tier 1: ${t1_min}–${t1_max} → ₹{t1_rate}\n"
        f"Tier 2: ${t2_min}–${t2_max} → ₹{t2_rate}\n"
        f"Tier 3: ${t3_min}+ → ₹{t3_rate}"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"📈 *Current Exchange Rate Tiers:*\n\n`{cur}`\n\n"
            f"Send the new rates in this exact format:\n"
            f"```\n"
            f"10,299,98\n"
            f"300,1350,97\n"
            f"1351,0,96\n"
            f"```\n"
            f"Format: `min,max,rate` (use `0` as max for the last tier)"
        ),
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_RATES


async def receive_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) != 3:
        await update.message.reply_text(
            "❌ Please send exactly 3 lines in `min,max,rate` format.",
            parse_mode="Markdown",
        )
        return ADMIN_AWAIT_RATES

    try:
        tiers = []
        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            tiers.append((float(parts[0]), float(parts[1]), int(parts[2])))
    except Exception:
        await update.message.reply_text("❌ Invalid format. Use `min,max,rate` per line.")
        return ADMIN_AWAIT_RATES

    await Database.set_setting("rate_tier_1_min",  str(tiers[0][0]))
    await Database.set_setting("rate_tier_1_max",  str(tiers[0][1]))
    await Database.set_setting("rate_tier_1_rate", str(tiers[0][2]))
    await Database.set_setting("rate_tier_2_min",  str(tiers[1][0]))
    await Database.set_setting("rate_tier_2_max",  str(tiers[1][1]))
    await Database.set_setting("rate_tier_2_rate", str(tiers[1][2]))
    await Database.set_setting("rate_tier_3_min",  str(tiers[2][0]))
    await Database.set_setting("rate_tier_3_rate", str(tiers[2][2]))

    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"✅ *Exchange rates updated!*\n\n"
            f"Tier 1: ${tiers[0][0]:g}–${tiers[0][1]:g} → ₹{tiers[0][2]}\n"
            f"Tier 2: ${tiers[1][0]:g}–${tiers[1][1]:g} → ₹{tiers[1][2]}\n"
            f"Tier 3: ${tiers[2][0]:g}+ → ₹{tiers[2][2]}"
        ),
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── View orders ─────────────────────────────────────────────────────────────────
def _format_orders(orders: list, title: str) -> str:
    if not orders:
        return f"{title}\n\n_No orders found._"
    lines = [title, ""]
    for o in orders:
        status_emoji = {"approved": "✅", "pending": "⏳", "rejected": "❌", "awaiting_utr": "🔘"}.get(o["status"], "❓")
        lines.append(
            f"{status_emoji} `{o['order_id']}`\n"
            f"   💰 ${float(o['amount_usd']):,.2f}  |  {o['network']}\n"
            f"   🔢 UTR: `{o.get('utr') or '—'}`\n"
        )
    return "\n".join(lines)


async def view_all_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)

    orders = await Database.get_all_orders(limit=10)
    text   = _format_orders(orders, "📦 *Last 10 Orders*")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("↩️ Admin Menu", callback_data="adm_back")],
        ]),
    )
    return ADMIN_VIEW_ORDERS


async def view_pending_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)

    orders = await Database.get_pending_orders(limit=10)
    text   = _format_orders(orders, "⏳ *Pending Orders*")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("↩️ Admin Menu", callback_data="adm_back")],
        ]),
    )
    return ADMIN_VIEW_ORDERS


# ── Approve / Reject ──────────────────────────────────────────────────────────
async def prompt_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ *Enter the Order ID to approve:*\n\n_(e.g. `CRB-20260306-ABC123`)_",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_APPROVE


async def receive_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = update.message.text.strip().upper()
    order    = await Database.approve_order(order_id)
    await _delete(update.message)

    if not order:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Order `{order_id}` not found or already processed.",
            parse_mode="Markdown",
            reply_markup=admin_home_keyboard(),
        )
        return ADMIN_HOME

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                f"✅ *Payment Approved!*\n\n"
                f"🆔 Order: `{order_id}`\n"
                f"💰 ${float(order['amount_usd']):,.2f}\n\n"
                f"Your crypto will be sent shortly. Thank you! 🙏"
            ),
            parse_mode="Markdown",
        )
    except Exception:
        pass

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ Order `{order_id}` approved and user notified.",
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


async def prompt_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="❌ *Enter the Order ID to reject:*\n\n_(e.g. `CRB-20260306-ABC123`)_",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_REJECT


async def receive_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = update.message.text.strip().upper()
    order    = await Database.reject_order(order_id)
    await _delete(update.message)

    if not order:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Order `{order_id}` not found or already processed.",
            parse_mode="Markdown",
            reply_markup=admin_home_keyboard(),
        )
        return ADMIN_HOME

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                f"❌ *Payment Rejected*\n\n"
                f"🆔 Order: `{order_id}`\n\n"
                f"Your payment was rejected. Please contact support for assistance."
            ),
            parse_mode="Markdown",
        )
    except Exception:
        pass

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"❌ Order `{order_id}` rejected and user notified.",
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── ConversationHandler factory ───────────────────────────────────────────────
def get_admin_conversation() -> ConversationHandler:
    back_btn = CallbackQueryHandler(admin_home, pattern="^adm_back$")

    return ConversationHandler(
        entry_points=[CommandHandler("admin", admin_home)],
        states={
            ADMIN_HOME: [
                CallbackQueryHandler(prompt_main_photo,    pattern="^adm_main_photo$"),
                CallbackQueryHandler(prompt_pay_photo,     pattern="^adm_pay_photo$"),
                CallbackQueryHandler(prompt_support,       pattern="^adm_support$"),
                CallbackQueryHandler(prompt_conv_msg,      pattern="^adm_conv_msg$"),
                CallbackQueryHandler(prompt_wallet_network,pattern="^adm_wallet$"),
                CallbackQueryHandler(prompt_qr_network,    pattern="^adm_qr$"),
                CallbackQueryHandler(prompt_rates,         pattern="^adm_rates$"),
                CallbackQueryHandler(view_all_orders,      pattern="^adm_orders$"),
                CallbackQueryHandler(view_pending_orders,  pattern="^adm_pending$"),
                CallbackQueryHandler(prompt_approve,       pattern="^adm_approve$"),
                CallbackQueryHandler(prompt_reject,        pattern="^adm_reject$"),
            ],
            ADMIN_AWAIT_MAIN_PHOTO:  [MessageHandler(filters.PHOTO, receive_main_photo), back_btn],
            ADMIN_AWAIT_PAY_PHOTO:   [MessageHandler(filters.PHOTO, receive_pay_photo),  back_btn],
            ADMIN_AWAIT_SUPPORT:     [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_support), back_btn],
            ADMIN_AWAIT_CONV_MSG:    [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_conv_msg), back_btn],
            ADMIN_CHOOSE_WALLET: [
                CallbackQueryHandler(choose_wallet_network, pattern="^wallet_(bep20|erc20|ton|trc20)$"),
                back_btn,
            ],
            ADMIN_AWAIT_WALLET:      [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_wallet), back_btn],
            ADMIN_CHOOSE_QR: [
                CallbackQueryHandler(choose_qr_network, pattern="^qr_(bep20|erc20|ton|trc20)$"),
                back_btn,
            ],
            ADMIN_AWAIT_QR_PHOTO:    [MessageHandler(filters.PHOTO, receive_qr_photo), back_btn],
            ADMIN_AWAIT_APPROVE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_approve), back_btn],
            ADMIN_AWAIT_REJECT:      [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_reject), back_btn],
            ADMIN_AWAIT_RATES:       [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_rates), back_btn],
            ADMIN_VIEW_ORDERS:       [back_btn],
        },
        fallbacks=[CommandHandler("admin", admin_home)],
        allow_reentry=True,
        per_message=False,
    )
