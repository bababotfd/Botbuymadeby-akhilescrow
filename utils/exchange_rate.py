from database import Database


async def get_rate_for_amount(amount_usd: float) -> int:
    """Return the INR-per-USD rate for the given amount based on admin-set tiers."""
    t1_min  = float(await Database.get_setting("rate_tier_1_min",  "10"))
    t1_max  = float(await Database.get_setting("rate_tier_1_max",  "299"))
    t1_rate = int(await Database.get_setting("rate_tier_1_rate", "98"))

    t2_min  = float(await Database.get_setting("rate_tier_2_min",  "300"))
    t2_max  = float(await Database.get_setting("rate_tier_2_max",  "1350"))
    t2_rate = int(await Database.get_setting("rate_tier_2_rate", "97"))

    t3_min  = float(await Database.get_setting("rate_tier_3_min",  "1351"))
    t3_rate = int(await Database.get_setting("rate_tier_3_rate", "96"))

    if t1_min <= amount_usd <= t1_max:
        return t1_rate
    elif t2_min <= amount_usd <= t2_max:
        return t2_rate
    elif amount_usd >= t3_min:
        return t3_rate
    else:
        return t1_rate  # fallback
