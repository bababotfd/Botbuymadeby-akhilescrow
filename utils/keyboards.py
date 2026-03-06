from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Buy Crypto", callback_data="buy")],
        [
            InlineKeyboardButton("📊 Stats",   callback_data="stats"),
            InlineKeyboardButton("👤 Profile", callback_data="profile"),
        ],
        [InlineKeyboardButton("🆘 Support", callback_data="support")],
    ])


def network_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟡 BEP20", callback_data="net_bep20"),
            InlineKeyboardButton("🔷 ERC20",  callback_data="net_erc20"),
        ],
        [
            InlineKeyboardButton("💎 TON",   callback_data="net_ton"),
            InlineKeyboardButton("🔴 TRC20", callback_data="net_trc20"),
        ],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])


def amount_entry_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 View Conversion Rates", callback_data="view_rates")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])


def receipt_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Submit UTR", callback_data="submit_utr")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])


def back_to_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ])


# ── Admin keyboards ────────────────────────────────────────────────────────────

def admin_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼 Main Menu Photo",  callback_data="adm_main_photo"),
            InlineKeyboardButton("💳 Payment Photo",    callback_data="adm_pay_photo"),
        ],
        [
            InlineKeyboardButton("📞 Support Username", callback_data="adm_support"),
            InlineKeyboardButton("💬 Rates Message",    callback_data="adm_conv_msg"),
        ],
        [
            InlineKeyboardButton("💼 Wallet Addresses", callback_data="adm_wallet"),
            InlineKeyboardButton("📷 QR Codes",         callback_data="adm_qr"),
        ],
        [
            InlineKeyboardButton("📈 Exchange Rate Tiers", callback_data="adm_rates"),
            InlineKeyboardButton("📢 Proof Channel",       callback_data="adm_channel"),
        ],
        [
            InlineKeyboardButton("📦 All Orders",    callback_data="adm_orders"),
            InlineKeyboardButton("⏳ Pending Only",  callback_data="adm_pending"),
        ],
        [
            InlineKeyboardButton("✅ Approve Order", callback_data="adm_approve"),
            InlineKeyboardButton("❌ Reject Order",  callback_data="adm_reject"),
        ],
    ])


def network_choice_keyboard(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("BEP20", callback_data=f"{prefix}_bep20"),
            InlineKeyboardButton("ERC20", callback_data=f"{prefix}_erc20"),
        ],
        [
            InlineKeyboardButton("TON",   callback_data=f"{prefix}_ton"),
            InlineKeyboardButton("TRC20", callback_data=f"{prefix}_trc20"),
        ],
        [InlineKeyboardButton("↩️ Admin Menu", callback_data="adm_back")],
    ])


def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Cancel", callback_data="adm_back")],
    ])


def channel_order_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Approve / Reject buttons posted to the proof channel."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"ch_approve_{order_id}"),
            InlineKeyboardButton("❌ Reject",  callback_data=f"ch_reject_{order_id}"),
        ]
    ])
