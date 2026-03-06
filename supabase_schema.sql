-- ============================================================
-- Crypto Buy Bot — Supabase Schema
-- Run this in your Supabase SQL Editor
-- ============================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id     BIGINT PRIMARY KEY,
    username    TEXT DEFAULT '',
    full_name   TEXT DEFAULT '',
    joined_at   TIMESTAMPTZ DEFAULT NOW(),
    total_buys  NUMERIC DEFAULT 0,
    successful_payments INTEGER DEFAULT 0,
    rejected_payments   INTEGER DEFAULT 0,
    total_orders        INTEGER DEFAULT 0
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id              SERIAL PRIMARY KEY,
    order_id        TEXT UNIQUE NOT NULL,
    user_id         BIGINT REFERENCES users(user_id),
    network         TEXT NOT NULL,
    wallet_address  TEXT NOT NULL,
    amount_usd      NUMERIC NOT NULL,
    amount_inr      NUMERIC NOT NULL,
    rate_used       NUMERIC NOT NULL,
    utr             TEXT DEFAULT '',
    status          TEXT DEFAULT 'awaiting_utr',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Bot settings table (key-value store)
CREATE TABLE IF NOT EXISTS bot_settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL DEFAULT '',
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Default settings
INSERT INTO bot_settings (key, value) VALUES
    ('main_menu_photo',       ''),
    ('payment_photo',         ''),
    ('support_username',      '@support'),
    ('conversion_rate_message',
     '🔹 *Exchange Rates*

🔹 10 - 299$    ➜   💰 Rate: ₹98
🔹 300 - 1350$  ➜   💵 Rate: ₹97
🔹 1351$+       ➜   📈 Rate: ₹96'),
    ('wallet_bep20',          'Not configured'),
    ('wallet_erc20',          'Not configured'),
    ('wallet_ton',            'Not configured'),
    ('wallet_trc20',          'Not configured'),
    ('qr_bep20',              ''),
    ('qr_erc20',              ''),
    ('qr_ton',                ''),
    ('qr_trc20',              ''),
    ('rate_tier_1_min',       '10'),
    ('rate_tier_1_max',       '299'),
    ('rate_tier_1_rate',      '98'),
    ('rate_tier_2_min',       '300'),
    ('rate_tier_2_max',       '1350'),
    ('rate_tier_2_rate',      '97'),
    ('rate_tier_3_min',       '1351'),
    ('rate_tier_3_rate',      '96')
ON CONFLICT (key) DO NOTHING;

-- Index for fast order lookups
CREATE INDEX IF NOT EXISTS idx_orders_user_id  ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status   ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
