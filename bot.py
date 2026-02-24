"""
Telegram Marketplace Bot
========================
A production-ready Telegram Bot Marketplace for purchasing virtual numbers
(Telegram accounts, sessions, WhatsApp SMS). Includes a user storefront, 
admin panel, referral system, OxaPay crypto payment gateway, and
fully automated OTP delivery via pre-registered Pyrogram session strings.

HOW TO RUN:
    pip install aiogram==3.25.0 web3==6.20.3 "qrcode[pil]==7.4.2" \
                sqlalchemy==2.0.36 eth-account==0.11.3 pillow==12.1.1 \
                aiohttp==3.13.3 cryptography aiosqlite \
                pyrogram tgcrypto
    python bot.py

SETUP GUIDE:
    1. Set BOT_TOKEN to your @BotFather token.
    2. Set ADMIN_IDS to your Telegram user ID(s).
    3. Set TELEGRAM_API_ID and TELEGRAM_API_HASH from https://my.telegram.org.
    4. Set OXAPAY_API_KEY from your OxaPay merchant dashboard.
    5. Generate Pyrogram session strings for your phone numbers using
       the included generate_session.py script:
           python generate_session.py
    6. In the Admin Panel, use "➕ Add Number" and paste the session string
       when prompted.  The bot handles OTP delivery automatically.

DATA PERSISTENCE:
    All user, product, order, and transaction data is stored in
    marketplace.db (SQLite).  The blockchain scan state is saved to
    blockchain_state.json so it survives bot restarts.
"""

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
# NOTE: For production use, move sensitive credentials to environment variables:
#   BOT_TOKEN = os.getenv("BOT_TOKEN")
#   OXAPAY_API_KEY = os.getenv("OXAPAY_API_KEY")
#   MASTER_WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
#   etc.
# ─────────────────────────────────────────────────────────────────────────────

BOT_TOKEN = "8320586826:AAGsP6LgRM0nKXw_eb9NU7cP0TMo7LSTBqc"

ADMIN_IDS: list[int] = [6083286836]

TELEGRAM_API_ID: int   = 31706595
TELEGRAM_API_HASH: str = "6e70d58c2db95a6558486e6b22fbfd45"

# OxaPay Configuration
OXAPAY_API_KEY = "sandbox"  # Replace with your actual OxaPay merchant API key
OXAPAY_API_URL = "https://api.oxapay.com/merchants/request"
OXAPAY_INQUIRY_URL = "https://api.oxapay.com/merchants/inquiry"
OXAPAY_CALLBACK_DOMAIN = "play-casino.app"

MASTER_WALLET_ADDRESS  = "0xD303d819DA527b6b402ae61B0405b5E65fA69292"
MASTER_WALLET_PRIVATE_KEY = "9cc02e54a5ce2b9ec69f121ce3b48c075017b63f3c0492a23b007305ca36093d"

FAUCET_WALLET_ADDRESS     = MASTER_WALLET_ADDRESS
FAUCET_WALLET_PRIVATE_KEY = MASTER_WALLET_PRIVATE_KEY

BSC_RPC_URL = "https://bsc-mainnet.nodereal.io/v1/1d9d76352b8c443587521a782cfe5537"
USDT_CONTRACT_ADDRESS = "0x55d398326f99059fF775485246999027B3197955"

BLOCKCHAIN_POLL_INTERVAL = 30
OXAPAY_POLL_INTERVAL = 30  # Check OxaPay payments every 30 seconds
GAS_BNB_AMOUNT = 0.001
BNB_CONFIRMATION_WAIT_SECONDS = 5
REFERRAL_COMMISSION_PCT = 1.5
SUPPORT_USERNAME = "jashanxjagy"  # Without @ prefix (added in URLs)
LOG_CHANNEL = ""  # Add your channel username here (without @), e.g. "mychannel"
GIFT_CODE_BYTES = 8  # Number of random bytes used to generate gift codes (8 bytes = 16-char hex code)
DATABASE_URL = "sqlite+aiosqlite:///marketplace.db"
BLOCKCHAIN_STATE_FILE = "blockchain_state.json"
FERNET_KEY = "m8gzSFYcYk41uYxNUqCwpn-YGvo1_sVwDNTg-2FgBTg="

# Deposit bonus configuration
DEPOSIT_BONUSES = {
    20: 5,    # 5% bonus for $20 deposit
    50: 10,   # 10% bonus for $50 deposit
}

# Product categories
CATEGORY_TELEGRAM_ACCOUNTS = "telegram_accounts"
CATEGORY_TELEGRAM_OLD = "telegram_old_accounts"
CATEGORY_TELEGRAM_SESSIONS = "telegram_sessions"
CATEGORY_WHATSAPP_SMS = "whatsapp_sms"

CATEGORY_TELEGRAM_PREMIUM = "telegram_premium"

PRODUCT_CATEGORIES = {
    CATEGORY_TELEGRAM_ACCOUNTS: "📱 Telegram Accounts",
    CATEGORY_TELEGRAM_OLD: "📱 Telegram Old Accounts",
    CATEGORY_TELEGRAM_SESSIONS: "🔐 Telegram Sessions",
    CATEGORY_WHATSAPP_SMS: "💬 WhatsApp SMS",
    CATEGORY_TELEGRAM_PREMIUM: "⭐ Telegram Premium",
}

COUNTRY_FLAGS: dict[str, str] = {
    "india": "🇮🇳", "pakistan": "🇵🇰", "bangladesh": "🇧🇩",
    "sri lanka": "🇱🇰", "nepal": "🇳🇵", "myanmar": "🇲🇲",
    "thailand": "🇹🇭", "vietnam": "🇻🇳", "indonesia": "🇮🇩",
    "malaysia": "🇲🇾", "philippines": "🇵🇭", "singapore": "🇸🇬",
    "cambodia": "🇰🇭", "laos": "🇱🇦", "brunei": "🇧🇳",
    "china": "🇨🇳", "japan": "🇯🇵", "south korea": "🇰🇷", "korea": "🇰🇷",
    "taiwan": "🇹🇼", "hong kong": "🇭🇰", "mongolia": "🇲🇳",
    "kazakhstan": "🇰🇿", "uzbekistan": "🇺🇿", "kyrgyzstan": "🇰🇬",
    "tajikistan": "🇹🇯", "turkmenistan": "🇹🇲", "afghanistan": "🇦🇫",
    "turkey": "🇹🇷", "iran": "🇮🇷", "iraq": "🇮🇶",
    "saudi arabia": "🇸🇦", "uae": "🇦🇪", "united arab emirates": "🇦🇪",
    "israel": "🇮🇱", "jordan": "🇯🇴", "kuwait": "🇰🇼",
    "qatar": "🇶🇦", "bahrain": "🇧🇭", "oman": "🇴🇲",
    "yemen": "🇾🇪", "syria": "🇸🇾", "lebanon": "🇱🇧",
    "palestine": "🇵🇸",
    "russia": "🇷🇺", "ukraine": "🇺🇦", "belarus": "🇧🇾",
    "moldova": "🇲🇩", "georgia": "🇬🇪", "armenia": "🇦🇲",
    "azerbaijan": "🇦🇿", "latvia": "🇱🇻", "lithuania": "🇱🇹",
    "estonia": "🇪🇪",
    "united kingdom": "🇬🇧", "uk": "🇬🇧", "great britain": "🇬🇧",
    "england": "🇬🇧", "germany": "🇩🇪", "france": "🇫🇷",
    "italy": "🇮🇹", "spain": "🇪🇸", "portugal": "🇵🇹",
    "netherlands": "🇳🇱", "belgium": "🇧🇪", "switzerland": "🇨🇭",
    "austria": "🇦🇹", "poland": "🇵🇱", "czech republic": "🇨🇿",
    "czechia": "🇨🇿", "slovakia": "🇸🇰", "hungary": "🇭🇺",
    "romania": "🇷🇴", "bulgaria": "🇧🇬", "serbia": "🇷🇸",
    "croatia": "🇭🇷", "sweden": "🇸🇪", "norway": "🇳🇴",
    "denmark": "🇩🇰", "finland": "🇫🇮", "greece": "🇬🇷",
    "ireland": "🇮🇪", "luxembourg": "🇱🇺", "iceland": "🇮🇸",
    "albania": "🇦🇱", "north macedonia": "🇲🇰", "bosnia": "🇧🇦",
    "slovenia": "🇸🇮", "kosovo": "🇽🇰", "montenegro": "🇲🇪",
    "egypt": "🇪🇬", "nigeria": "🇳🇬", "ghana": "🇬🇭",
    "kenya": "🇰🇪", "ethiopia": "🇪🇹", "tanzania": "🇹🇿",
    "uganda": "🇺🇬", "south africa": "🇿🇦", "cameroon": "🇨🇲",
    "senegal": "🇸🇳", "ivory coast": "🇨🇮", "côte d'ivoire": "🇨🇮",
    "morocco": "🇲🇦", "algeria": "🇩🇿", "tunisia": "🇹🇳",
    "libya": "🇱🇾", "sudan": "🇸🇩", "somalia": "🇸🇴",
    "mozambique": "🇲🇿", "zambia": "🇿🇲", "zimbabwe": "🇿🇼",
    "angola": "🇦🇴", "congo": "🇨🇩", "mali": "🇲🇱",
    "burkina faso": "🇧🇫", "niger": "🇳🇪", "chad": "🇹🇩",
    "rwanda": "🇷🇼",
    "united states": "🇺🇸", "usa": "🇺🇸", "us": "🇺🇸",
    "america": "🇺🇸", "canada": "🇨🇦", "mexico": "🇲🇽",
    "brazil": "🇧🇷", "argentina": "🇦🇷", "colombia": "🇨🇴",
    "venezuela": "🇻🇪", "peru": "🇵🇪", "chile": "🇨🇱",
    "ecuador": "🇪🇨", "bolivia": "🇧🇴", "paraguay": "🇵🇾",
    "uruguay": "🇺🇾", "cuba": "🇨🇺", "guatemala": "🇬🇹",
    "honduras": "🇭🇳", "el salvador": "🇸🇻", "nicaragua": "🇳🇮",
    "costa rica": "🇨🇷", "panama": "🇵🇦", "haiti": "🇭🇹",
    "dominican republic": "🇩🇴", "jamaica": "🇯🇲",
    "australia": "🇦🇺", "new zealand": "🇳🇿",
    "papua new guinea": "🇵🇬", "fiji": "🇫🇯",
}

# ─────────────────────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

import asyncio
import functools
import io
import json
import logging
import os
import random
import re
import secrets
import signal
import traceback
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Optional

import aiohttp
import qrcode
from cryptography.fernet import Fernet
from eth_account import Account
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Integer, Numeric,
    String, Text, delete, select, text, update,
)
from sqlalchemy.exc import OperationalError as SAOperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from web3 import AsyncWeb3, Web3
from web3.exceptions import ContractLogicError

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  PYROGRAM AVAILABILITY CHECK
# ─────────────────────────────────────────────────────────────────────────────

try:
    from pyrogram import Client as PyroClient
    from pyrogram import errors as pyro_errors

    PYROGRAM_AVAILABLE = True
    log.info("Pyrogram loaded successfully.")
except ImportError:
    PYROGRAM_AVAILABLE = False
    log.warning(
        "pyrogram/tgcrypto not installed – OTP fetching will be unavailable. "
        "Run: pip install pyrogram tgcrypto"
    )

# ─────────────────────────────────────────────────────────────────────────────
#  DATABASE MODELS
# ─────────────────────────────────────────────────────────────────────────────

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id                     = Column(BigInteger, primary_key=True)
    username               = Column(String(128), nullable=True)
    first_name             = Column(String(128), nullable=True)
    balance                = Column(Numeric(18, 6), default=0)
    total_deposited        = Column(Numeric(18, 6), default=0)
    total_bonus_received   = Column(Numeric(18, 6), default=0)
    numbers_bought         = Column(Integer, default=0)
    deposit_wallet_address = Column(String(64), unique=True, nullable=True)
    deposit_wallet_privkey = Column(Text, nullable=True)
    referred_by            = Column(BigInteger, nullable=True)
    created_at             = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_banned              = Column(Boolean, default=False, nullable=False, server_default="0")


class Product(Base):
    __tablename__ = "products"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    category       = Column(String(32), nullable=False, default="telegram_accounts")
    country        = Column(String(64), nullable=False)
    phone_number   = Column(String(32), nullable=False, unique=True)
    price          = Column(Numeric(18, 6), nullable=False)
    session_string = Column(Text, nullable=True)
    status         = Column(String(16), default="Available")
    latest_otp     = Column(String(16), nullable=True)
    otp_updated_at = Column(DateTime, nullable=True)
    year           = Column(Integer, nullable=True)  # For telegram_old_accounts
    twofa_password = Column(Text, nullable=True)


class Transaction(Base):
    __tablename__ = "transactions"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(BigInteger, nullable=False)
    order_id   = Column(Integer, nullable=True)
    type       = Column(String(32), nullable=False)
    amount     = Column(Numeric(18, 6), nullable=False)
    bonus      = Column(Numeric(18, 6), default=0)
    tx_hash    = Column(String(128), nullable=True)
    status     = Column(String(16), default="Pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Order(Base):
    __tablename__ = "orders"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(BigInteger, nullable=False)
    product_id = Column(Integer, nullable=False)
    status     = Column(String(16), default="PendingAdmin")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class OxaPayPayment(Base):
    """Track OxaPay payment requests."""
    __tablename__ = "oxapay_payments"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(BigInteger, nullable=False)
    track_id     = Column(String(64), unique=True, nullable=False)
    amount       = Column(Numeric(18, 6), nullable=False)
    bonus_amount = Column(Numeric(18, 6), default=0)
    status       = Column(String(32), default="Waiting")  # Waiting, Confirming, Confirmed, Expired, Failed
    pay_link     = Column(Text, nullable=True)
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at   = Column(DateTime, nullable=True)


class DiscountTier(Base):
    __tablename__ = "discount_tiers"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    min_deposit  = Column(Numeric(18, 6), nullable=False)
    discount_pct = Column(Numeric(6, 2), nullable=False)
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class UserDiscount(Base):
    __tablename__ = "user_discounts"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(BigInteger, nullable=False, unique=True)
    min_deposit  = Column(Numeric(18, 6), nullable=False)
    discount_pct = Column(Numeric(6, 2), nullable=False)
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class GiftCode(Base):
    __tablename__ = "gift_codes"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    code           = Column(String(64), unique=True, nullable=False)
    amount         = Column(Numeric(18, 6), nullable=False)
    max_claims     = Column(Integer, nullable=False)
    min_buy_volume = Column(Numeric(18, 6), default=0)
    claims_count   = Column(Integer, default=0)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class GiftCodeClaim(Base):
    __tablename__ = "gift_code_claims"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    code_id    = Column(Integer, nullable=False)
    user_id    = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CustomCategory(Base):
    __tablename__ = "custom_categories"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    slug       = Column(String(64), unique=True, nullable=False)
    name       = Column(String(128), nullable=False)
    sub_name   = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PremiumCountry(Base):
    __tablename__ = "premium_countries"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    country    = Column(String(64), nullable=False, unique=True)
    price      = Column(Numeric(18, 6), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PremiumOrder(Base):
    __tablename__ = "premium_orders"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    order_ref      = Column(String(32), unique=True, nullable=False)
    user_id        = Column(BigInteger, nullable=False)
    country        = Column(String(64), nullable=False)
    price          = Column(Numeric(18, 6), nullable=False)
    status         = Column(String(16), default="Pending")
    phone_number   = Column(String(32), nullable=True)
    session_string = Column(Text, nullable=True)
    twofa_password = Column(Text, nullable=True)
    product_id     = Column(Integer, nullable=True)
    created_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc))


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Migration: add new columns to existing databases
        migrations = [
            "ALTER TABLE users ADD COLUMN is_banned BOOLEAN NOT NULL DEFAULT 0",
            "ALTER TABLE users ADD COLUMN first_name VARCHAR(128)",
            "ALTER TABLE users ADD COLUMN total_deposited NUMERIC(18, 6) DEFAULT 0",
            "ALTER TABLE users ADD COLUMN total_bonus_received NUMERIC(18, 6) DEFAULT 0",
            "ALTER TABLE users ADD COLUMN numbers_bought INTEGER DEFAULT 0",
            "ALTER TABLE products ADD COLUMN category VARCHAR(32) DEFAULT 'telegram_accounts'",
            "ALTER TABLE transactions ADD COLUMN bonus NUMERIC(18, 6) DEFAULT 0",
            "ALTER TABLE products ADD COLUMN year INTEGER",
            "CREATE TABLE IF NOT EXISTS discount_tiers (id INTEGER PRIMARY KEY AUTOINCREMENT, min_deposit NUMERIC(18,6) NOT NULL, discount_pct NUMERIC(6,2) NOT NULL, created_at DATETIME)",
            "CREATE TABLE IF NOT EXISTS user_discounts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id BIGINT NOT NULL UNIQUE, min_deposit NUMERIC(18,6) NOT NULL, discount_pct NUMERIC(6,2) NOT NULL, created_at DATETIME)",
            "CREATE TABLE IF NOT EXISTS gift_codes (id INTEGER PRIMARY KEY AUTOINCREMENT, code VARCHAR(64) NOT NULL UNIQUE, amount NUMERIC(18,6) NOT NULL, max_claims INTEGER NOT NULL, min_buy_volume NUMERIC(18,6) DEFAULT 0, claims_count INTEGER DEFAULT 0, is_active BOOLEAN DEFAULT 1, created_at DATETIME)",
            "CREATE TABLE IF NOT EXISTS gift_code_claims (id INTEGER PRIMARY KEY AUTOINCREMENT, code_id INTEGER NOT NULL, user_id BIGINT NOT NULL, created_at DATETIME)",
            "ALTER TABLE products ADD COLUMN twofa_password TEXT",
            "CREATE TABLE IF NOT EXISTS premium_countries (id INTEGER PRIMARY KEY AUTOINCREMENT, country VARCHAR(64) NOT NULL UNIQUE, price NUMERIC(18,6) NOT NULL, created_at DATETIME)",
            "CREATE TABLE IF NOT EXISTS premium_orders (id INTEGER PRIMARY KEY AUTOINCREMENT, order_ref VARCHAR(32) UNIQUE NOT NULL, user_id BIGINT NOT NULL, country VARCHAR(64) NOT NULL, price NUMERIC(18,6) NOT NULL, status VARCHAR(16) DEFAULT 'Pending', phone_number VARCHAR(32), session_string TEXT, twofa_password TEXT, product_id INTEGER, created_at DATETIME)",
        ]
        for migration in migrations:
            try:
                await conn.execute(text(migration))
            except SAOperationalError:
                pass  # Column already exists


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

_fernet: Optional[Fernet] = None


def get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(FERNET_KEY.encode())
    return _fernet


def encrypt_privkey(private_key: str) -> str:
    return get_fernet().encrypt(private_key.encode()).decode()


def decrypt_privkey(encrypted: str) -> str:
    return get_fernet().decrypt(encrypted.encode()).decode()


def generate_wallet() -> tuple[str, str]:
    acct = Account.create()
    return acct.address, acct.key.hex()


def make_qr_bytes(data: str) -> bytes:
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def apply_button_style(button: InlineKeyboardButton, style: str, custom_emoji_id: str | None = None) -> InlineKeyboardButton:
    """Apply color style to an InlineKeyboardButton for Telegram Bot API 9.4+.
    style: 'primary' (blue), 'success' (green), 'danger' (red)
    custom_emoji_id: optional Telegram Premium Custom Emoji ID for the button icon.
    Since aiogram's TelegramObject has extra='allow', extra fields are preserved.
    """
    data = button.model_dump(exclude_none=True)
    data['style'] = style
    if custom_emoji_id is not None:
        data['icon_custom_emoji_id'] = custom_emoji_id
    return InlineKeyboardButton(**data)


def create_styled_keyboard(keyboard_array) -> InlineKeyboardMarkup:
    """Create InlineKeyboardMarkup from a 2D array supporting styled buttons."""
    return InlineKeyboardMarkup(inline_keyboard=keyboard_array)


SESSION_STRING_PREVIEW_LEN = 60


def format_session_preview(session_string: Optional[str]) -> str:
    """Return a formatted block for displaying a session string in messages."""
    if not session_string:
        return "🔐 <b>Session String:</b> Not configured"
    preview = session_string[:SESSION_STRING_PREVIEW_LEN]
    if len(session_string) > SESSION_STRING_PREVIEW_LEN:
        preview += "…"
    return (
        f"🔐 <b>Session String (preview):</b>\n"
        f"<code>{preview}</code>\n"
        f"<i>(Full string available in My Purchases → this number)</i>"
    )


def format_session_full(session_string: Optional[str]) -> str:
    """Return a formatted block showing the complete session string."""
    if not session_string:
        return "🔐 <b>Session String:</b> Not configured"
    return f"🔐 <b>Session String:</b>\n<code>{session_string}</code>"



def get_country_flag(country: str) -> str:
    """Return the flag emoji for a given country name."""
    return COUNTRY_FLAGS.get(country.lower().strip(), "🌍")


def get_welcome_text(first_name: str, balance: Decimal) -> str:
    """Generate personalized welcome text with user's name and balance."""
    return (
        f'<tg-emoji emoji-id="5456140674028019486">✨</tg-emoji> <b>Hey {first_name}! Ready to explore?</b> <tg-emoji emoji-id="5438496463044752972">✨</tg-emoji>\n\n'
        f'<tg-emoji emoji-id="5409048419211682843">💰</tg-emoji> <b>Your Balance:</b> ${balance:.2f} USDT\n\n'
        f'<tg-emoji emoji-id="5217712513847676489">🎯</tg-emoji> What are you in the mood for today?\n'
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f'<tg-emoji emoji-id="5424972470023104089">🔥</tg-emoji> <b>Premium Accounts</b> • Instant OTPs\n'
        f'<tg-emoji emoji-id="5411590687663608498">⚡</tg-emoji> <b>Lightning Fast</b> • Auto Delivery\n'
        f'<tg-emoji emoji-id="5251203410396458957">🛡️</tg-emoji> <b>24/7 Support</b> • Secure Payments\n'
        f"━━━━━━━━━━━━━━━━━━━━━"
    )


def get_help_text() -> str:
    """Generate comprehensive help text."""
    return (
        "<tg-emoji emoji-id='5305265301917549162'>📖</tg-emoji> <b>Complete Guide to Our Bot</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<tg-emoji emoji-id='5427168083074628963'>💎</tg-emoji> <b>1. DEPOSIT FUNDS</b>\n"
        "• Tap <tg-emoji emoji-id='5427168083074628963'>💎</tg-emoji> Deposit → OxaPay Crypto\n"
        "• Select an amount or enter custom\n"
        "• Complete payment via crypto\n"
        "• Balance updates automatically!\n\n"
        "<tg-emoji emoji-id='5406683434124859552'>🛒</tg-emoji> <b>2. BUY ACCOUNTS</b>\n"
        "• Tap <tg-emoji emoji-id='5406683434124859552'>🛍️</tg-emoji> Buy Accounts\n"
        "• Choose category (Telegram)\n"
        "• Select a country from the list\n"
        "• Tap Buy Now if balance is sufficient\n\n"
        "<tg-emoji emoji-id='5253742260054409879'>📲</tg-emoji> <b>3. GET YOUR OTP</b>\n"
        "• After purchase, use the number in Telegram\n"
        "• Request login code in Telegram app\n"
        "• Come back & tap Get OTP\n"
        "• Code appears instantly!\n\n"
        "<tg-emoji emoji-id='5242311354919963946'>🎁</tg-emoji> <b>4. GIFT CODES</b>\n"
        "• Use <code>/claim CODE</code> to redeem a gift code\n"
        "• Gift codes add balance to your account instantly!\n"
        "• Check back regularly for special codes\n\n"
        "👥 <b>5. REFERRAL PROGRAM</b>\n"
        f"• Earn {REFERRAL_COMMISSION_PCT}% on referral deposits\n"
        "• Share your unique link\n"
        "• Track earnings in Referral section\n\n"
        "<tg-emoji emoji-id='5319175438268913255'>👤</tg-emoji> <b>6. PROFILE</b>\n"
        "• View your complete statistics\n"
        "• Check purchase history\n"
        "• Monitor bonus earnings\n\n"
        "<tg-emoji emoji-id='5427168083074628963'>🏷️</tg-emoji> <b>7. DISCOUNTS</b>\n"
        "• Deposit more to unlock exclusive discounts!\n"
        "• Discounts are applied automatically at checkout\n"
        "• The more you deposit, the bigger the discount!\n\n"
        "<tg-emoji emoji-id='5253742260054409879'>🆘</tg-emoji> <b>NEED HELP?</b>\n"
        f"Contact: @{SUPPORT_USERNAME}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str],
    first_name: Optional[str] = None,
    referred_by: Optional[int] = None,
) -> User:
    result = await session.execute(select(User).where(User.id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            id=telegram_id, 
            username=username, 
            first_name=first_name or "User",
            balance=Decimal("0"),
            referred_by=referred_by,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        # Update first_name if provided and different
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            await session.commit()
    return user


def build_main_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Build the main menu with styled inline buttons and custom emojis."""
    buttons = [
        # Row 1 (Full width)
        [apply_button_style(InlineKeyboardButton(text="Buy Accounts", callback_data="buy"), 'primary', "5312361253610475399")],

        # Row 2 (Two columns)
        [
            apply_button_style(InlineKeyboardButton(text="Deposit", callback_data="deposit"), 'primary', "5424976816530014958"),
            apply_button_style(InlineKeyboardButton(text="Profile", callback_data="profile"), 'primary', "5258011929993026890")
        ],

        # Row 3 (Two columns)
        [
            apply_button_style(InlineKeyboardButton(text="Referral", callback_data="referral"), 'primary', "5461151367559141950"),
            apply_button_style(InlineKeyboardButton(text="Help", callback_data="help"), 'primary', "5334544901428229844")
        ],

        # Row 4 (Full width)
        [apply_button_style(InlineKeyboardButton(text="Support", url=f"https://t.me/{SUPPORT_USERNAME}"), 'danger', "5197252827247841976")]
    ]

    # Row 5 (Admin only)
    if is_admin:
        buttons.append([apply_button_style(InlineKeyboardButton(text="Admin Panel", callback_data="admin_menu"), 'primary', "5260343246831237239")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─────────────────────────────────────────────────────────────────────────────
#  OTP ENGINE  –  Complete Redesign
# ─────────────────────────────────────────────────────────────────────────────
#
#  Architecture:
#    • OTPSessionManager – singleton that manages Pyrogram client lifecycle.
#      Each product that is sold gets a dedicated client that stays alive.
#    • On purchase, a persistent listener is started that runs for 30 min.
#    • On "Get OTP" press, if no fresh OTP is in the DB, we do an active
#      history scan of chat 777000 looking for the newest 5-digit code.
#    • Both the listener AND the on-demand scan write to the same DB column,
#      so the user always gets the freshest code.
#
#  Why this is better:
#    1. The Pyrogram client is started ONCE and reused – no repeated
#       connect/disconnect per OTP request.
#    2. The on-demand scan acts as a reliable fallback when the live listener
#       misses a message (race condition / slow connect).
#    3. Proper error handling with user-visible status messages.
#    4. Graceful cleanup on shutdown.
# ─────────────────────────────────────────────────────────────────────────────

_TELEGRAM_SERVICE_CHAT_ID = 777000
_OTP_PATTERN = re.compile(r'(?<!\d)(\d{5})(?!\d)')
_OTP_FRESHNESS_SECONDS = 15 * 60   # 15 minutes
_LISTENER_LIFETIME = 30 * 60       # 30 minutes


class OTPSessionManager:
    """
    Manages one Pyrogram client per product.
    Provides:
      - start_listener(product_id, session_string)  → background live listener
      - fetch_otp_now(product_id, session_string)    → on-demand history scan
      - shutdown()                                    → clean up all clients
    """

    def __init__(self):
        # product_id → PyroClient (connected)
        self._clients: dict[int, "PyroClient"] = {}
        # product_id → asyncio.Task (the listener coroutine)
        self._tasks: dict[int, asyncio.Task] = {}
        # Lock per product to avoid duplicate client starts
        self._locks: dict[int, asyncio.Lock] = {}

    def _get_lock(self, product_id: int) -> asyncio.Lock:
        if product_id not in self._locks:
            self._locks[product_id] = asyncio.Lock()
        return self._locks[product_id]

    async def _get_or_create_client(
        self, product_id: int, session_string: str
    ) -> Optional["PyroClient"]:
        """Return a connected Pyrogram client, creating one if needed."""
        if not PYROGRAM_AVAILABLE:
            log.error("[OTP %s] Pyrogram not installed", product_id)
            return None
        if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
            log.error("[OTP %s] TELEGRAM_API_ID / TELEGRAM_API_HASH not set", product_id)
            return None
        if not session_string or len(session_string.strip()) < 20:
            log.error("[OTP %s] Session string is empty or too short", product_id)
            return None

        async with self._get_lock(product_id):
            # Already have a live client?
            existing = self._clients.get(product_id)
            if existing is not None:
                try:
                    if existing.is_connected:
                        return existing
                except Exception:
                    pass
                # Dead client – remove and recreate
                await self._stop_client(product_id)

            client = PyroClient(
                name=f"otp_{product_id}",
                api_id=TELEGRAM_API_ID,
                api_hash=TELEGRAM_API_HASH,
                session_string=session_string.strip(),
                in_memory=True,
                no_updates=False,
            )

            try:
                log.info("[OTP %s] Connecting Pyrogram client…", product_id)
                await client.start()
                me = await client.get_me()
                log.info(
                    "[OTP %s] Connected as %s (%s)",
                    product_id, me.phone_number, me.first_name,
                )
                self._clients[product_id] = client
                return client
            except Exception as exc:
                log.error(
                    "[OTP %s] Failed to start Pyrogram client: %s\n%s",
                    product_id, exc, traceback.format_exc(),
                )
                try:
                    await client.stop()
                except Exception:
                    pass
                return None

    async def _stop_client(self, product_id: int) -> None:
        client = self._clients.pop(product_id, None)
        if client is not None:
            try:
                await client.stop()
                log.info("[OTP %s] Client stopped", product_id)
            except Exception as exc:
                log.warning("[OTP %s] Error stopping client: %s", product_id, exc)

    # ── Live background listener ──────────────────────────────────────────

    async def start_listener(self, product_id: int, session_string: str) -> None:
        """
        Spawn a background task that keeps a Pyrogram client alive and
        watches for OTP messages from 777000 for up to _LISTENER_LIFETIME.
        """
        # Cancel any previous listener for this product
        old_task = self._tasks.pop(product_id, None)
        if old_task and not old_task.done():
            old_task.cancel()
            await asyncio.sleep(0.1)

        task = asyncio.create_task(self._listener_loop(product_id, session_string))
        self._tasks[product_id] = task

        def _on_done(t: asyncio.Task):
            if t.exception():
                log.error(
                    "[OTP %s] Listener task died: %s", product_id, t.exception()
                )

        task.add_done_callback(_on_done)
        log.info("[OTP %s] Listener task spawned", product_id)

    async def _listener_loop(self, product_id: int, session_string: str) -> None:
        """
        Core listener loop.  Strategy:
          1. Connect the client.
          2. Do an immediate history scan to capture any OTP that arrived
             before we connected (covers the race window).
          3. Then poll the history every 5 seconds for _LISTENER_LIFETIME.
             (Polling is far more reliable than Pyrogram's on_message handler
              because it doesn't depend on update ordering or gaps.)
        """
        client = await self._get_or_create_client(product_id, session_string)
        if client is None:
            return

        # Immediate first scan
        await self._scan_and_store(product_id, client)

        end_time = asyncio.get_running_loop().time() + _LISTENER_LIFETIME
        while asyncio.get_running_loop().time() < end_time:
            await asyncio.sleep(5)
            try:
                if not client.is_connected:
                    log.warning("[OTP %s] Client disconnected mid-listen, reconnecting…", product_id)
                    client = await self._get_or_create_client(product_id, session_string)
                    if client is None:
                        return
                await self._scan_and_store(product_id, client)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                log.warning("[OTP %s] Listener poll error: %s", product_id, exc)

        log.info("[OTP %s] Listener lifetime expired – cleaning up", product_id)
        await self._stop_client(product_id)

    async def _scan_and_store(self, product_id: int, client: "PyroClient") -> Optional[str]:
        """
        Scan the last 10 messages from chat 777000, find the newest 5-digit
        code, and store it in the DB if it's newer than what we have.
        Returns the OTP string or None.
        """
        best_otp: Optional[str] = None
        best_date: Optional[datetime] = None

        try:
            async for msg in client.get_chat_history(_TELEGRAM_SERVICE_CHAT_ID, limit=10):
                if not msg.text:
                    continue
                match = _OTP_PATTERN.search(msg.text)
                if match:
                    code = match.group(1)
                    msg_date = msg.date  # already a datetime object (UTC)
                    if msg_date.tzinfo is None:
                        msg_date = msg_date.replace(tzinfo=timezone.utc)
                    if best_date is None or msg_date > best_date:
                        best_otp = code
                        best_date = msg_date
        except Exception as exc:
            log.warning("[OTP %s] History scan error: %s", product_id, exc)
            return None

        if best_otp is None or best_date is None:
            return None

        # Check freshness
        age = (datetime.now(timezone.utc) - best_date).total_seconds()
        if age > _OTP_FRESHNESS_SECONDS:
            return None

        # Store only if newer than existing
        try:
            async with AsyncSessionFactory() as session:
                result = await session.execute(
                    select(Product).where(Product.id == product_id)
                )
                product = result.scalar_one_or_none()
                if product is None:
                    return None

                existing_ts = product.otp_updated_at
                if existing_ts is not None:
                    if existing_ts.tzinfo is None:
                        existing_ts = existing_ts.replace(tzinfo=timezone.utc)
                    if best_date <= existing_ts:
                        # Already have a newer or equal OTP
                        return product.latest_otp

                await session.execute(
                    update(Product)
                    .where(Product.id == product_id)
                    .values(latest_otp=best_otp, otp_updated_at=best_date)
                )
                await session.commit()
                log.info("[OTP %s] Stored OTP %s (from %s)", product_id, best_otp, best_date)
                return best_otp
        except Exception as exc:
            log.error("[OTP %s] DB error storing OTP: %s", product_id, exc)
            return None

    # ── On-demand OTP fetch (called when user taps "Get OTP") ─────────────

    async def fetch_otp_now(
        self, product_id: int, session_string: str
    ) -> tuple[Optional[str], str]:
        """
        Actively fetch the latest OTP right now.

        Returns (otp_code_or_None, status_message).
        status_message is a human-readable explanation for the UI.
        """
        if not PYROGRAM_AVAILABLE:
            return None, "Pyrogram is not installed on the server."
        if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
            return None, "Telegram API credentials are not configured."
        if not session_string or len(session_string.strip()) < 20:
            return None, "No valid session string for this number."

        client = await self._get_or_create_client(product_id, session_string)
        if client is None:
            return None, "Could not connect to Telegram for this number."

        otp = await self._scan_and_store(product_id, client)
        if otp:
            return otp, "OK"

        # Nothing found – read from DB in case the listener stored something
        try:
            async with AsyncSessionFactory() as session:
                result = await session.execute(
                    select(Product).where(Product.id == product_id)
                )
                p = result.scalar_one_or_none()
                if p and p.latest_otp and p.otp_updated_at:
                    ts = p.otp_updated_at
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    age = (datetime.now(timezone.utc) - ts).total_seconds()
                    if age < _OTP_FRESHNESS_SECONDS:
                        return p.latest_otp, "OK"
        except Exception:
            pass

        return None, "No OTP found yet. Make sure you requested the code in Telegram."

    # ── Shutdown ──────────────────────────────────────────────────────────

    async def stop_product(self, product_id: int) -> None:
        """Cancel any listener task and stop the Pyrogram client for a product."""
        old_task = self._tasks.pop(product_id, None)
        if old_task and not old_task.done():
            old_task.cancel()
        await self._stop_client(product_id)

    async def shutdown(self) -> None:
        """Stop all running clients and cancel all tasks."""
        log.info("OTPSessionManager shutting down (%d clients)…", len(self._clients))
        for task in self._tasks.values():
            if not task.done():
                task.cancel()
        for pid in list(self._clients.keys()):
            await self._stop_client(pid)
        self._tasks.clear()
        self._locks.clear()
        log.info("OTPSessionManager shutdown complete.")


# Global singleton
otp_manager = OTPSessionManager()


# ─────────────────────────────────────────────────────────────────────────────
#  WEB3 / BSC SETUP
# ─────────────────────────────────────────────────────────────────────────────

USDT_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to",    "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True,  "name": "from",  "type": "address"},
            {"indexed": True,  "name": "to",    "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"},
        ],
        "name": "Transfer",
        "type": "event",
    },
]

w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(BSC_RPC_URL))


async def get_usdt_balance(address: str) -> Decimal:
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(USDT_CONTRACT_ADDRESS), abi=USDT_ABI,
    )
    raw = await contract.functions.balanceOf(
        Web3.to_checksum_address(address)
    ).call()
    return Decimal(raw) / Decimal(10 ** 18)


async def send_bnb(
    from_address: str, from_privkey: str, to_address: str, amount_bnb: float
) -> str:
    nonce = await w3.eth.get_transaction_count(Web3.to_checksum_address(from_address))
    gas_price = await w3.eth.gas_price
    tx = {
        "nonce": nonce,
        "to": Web3.to_checksum_address(to_address),
        "value": w3.to_wei(amount_bnb, "ether"),
        "gas": 21000,
        "gasPrice": gas_price,
        "chainId": 56,
    }
    signed = w3.eth.account.sign_transaction(tx, private_key=from_privkey)
    tx_hash = await w3.eth.send_raw_transaction(signed.raw_transaction)
    return tx_hash.hex()


async def sweep_usdt(
    user_address: str, user_privkey: str, amount_usdt: Decimal
) -> str:
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(USDT_CONTRACT_ADDRESS), abi=USDT_ABI,
    )
    amount_wei = int(amount_usdt * Decimal(10 ** 18))
    nonce = await w3.eth.get_transaction_count(Web3.to_checksum_address(user_address))
    gas_price = await w3.eth.gas_price
    tx = await contract.functions.transfer(
        Web3.to_checksum_address(MASTER_WALLET_ADDRESS), amount_wei,
    ).build_transaction({
        "chainId": 56, "gas": 65000, "gasPrice": gas_price, "nonce": nonce,
    })
    signed = w3.eth.account.sign_transaction(tx, private_key=user_privkey)
    tx_hash = await w3.eth.send_raw_transaction(signed.raw_transaction)
    return tx_hash.hex()


# ─────────────────────────────────────────────────────────────────────────────
#  FSM STATES
# ─────────────────────────────────────────────────────────────────────────────

class AdminAddNumber(StatesGroup):
    category       = State()
    country        = State()
    phone          = State()
    price          = State()
    session_string = State()
    twofa_password = State()


class AdminFulfillOrder(StatesGroup):
    account_details = State()


class AdminBroadcast(StatesGroup):
    message = State()


class AdminSearchUser(StatesGroup):
    user_input = State()


class AdminDiscountState(StatesGroup):
    discount_pct = State()
    min_deposit  = State()


class AdminUserDiscountState(StatesGroup):
    discount_pct = State()
    min_deposit  = State()


class AdminCreateGiftCode(StatesGroup):
    amount         = State()
    max_claims     = State()
    min_buy_volume = State()


class OxaPayCustomAmount(StatesGroup):
    amount = State()


class AdminCustomCategoryState(StatesGroup):
    name     = State()
    sub_name = State()


class AdminAddPremiumCountry(StatesGroup):
    country = State()
    price   = State()


class AdminFulfillPremiumOrder(StatesGroup):
    phone          = State()
    session_string = State()
    twofa_password = State()


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────────────────────

router = Router()


# ── /start ────────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    parts = message.text.split(maxsplit=1)
    args = parts[1] if len(parts) > 1 else ""
    referred_by: Optional[int] = None
    if args.startswith("ref_"):
        try:
            referred_by = int(args[4:])
            if referred_by == message.from_user.id:
                referred_by = None
        except ValueError:
            referred_by = None

    async with AsyncSessionFactory() as session:
        user = await get_or_create_user(
            session, 
            message.from_user.id, 
            message.from_user.username,
            first_name=message.from_user.first_name or "User",
            referred_by=referred_by,
        )
        if user.is_banned:
            await message.answer("🚫 You have been banned from using this bot.")
            return
        balance = Decimal(str(user.balance or 0))
        first_name = user.first_name or message.from_user.first_name or "User"

    is_admin = message.from_user.id in ADMIN_IDS
    welcome_text = get_welcome_text(first_name, balance)
    await message.answer(
        welcome_text,
        reply_markup=build_main_keyboard(is_admin),
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with AsyncSessionFactory() as session:
        user = await get_or_create_user(
            session,
            message.from_user.id,
            message.from_user.username,
            first_name=message.from_user.first_name or "User",
        )
        balance = Decimal(str(user.balance or 0))
        first_name = user.first_name or message.from_user.first_name or "User"
    
    is_admin = message.from_user.id in ADMIN_IDS
    welcome_text = get_welcome_text(first_name, balance)
    await message.answer(
        welcome_text, 
        reply_markup=build_main_keyboard(is_admin),
        parse_mode=ParseMode.HTML,
    )


# ── Profile ───────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "profile")
async def cb_profile(query: CallbackQuery) -> None:
    await query.answer()
    user_id = query.from_user.id
    async with AsyncSessionFactory() as session:
        user = await get_or_create_user(
            session, user_id, query.from_user.username,
            first_name=query.from_user.first_name,
        )
        
        ref_result, ord_result, bonus_result = await asyncio.gather(
            session.execute(
                select(User).where(User.referred_by == user_id)
            ),
            session.execute(
                select(Order).where(Order.user_id == user_id, Order.status == "Completed")
            ),
            session.execute(
                select(Transaction).where(
                    Transaction.user_id == user_id,
                    Transaction.type.in_(["ReferralBonus", "DepositBonus"]),
                )
            ),
        )
        referrals = ref_result.scalars().all()
        purchases = ord_result.scalars().all()
        bonuses = bonus_result.scalars().all()
        total_bonus = sum(Decimal(str(b.amount)) for b in bonuses)

    first_name = user.first_name or query.from_user.first_name or "User"
    joined = user.created_at.strftime("%Y-%m-%d") if user.created_at else "N/A"
    
    await query.message.edit_text(
        f"<tg-emoji emoji-id='5319175438268913255'>👤</tg-emoji> <b>Your Profile</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id=\"5240228673738527951\">🆔</tg-emoji> <b>User ID:</b> <code>{user.id}</code>\n"
        f"<tg-emoji emoji-id=\"5240228673738527951\">📛</tg-emoji> <b>Name:</b> {first_name}\n"
        f"<tg-emoji emoji-id='5319175438268913255'>👤</tg-emoji> <b>Username:</b> @{user.username or 'Not set'}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5409048419211682843'>💰</tg-emoji> <b>Balance:</b> ${user.balance:.2f} USDT\n"
        f"<tg-emoji emoji-id='5427168083074628963'>💎</tg-emoji> <b>Total Deposited:</b> ${user.total_deposited or 0:.2f}\n"
        f"<tg-emoji emoji-id='5242311354919963946'>🎁</tg-emoji> <b>Total Bonus:</b> ${total_bonus:.2f}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5406683434124859552'>📱</tg-emoji> <b>Numbers Bought:</b> {len(purchases)}\n"
        f"<tg-emoji emoji-id=\"5319175438268913255\">👥</tg-emoji> <b>Total Referrals:</b> {len(referrals)}\n"
        f"<tg-emoji emoji-id=\"5274055917766202507\">📅</tg-emoji> <b>Joined:</b> {joined}\n"
        f"━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="My Purchases", callback_data="my_purchases"), 'primary', "5406683434124859552")],
            [apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


# ── Help ──────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "help")
async def cb_help(query: CallbackQuery) -> None:
    await query.answer()
    await query.message.edit_text(
        get_help_text(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Check Stock", callback_data="check_stock"), 'primary', "5406683434124859552")],
            [apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "check_stock")
async def cb_check_stock(query: CallbackQuery) -> None:
    """Show all available stock by country and category with quantity and price."""
    await query.answer()
    from sqlalchemy import func
    async with AsyncSessionFactory() as session:
        rows = await session.execute(
            select(
                Product.category,
                Product.country,
                func.count(Product.id).label("qty"),
                func.min(Product.price).label("price"),
            )
            .where(Product.status == "Available")
            .group_by(Product.category, Product.country)
            .order_by(Product.category, Product.country)
        )
        stock_data = rows.fetchall()

    if not stock_data:
        await query.message.edit_text(
            "<tg-emoji emoji-id=\"5406683434124859552\">📦</tg-emoji> <b>Current Stock</b>\n\n"
            "😔 No numbers available right now.\n"
            "Check back soon — we restock regularly! 🔄",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Back to Help", callback_data="help"), 'danger', "5416041192905265756"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
        return

    lines = ["<tg-emoji emoji-id=\"5406683434124859552\">📦</tg-emoji> <b>Available Stock</b>\n", "━━━━━━━━━━━━━━━━━━━━━\n"]
    current_cat = None
    total_qty = 0
    for category, country, qty, price in stock_data:
        total_qty += qty
        cat_name = PRODUCT_CATEGORIES.get(category, category)
        if category != current_cat:
            if current_cat is not None:
                lines.append("")
            lines.append(f"<tg-emoji emoji-id=\"5305265301917549162\">📁</tg-emoji> <b>{cat_name}</b>")
            current_cat = category
        flag = get_country_flag(country)
        lines.append(f"  {flag} {country.title()} — {qty} available @ <b>${price:.2f}</b>/each")

    lines.append(f"\n━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📊 <b>Total Available:</b> {total_qty} numbers")
    lines.append(f"\n<i><tg-emoji emoji-id=\"5262844652964303985\">💡</tg-emoji> Prices shown are per number. Tap Buy Accounts to purchase!</i>")

    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Buy Now", callback_data="buy"), 'primary', "5406683434124859552")],
            [apply_button_style(InlineKeyboardButton(text="Back to Help", callback_data="help"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


# ── Deposit ───────────────────────────────────────────────────────────────────

@router.message(Command("deposit"))
async def cmd_deposit(message: Message) -> None:
    """Show deposit options menu."""
    await message.answer(
        "💳 <b>Deposit Funds</b>\n\n"
        "Choose your preferred deposit method:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="OxaPay Crypto", callback_data="oxapay_menu"), 'success', "5427168083074628963")],
            [apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="back_main"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "deposit")
async def cb_deposit(query: CallbackQuery) -> None:
    """Show deposit options menu."""
    await query.answer()
    await query.message.edit_text(
        "💳 <b>Deposit Funds</b>\n\n"
        "Choose your preferred deposit method:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="OxaPay Crypto", callback_data="oxapay_menu"), 'success', "5427168083074628963")],
            [apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


# ── OxaPay Payment System ─────────────────────────────────────────────────────

@router.callback_query(F.data == "oxapay_menu")
async def cb_oxapay_menu(query: CallbackQuery) -> None:
    """Show OxaPay amount selection menu."""
    await query.answer()
    await query.message.edit_text(
        "<tg-emoji emoji-id=\"5427168083074628963\">💎</tg-emoji> <b>OxaPay Crypto Deposit</b>\n\n"
        "Select the amount to deposit:\n\n"
        "<tg-emoji emoji-id=\"5262844652964303985\">💡</tg-emoji> <i>Bonus amounts are added to your balance after payment!</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                apply_button_style(InlineKeyboardButton(text="$1", callback_data="oxapay_1"), 'success', "5409048419211682843"),
                apply_button_style(InlineKeyboardButton(text="$5", callback_data="oxapay_5"), 'success', "5409048419211682843"),
                apply_button_style(InlineKeyboardButton(text="$10", callback_data="oxapay_10"), 'success', "5409048419211682843"),
            ],
            [
                apply_button_style(InlineKeyboardButton(text="$20 (+5%)", callback_data="oxapay_20"), 'success', "5409048419211682843"),
                apply_button_style(InlineKeyboardButton(text="$50 (+10%)", callback_data="oxapay_50"), 'success', "5409048419211682843"),
            ],
            [apply_button_style(InlineKeyboardButton(text="Custom Amount", callback_data="oxapay_custom"), 'primary', "5368341238871248978")],
            [apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="back_main"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("oxapay_") & ~F.data.in_(["oxapay_menu", "oxapay_custom"]))
async def cb_oxapay_amount(query: CallbackQuery) -> None:
    """Process OxaPay payment for preset amounts."""
    try:
        amount = int(query.data.split("_")[1])
    except (ValueError, IndexError):
        await query.answer("❌ Invalid amount.", show_alert=True)
        return
    
    await _create_oxapay_payment(query, amount)


@router.callback_query(F.data == "oxapay_custom")
async def cb_oxapay_custom(query: CallbackQuery, state: FSMContext) -> None:
    """Prompt user for custom deposit amount."""
    await query.answer()
    await state.set_state(OxaPayCustomAmount.amount)
    await query.message.edit_text(
        "✏️ <b>Custom Deposit Amount</b>\n\n"
        "Enter the amount in USD (minimum $1):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="oxapay_cancel"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "oxapay_cancel")
async def cb_oxapay_cancel(query: CallbackQuery, state: FSMContext) -> None:
    """Cancel OxaPay custom amount input."""
    await state.clear()
    await cb_oxapay_menu(query)


@router.message(OxaPayCustomAmount.amount)
async def fsm_oxapay_custom_amount(message: Message, state: FSMContext) -> None:
    """Process custom deposit amount input."""
    await state.clear()
    
    try:
        amount = Decimal(message.text.strip().replace("$", "").replace(",", ""))
        if amount < 1:
            await message.answer(
                "❌ Minimum deposit amount is $1.\n\nPlease try again:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    apply_button_style(InlineKeyboardButton(text="Try Again", callback_data="oxapay_custom"), 'primary', "5427168083074628963"),
                    apply_button_style(InlineKeyboardButton(text="Back", callback_data="deposit"), 'danger', "5416041192905265756"),
                ]]),
                parse_mode=ParseMode.HTML,
            )
            return
        if amount > 10000:
            await message.answer(
                "❌ Maximum deposit amount is $10,000.\n\nPlease try again:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    apply_button_style(InlineKeyboardButton(text="Try Again", callback_data="oxapay_custom"), 'primary', "5427168083074628963"),
                    apply_button_style(InlineKeyboardButton(text="Back", callback_data="deposit"), 'danger', "5416041192905265756"),
                ]]),
                parse_mode=ParseMode.HTML,
            )
            return
    except (ValueError, InvalidOperation):
        await message.answer(
            "❌ Invalid amount. Please enter a valid number like 25 or 50.5",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Try Again", callback_data="oxapay_custom"), 'primary', "5427168083074628963"),
                apply_button_style(InlineKeyboardButton(text="Back", callback_data="deposit"), 'danger', "5416041192905265756"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
        return
    
    # Calculate bonus
    bonus_percent = 0
    for threshold, bonus in sorted(DEPOSIT_BONUSES.items(), reverse=True):
        if amount >= threshold:
            bonus_percent = bonus
            break
    
    bonus_amount = (amount * Decimal(bonus_percent) / Decimal(100)) if bonus_percent > 0 else Decimal(0)
    
    await _create_oxapay_payment_from_message(message, float(amount), float(bonus_amount))


async def _create_oxapay_payment(query: CallbackQuery, amount: int) -> None:
    """Create OxaPay payment invoice for preset amounts."""
    user_id = query.from_user.id
    
    # Calculate bonus
    bonus_percent = DEPOSIT_BONUSES.get(amount, 0)
    bonus_amount = Decimal(amount) * Decimal(bonus_percent) / Decimal(100)
    
    # Generate unique track ID
    track_id = f"dep_{user_id}_{uuid.uuid4().hex[:8]}"
    
    # Create payment request to OxaPay
    try:
        async with aiohttp.ClientSession() as http_session:
            payload = {
                "merchant": OXAPAY_API_KEY,
                "amount": amount,
                "currency": "USD",
                "lifeTime": 60,  # 60 minutes
                "callbackUrl": f"https://{OXAPAY_CALLBACK_DOMAIN}/oxapay/callback",
                "returnUrl": f"https://{OXAPAY_CALLBACK_DOMAIN}/success",
                "description": f"Deposit ${amount} USDT",
                "orderId": track_id,
            }
            
            async with http_session.post(OXAPAY_API_URL, json=payload) as resp:
                if resp.status != 200:
                    log.error("OxaPay API error: status %d", resp.status)
                    await query.message.edit_text(
                        "❌ Payment system temporarily unavailable.\n\nPlease try again later.",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                            apply_button_style(InlineKeyboardButton(text="Retry", callback_data="oxapay_menu"), 'primary', "5427168083074628963"),
                            apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756"),
                        ]]),
                        parse_mode=ParseMode.HTML,
                    )
                    await query.answer()
                    return
                
                data = await resp.json()
                
                if data.get("result") != 100:
                    log.error("OxaPay error: %s", data)
                    await query.message.edit_text(
                        f"❌ Payment creation failed.\n\nError: {data.get('message', 'Unknown error')}",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                            apply_button_style(InlineKeyboardButton(text="Retry", callback_data="oxapay_menu"), 'primary', "5427168083074628963"),
                            apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756"),
                        ]]),
                        parse_mode=ParseMode.HTML,
                    )
                    await query.answer()
                    return
                
                pay_link = data.get("payLink")
                oxapay_track_id = data.get("trackId")
                
    except Exception as exc:
        log.error("OxaPay request error: %s", exc)
        await query.message.edit_text(
            "❌ Connection error. Please try again.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Retry", callback_data="oxapay_menu"), 'primary', "5427168083074628963"),
                apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
        await query.answer()
        return
    
    # Store payment in database
    async with AsyncSessionFactory() as session:
        payment = OxaPayPayment(
            user_id=user_id,
            track_id=oxapay_track_id or track_id,
            amount=Decimal(amount),
            bonus_amount=bonus_amount,
            status="Waiting",
            pay_link=pay_link,
        )
        session.add(payment)
        await session.commit()
    
    # Show payment link to user
    bonus_text = f"\n<tg-emoji emoji-id=\"5242311354919963946\">🎁</tg-emoji> <b>Bonus:</b> +${bonus_amount:.2f} ({bonus_percent}%)" if bonus_percent > 0 else ""
    
    await query.message.edit_text(
        f"<tg-emoji emoji-id=\"5427168083074628963\">💎</tg-emoji> <b>OxaPay Payment</b>\n\n"
        f"<tg-emoji emoji-id=\"5409048419211682843\">💵</tg-emoji> <b>Amount:</b> ${amount:.2f}{bonus_text}\n"
        f"📝 <b>Order ID:</b> <code>{oxapay_track_id or track_id}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Click the button below to complete your payment.\n"
        f"Your balance will be updated automatically!\n\n"
        f"⏰ <i>Payment expires in 60 minutes</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Pay Now", url=pay_link), 'success', "5409048419211682843")],
            [apply_button_style(InlineKeyboardButton(text="Check Status", callback_data=f"oxapay_check_{oxapay_track_id or track_id}"), 'primary', "5206607081334906820")],
            [apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="back_main"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )
    await query.answer()


async def _create_oxapay_payment_from_message(message: Message, amount: float, bonus_amount: float) -> None:
    """Create OxaPay payment from message (for custom amounts)."""
    user_id = message.from_user.id
    
    # Calculate bonus percentage for display
    bonus_percent = 0
    for threshold, bonus in sorted(DEPOSIT_BONUSES.items(), reverse=True):
        if amount >= threshold:
            bonus_percent = bonus
            break
    
    # Generate unique track ID  
    track_id = f"dep_{user_id}_{uuid.uuid4().hex[:8]}"
    
    # Create payment request to OxaPay
    try:
        async with aiohttp.ClientSession() as http_session:
            payload = {
                "merchant": OXAPAY_API_KEY,
                "amount": amount,
                "currency": "USD",
                "lifeTime": 60,
                "callbackUrl": f"https://{OXAPAY_CALLBACK_DOMAIN}/oxapay/callback",
                "returnUrl": f"https://{OXAPAY_CALLBACK_DOMAIN}/success",
                "description": f"Deposit ${amount:.2f} USDT",
                "orderId": track_id,
            }
            
            async with http_session.post(OXAPAY_API_URL, json=payload) as resp:
                if resp.status != 200:
                    await message.answer(
                        "❌ Payment system temporarily unavailable.\n\nPlease try again later.",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                            apply_button_style(InlineKeyboardButton(text="Retry", callback_data="oxapay_custom"), 'primary', "5427168083074628963"),
                            apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756"),
                        ]]),
                        parse_mode=ParseMode.HTML,
                    )
                    return
                
                data = await resp.json()
                
                if data.get("result") != 100:
                    await message.answer(
                        f"❌ Payment creation failed.\n\nError: {data.get('message', 'Unknown error')}",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                            apply_button_style(InlineKeyboardButton(text="Retry", callback_data="oxapay_custom"), 'primary', "5427168083074628963"),
                            apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756"),
                        ]]),
                        parse_mode=ParseMode.HTML,
                    )
                    return
                
                pay_link = data.get("payLink")
                oxapay_track_id = data.get("trackId")
                
    except Exception as exc:
        log.error("OxaPay request error: %s", exc)
        await message.answer(
            "❌ Connection error. Please try again.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Retry", callback_data="oxapay_custom"), 'primary', "5427168083074628963"),
                apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
        return
    
    # Store payment in database
    async with AsyncSessionFactory() as session:
        payment = OxaPayPayment(
            user_id=user_id,
            track_id=oxapay_track_id or track_id,
            amount=Decimal(str(amount)),
            bonus_amount=Decimal(str(bonus_amount)),
            status="Waiting",
            pay_link=pay_link,
        )
        session.add(payment)
        await session.commit()
    
    # Show payment link to user
    bonus_text = f"\n<tg-emoji emoji-id=\"5242311354919963946\">🎁</tg-emoji> <b>Bonus:</b> +${bonus_amount:.2f} ({bonus_percent}%)" if bonus_percent > 0 else ""
    
    await message.answer(
        f"<tg-emoji emoji-id=\"5427168083074628963\">💎</tg-emoji> <b>OxaPay Payment</b>\n\n"
        f"<tg-emoji emoji-id=\"5409048419211682843\">💵</tg-emoji> <b>Amount:</b> ${amount:.2f}{bonus_text}\n"
        f"📝 <b>Order ID:</b> <code>{oxapay_track_id or track_id}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Click the button below to complete your payment.\n"
        f"Your balance will be updated automatically!\n\n"
        f"⏰ <i>Payment expires in 60 minutes</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Pay Now", url=pay_link), 'success', "5409048419211682843")],
            [apply_button_style(InlineKeyboardButton(text="Check Status", callback_data=f"oxapay_check_{oxapay_track_id or track_id}"), 'primary', "5206607081334906820")],
            [apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="back_main"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("oxapay_check_"))
async def cb_oxapay_check(query: CallbackQuery) -> None:
    """Check OxaPay payment status."""
    track_id = query.data.replace("oxapay_check_", "")
    
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(OxaPayPayment).where(OxaPayPayment.track_id == track_id)
        )
        payment = result.scalar_one_or_none()
        
        if payment is None:
            await query.answer("❌ Payment not found.", show_alert=True)
            return
        
        if payment.status == "Confirmed":
            await query.answer("✅ Payment already confirmed!", show_alert=True)
            return
    
    # Check with OxaPay API
    try:
        async with aiohttp.ClientSession() as http_session:
            payload = {
                "merchant": OXAPAY_API_KEY,
                "trackId": track_id,
            }
            
            async with http_session.post(OXAPAY_INQUIRY_URL, json=payload) as resp:
                if resp.status != 200:
                    await query.answer("⏳ Checking... Please wait.", show_alert=True)
                    return
                
                data = await resp.json()
                status = data.get("status", "").lower()
                
                if status in ["paid", "confirmed"]:
                    # Payment confirmed! Credit user
                    await _process_oxapay_confirmation(payment, data)
                    await query.answer("✅ Payment confirmed! Balance updated.", show_alert=True)
                    
                    # Update message
                    await query.message.edit_text(
                        f"<tg-emoji emoji-id=\"5206607081334906820\">✅</tg-emoji> <b>Payment Confirmed!</b>\n\n"
                        f"<tg-emoji emoji-id=\"5409048419211682843\">💵</tg-emoji> <b>Amount:</b> ${payment.amount:.2f}\n"
                        f"<tg-emoji emoji-id=\"5242311354919963946\">🎁</tg-emoji> <b>Bonus:</b> +${payment.bonus_amount:.2f}\n"
                        f"📝 <b>Order ID:</b> <code>{track_id}</code>\n\n"
                        f"Your balance has been updated!",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                            apply_button_style(InlineKeyboardButton(text="Back to Menu", callback_data="back_main"), 'danger', "5416041192905265756"),
                        ]]),
                        parse_mode=ParseMode.HTML,
                    )
                elif status == "expired":
                    await query.answer("❌ Payment expired. Please create a new one.", show_alert=True)
                    async with AsyncSessionFactory() as session:
                        await session.execute(
                            update(OxaPayPayment)
                            .where(OxaPayPayment.track_id == track_id)
                            .values(status="Expired", updated_at=datetime.now(timezone.utc))
                        )
                        await session.commit()
                else:
                    await query.answer(f"⏳ Payment status: {status}. Please complete payment.", show_alert=True)
                    
    except Exception as exc:
        log.error("OxaPay inquiry error: %s", exc)
        await query.answer("⏳ Checking... Please wait and try again.", show_alert=True)


async def _process_oxapay_confirmation(payment: OxaPayPayment, data: dict) -> None:
    """Process confirmed OxaPay payment and credit user."""
    async with AsyncSessionFactory() as session:
        # Update payment status
        await session.execute(
            update(OxaPayPayment)
            .where(OxaPayPayment.id == payment.id)
            .values(status="Confirmed", updated_at=datetime.now(timezone.utc))
        )
        
        # Credit user balance
        total_credit = Decimal(str(payment.amount)) + Decimal(str(payment.bonus_amount))
        await session.execute(
            update(User)
            .where(User.id == payment.user_id)
            .values(
                balance=User.balance + total_credit,
                total_deposited=User.total_deposited + Decimal(str(payment.amount)),
                total_bonus_received=User.total_bonus_received + Decimal(str(payment.bonus_amount)),
            )
        )
        
        # Record transaction
        txn = Transaction(
            user_id=payment.user_id,
            type="OxaPayDeposit",
            amount=payment.amount,
            bonus=payment.bonus_amount,
            tx_hash=payment.track_id,
            status="Completed",
        )
        session.add(txn)
        
        # Handle referral commission
        user_result = await session.execute(
            select(User).where(User.id == payment.user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user and user.referred_by:
            commission = (
                Decimal(str(payment.amount))
                * Decimal(str(REFERRAL_COMMISSION_PCT))
                / Decimal(100)
            )
            await session.execute(
                update(User)
                .where(User.id == user.referred_by)
                .values(balance=User.balance + commission)
            )
            ref_txn = Transaction(
                user_id=user.referred_by,
                type="ReferralBonus",
                amount=commission,
                tx_hash=payment.track_id,
                status="Completed",
            )
            session.add(ref_txn)
        
        await session.commit()


# ── Buy flow ──────────────────────────────────────────────────────────────────

async def get_applicable_discount(session: AsyncSession, user_id: int, total_deposited: Decimal) -> Decimal:
    """
    Returns the applicable discount percentage for a user.
    Checks user-specific discount first, then global tiers.
    """
    # Check user-specific discount first
    user_disc_res = await session.execute(
        select(UserDiscount).where(UserDiscount.user_id == user_id)
    )
    user_disc = user_disc_res.scalar_one_or_none()
    if user_disc is not None and total_deposited >= Decimal(str(user_disc.min_deposit)):
        return Decimal(str(user_disc.discount_pct))

    # Check global tiers - return highest applicable discount
    tiers_res = await session.execute(
        select(DiscountTier).order_by(DiscountTier.min_deposit.desc())
    )
    tiers = tiers_res.scalars().all()
    for tier in tiers:
        if total_deposited >= Decimal(str(tier.min_deposit)):
            return Decimal(str(tier.discount_pct))

    return Decimal("0")


async def post_to_log_channel(bot: Bot, user_display: str, category: str, country: str, price: Decimal, phone_number: str, discount_pct: Decimal = Decimal("0"), user_id=None, total_deposited: Decimal = Decimal("0")) -> None:
    """Post purchase details to the log channel if configured."""
    if not LOG_CHANNEL:
        return
    try:
        cat_name = PRODUCT_CATEGORIES.get(category, category)
        flag = get_country_flag(country)
        # Show only first half of the number for privacy
        half = max(3, len(phone_number) // 2)
        masked_phone = phone_number[:half] + "X" * (len(phone_number) - half)
        disc_line = f"\n🏷️ <b>Discount Applied:</b> {discount_pct:.0f}%" if discount_pct > 0 else ""
        await bot.send_message(
            f"@{LOG_CHANNEL}",
            f"🛒 <b>New Purchase!</b>\n\n"
            f"👤 <b>Buyer:</b> {user_display}\n"
            f"💰 <b>Total Deposited:</b> ${total_deposited:.2f} USDT\n"
            f"📁 <b>Category:</b> {cat_name}\n"
            f"🌍 <b>Country:</b> {flag} {country.title()}\n"
            f"📱 <b>Number:</b> <code>{masked_phone}</code>\n"
            f"💵 <b>Price Paid:</b> ${price:.2f} USDT"
            f"{disc_line}\n\n"
            f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            parse_mode=ParseMode.HTML,
        )
    except Exception as exc:
        log.warning("Could not post to log channel: %s", exc)


PAGE_SIZE = 10
MAX_DISPLAY_ITEMS = 20


@router.message(Command("buy"))
async def cmd_buy(message: Message) -> None:
    """Show main buy menu with categories."""
    async with AsyncSessionFactory() as session:
        cc_rows = await session.execute(select(CustomCategory).order_by(CustomCategory.created_at))
        custom_cats = cc_rows.scalars().all()

    kb_rows = [
        [apply_button_style(InlineKeyboardButton(text="Telegram Accounts", callback_data="buy_cat_telegram"), 'primary', "5197252827247841976")],
        [apply_button_style(InlineKeyboardButton(text="Telegram Sessions", callback_data=f"buy_cat_{CATEGORY_TELEGRAM_SESSIONS}"), 'primary', "5197252827247841976")],
    ]
    for cc in custom_cats:
        cb = f"buy_custom_sub_{cc.slug}" if cc.sub_name else f"buy_cat_{cc.slug}"
        kb_rows.append([apply_button_style(InlineKeyboardButton(text=cc.name, callback_data=cb), 'primary', "5197252827247841976")])
    kb_rows.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756")])

    await message.answer(
        "<tg-emoji emoji-id=\"5406683434124859552\">🛍️</tg-emoji> <b>Buy Accounts</b>\n\n"
        "Select a category to browse:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "buy")
async def cb_buy(query: CallbackQuery) -> None:
    """Show main buy menu with categories."""
    await query.answer()
    async with AsyncSessionFactory() as session:
        cc_rows = await session.execute(select(CustomCategory).order_by(CustomCategory.created_at))
        custom_cats = cc_rows.scalars().all()

    kb_rows = [
        [apply_button_style(InlineKeyboardButton(text="Telegram Accounts", callback_data="buy_cat_telegram"), 'primary', "5197252827247841976")],
        [apply_button_style(InlineKeyboardButton(text="Telegram Sessions", callback_data=f"buy_cat_{CATEGORY_TELEGRAM_SESSIONS}"), 'primary', "5197252827247841976")],
    ]
    for cc in custom_cats:
        cb = f"buy_custom_sub_{cc.slug}" if cc.sub_name else f"buy_cat_{cc.slug}"
        kb_rows.append([apply_button_style(InlineKeyboardButton(text=cc.name, callback_data=cb), 'primary', "5197252827247841976")])
    kb_rows.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756")])

    await query.message.edit_text(
        "<tg-emoji emoji-id=\"5406683434124859552\">🛍️</tg-emoji> <b>Buy Accounts</b>\n\n"
        "Select a category to browse:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "buy_cat_telegram")
async def cb_buy_cat_telegram(query: CallbackQuery) -> None:
    """Show Telegram account subcategories."""
    await query.answer()
    await query.message.edit_text(
        "<tg-emoji emoji-id=\"5197252827247841976\">📱</tg-emoji> <b>Telegram Accounts</b>\n\n"
        "Choose account type:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Telegram Accounts", callback_data=f"buy_cat_{CATEGORY_TELEGRAM_ACCOUNTS}"), 'primary', "5197252827247841976")],
            [apply_button_style(InlineKeyboardButton(text="Telegram Old Accounts", callback_data=f"buy_cat_{CATEGORY_TELEGRAM_OLD}"), 'primary', "5197252827247841976")],
            [apply_button_style(InlineKeyboardButton(text="Telegram Premium", callback_data="buy_prem"), 'success', "5453901475648390219")],
            [apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("buy_custom_sub_"))
async def cb_buy_custom_sub(query: CallbackQuery) -> None:
    """Show sub-menu for a custom category that has a sub_name."""
    await query.answer()
    slug = query.data.replace("buy_custom_sub_", "")
    async with AsyncSessionFactory() as session:
        cc_res = await session.execute(select(CustomCategory).where(CustomCategory.slug == slug))
        cc = cc_res.scalar_one_or_none()
    if not cc:
        await query.answer("Category not found.", show_alert=True)
        return
    await query.message.edit_text(
        f"<tg-emoji emoji-id=\"5197252827247841976\">📱</tg-emoji> <b>{cc.name}</b>\n\n"
        "Choose a subcategory:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text=cc.sub_name, callback_data=f"buy_cat_{slug}"), 'primary', "5197252827247841976")],
            [apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("buy_cat_"))
async def cb_buy_category(query: CallbackQuery) -> None:
    """Show countries for selected category."""
    await query.answer()
    category = query.data.replace("buy_cat_", "")
    
    if category == "telegram":
        # This is handled separately above
        return

    if category == CATEGORY_TELEGRAM_OLD:
        # Show year selection instead of countries directly
        await _show_old_account_years(query.message, edit=True)
        return

    await _show_category_countries(query.message, category, page=0, edit=True)


@router.callback_query(F.data.startswith("cat_countries_"))
async def cb_cat_countries_page(query: CallbackQuery) -> None:
    """Handle pagination for category countries."""
    await query.answer()
    # Format: cat_countries_{category}_{page}
    parts = query.data.replace("cat_countries_", "").rsplit("_", 1)
    if len(parts) != 2:
        await query.answer("Invalid request", show_alert=True)
        return
    
    category, page_str = parts
    try:
        page = int(page_str)
    except ValueError:
        page = 0
    
    await _show_category_countries(query.message, category, page=page, edit=True)


async def _show_category_countries(
    message: Message, category: str, page: int = 0, edit: bool = False
) -> None:
    """Show available countries for a specific category with availability counts."""
    category_name = PRODUCT_CATEGORIES.get(category)
    _custom_cat_sub = None
    if category_name is None:
        async with AsyncSessionFactory() as session:
            cc_res = await session.execute(select(CustomCategory).where(CustomCategory.slug == category))
            _cc = cc_res.scalar_one_or_none()
            if _cc:
                category_name = _cc.name
                _custom_cat_sub = _cc.sub_name
            else:
                category_name = "Unknown Category"
    
    async with AsyncSessionFactory() as session:
        # Get distinct countries with available count for this category
        from sqlalchemy import func
        rows = await session.execute(
            select(Product.country, func.count(Product.id).label("count"))
            .where(Product.status == "Available", Product.category == category)
            .group_by(Product.country)
            .order_by(Product.country)
        )
        countries_data = rows.fetchall()

    if not countries_data:
        text = f'<tg-emoji emoji-id="5224607267797606837">😔</tg-emoji> No {category_name} available right now.\n\nCheck back later!'
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy"), 'danger', "5416041192905265756"),
        ]])
        if edit:
            await message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
        else:
            await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
        return

    total_pages = (len(countries_data) + PAGE_SIZE - 1) // PAGE_SIZE
    page_data = countries_data[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]

    # Build buttons 2 countries per row
    buttons = []
    row: list[InlineKeyboardButton] = []
    for country, count in page_data:
        btn = apply_button_style(InlineKeyboardButton(
            text=f"{get_country_flag(country)} {country.title()} ({count})",
            callback_data=f"cat_country_{category}|{country}",
        ), 'primary', "5240428351063081133")
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    nav_row: list[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(
            apply_button_style(InlineKeyboardButton(text="Prev", callback_data=f"cat_countries_{category}_{page - 1}"), 'primary', "5416041192905265756")
        )
    if page < total_pages - 1:
        nav_row.append(
            apply_button_style(InlineKeyboardButton(text="Next", callback_data=f"cat_countries_{category}_{page + 1}"), 'primary', "5416117059207572332")
        )
    if nav_row:
        buttons.append(nav_row)
    
    # Back button based on category
    if category in [CATEGORY_TELEGRAM_ACCOUNTS, CATEGORY_TELEGRAM_OLD]:
        buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy_cat_telegram"), 'danger', "5416041192905265756")])
    elif _custom_cat_sub:
        buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"buy_custom_sub_{category}"), 'danger', "5416041192905265756")])
    else:
        buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy"), 'danger', "5416041192905265756")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    text = (
        f"{category_name}\n\n"
        f"<tg-emoji emoji-id=\"5460755126761312667\">🌍</tg-emoji> <b>Select a Country</b> (Page {page + 1}/{total_pages}):\n"
        f"<i>Number in brackets = Available count</i>"
    )
    if edit:
        await message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("cat_country_"))
async def cb_cat_country(query: CallbackQuery) -> None:
    """Show country availability info and buy button."""
    # Format: cat_country_{category}|{country}
    parts = query.data.replace("cat_country_", "").split("|", 1)
    if len(parts) != 2:
        await query.answer("Invalid request", show_alert=True)
        return

    category, country = parts
    category_name = PRODUCT_CATEGORIES.get(category, "Unknown")

    async with AsyncSessionFactory() as session:
        # Get available count and price for this country/category
        rows = await session.execute(
            select(Product)
            .where(
                Product.country == country,
                Product.category == category,
                Product.status == "Available"
            )
            .order_by(Product.price)
        )
        products = rows.scalars().all()

    if not products:
        await query.answer()
        await query.message.edit_text(
            f"😔 <b>No numbers available</b> for "
            f"{get_country_flag(country)} {country.title()} right now.\n\n"
            f"Please check back later or choose another country.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"buy_cat_{category}"), 'danger', "5416041192905265756"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
        return

    await query.answer()
    available_count = len(products)
    price = Decimal(str(products[0].price))  # All should have same price per country

    # Get user's applicable discount
    user_id = query.from_user.id
    async with AsyncSessionFactory() as disc_session:
        u_res = await disc_session.execute(select(User).where(User.id == user_id))
        u_obj = u_res.scalar_one_or_none()
        total_dep = Decimal(str(u_obj.total_deposited or 0)) if u_obj else Decimal("0")
        disc_pct = await get_applicable_discount(disc_session, user_id, total_dep)

    if disc_pct > 0:
        discounted_price = price * (1 - disc_pct / 100)
        price_line = f"💰 <b>Price:</b> <s>${price:.2f}</s> → <b>${discounted_price:.2f} USDT</b> ({disc_pct:.0f}% off 🎉)\n"
    else:
        price_line = f"💰 <b>Price per Number:</b> ${price:.2f} USDT\n"

    await query.message.edit_text(
        f"🌍 <b>{get_country_flag(country)} {country.title()}</b>\n"
        f"📁 <b>Category:</b> {category_name}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 <b>Available Numbers:</b> {available_count}\n"
        f"{price_line}"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Click <b>Buy Now</b> to purchase a random number from this pool.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Buy Now", callback_data=f"buy_confirm_{category}|{country}"), 'primary', "5406683434124859552")],
            [apply_button_style(InlineKeyboardButton(text="Cancel", callback_data=f"buy_cat_{category}"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("buy_confirm_"))
async def cb_buy_confirm(query: CallbackQuery) -> None:
    """Show purchase confirmation dialog before buying."""
    await query.answer()
    # Format: buy_confirm_{category}|{country}
    parts = query.data.replace("buy_confirm_", "").split("|", 1)
    if len(parts) != 2:
        await query.answer("Invalid request", show_alert=True)
        return

    category, country = parts
    user_id = query.from_user.id

    async with AsyncSessionFactory() as session:
        user = await get_or_create_user(
            session, user_id, query.from_user.username,
            first_name=query.from_user.first_name,
        )

        if user.is_banned:
            await query.answer("🚫 You are banned from using this bot.", show_alert=True)
            return

        rows = await session.execute(
            select(Product)
            .where(
                Product.country == country,
                Product.category == category,
                Product.status == "Available"
            )
            .order_by(Product.price)
        )
        products = rows.scalars().all()

    if not products:
        await query.message.edit_text(
            "❌ <b>No Numbers Available</b>\n\nThis country's stock is now empty. "
            "Please choose another country.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"buy_cat_{category}"), 'danger', "5416041192905265756"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
        return

    price = Decimal(str(products[0].price))
    available_count = len(products)
    user_balance = Decimal(str(user.balance or 0))
    can_afford = user_balance >= price
    flag = get_country_flag(country)
    balance_after = user_balance - price if can_afford else user_balance

    if can_afford:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(
                text="Confirm Purchase",
                callback_data=f"buy_execute_{category}|{country}",
            ), 'primary', "5206607081334906820")],
            [apply_button_style(InlineKeyboardButton(
                text="Cancel",
                callback_data=f"cat_country_{category}|{country}",
            ), 'danger', "5416041192905265756")],
        ])
        balance_line = (
            f"💰 <b>Your Balance:</b> ${user_balance:.2f} USDT\n"
            f"💵 <b>Cost:</b> ${price:.2f} USDT\n"
            f"📉 <b>Balance after purchase:</b> ${balance_after:.2f} USDT"
        )
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Deposit Funds", callback_data="deposit"), 'primary', "5424976816530014958")],
            [apply_button_style(InlineKeyboardButton(
                text="Cancel",
                callback_data=f"cat_country_{category}|{country}",
            ), 'danger', "5416041192905265756")],
        ])
        balance_line = (
            f"💰 <b>Your Balance:</b> ${user_balance:.2f} USDT\n"
            f"💵 <b>Required:</b> ${price:.2f} USDT\n\n"
            f"❌ <b>Insufficient balance.</b> Please deposit funds first."
        )

    await query.message.edit_text(
        f"🛒 <b>Confirm Purchase</b>\n\n"
        f"🌍 <b>Country:</b> {flag} {country.title()}\n"
        f"📱 <b>Available:</b> {available_count} number(s)\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{balance_line}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{'Tap <b>Confirm Purchase</b> to proceed.' if can_afford else 'Deposit to unlock purchase.'}",
        reply_markup=kb,
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("buy_execute_"))
async def cb_buy_execute(query: CallbackQuery) -> None:
    """Process purchase - randomly assign a number from the pool."""
    await query.answer()
    # Format: buy_execute_{category}|{country}
    parts = query.data.replace("buy_execute_", "").split("|", 1)
    if len(parts) != 2:
        await query.answer("Invalid request", show_alert=True)
        return

    category, country = parts
    user_id = query.from_user.id

    async with AsyncSessionFactory() as session:
        # Get user
        user = await get_or_create_user(
            session, user_id, query.from_user.username,
            first_name=query.from_user.first_name,
        )

        if user.is_banned:
            await query.answer("🚫 You are banned from using this bot.", show_alert=True)
            return

        # Get available products for this category/country
        rows = await session.execute(
            select(Product)
            .where(
                Product.country == country,
                Product.category == category,
                Product.status == "Available"
            )
        )
        available_products = rows.scalars().all()

        if not available_products:
            await query.message.edit_text(
                "❌ <b>No numbers available.</b>\n\nThis stock just ran out. "
                "Please try another country.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"buy_cat_{category}"), 'danger', "5416041192905265756"),
                ]]),
                parse_mode=ParseMode.HTML,
            )
            return

        # Securely randomly select one product
        product = secrets.choice(available_products)

        # Check balance
        if Decimal(str(user.balance)) < Decimal(str(product.price)):
            await query.message.edit_text(
                f"❌ <b>Insufficient Balance</b>\n\n"
                f"💰 Your balance: <b>${user.balance:.2f}</b>\n"
                f"💵 Required: <b>${product.price:.2f}</b>\n\n"
                f"Please deposit funds first.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [apply_button_style(InlineKeyboardButton(text="Deposit", callback_data="deposit"), 'primary', "5424976816530014958")],
                    [apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"cat_country_{category}|{country}"), 'danger', "5416041192905265756")],
                ]),
                parse_mode=ParseMode.HTML,
            )
            return

        # Apply discount
        base_price = Decimal(str(product.price))
        total_deposited_user = Decimal(str(user.total_deposited or 0))
        disc_pct = await get_applicable_discount(session, user_id, total_deposited_user)
        actual_price = base_price * (1 - disc_pct / 100) if disc_pct > 0 else base_price

        # Re-check balance with discounted price
        if Decimal(str(user.balance)) < actual_price:
            await query.message.edit_text(
                f"❌ <b>Insufficient Balance</b>\n\n"
                f"💰 Your balance: <b>${user.balance:.2f}</b>\n"
                f"💵 Required: <b>${actual_price:.2f}</b>\n\n"
                f"Please deposit funds first.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [apply_button_style(InlineKeyboardButton(text="Deposit", callback_data="deposit"), 'primary', "5424976816530014958")],
                    [apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"cat_country_{category}|{country}"), 'danger', "5416041192905265756")],
                ]),
                parse_mode=ParseMode.HTML,
            )
            return

        # Process purchase
        new_balance = Decimal(str(user.balance)) - actual_price
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                balance=new_balance,
                numbers_bought=User.numbers_bought + 1
            )
        )
        await session.execute(
            update(Product)
            .where(Product.id == product.id)
            .values(status="Sold")
        )

        order = Order(user_id=user_id, product_id=product.id, status="Completed")
        session.add(order)
        await session.flush()

        txn = Transaction(
            user_id=user_id,
            order_id=order.id,
            type="Purchase",
            amount=actual_price,
            status="Completed",
        )
        session.add(txn)
        await session.commit()

        phone = product.phone_number
        price = actual_price
        sess_str = product.session_string
        twofa_enc = product.twofa_password
        pid = product.id

    # Clear any stale OTP from previous ownership
    async with AsyncSessionFactory() as session:
        await session.execute(
            update(Product)
            .where(Product.id == pid)
            .values(latest_otp=None, otp_updated_at=None)
        )
        await session.commit()

    # Start the background OTP listener via the manager
    if sess_str:
        await otp_manager.start_listener(pid, sess_str)

    # Post to log channel
    _uname = query.from_user.username
    user_display = f"@{_uname}" if _uname else str(query.from_user.id)
    async with AsyncSessionFactory() as _log_session:
        _log_user = await _log_session.execute(select(User).where(User.id == user_id))
        _log_user_obj = _log_user.scalar_one_or_none()
        _total_dep = Decimal(str(_log_user_obj.total_deposited or 0)) if _log_user_obj else Decimal("0")
    await post_to_log_channel(query.bot, user_display, category, country, price, phone, disc_pct, user_id=user_id, total_deposited=_total_dep)
    twofa_line = ""
    if twofa_enc:
        try:
            twofa_plain = decrypt_privkey(twofa_enc)
            twofa_line = f"🔐 <b>2FA Password:</b> <code>{twofa_plain}</code>\n"
        except Exception:
            pass

    # Session string is only shown for Telegram Sessions category
    if category == CATEGORY_TELEGRAM_SESSIONS:
        session_line = format_session_preview(sess_str) + "\n"
    else:
        session_line = ""

    disc_line = f"<tg-emoji emoji-id=\"5240228673738527951\">🏷️</tg-emoji> <b>Discount:</b> {disc_pct:.0f}% off\n" if disc_pct > 0 else ""
    await query.message.edit_text(
        f"<tg-emoji emoji-id=\"5461151367559141950\">🎉</tg-emoji> <b>Purchase Successful!</b>\n\n"
        f"<tg-emoji emoji-id=\"5197252827247841976\">📱</tg-emoji> <b>Number:</b> <code>{phone}</code>\n"
        f"<tg-emoji emoji-id=\"5460755126761312667\">🌍</tg-emoji> <b>Country:</b> {get_country_flag(country)} {country.title()}\n"
        f"<tg-emoji emoji-id=\"5409048419211682843\">💵</tg-emoji> <b>Paid:</b> ${price:.2f} USDT\n"
        f"{disc_line}"
        f"{session_line}"
        f"{twofa_line}"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id=\"5274055917766202507\">📋</tg-emoji> <b>Next Steps:</b>\n"
        f"<tg-emoji emoji-id=\"5382322671679708881\">1️⃣</tg-emoji> Open <b>Telegram / Telegram X / TurboTel</b>\n"
        f"<tg-emoji emoji-id=\"5381990043642502553\">2️⃣</tg-emoji> Enter the number: <code>{phone}</code>\n"
        f"<tg-emoji emoji-id=\"5381879959335738545\">3️⃣</tg-emoji> Tap <b>Send Code</b> in Telegram\n"
        f"<tg-emoji emoji-id=\"5382054253403577563\">4️⃣</tg-emoji> Come back here and press <b>🔄 Get OTP</b>\n\n"
        f"<tg-emoji emoji-id=\"5411590687663608498\">⚡</tg-emoji> OTP is fetched <b>instantly</b> from the account!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Get OTP", callback_data=f"getotp_{pid}"), 'primary', "5449569374065152798")],
            [apply_button_style(InlineKeyboardButton(text="Main Menu", callback_data="back_main"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


# ── Telegram Old Accounts – Year-based Buy Flow ───────────────────────────────

async def _show_old_account_years(message: Message, edit: bool = False) -> None:
    """Show available years for Telegram Old Accounts (only years with stock)."""
    async with AsyncSessionFactory() as session:
        rows = await session.execute(
            select(Product.year)
            .where(
                Product.category == CATEGORY_TELEGRAM_OLD,
                Product.status == "Available",
                Product.year.isnot(None),
            )
            .distinct()
            .order_by(Product.year)
        )
        years = [r[0] for r in rows.fetchall()]

    if not years:
        text = '<tg-emoji emoji-id="5224607267797606837">😔</tg-emoji> No <tg-emoji emoji-id="5197252827247841976">📱</tg-emoji> Telegram Old Accounts available right now.\n\nCheck back later!'
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy_cat_telegram"), 'danger', "5416041192905265756"),
        ]])
        if edit:
            await message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
        else:
            await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
        return

    # 3 year buttons per row
    year_buttons: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for yr in years:
        btn = apply_button_style(InlineKeyboardButton(
            text=str(yr),
            callback_data=f"tgold_yr_{yr}",
        ), 'primary', "5416041192905265756")
        row.append(btn)
        if len(row) == 3:
            year_buttons.append(row)
            row = []
    if row:
        year_buttons.append(row)
    year_buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy_cat_telegram"), 'danger', "5416041192905265756")])

    kb = InlineKeyboardMarkup(inline_keyboard=year_buttons)
    text_msg = (
        "📱 <b>Telegram Old Accounts</b>\n\n"
        "🗓️ <b>Select a Year:</b>\n"
        "<i>Only years with available stock are shown</i>"
    )
    if edit:
        await message.edit_text(text_msg, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await message.answer(text_msg, reply_markup=kb, parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("tgold_yr_"))
async def cb_tgold_year(query: CallbackQuery) -> None:
    """User selected a year for Telegram Old Accounts."""
    await query.answer()
    try:
        year = int(query.data.replace("tgold_yr_", ""))
    except ValueError:
        await query.answer("Invalid request", show_alert=True)
        return
    await _show_old_account_countries(query.message, year, edit=True)


async def _show_old_account_countries(
    message: Message, year: int, edit: bool = False
) -> None:
    """Show countries with available Telegram Old Accounts for a specific year (2 per row)."""
    from sqlalchemy import func
    async with AsyncSessionFactory() as session:
        rows = await session.execute(
            select(Product.country, func.count(Product.id).label("count"))
            .where(
                Product.category == CATEGORY_TELEGRAM_OLD,
                Product.status == "Available",
                Product.year == year,
            )
            .group_by(Product.country)
            .order_by(Product.country)
        )
        countries_data = rows.fetchall()

    if not countries_data:
        text = f"😔 No Telegram Old Accounts available for {year}.\n\nCheck back later!"
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"buy_cat_{CATEGORY_TELEGRAM_OLD}"), 'danger', "5416041192905265756"),
        ]])
        if edit:
            await message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
        else:
            await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
        return

    buttons: list[list[InlineKeyboardButton]] = []
    row_: list[InlineKeyboardButton] = []
    for country, count in countries_data:
        btn = apply_button_style(InlineKeyboardButton(
            text=f"{get_country_flag(country)} {country.title()} ({count})",
            callback_data=f"tgold_ctry_{year}|{country}",
        ), 'primary', "5240428351063081133")
        row_.append(btn)
        if len(row_) == 2:
            buttons.append(row_)
            row_ = []
    if row_:
        buttons.append(row_)
    buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"buy_cat_{CATEGORY_TELEGRAM_OLD}"), 'danger', "5416041192905265756")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    text_msg = (
        f"📱 <b>Telegram Old Accounts ({year})</b>\n\n"
        f"🌍 <b>Select a Country:</b>\n"
        f"<i>Number in brackets = Available count</i>"
    )
    if edit:
        await message.edit_text(text_msg, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await message.answer(text_msg, reply_markup=kb, parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("tgold_ctry_"))
async def cb_tgold_country(query: CallbackQuery) -> None:
    """Show details for selected country/year in Telegram Old Accounts."""
    await query.answer()
    parts = query.data.replace("tgold_ctry_", "").split("|", 1)
    if len(parts) != 2:
        await query.answer("Invalid request", show_alert=True)
        return
    try:
        year = int(parts[0])
    except ValueError:
        await query.answer("Invalid request", show_alert=True)
        return
    country = parts[1]

    async with AsyncSessionFactory() as session:
        rows = await session.execute(
            select(Product)
            .where(
                Product.category == CATEGORY_TELEGRAM_OLD,
                Product.country == country,
                Product.year == year,
                Product.status == "Available",
            )
            .order_by(Product.price)
        )
        products = rows.scalars().all()

    if not products:
        await query.message.edit_text(
            f"😔 <b>No numbers available</b> for "
            f"{get_country_flag(country)} {country.title()} ({year}) right now.\n\n"
            f"Please check back later or choose another country.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"tgold_yr_{year}"), 'danger', "5416041192905265756"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
        return

    available_count = len(products)
    price = products[0].price
    await query.message.edit_text(
        f"🌍 <b>{get_country_flag(country)} {country.title()}</b>\n"
        f"📁 <b>Category:</b> 📱 Telegram Old Accounts ({year})\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 <b>Available Numbers:</b> {available_count}\n"
        f"💰 <b>Price per Number:</b> ${price:.2f} USDT\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Click <b>Buy Now</b> to purchase a random number from this pool.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Buy Now", callback_data=f"tgold_confirm_{year}|{country}"), 'primary', "5406683434124859552")],
            [apply_button_style(InlineKeyboardButton(text="Cancel", callback_data=f"tgold_yr_{year}"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("tgold_confirm_"))
async def cb_tgold_confirm(query: CallbackQuery) -> None:
    """Show purchase confirmation for Telegram Old Accounts."""
    await query.answer()
    parts = query.data.replace("tgold_confirm_", "").split("|", 1)
    if len(parts) != 2:
        await query.answer("Invalid request", show_alert=True)
        return
    try:
        year = int(parts[0])
    except ValueError:
        await query.answer("Invalid request", show_alert=True)
        return
    country = parts[1]
    user_id = query.from_user.id

    async with AsyncSessionFactory() as session:
        user = await get_or_create_user(
            session, user_id, query.from_user.username,
            first_name=query.from_user.first_name,
        )
        if user.is_banned:
            await query.answer("🚫 You are banned from using this bot.", show_alert=True)
            return

        rows = await session.execute(
            select(Product)
            .where(
                Product.category == CATEGORY_TELEGRAM_OLD,
                Product.country == country,
                Product.year == year,
                Product.status == "Available",
            )
            .order_by(Product.price)
        )
        products = rows.scalars().all()

    if not products:
        await query.message.edit_text(
            "❌ <b>No Numbers Available</b>\n\nThis country's stock is now empty. "
            "Please choose another country.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"tgold_yr_{year}"), 'danger', "5416041192905265756"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
        return

    price = Decimal(str(products[0].price))
    available_count = len(products)
    user_balance = Decimal(str(user.balance or 0))
    can_afford = user_balance >= price
    flag = get_country_flag(country)
    balance_after = user_balance - price if can_afford else user_balance

    if can_afford:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(
                text="Confirm Purchase",
                callback_data=f"tgold_exec_{year}|{country}",
            ), 'primary', "5206607081334906820")],
            [apply_button_style(InlineKeyboardButton(
                text="Cancel",
                callback_data=f"tgold_ctry_{year}|{country}",
            ), 'danger', "5416041192905265756")],
        ])
        balance_line = (
            f"💰 <b>Your Balance:</b> ${user_balance:.2f} USDT\n"
            f"💵 <b>Cost:</b> ${price:.2f} USDT\n"
            f"📉 <b>Balance after purchase:</b> ${balance_after:.2f} USDT"
        )
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Deposit Funds", callback_data="deposit"), 'primary', "5424976816530014958")],
            [apply_button_style(InlineKeyboardButton(
                text="Cancel",
                callback_data=f"tgold_ctry_{year}|{country}",
            ), 'danger', "5416041192905265756")],
        ])
        balance_line = (
            f"💰 <b>Your Balance:</b> ${user_balance:.2f} USDT\n"
            f"💵 <b>Required:</b> ${price:.2f} USDT\n\n"
            f"❌ <b>Insufficient balance.</b> Please deposit funds first."
        )

    await query.message.edit_text(
        f"🛒 <b>Confirm Purchase</b>\n\n"
        f"🌍 <b>Country:</b> {flag} {country.title()}\n"
        f"📅 <b>Year:</b> {year}\n"
        f"📱 <b>Available:</b> {available_count} number(s)\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{balance_line}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{'Tap <b>Confirm Purchase</b> to proceed.' if can_afford else 'Deposit to unlock purchase.'}",
        reply_markup=kb,
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("tgold_exec_"))
async def cb_tgold_execute(query: CallbackQuery) -> None:
    """Execute purchase for Telegram Old Accounts."""
    await query.answer()
    parts = query.data.replace("tgold_exec_", "").split("|", 1)
    if len(parts) != 2:
        await query.answer("Invalid request", show_alert=True)
        return
    try:
        year = int(parts[0])
    except ValueError:
        await query.answer("Invalid request", show_alert=True)
        return
    country = parts[1]
    user_id = query.from_user.id

    async with AsyncSessionFactory() as session:
        user = await get_or_create_user(
            session, user_id, query.from_user.username,
            first_name=query.from_user.first_name,
        )
        if user.is_banned:
            await query.answer("🚫 You are banned from using this bot.", show_alert=True)
            return

        rows = await session.execute(
            select(Product)
            .where(
                Product.category == CATEGORY_TELEGRAM_OLD,
                Product.country == country,
                Product.year == year,
                Product.status == "Available",
            )
        )
        available_products = rows.scalars().all()

        if not available_products:
            await query.message.edit_text(
                "❌ <b>No numbers available.</b>\n\nThis stock just ran out. "
                "Please try another country.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"tgold_yr_{year}"), 'danger', "5416041192905265756"),
                ]]),
                parse_mode=ParseMode.HTML,
            )
            return

        product = secrets.choice(available_products)

        if Decimal(str(user.balance)) < Decimal(str(product.price)):
            await query.message.edit_text(
                f"❌ <b>Insufficient Balance</b>\n\n"
                f"💰 Your balance: <b>${user.balance:.2f}</b>\n"
                f"💵 Required: <b>${product.price:.2f}</b>\n\n"
                f"Please deposit funds first.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [apply_button_style(InlineKeyboardButton(text="Deposit", callback_data="deposit"), 'primary', "5424976816530014958")],
                    [apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"tgold_ctry_{year}|{country}"), 'danger', "5416041192905265756")],
                ]),
                parse_mode=ParseMode.HTML,
            )
            return

        # Apply discount
        base_price = Decimal(str(product.price))
        total_deposited_user = Decimal(str(user.total_deposited or 0))
        disc_pct = await get_applicable_discount(session, user_id, total_deposited_user)
        actual_price = base_price * (1 - disc_pct / 100) if disc_pct > 0 else base_price

        new_balance = Decimal(str(user.balance)) - actual_price
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(balance=new_balance, numbers_bought=User.numbers_bought + 1)
        )
        await session.execute(
            update(Product).where(Product.id == product.id).values(status="Sold")
        )
        order = Order(user_id=user_id, product_id=product.id, status="Completed")
        session.add(order)
        await session.flush()
        txn = Transaction(
            user_id=user_id, order_id=order.id,
            type="Purchase", amount=actual_price, status="Completed",
        )
        session.add(txn)
        await session.commit()

        phone = product.phone_number
        price = actual_price
        sess_str = product.session_string
        twofa_enc = product.twofa_password
        pid = product.id

    # Clear any stale OTP
    async with AsyncSessionFactory() as session:
        await session.execute(
            update(Product)
            .where(Product.id == pid)
            .values(latest_otp=None, otp_updated_at=None)
        )
        await session.commit()

    if sess_str:
        await otp_manager.start_listener(pid, sess_str)

    # Post to log channel
    _uname = query.from_user.username
    user_display = f"@{_uname}" if _uname else str(query.from_user.id)
    async with AsyncSessionFactory() as _log_session:
        _log_user = await _log_session.execute(select(User).where(User.id == user_id))
        _log_user_obj = _log_user.scalar_one_or_none()
        _total_dep = Decimal(str(_log_user_obj.total_deposited or 0)) if _log_user_obj else Decimal("0")
    await post_to_log_channel(query.bot, user_display, CATEGORY_TELEGRAM_OLD, country, price, phone, disc_pct, user_id=user_id, total_deposited=_total_dep)
    twofa_line = ""
    if twofa_enc:
        try:
            twofa_plain = decrypt_privkey(twofa_enc)
            twofa_line = f"🔐 <b>2FA Password:</b> <code>{twofa_plain}</code>\n"
        except Exception:
            pass

    # Old accounts show only OTP, not session string
    disc_line = f"<tg-emoji emoji-id=\"5240228673738527951\">🏷️</tg-emoji> <b>Discount:</b> {disc_pct:.0f}% off\n" if disc_pct > 0 else ""
    await query.message.edit_text(
        f"<tg-emoji emoji-id=\"5461151367559141950\">🎉</tg-emoji> <b>Purchase Successful!</b>\n\n"
        f"<tg-emoji emoji-id=\"5197252827247841976\">📱</tg-emoji> <b>Number:</b> <code>{phone}</code>\n"
        f"<tg-emoji emoji-id=\"5460755126761312667\">🌍</tg-emoji> <b>Country:</b> {get_country_flag(country)} {country.title()}\n"
        f"<tg-emoji emoji-id=\"5274055917766202507\">📅</tg-emoji> <b>Year:</b> {year}\n"
        f"<tg-emoji emoji-id=\"5409048419211682843\">💵</tg-emoji> <b>Paid:</b> ${price:.2f} USDT\n"
        f"{disc_line}"
        f"{twofa_line}"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id=\"5274055917766202507\">📋</tg-emoji> <b>Next Steps:</b>\n"
        f"<tg-emoji emoji-id=\"5382322671679708881\">1️⃣</tg-emoji> Open <b>Telegram / Telegram X / TurboTel</b>\n"
        f"<tg-emoji emoji-id=\"5381990043642502553\">2️⃣</tg-emoji> Enter the number: <code>{phone}</code>\n"
        f"<tg-emoji emoji-id=\"5381879959335738545\">3️⃣</tg-emoji> Tap <b>Send Code</b> in Telegram\n"
        f"<tg-emoji emoji-id=\"5382054253403577563\">4️⃣</tg-emoji> Come back here and press <b>🔄 Get OTP</b>\n\n"
        f"<tg-emoji emoji-id=\"5411590687663608498\">⚡</tg-emoji> OTP is fetched <b>instantly</b> from the account!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Get OTP", callback_data=f"getotp_{pid}"), 'primary', "5449569374065152798")],
            [apply_button_style(InlineKeyboardButton(text="Main Menu", callback_data="back_main"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )



# ── Telegram Premium Buy Flow ─────────────────────────────────────────────────

@router.callback_query(F.data == "buy_prem")
async def cb_buy_prem(query: CallbackQuery) -> None:
    """Show available premium countries."""
    await query.answer()
    async with AsyncSessionFactory() as session:
        rows = await session.execute(
            select(PremiumCountry).order_by(PremiumCountry.country)
        )
        countries = rows.scalars().all()

    if not countries:
        await query.message.edit_text(
            '<tg-emoji emoji-id="5224607267797606837">😔</tg-emoji> No Telegram Premium accounts available right now.',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy_cat_telegram"), 'danger', "5416041192905265756"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
        return

    buttons = []
    for c in countries:
        flag = get_country_flag(c.country)
        buttons.append([apply_button_style(InlineKeyboardButton(
            text=f"{flag} {c.country.title()} — ${float(c.price):.2f}",
            callback_data=f"buy_prem_ctry_{c.id}",
        ), 'primary', "5453901475648390219")])
    buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy_cat_telegram"), 'danger', "5416041192905265756")])

    await query.message.edit_text(
        "<tg-emoji emoji-id=\"5453901475648390219\">⭐</tg-emoji> <b>Telegram Premium</b>\n\n"
        "Select a country:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("buy_prem_ctry_"))
async def cb_buy_prem_country(query: CallbackQuery) -> None:
    """Show premium country details and confirm button."""
    await query.answer()
    try:
        country_id = int(query.data.replace("buy_prem_ctry_", ""))
    except ValueError:
        await query.answer("Invalid request", show_alert=True)
        return

    async with AsyncSessionFactory() as session:
        res = await session.execute(select(PremiumCountry).where(PremiumCountry.id == country_id))
        pc = res.scalar_one_or_none()

    if pc is None:
        await query.answer("Country not found.", show_alert=True)
        return

    user_id = query.from_user.id
    async with AsyncSessionFactory() as session:
        u_res = await session.execute(select(User).where(User.id == user_id))
        u_obj = u_res.scalar_one_or_none()
        user_balance = Decimal(str(u_obj.balance or 0)) if u_obj else Decimal("0")

    flag = get_country_flag(pc.country)
    price = Decimal(str(pc.price))

    await query.message.edit_text(
        f"<tg-emoji emoji-id=\"5453901475648390219\">⭐</tg-emoji> <b>Telegram Premium</b>\n\n"
        f"<tg-emoji emoji-id=\"5460755126761312667\">🌍</tg-emoji> <b>Country:</b> {flag} {pc.country.title()}\n"
        f"<tg-emoji emoji-id=\"5409048419211682843\">💵</tg-emoji> <b>Price:</b> ${price:.2f} USDT\n"
        f"<tg-emoji emoji-id=\"5409048419211682843\">💰</tg-emoji> <b>Your Balance:</b> ${user_balance:.2f} USDT\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Your order will be completed within <b>24 hours</b>.\n"
        f"You'll receive the account details once ready.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Confirm Order", callback_data=f"buy_prem_confirm_{country_id}"), 'success', "5206607081334906820")],
            [apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="buy_prem"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("buy_prem_confirm_"))
async def cb_buy_prem_confirm(query: CallbackQuery) -> None:
    """Process premium order placement."""
    await query.answer()
    try:
        country_id = int(query.data.replace("buy_prem_confirm_", ""))
    except ValueError:
        await query.answer("Invalid request", show_alert=True)
        return

    user_id = query.from_user.id

    async with AsyncSessionFactory() as session:
        res = await session.execute(select(PremiumCountry).where(PremiumCountry.id == country_id))
        pc = res.scalar_one_or_none()
        if pc is None:
            await query.answer("Country not found.", show_alert=True)
            return

        user = await get_or_create_user(session, user_id, query.from_user.username, first_name=query.from_user.first_name)
        if user.is_banned:
            await query.answer("🚫 You are banned.", show_alert=True)
            return

        price = Decimal(str(pc.price))
        if Decimal(str(user.balance)) < price:
            await query.message.edit_text(
                f"❌ <b>Insufficient Balance</b>\n\n"
                f"💰 Your balance: <b>${user.balance:.2f}</b>\n"
                f"💵 Required: <b>${price:.2f}</b>\n\n"
                f"Please deposit funds first.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [apply_button_style(InlineKeyboardButton(text="Deposit", callback_data="deposit"), 'primary', "5424976816530014958")],
                    [apply_button_style(InlineKeyboardButton(text="Back", callback_data=f"buy_prem_ctry_{country_id}"), 'danger', "5416041192905265756")],
                ]),
                parse_mode=ParseMode.HTML,
            )
            return

        # Deduct balance
        await session.execute(
            update(User).where(User.id == user_id).values(balance=User.balance - price)
        )

        # Create order
        order_ref = f"PRM-{secrets.token_hex(4).upper()}"
        prem_order = PremiumOrder(
            order_ref=order_ref,
            user_id=user_id,
            country=pc.country,
            price=price,
            status="Pending",
        )
        session.add(prem_order)
        await session.flush()

        # Record transaction
        txn = Transaction(
            user_id=user_id,
            type="Purchase",
            amount=price,
            status="Pending",
        )
        session.add(txn)
        await session.commit()
        country_name = pc.country

    flag = get_country_flag(country_name)

    # Show success message to user
    await query.message.edit_text(
        f"<tg-emoji emoji-id='5461151367559141950'>🎉</tg-emoji> <b>Order Placed Successfully!</b>\n\n"
        f"<tg-emoji emoji-id='5397782960512444700'>📌</tg-emoji> <b>Order ID:</b> <code>{order_ref}</code>\n"
        f"<tg-emoji emoji-id='5460755126761312667'>🌍</tg-emoji> <b>Country:</b> {flag} {country_name.title()}\n"
        f"<tg-emoji emoji-id='5409048419211682843'>💵</tg-emoji> <b>Price Paid:</b> ${price:.2f} USDT\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji emoji-id='5411590687663608498'>⚡</tg-emoji> Your order will be completed within <b>24 hours</b>.\n"
        f"We will notify you once your account is ready!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Main Menu", callback_data="back_main"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )

    # Notify admins
    username = query.from_user.username
    user_display = f"@{username}" if username else str(user_id)
    dt_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    admin_text = (
        f"🆕 <b>New Premium Order!</b>\n\n"
        f"📌 <b>Order ID:</b> {order_ref}\n"
        f"👤 <b>User:</b> {user_display}\n"
        f"🌍 <b>Country:</b> {flag} {country_name.title()}\n"
        f"💵 <b>Price:</b> ${price:.2f} USDT\n"
        f"⏰ {dt_str}"
    )
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            apply_button_style(InlineKeyboardButton(text="Confirm", callback_data=f"prem_admin_confirm_{order_ref}"), 'success', "5206607081334906820"),
            apply_button_style(InlineKeyboardButton(text="Decline", callback_data=f"prem_admin_decline_{order_ref}"), 'danger', "5416041192905265756"),
        ]
    ])
    for admin_id in ADMIN_IDS:
        try:
            await query.bot.send_message(admin_id, admin_text, reply_markup=admin_kb, parse_mode=ParseMode.HTML)
        except Exception as exc:
            log.warning("Could not notify admin %s of premium order: %s", admin_id, exc)


@router.callback_query(F.data.startswith("prem_admin_confirm_"))
@admin_only
async def cb_prem_admin_confirm(query: CallbackQuery, state: FSMContext) -> None:
    """Admin confirms a premium order - starts fulfillment FSM."""
    await query.answer()
    order_ref = query.data.replace("prem_admin_confirm_", "")
    await state.set_state(AdminFulfillPremiumOrder.phone)
    await state.update_data(prem_order_ref=order_ref)
    await query.message.answer(
        f"📌 Fulfilling Premium Order <code>{order_ref}</code>\n\n"
        f"Enter the <b>phone number</b> for this premium order:",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminFulfillPremiumOrder.phone)
@admin_only
async def fsm_prem_fulfill_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(prem_phone=message.text.strip())
    await state.set_state(AdminFulfillPremiumOrder.session_string)
    await message.answer(
        "Now paste the <b>Pyrogram session string</b>:",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminFulfillPremiumOrder.session_string)
@admin_only
async def fsm_prem_fulfill_session(message: Message, state: FSMContext) -> None:
    await state.update_data(prem_session=message.text.strip())
    await state.set_state(AdminFulfillPremiumOrder.twofa_password)
    await message.answer(
        "Does this account have a 2FA password? Enter it, or send <code>0</code> to skip:",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminFulfillPremiumOrder.twofa_password)
@admin_only
async def fsm_prem_fulfill_twofa(message: Message, state: FSMContext) -> None:
    raw = message.text.strip()
    twofa_enc: Optional[str] = None
    if raw != "0":
        twofa_enc = encrypt_privkey(raw)
    twofa_plain = raw if raw != "0" else None

    data = await state.get_data()
    order_ref = data["prem_order_ref"]
    phone = data["prem_phone"]
    sess_str = data["prem_session"]
    await state.clear()

    async with AsyncSessionFactory() as session:
        res = await session.execute(select(PremiumOrder).where(PremiumOrder.order_ref == order_ref))
        prem_order = res.scalar_one_or_none()
        if prem_order is None:
            await message.answer(f"❌ Premium order {order_ref} not found.")
            return

        # Create a Product for this premium order
        product = Product(
            category=CATEGORY_TELEGRAM_PREMIUM,
            country=prem_order.country,
            phone_number=phone,
            price=prem_order.price,
            session_string=sess_str,
            twofa_password=twofa_enc,
            status="Sold",
        )
        session.add(product)
        await session.flush()

        # Update PremiumOrder
        await session.execute(
            update(PremiumOrder).where(PremiumOrder.order_ref == order_ref).values(
                status="Completed",
                phone_number=phone,
                session_string=sess_str,
                twofa_password=twofa_enc,
                product_id=product.id,
            )
        )

        # Update the most recent matching pending transaction to Completed
        _txn_res = await session.execute(
            select(Transaction)
            .where(
                Transaction.user_id == prem_order.user_id,
                Transaction.type == "Purchase",
                Transaction.status == "Pending",
                Transaction.amount == prem_order.price,
            )
            .order_by(Transaction.created_at.desc())
            .limit(1)
        )
        _latest_txn = _txn_res.scalar_one_or_none()
        if _latest_txn:
            await session.execute(
                update(Transaction).where(Transaction.id == _latest_txn.id).values(status="Completed")
            )

        await session.commit()
        buyer_id = prem_order.user_id
        country_name = prem_order.country
        price = Decimal(str(prem_order.price))
        pid = product.id

    # Start OTP listener
    if sess_str:
        await otp_manager.start_listener(pid, sess_str)

    # Notify user
    flag = get_country_flag(country_name)
    twofa_line = f"🔐 <b>2FA Password:</b> <code>{twofa_plain}</code>\n" if twofa_plain else ""
    try:
        await message.bot.send_message(
            buyer_id,
            f"<tg-emoji emoji-id='5206607081334906820'>✅</tg-emoji> <b>Your Premium Order is Ready!</b>\n\n"
            f"<tg-emoji emoji-id='5397782960512444700'>📌</tg-emoji> <b>Order ID:</b> <code>{order_ref}</code>\n"
            f"<tg-emoji emoji-id='5197252827247841976'>📱</tg-emoji> <b>Number:</b> <code>{phone}</code>\n"
            f"<tg-emoji emoji-id='5460755126761312667'>🌍</tg-emoji> <b>Country:</b> {flag} {country_name.title()}\n"
            f"{twofa_line}"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<tg-emoji emoji-id='5274055917766202507'>📋</tg-emoji> <b>Next Steps:</b>\n"
            f"<tg-emoji emoji-id='5382322671679708881'>1️⃣</tg-emoji> Open Telegram / Telegram X / TurboTel\n"
            f"<tg-emoji emoji-id='5381990043642502553'>2️⃣</tg-emoji> Enter the number: {phone}\n"
            f"<tg-emoji emoji-id='5381879959335738545'>3️⃣</tg-emoji> Tap Send Code in Telegram\n"
            f"<tg-emoji emoji-id='5382054253403577563'>4️⃣</tg-emoji> Come back here and press 🔄 Get OTP\n\n"
            f"<tg-emoji emoji-id='5411590687663608498'>⚡</tg-emoji> OTP is fetched instantly from the account!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Get OTP", callback_data=f"getotp_{pid}"), 'primary', "5449569374065152798"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
    except Exception as exc:
        log.warning("Could not notify premium buyer %s: %s", buyer_id, exc)

    await message.answer(
        f"✅ Premium order <code>{order_ref}</code> fulfilled and buyer notified.",
        reply_markup=build_admin_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("prem_admin_decline_"))
@admin_only
async def cb_prem_admin_decline(query: CallbackQuery) -> None:
    """Admin declines a premium order - refund user."""
    await query.answer()
    order_ref = query.data.replace("prem_admin_decline_", "")

    async with AsyncSessionFactory() as session:
        res = await session.execute(select(PremiumOrder).where(PremiumOrder.order_ref == order_ref))
        prem_order = res.scalar_one_or_none()
        if prem_order is None:
            await query.answer("Order not found.", show_alert=True)
            return

        if prem_order.status != "Pending":
            await query.answer("Order already processed.", show_alert=True)
            return

        price = Decimal(str(prem_order.price))
        buyer_id = prem_order.user_id

        await session.execute(
            update(PremiumOrder).where(PremiumOrder.order_ref == order_ref).values(status="Declined")
        )
        # Refund user
        await session.execute(
            update(User).where(User.id == buyer_id).values(balance=User.balance + price)
        )
        # Update the most recent matching pending transaction to Refunded
        _txn_res = await session.execute(
            select(Transaction)
            .where(
                Transaction.user_id == buyer_id,
                Transaction.type == "Purchase",
                Transaction.status == "Pending",
                Transaction.amount == price,
            )
            .order_by(Transaction.created_at.desc())
            .limit(1)
        )
        _latest_txn = _txn_res.scalar_one_or_none()
        if _latest_txn:
            await session.execute(
                update(Transaction).where(Transaction.id == _latest_txn.id).values(status="Refunded")
            )
        await session.commit()

    # Notify user
    try:
        await query.bot.send_message(
            buyer_id,
            f"❌ <b>Your Premium Order has been Declined</b>\n\n"
            f"📌 <b>Order ID:</b> <code>{order_ref}</code>\n"
            f"↩️ <b>Refund:</b> ${price:.2f} USDT has been returned to your balance.\n\n"
            f"We apologize for the inconvenience. Please contact support if you have questions.",
            parse_mode=ParseMode.HTML,
        )
    except Exception as exc:
        log.warning("Could not notify premium buyer %s of decline: %s", buyer_id, exc)

    await query.message.edit_text(
        f"✅ Order <code>{order_ref}</code> declined and user refunded.",
        parse_mode=ParseMode.HTML,
    )


# Legacy buy flow compatibility (for direct country selection without category)
@router.callback_query(F.data.startswith("countries_page_"))
async def cb_countries_page(query: CallbackQuery) -> None:
    page = int(query.data.split("_")[-1])
    await query.answer()
    await _show_countries(query.message, page=page, edit=True)


async def _show_countries(
    message: Message, page: int = 0, edit: bool = False
) -> None:
    async with AsyncSessionFactory() as session:
        rows = await session.execute(
            select(Product.country)
            .where(Product.status == "Available")
            .distinct()
            .order_by(Product.country)
        )
        countries = [r[0] for r in rows.fetchall()]

    if not countries:
        text = "😔 No accounts available right now. Check back later!"
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756"),
        ]])
        if edit:
            await message.edit_text(text, reply_markup=kb)
        else:
            await message.answer(text, reply_markup=kb)
        return

    total_pages = (len(countries) + PAGE_SIZE - 1) // PAGE_SIZE
    page_countries = countries[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]

    buttons = [
        [apply_button_style(InlineKeyboardButton(
            text=f"{get_country_flag(c)} {c}",
            callback_data=f"country_{c}",
        ), 'primary', "5240428351063081133")]
        for c in page_countries
    ]
    nav_row: list[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(
            apply_button_style(InlineKeyboardButton(text="Prev", callback_data=f"countries_page_{page - 1}"), 'primary', "5416041192905265756")
        )
    if page < total_pages - 1:
        nav_row.append(
            apply_button_style(InlineKeyboardButton(text="Next", callback_data=f"countries_page_{page + 1}"), 'primary', "5416117059207572332")
        )
    if nav_row:
        buttons.append(nav_row)
    buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    text = f"🌍 Select a country (Page {page + 1}/{total_pages}):"
    if edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("country_"))
async def cb_country(query: CallbackQuery) -> None:
    await query.answer()
    country = query.data[len("country_"):]
    async with AsyncSessionFactory() as session:
        rows = await session.execute(
            select(Product)
            .where(Product.country == country, Product.status == "Available")
            .order_by(Product.price)
        )
        products = rows.scalars().all()

    if not products:
        await query.answer("No stock for this country!", show_alert=True)
        return

    buttons = [
        [apply_button_style(InlineKeyboardButton(
            text=f"{p.phone_number}  –  ${p.price:.2f}",
            callback_data=f"product_{p.id}",
        ), 'primary', "5197252827247841976")]
        for p in products
    ]
    buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy"), 'danger', "5416041192905265756")])
    await query.message.edit_text(
        f"📋 Available numbers in <b>{get_country_flag(country)} {country}</b>:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("product_"))
async def cb_product(query: CallbackQuery) -> None:
    await query.answer()
    product_id = int(query.data.split("_")[1])
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        p = result.scalar_one_or_none()

    if p is None or p.status != "Available":
        await query.answer("This number is no longer available.", show_alert=True)
        return

    await query.message.edit_text(
        f"📱 <b>{p.phone_number}</b> ({p.country})\n"
        f"💵 Price: <b>${p.price:.2f} USDT</b>\n\n"
        f"Tap <b>Buy Now</b> to proceed to confirmation.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Buy Now", callback_data=f"buynow_{product_id}"), 'primary', "5406683434124859552")],
            [apply_button_style(InlineKeyboardButton(text="Back",    callback_data=f"country_{p.country}"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("buynow_"))
async def cb_buynow(query: CallbackQuery) -> None:
    """Show confirmation dialog before legacy single-number purchase."""
    await query.answer()
    product_id = int(query.data.split("_")[1])
    user_id = query.from_user.id

    async with AsyncSessionFactory() as session:
        result_p = await session.execute(select(Product).where(Product.id == product_id))
        p = result_p.scalar_one_or_none()
        if p is None or p.status != "Available":
            await query.message.edit_text(
                "❌ This number is no longer available.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy"), 'danger', "5416041192905265756"),
                ]]),
                parse_mode=ParseMode.HTML,
            )
            return

        user = await get_or_create_user(session, user_id, query.from_user.username,
                                        first_name=query.from_user.first_name)

    if user.is_banned:
        await query.answer("🚫 You are banned from using this bot.", show_alert=True)
        return

    price = Decimal(str(p.price))
    user_balance = Decimal(str(user.balance or 0))
    can_afford = user_balance >= price
    balance_after = user_balance - price if can_afford else user_balance

    if can_afford:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(
                text="Confirm Purchase",
                callback_data=f"buynowexec_{product_id}",
            ), 'primary', "5206607081334906820")],
            [apply_button_style(InlineKeyboardButton(
                text="Cancel",
                callback_data=f"product_{product_id}",
            ), 'danger', "5416041192905265756")],
        ])
        balance_line = (
            f"💰 <b>Your Balance:</b> ${user_balance:.2f} USDT\n"
            f"💵 <b>Cost:</b> ${price:.2f} USDT\n"
            f"📉 <b>Balance after purchase:</b> ${balance_after:.2f} USDT"
        )
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Deposit Funds", callback_data="deposit"), 'primary', "5424976816530014958")],
            [apply_button_style(InlineKeyboardButton(
                text="Cancel",
                callback_data=f"product_{product_id}",
            ), 'danger', "5416041192905265756")],
        ])
        balance_line = (
            f"💰 <b>Your Balance:</b> ${user_balance:.2f} USDT\n"
            f"💵 <b>Required:</b> ${price:.2f} USDT\n\n"
            f"❌ <b>Insufficient balance.</b> Please deposit funds first."
        )

    await query.message.edit_text(
        f"🛒 <b>Confirm Purchase</b>\n\n"
        f"📱 <b>Number:</b> <code>{p.phone_number}</code>\n"
        f"🌍 <b>Country:</b> {get_country_flag(p.country)} {p.country.title()}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{balance_line}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{'Tap <b>Confirm Purchase</b> to proceed.' if can_afford else 'Deposit to unlock purchase.'}",
        reply_markup=kb,
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("buynowexec_"))
async def cb_buynow_execute(query: CallbackQuery) -> None:
    """Execute legacy single-number purchase after confirmation."""
    await query.answer()
    product_id = int(query.data.split("_")[1])
    user_id = query.from_user.id

    async with AsyncSessionFactory() as session:
        result_p = await session.execute(select(Product).where(Product.id == product_id))
        p = result_p.scalar_one_or_none()
        if p is None or p.status != "Available":
            await query.message.edit_text(
                "❌ This number is no longer available.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    apply_button_style(InlineKeyboardButton(text="Back", callback_data="buy"), 'danger', "5416041192905265756"),
                ]]),
                parse_mode=ParseMode.HTML,
            )
            return

        user = await get_or_create_user(session, user_id, query.from_user.username,
                                        first_name=query.from_user.first_name)

        if user.is_banned:
            await query.answer("🚫 You are banned from using this bot.", show_alert=True)
            return

        if Decimal(str(user.balance)) < Decimal(str(p.price)):
            await query.message.edit_text(
                f"❌ Insufficient balance.\n"
                f"Your balance: <b>${user.balance:.2f}</b>\n"
                f"Required: <b>${p.price:.2f}</b>\n\n"
                f"Please deposit funds first.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [apply_button_style(InlineKeyboardButton(text="Deposit", callback_data="deposit"), 'primary', "5424976816530014958")],
                    [apply_button_style(InlineKeyboardButton(text="Back",    callback_data=f"product_{product_id}"), 'danger', "5416041192905265756")],
                ]),
                parse_mode=ParseMode.HTML,
            )
            return

        # Apply discount
        base_price = Decimal(str(p.price))
        total_deposited_user = Decimal(str(user.total_deposited or 0))
        disc_pct = await get_applicable_discount(session, user_id, total_deposited_user)
        actual_price = base_price * (1 - disc_pct / 100) if disc_pct > 0 else base_price

        new_balance = Decimal(str(user.balance)) - actual_price
        await session.execute(
            update(User).where(User.id == user_id).values(
                balance=new_balance,
                numbers_bought=User.numbers_bought + 1,
            )
        )
        await session.execute(
            update(Product).where(Product.id == product_id).values(status="Sold")
        )
        order = Order(user_id=user_id, product_id=product_id, status="Completed")
        session.add(order)
        await session.flush()
        txn = Transaction(
            user_id=user_id, order_id=order.id, type="Purchase",
            amount=actual_price, status="Completed",
        )
        session.add(txn)
        await session.commit()
        phone = p.phone_number
        price = actual_price
        country = p.country
        sess_str = p.session_string
        twofa_enc = p.twofa_password
        pid = p.id
        p_category = p.category

    # Clear any stale OTP from previous ownership
    async with AsyncSessionFactory() as session:
        await session.execute(
            update(Product)
            .where(Product.id == pid)
            .values(latest_otp=None, otp_updated_at=None)
        )
        await session.commit()

    # Start the background OTP listener via the manager
    if sess_str:
        await otp_manager.start_listener(pid, sess_str)

    # Post to log channel
    _uname = query.from_user.username
    user_display = f"@{_uname}" if _uname else str(query.from_user.id)
    async with AsyncSessionFactory() as _log_session:
        _log_user = await _log_session.execute(select(User).where(User.id == user_id))
        _log_user_obj = _log_user.scalar_one_or_none()
        _total_dep = Decimal(str(_log_user_obj.total_deposited or 0)) if _log_user_obj else Decimal("0")
    await post_to_log_channel(query.bot, user_display, p_category, country, price, phone, disc_pct, user_id=user_id, total_deposited=_total_dep)
    twofa_line = ""
    if twofa_enc:
        try:
            twofa_plain = decrypt_privkey(twofa_enc)
            twofa_line = f"🔐 <b>2FA Password:</b> <code>{twofa_plain}</code>\n"
        except Exception:
            pass

    # Session string is only shown for Telegram Sessions category
    if p_category == CATEGORY_TELEGRAM_SESSIONS:
        session_line = format_session_preview(sess_str) + "\n"
    else:
        session_line = ""

    disc_line = f"<tg-emoji emoji-id=\"5240228673738527951\">🏷️</tg-emoji> <b>Discount:</b> {disc_pct:.0f}% off\n" if disc_pct > 0 else ""
    await query.message.edit_text(
        f"<tg-emoji emoji-id=\"5461151367559141950\">🎉</tg-emoji> <b>Purchase Successful!</b>\n\n"
        f"<tg-emoji emoji-id=\"5197252827247841976\">📱</tg-emoji> <b>Number:</b> <code>{phone}</code>\n"
        f"<tg-emoji emoji-id=\"5460755126761312667\">🌍</tg-emoji> <b>Country:</b> {get_country_flag(country)} {country}\n"
        f"<tg-emoji emoji-id=\"5409048419211682843\">💵</tg-emoji> <b>Paid:</b> ${price:.2f} USDT\n"
        f"{disc_line}"
        f"{session_line}"
        f"{twofa_line}"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b><tg-emoji emoji-id=\"5274055917766202507\">📋</tg-emoji> Next Steps:</b>\n"
        f"<tg-emoji emoji-id=\"5382322671679708881\">1️⃣</tg-emoji> Open <b>Telegram / Telegram X / TurboTel</b>\n"
        f"<tg-emoji emoji-id=\"5381990043642502553\">2️⃣</tg-emoji> Enter the number: <code>{phone}</code>\n"
        f"<tg-emoji emoji-id=\"5381879959335738545\">3️⃣</tg-emoji> Tap <b>Send Code</b> in Telegram\n"
        f"<tg-emoji emoji-id=\"5382054253403577563\">4️⃣</tg-emoji> Come back here and press <b>🔄 Get OTP</b>\n\n"
        f"<tg-emoji emoji-id=\"5411590687663608498\">⚡</tg-emoji> OTP is fetched <b>instantly</b> from the account!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Get OTP", callback_data=f"getotp_{pid}"), 'primary', "5449569374065152798")],
            [apply_button_style(InlineKeyboardButton(text="Main Menu", callback_data="back_main"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


# ── Get OTP (redesigned) ─────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("getotp_"))
async def cb_getotp(query: CallbackQuery) -> None:
    try:
        product_id = int(query.data.split("_")[1])
    except (IndexError, ValueError):
        await query.answer("❌ Invalid request.", show_alert=True)
        return

    await query.answer("⏳ Fetching OTP…")

    # Load product from DB
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        p = result.scalar_one_or_none()

    if p is None:
        await _safe_edit(
            query.message,
            "❌ <b>Product not found.</b>\n\nPlease contact support.",
            InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Main Menu", callback_data="back_main"), 'danger', "5416041192905265756"),
            ]]),
        )
        return

    if not p.session_string:
        await _safe_edit(
            query.message,
            "❌ <b>OTP fetch unavailable.</b>\n\n"
            "No session string is configured for this number. "
            "Please contact support.",
            InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Main Menu", callback_data="back_main"), 'danger', "5416041192905265756"),
            ]]),
        )
        return

    # Active on-demand fetch via the OTP manager
    otp_code, status_msg = await otp_manager.fetch_otp_now(product_id, p.session_string)

    if otp_code:
        await _safe_edit(
            query.message,
            f"✅ <b>Your OTP Code:</b>\n\n"
            f"<code>{otp_code}</code>\n\n"
            f"📱 Enter this code in Telegram to complete login.\n"
            f"⚠️ Do <b>not</b> share this code with anyone.",
            InlineKeyboardMarkup(inline_keyboard=[
                [apply_button_style(InlineKeyboardButton(text="Main Menu", callback_data="back_main"), 'danger', "5416041192905265756")],
            ]),
        )
    else:
        checked_at = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        await _safe_edit(
            query.message,
            f"⏳ <b>No OTP detected yet.</b>\n\n"
            f"<b>Status:</b> {status_msg}\n\n"
            f"Make sure you opened Telegram and requested a login code "
            f"for number <b>{p.phone_number}</b>, then tap Refresh.\n\n"
            f"🕐 <i>Last checked: {checked_at}</i>",
            InlineKeyboardMarkup(inline_keyboard=[
                [apply_button_style(InlineKeyboardButton(
                    text="Refresh", callback_data=f"getotp_{product_id}"
                ), 'primary', "5449569374065152798")],
                [apply_button_style(InlineKeyboardButton(text="Main Menu", callback_data="back_main"), 'danger', "5416041192905265756")],
            ]),
        )


async def _safe_edit(
    message: Message, text: str, reply_markup: InlineKeyboardMarkup
) -> None:
    """Edit a message, silently ignoring 'message is not modified' errors."""
    try:
        await message.edit_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TelegramAPIError as exc:
        if "message is not modified" not in str(exc).lower():
            raise


# ── Back to main ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "back_main")
async def cb_back_main(query: CallbackQuery) -> None:
    await query.answer()
    async with AsyncSessionFactory() as session:
        user = await get_or_create_user(
            session,
            query.from_user.id,
            query.from_user.username,
            first_name=query.from_user.first_name or "User",
        )
        balance = Decimal(str(user.balance or 0))
        first_name = user.first_name or query.from_user.first_name or "User"
    
    is_admin = query.from_user.id in ADMIN_IDS
    kb = build_main_keyboard(is_admin)
    welcome_text = get_welcome_text(first_name, balance)
    
    if query.message.photo or query.message.video or query.message.document:
        await query.message.delete()
        await query.message.answer(welcome_text, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await query.message.edit_text(welcome_text, reply_markup=kb, parse_mode=ParseMode.HTML)


# ── Referral ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "referral")
async def cb_referral(query: CallbackQuery) -> None:
    await query.answer()
    user_id = query.from_user.id
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(User).where(User.referred_by == user_id))
        referred_users = result.scalars().all()
        result2 = await session.execute(
            select(Transaction).where(
                Transaction.user_id == user_id,
                Transaction.type == "ReferralBonus",
            )
        )
        bonuses = result2.scalars().all()
        total_earned = sum(Decimal(str(b.amount)) for b in bonuses)

    bot_info = await query.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"

    await query.message.edit_text(
        f"<tg-emoji emoji-id=\"5253576920993388584\">🤝</tg-emoji> <b>Your Referral Program</b>\n\n"
        f"<tg-emoji emoji-id=\"5305265301917549162\">🔗</tg-emoji> Your link:\n<code>{ref_link}</code>\n\n"
        f"<tg-emoji emoji-id=\"5319175438268913255\">👥</tg-emoji> Total referrals: <b>{len(referred_users)}</b>\n"
        f"<tg-emoji emoji-id=\"5409048419211682843\">💵</tg-emoji> Total earned: <b>${total_earned:.2f} USDT</b>\n\n"
        f"Earn <b>{REFERRAL_COMMISSION_PCT}%</b> commission on every deposit "
        f"made by your referrals!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  ADMIN PANEL
# ─────────────────────────────────────────────────────────────────────────────

def admin_only(func):
    @functools.wraps(func)
    async def wrapper(event, *args, **kwargs):
        uid = (
            event.from_user.id
            if isinstance(event, (Message, CallbackQuery))
            else None
        )
        if uid not in ADMIN_IDS:
            if isinstance(event, CallbackQuery):
                await event.answer("⛔ Unauthorized", show_alert=True)
            elif isinstance(event, Message):
                await event.answer("⛔ Unauthorized.")
            return
        return await func(event, *args, **kwargs)
    return wrapper


def build_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [apply_button_style(InlineKeyboardButton(text="Add Number",        callback_data="admin_add_number"), 'primary', "5397916757333654639")],
        [apply_button_style(InlineKeyboardButton(text="View Inventory",    callback_data="admin_inventory_0"), 'primary', "5406683434124859552")],
        [apply_button_style(InlineKeyboardButton(text="Pending Orders",    callback_data="admin_orders"), 'primary', "5406683434124859552")],
        [
            apply_button_style(InlineKeyboardButton(text="Users",          callback_data="admin_users_0"), 'primary', "5260343246831237239"),
            apply_button_style(InlineKeyboardButton(text="Search User",    callback_data="admin_search_user"), 'primary', "5368341238871248978"),
        ],
        [
            apply_button_style(InlineKeyboardButton(text="Stats",          callback_data="admin_stats"), 'primary', "5260343246831237239"),
            apply_button_style(InlineKeyboardButton(text="Discounts",      callback_data="admin_discount"), 'primary', "5427168083074628963"),
        ],
        [apply_button_style(InlineKeyboardButton(text="Create Gift Code",  callback_data="admin_create_gift_code"), 'primary', "5461151367559141950")],
        [apply_button_style(InlineKeyboardButton(text="Broadcast",         callback_data="admin_broadcast"), 'primary', "5368341238871248978")],
        [apply_button_style(InlineKeyboardButton(text="Main Menu",         callback_data="back_main"), 'danger', "5416041192905265756")],
    ])


@router.message(Command("admin"))
@admin_only
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🔐 <b>Admin Panel</b>", reply_markup=build_admin_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "admin_menu")
@admin_only
async def cb_admin_menu(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await state.clear()
    await query.message.edit_text(
        "🔐 <b>Admin Panel</b>", reply_markup=build_admin_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "admin_stats")
@admin_only
async def cb_admin_stats(query: CallbackQuery) -> None:
    """Show comprehensive bot statistics."""
    await query.answer()
    from sqlalchemy import func
    async with AsyncSessionFactory() as session:
        # Total users
        total_users_res = await session.execute(select(func.count(User.id)))
        total_users = total_users_res.scalar() or 0

        # Active users (not banned)
        active_users_res = await session.execute(
            select(func.count(User.id)).where(User.is_banned.is_(False))
        )
        active_users = active_users_res.scalar() or 0

        # Total sell volume (sum of completed purchase transactions)
        sell_vol_res = await session.execute(
            select(func.sum(Transaction.amount)).where(
                Transaction.type == "Purchase", Transaction.status == "Completed"
            )
        )
        sell_volume = sell_vol_res.scalar() or Decimal(0)

        # Total deposited (OxaPay + blockchain)
        dep_vol_res = await session.execute(
            select(func.sum(Transaction.amount)).where(
                Transaction.type.in_(["OxaPayDeposit", "Deposit"]),
                Transaction.status == "Completed",
            )
        )
        total_deposited = dep_vol_res.scalar() or Decimal(0)

        # Available numbers
        avail_res = await session.execute(
            select(func.count(Product.id)).where(Product.status == "Available")
        )
        available_numbers = avail_res.scalar() or 0

        # Total numbers sold
        sold_res = await session.execute(
            select(func.count(Product.id)).where(Product.status == "Sold")
        )
        sold_numbers = sold_res.scalar() or 0

        # Total orders
        total_orders_res = await session.execute(
            select(func.count(Order.id)).where(Order.status == "Completed")
        )
        total_orders = total_orders_res.scalar() or 0

        # Banned users
        banned_res = await session.execute(
            select(func.count(User.id)).where(User.is_banned.is_(True))
        )
        banned_users = banned_res.scalar() or 0

        # Discount tiers
        tiers_res = await session.execute(
            select(DiscountTier).order_by(DiscountTier.min_deposit)
        )
        tiers = tiers_res.scalars().all()

        # Active gift codes
        gift_res = await session.execute(
            select(func.count(GiftCode.id)).where(GiftCode.is_active.is_(True))
        )
        active_gifts = gift_res.scalar() or 0

    tiers_text = ""
    if tiers:
        tiers_text = "\n".join(
            f"  • ${float(t.min_deposit):.0f}+ deposit → {float(t.discount_pct):.0f}% off"
            for t in tiers
        )
    else:
        tiers_text = "  No discount tiers set"

    await query.message.edit_text(
        f"<tg-emoji emoji-id='5260343246831237239'>📊</tg-emoji> <b>Bot Statistics</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Users</b>\n"
        f"  Total: <b>{total_users}</b>\n"
        f"  Active: <b>{active_users}</b>\n"
        f"  Banned: <b>{banned_users}</b>\n\n"
        f"<tg-emoji emoji-id='5409048419211682843'>💰</tg-emoji> <b>Financials</b>\n"
        f"  Total Deposited: <b>${float(total_deposited):.2f} USDT</b>\n"
        f"  Total Sell Volume: <b>${float(sell_volume):.2f} USDT</b>\n\n"
        f"<tg-emoji emoji-id='5406683434124859552'>📱</tg-emoji> <b>Numbers</b>\n"
        f"  Available: <b>{available_numbers}</b>\n"
        f"  Sold: <b>{sold_numbers}</b>\n"
        f"  Total Orders: <b>{total_orders}</b>\n\n"
        f"<tg-emoji emoji-id='5427168083074628963'>🏷️</tg-emoji> <b>Discount Tiers</b>\n"
        f"{tiers_text}\n\n"
        f"<tg-emoji emoji-id='5242311354919963946'>🎁</tg-emoji> <b>Active Gift Codes:</b> {active_gifts}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Back", callback_data="admin_menu"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "admin_discount")
@admin_only
async def cb_admin_discount(query: CallbackQuery, state: FSMContext) -> None:
    """Show current discount tiers and option to add new tier."""
    await query.answer()
    async with AsyncSessionFactory() as session:
        tiers_res = await session.execute(
            select(DiscountTier).order_by(DiscountTier.min_deposit)
        )
        tiers = tiers_res.scalars().all()

    if tiers:
        tiers_text = "\n".join(
            f"  🏷️ ${float(t.min_deposit):.0f}+ deposit → <b>{float(t.discount_pct):.0f}% discount</b>"
            for t in tiers
        )
    else:
        tiers_text = "  <i>No discount tiers configured yet.</i>"

    await query.message.edit_text(
        f"🏷️ <b>Discount Management</b>\n\n"
        f"<b>Current Discount Tiers:</b>\n{tiers_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"You can add a new discount tier below.\n"
        f"Tiers are cumulative — users get the highest tier they qualify for.\n\n"
        f"💡 <i>Example: Set 10% for $20+ and 20% for $50+</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [apply_button_style(InlineKeyboardButton(text="Add Discount Tier", callback_data="admin_add_discount_tier"), 'primary', "5397916757333654639")],
            [apply_button_style(InlineKeyboardButton(text="Back", callback_data="admin_menu"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "admin_add_discount_tier")
@admin_only
async def cb_admin_add_discount_tier(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await state.set_state(AdminDiscountState.discount_pct)
    await query.message.edit_text(
        "🏷️ <b>Add Discount Tier</b>\n\n"
        "Step 1/2: Enter the <b>discount percentage</b>\n"
        "Example: <code>10</code> for 10% discount",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_discount"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminDiscountState.discount_pct)
@admin_only
async def fsm_discount_pct(message: Message, state: FSMContext) -> None:
    try:
        pct = Decimal(message.text.strip().replace("%", ""))
        if pct <= 0 or pct >= 100:
            raise ValueError("out_of_range")
    except (ValueError, InvalidOperation):
        await message.answer(
            "❌ Invalid percentage. Enter a whole number between 1 and 99 (e.g. 10):",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_discount"), 'danger', "5416041192905265756"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
        return
    await state.update_data(discount_pct=str(pct))
    await state.set_state(AdminDiscountState.min_deposit)
    await message.answer(
        f"✅ Discount: <b>{pct:.0f}%</b>\n\n"
        f"Step 2/2: Enter the <b>minimum deposit amount</b> (in USD)\n"
        f"Users who have deposited this amount or more will get the discount.\n"
        f"Example: <code>20</code> for users who deposited $20+",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_discount"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminDiscountState.min_deposit)
@admin_only
async def fsm_discount_min_deposit(message: Message, state: FSMContext) -> None:
    try:
        min_dep = Decimal(message.text.strip().replace("$", ""))
        if min_dep < 0:
            raise ValueError
    except Exception:
        await message.answer(
            "❌ Invalid amount. Enter a non-negative number (e.g. 20):",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_discount"), 'danger', "5416041192905265756"),
            ]]),
            parse_mode=ParseMode.HTML,
        )
        return

    data = await state.get_data()
    pct = Decimal(data["discount_pct"])
    await state.clear()

    async with AsyncSessionFactory() as session:
        tier = DiscountTier(min_deposit=min_dep, discount_pct=pct)
        session.add(tier)
        await session.commit()

    await message.answer(
        f"✅ <b>Discount Tier Added!</b>\n\n"
        f"🏷️ Users depositing <b>${min_dep:.0f}+</b> will get <b>{pct:.0f}% discount</b> on all purchases!",
        reply_markup=build_admin_keyboard(),
        parse_mode=ParseMode.HTML,
    )


# ── Add Number FSM ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_add_number")
@admin_only
async def cb_admin_add_number(query: CallbackQuery, state: FSMContext) -> None:
    """Start add number flow - first select category."""
    await query.answer()
    # Load custom categories from DB
    async with AsyncSessionFactory() as session:
        cc_rows = await session.execute(select(CustomCategory).order_by(CustomCategory.created_at))
        custom_cats = cc_rows.scalars().all()

    kb_rows = [
        [apply_button_style(InlineKeyboardButton(text="Telegram Accounts", callback_data=f"admin_add_cat_{CATEGORY_TELEGRAM_ACCOUNTS}"), 'primary', "5197252827247841976")],
        [apply_button_style(InlineKeyboardButton(text="Telegram Old Accounts", callback_data=f"admin_add_cat_{CATEGORY_TELEGRAM_OLD}"), 'primary', "5197252827247841976")],
        [apply_button_style(InlineKeyboardButton(text="Telegram Sessions", callback_data=f"admin_add_cat_{CATEGORY_TELEGRAM_SESSIONS}"), 'primary', "5197252827247841976")],
    ]
    for cc in custom_cats:
        kb_rows.append([apply_button_style(InlineKeyboardButton(text=cc.name, callback_data=f"admin_add_cat_{cc.slug}"), 'primary', "5197252827247841976")])
    kb_rows.append([apply_button_style(InlineKeyboardButton(text="Add Premium Country", callback_data="admin_add_premium_country"), 'success', "5453901475648390219")])
    kb_rows.append([apply_button_style(InlineKeyboardButton(text="➕ Custom Category", callback_data="admin_add_custom_cat"), 'success', "5461151367559141950")])
    kb_rows.append([apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_menu"), 'danger', "5416041192905265756")])

    await query.message.edit_text(
        "➕ <b>Add New Number</b>\n\n"
        "Step 1/5: Select the <b>category</b>:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("admin_add_cat_"))
@admin_only
async def cb_admin_add_category(query: CallbackQuery, state: FSMContext) -> None:
    """Category selected, now ask for country (or year for old accounts)."""
    await query.answer()
    category = query.data.replace("admin_add_cat_", "")
    category_name = PRODUCT_CATEGORIES.get(category)
    if category_name is None:
        async with AsyncSessionFactory() as session:
            cc_res = await session.execute(select(CustomCategory).where(CustomCategory.slug == category))
            cc = cc_res.scalar_one_or_none()
            category_name = cc.name if cc else "Custom Category"
    
    await state.update_data(category=category)

    if category == CATEGORY_TELEGRAM_OLD:
        # Show year selection buttons (2013–2024, 12 years)
        year_buttons: list[list[InlineKeyboardButton]] = []
        row: list[InlineKeyboardButton] = []
        for yr in range(2013, 2025):
            btn = apply_button_style(InlineKeyboardButton(
                text=str(yr),
                callback_data=f"admin_add_year_{yr}",
            ), 'primary', "5416041192905265756")
            row.append(btn)
            if len(row) == 4:
                year_buttons.append(row)
                row = []
        if row:
            year_buttons.append(row)
        year_buttons.append([apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_cancel_add"), 'danger', "5416041192905265756")])
        await query.message.edit_text(
            f"➕ <b>Add New Number</b>\n\n"
            f"📁 Category: <b>{category_name}</b>\n\n"
            f"Step 2/6: Select the <b>account year</b>:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=year_buttons),
            parse_mode=ParseMode.HTML,
        )
        return

    await state.set_state(AdminAddNumber.country)
    
    await query.message.edit_text(
        f"➕ <b>Add New Number</b>\n\n"
        f"📁 Category: <b>{category_name}</b>\n\n"
        f"Step 2/5: Enter the <b>country name</b>:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_cancel_add"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("admin_add_year_"))
@admin_only
async def cb_admin_add_year(query: CallbackQuery, state: FSMContext) -> None:
    """Year selected for Telegram Old Accounts, now ask for country."""
    await query.answer()
    try:
        year = int(query.data.replace("admin_add_year_", ""))
    except ValueError:
        await query.answer("Invalid year.", show_alert=True)
        return

    await state.update_data(year=year)
    await state.set_state(AdminAddNumber.country)

    await query.message.edit_text(
        f"➕ <b>Add New Number</b>\n\n"
        f"📁 Category: <b>📱 Telegram Old Accounts</b>\n"
        f"📅 Year: <b>{year}</b>\n\n"
        f"Step 3/6: Enter the <b>country name</b>:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_cancel_add"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminAddNumber.country)
@admin_only
async def fsm_add_country(message: Message, state: FSMContext) -> None:
    await state.update_data(country=message.text.strip().lower())
    await state.set_state(AdminAddNumber.phone)
    await message.answer(
        "Step 3/5: Enter the <b>phone number</b> (e.g. +91 9876543210):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_cancel_add"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminAddNumber.phone)
@admin_only
async def fsm_add_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(phone=message.text.strip())
    await state.set_state(AdminAddNumber.price)
    await message.answer(
        "Step 4/5: Enter the <b>price in USDT</b> (e.g. 5.00):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_cancel_add"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminAddNumber.price)
@admin_only
async def fsm_add_price(message: Message, state: FSMContext) -> None:
    try:
        price = Decimal(message.text.strip())
        if price <= 0:
            raise ValueError
    except Exception:
        await message.answer("❌ Invalid price. Please enter a positive number like 5.00")
        return
    await state.update_data(price=str(price))
    await state.set_state(AdminAddNumber.session_string)
    await message.answer(
        "Step 5/5: Paste the <b>Pyrogram Session String</b> for this number\n"
        "(generate it with <code>generate_session.py</code>):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_cancel_add"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminAddNumber.session_string)
@admin_only
async def fsm_add_session_string(message: Message, state: FSMContext) -> None:
    await state.update_data(session_string=message.text.strip())
    await state.set_state(AdminAddNumber.twofa_password)
    await message.answer(
        "Does this account have a 2FA password? Enter it now, or send <code>0</code> to skip.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_cancel_add"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminAddNumber.twofa_password)
@admin_only
async def fsm_add_twofa_password(message: Message, state: FSMContext) -> None:
    raw = message.text.strip()
    twofa_enc: Optional[str] = None
    if raw != "0":
        twofa_enc = encrypt_privkey(raw)

    data = await state.get_data()
    session_str = data.get("session_string", "")
    if not session_str:
        await message.answer("❌ Session string is missing. Please restart the add number flow.")
        await state.clear()
        return
    category = data.get("category", CATEGORY_TELEGRAM_ACCOUNTS)
    category_name = PRODUCT_CATEGORIES.get(category)
    if category_name is None:
        async with AsyncSessionFactory() as session:
            cc_res = await session.execute(select(CustomCategory).where(CustomCategory.slug == category))
            cc = cc_res.scalar_one_or_none()
            category_name = cc.name if cc else "Custom Category"

    async with AsyncSessionFactory() as session:
        product = Product(
            category=category,
            country=data["country"],
            phone_number=data["phone"],
            price=Decimal(data["price"]),
            session_string=session_str,
            twofa_password=twofa_enc,
            status="Available",
            year=data.get("year"),
        )
        session.add(product)
        await session.commit()

    year = data.get("year")
    year_line = f"📅 Year: <b>{year}</b>\n" if year else ""
    twofa_line = "🔐 2FA: ✅ Set\n" if twofa_enc else ""
    await state.clear()
    await message.answer(
        f"✅ <b>Number Added Successfully!</b>\n\n"
        f"📁 Category: <b>{category_name}</b>\n"
        f"{year_line}"
        f"📱 Number: <b>{data['phone']}</b>\n"
        f"🌍 Country: <b>{get_country_flag(data['country'])} {data['country'].title()}</b>\n"
        f"💰 Price: <b>${data['price']} USDT</b>\n"
        f"🔐 Session: ✅ Configured\n"
        f"{twofa_line}",
        reply_markup=build_admin_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "admin_cancel_add")
@admin_only
async def cb_admin_cancel_add(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await state.clear()
    try:
        await query.message.edit_text(
            "❌ Number addition cancelled.\n\n🔐 <b>Admin Panel</b>",
            reply_markup=build_admin_keyboard(),
            parse_mode=ParseMode.HTML,
        )
    except TelegramAPIError:
        await query.message.answer(
            "❌ Cancelled.\n\n🔐 <b>Admin Panel</b>",
            reply_markup=build_admin_keyboard(),
            parse_mode=ParseMode.HTML,
        )


@router.callback_query(F.data == "admin_add_premium_country")
@admin_only
async def cb_admin_add_premium_country(query: CallbackQuery, state: FSMContext) -> None:
    """Start add premium country flow."""
    await query.answer()
    await state.set_state(AdminAddPremiumCountry.country)
    await query.message.edit_text(
        "⭐ <b>Add Premium Country</b>\n\nEnter the <b>country name</b> for Telegram Premium:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_menu"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminAddPremiumCountry.country)
@admin_only
async def fsm_prem_country_name(message: Message, state: FSMContext) -> None:
    country_name = message.text.strip().lower()
    await state.update_data(prem_add_country=country_name)
    await state.set_state(AdminAddPremiumCountry.price)
    await message.answer(
        f"Country: <b>{country_name.title()}</b>\n\nEnter the <b>price per account</b> (USDT):",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminAddPremiumCountry.price)
@admin_only
async def fsm_prem_country_price(message: Message, state: FSMContext) -> None:
    try:
        price = Decimal(message.text.strip())
        if price <= 0:
            raise ValueError
    except Exception:
        await message.answer("❌ Invalid price. Enter a positive number like 5.00:", parse_mode=ParseMode.HTML)
        return

    data = await state.get_data()
    country_name = data["prem_add_country"]
    await state.clear()

    async with AsyncSessionFactory() as session:
        existing = await session.execute(
            select(PremiumCountry).where(PremiumCountry.country == country_name.lower())
        )
        pc = existing.scalar_one_or_none()
        if pc:
            await session.execute(
                update(PremiumCountry).where(PremiumCountry.country == country_name.lower()).values(price=price)
            )
        else:
            session.add(PremiumCountry(country=country_name.lower(), price=price))
        await session.commit()

    await message.answer(
        f"✅ Premium country <b>{country_name.title()}</b> added at <b>${price:.2f}</b> USDT.",
        reply_markup=build_admin_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "admin_add_custom_cat")
@admin_only
async def cb_admin_add_custom_cat(query: CallbackQuery, state: FSMContext) -> None:
    """Start custom category creation flow."""
    await query.answer()
    await state.set_state(AdminCustomCategoryState.name)
    await query.message.edit_text(
        "➕ <b>Create Custom Category</b>\n\n"
        "Enter the <b>category name</b>.\n"
        "<i>⚠️ Keep it short — this exact name will appear as an inline button in the Buy Numbers menu.</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_cancel_add"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminCustomCategoryState.name)
@admin_only
async def fsm_custom_cat_name(message: Message, state: FSMContext) -> None:
    """Store category name, ask for optional sub-menu name."""
    name = message.text.strip()
    if not name:
        await message.answer("❌ Name cannot be empty. Please enter a category name:")
        return
    slug_suffix = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    if not slug_suffix:
        await message.answer("❌ Category name must contain at least one letter or digit. Please try again:")
        return
    slug = "custom_" + slug_suffix
    await state.update_data(custom_cat_name=name, custom_cat_slug=slug)
    await state.set_state(AdminCustomCategoryState.sub_name)
    await message.answer(
        f"✅ Category name set: <b>{name}</b>\n\n"
        f"Now enter a <b>sub-menu button name</b> to display inside this category "
        f"(e.g. <i>Buy {name}</i>), or send <b>0</b> to skip.\n\n"
        f"<i>If you enter a name, tapping the category will first show that sub-button "
        f"before listing countries.</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_cancel_add"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminCustomCategoryState.sub_name)
@admin_only
async def fsm_custom_cat_sub_name(message: Message, state: FSMContext) -> None:
    """Save custom category to DB, then continue to add number."""
    raw = message.text.strip()
    sub_name: str | None = None if raw == "0" else raw

    data = await state.get_data()
    name: str = data["custom_cat_name"]
    slug: str = data["custom_cat_slug"]

    async with AsyncSessionFactory() as session:
        # Ensure slug uniqueness
        existing = await session.execute(select(CustomCategory).where(CustomCategory.slug == slug))
        if existing.scalar_one_or_none() is not None:
            slug = slug + "_" + uuid.uuid4().hex[:8]
        cc = CustomCategory(slug=slug, name=name, sub_name=sub_name)
        session.add(cc)
        await session.commit()

    await state.update_data(category=slug)
    await state.set_state(AdminAddNumber.country)

    sub_label = sub_name if sub_name else "None (shows countries directly)"
    await message.answer(
        f"<tg-emoji emoji-id=\"5206607081334906820\">✅</tg-emoji> <b>Custom Category Created!</b>\n\n"
        f"<tg-emoji emoji-id=\"5305265301917549162\">📁</tg-emoji> Name: <b>{name}</b>\n"
        f"<tg-emoji emoji-id=\"5305265301917549162\">🔗</tg-emoji> Sub-menu: <b>{sub_label}</b>\n\n"
        f"Now continue adding the number.\n"
        f"Step 2/5: Enter the <b>country name</b>:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_cancel_add"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


# ── View / Remove Inventory ───────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_inventory_"))
@admin_only
async def cb_admin_inventory(query: CallbackQuery) -> None:
    await query.answer()
    page = int(query.data.split("_")[-1])
    async with AsyncSessionFactory() as session:
        rows = await session.execute(
            select(Product).where(Product.status != "Sold").order_by(Product.id)
        )
        products = rows.scalars().all()

    if not products:
        await query.message.edit_text(
            "📦 Inventory is empty.",
            reply_markup=build_admin_keyboard(),
        )
        return

    total_pages = (len(products) + PAGE_SIZE - 1) // PAGE_SIZE
    page_products = products[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]

    buttons = [
        [apply_button_style(InlineKeyboardButton(
            text=f"[{p.status}] {p.phone_number} ({p.country}) ${p.price:.2f}",
            callback_data=f"admin_inv_item_{p.id}",
        ), 'primary', "5406683434124859552")]
        for p in page_products
    ]
    nav_row: list[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(
            apply_button_style(InlineKeyboardButton(text="Prev", callback_data=f"admin_inventory_{page - 1}"), 'primary', "5416041192905265756")
        )
    if page < total_pages - 1:
        nav_row.append(
            apply_button_style(InlineKeyboardButton(text="Next", callback_data=f"admin_inventory_{page + 1}"), 'primary', "5416117059207572332")
        )
    if nav_row:
        buttons.append(nav_row)
    buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="admin_menu"), 'danger', "5416041192905265756")])

    await query.message.edit_text(
        f"📦 <b>Inventory</b> (Page {page + 1}/{total_pages}):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("admin_inv_item_"))
@admin_only
async def cb_admin_inv_item(query: CallbackQuery) -> None:
    await query.answer()
    product_id = int(query.data.split("_")[-1])
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        p = result.scalar_one_or_none()
    if p is None:
        await query.answer("Product not found.", show_alert=True)
        return

    await query.message.edit_text(
        f"📱 <b>{p.phone_number}</b>\nCountry: {p.country}\n"
        f"Price: ${p.price:.2f}\nStatus: {p.status}\n"
        f"Session: {'✅ Set' if p.session_string else '❌ Not set'}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                apply_button_style(InlineKeyboardButton(
                    text="Remove/Mark Sold", callback_data=f"admin_remove_{p.id}"
                ), 'danger', "5276032951342088188"),
            ],
            [apply_button_style(InlineKeyboardButton(text="Back", callback_data="admin_inventory_0"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("admin_remove_"))
@admin_only
async def cb_admin_remove(query: CallbackQuery) -> None:
    await query.answer()
    product_id = int(query.data.split("_")[-1])
    async with AsyncSessionFactory() as session:
        await session.execute(
            update(Product).where(Product.id == product_id).values(status="Sold")
        )
        await session.commit()
    await query.message.edit_text(
        "✅ Number marked as Sold / removed from storefront.",
        reply_markup=build_admin_keyboard(),
    )


# ── Pending Orders ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_orders")
@admin_only
async def cb_admin_orders(query: CallbackQuery) -> None:
    await query.answer()
    async with AsyncSessionFactory() as session:
        rows = await session.execute(
            select(Order).where(Order.status == "PendingAdmin").order_by(Order.id)
        )
        orders = rows.scalars().all()

    if not orders:
        await query.message.edit_text(
            "📋 No pending orders.",
            reply_markup=build_admin_keyboard(),
        )
        return

    buttons = [
        [apply_button_style(InlineKeyboardButton(
            text=f"Order #{o.id} (User {o.user_id})",
            callback_data=f"admin_order_detail_{o.id}",
        ), 'primary', "5406683434124859552")]
        for o in orders
    ]
    buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="admin_menu"), 'danger', "5416041192905265756")])
    await query.message.edit_text(
        "📋 <b>Pending Orders:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("admin_order_detail_"))
@admin_only
async def cb_admin_order_detail(query: CallbackQuery) -> None:
    await query.answer()
    order_id = int(query.data.split("_")[-1])
    async with AsyncSessionFactory() as session:
        result_o = await session.execute(select(Order).where(Order.id == order_id))
        order = result_o.scalar_one_or_none()
        if order is None:
            await query.answer("Order not found.", show_alert=True)
            return
        result_p = await session.execute(
            select(Product).where(Product.id == order.product_id)
        )
        p = result_p.scalar_one_or_none()
        result_u = await session.execute(select(User).where(User.id == order.user_id))
        u = result_u.scalar_one_or_none()

    await query.message.edit_text(
        f"📋 <b>Order #{order_id}</b>\n"
        f"Buyer: @{u.username or 'N/A'} (ID: {order.user_id})\n"
        f"Item: {p.phone_number if p else 'N/A'} ({p.country if p else ''})\n"
        f"Price: ${p.price:.2f if p else 0}\n"
        f"Status: {order.status}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                apply_button_style(InlineKeyboardButton(
                    text="Fulfill", callback_data=f"admin_fulfill_{order_id}"
                ), 'success', "5206607081334906820"),
                apply_button_style(InlineKeyboardButton(
                    text="Refund", callback_data=f"admin_refund_{order_id}"
                ), 'danger', "5416041192905265756"),
            ],
            [apply_button_style(InlineKeyboardButton(text="Back", callback_data="admin_orders"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("admin_fulfill_"))
@admin_only
async def cb_admin_fulfill(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    order_id = int(query.data.split("_")[-1])
    await state.set_state(AdminFulfillOrder.account_details)
    await state.update_data(order_id=order_id)
    await query.message.answer(
        f"✅ Fulfilling Order #{order_id}.\n\n"
        f"Please send the account credentials / OTP details to forward to the buyer:",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminFulfillOrder.account_details)
@admin_only
async def fsm_fulfill_details(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    order_id = data["order_id"]
    details = message.text.strip()

    async with AsyncSessionFactory() as session:
        result_o = await session.execute(select(Order).where(Order.id == order_id))
        order = result_o.scalar_one_or_none()
        if order is None:
            await message.answer("Order not found.")
            await state.clear()
            return

        result_p = await session.execute(
            select(Product).where(Product.id == order.product_id)
        )
        p = result_p.scalar_one_or_none()

        await session.execute(
            update(Order).where(Order.id == order_id).values(status="Completed")
        )
        if p:
            await session.execute(
                update(Product).where(Product.id == p.id).values(status="Sold")
            )
        await session.execute(
            update(Transaction)
            .where(
                Transaction.order_id == order_id,
                Transaction.type == "Purchase",
                Transaction.status == "Pending",
            )
            .values(status="Completed")
        )
        await session.commit()
        buyer_id = order.user_id

    await state.clear()
    try:
        await message.bot.send_message(
            buyer_id,
            f"🎉 <b>Your order is ready!</b>\n\n"
            f"Here are your account details:\n<code>{details}</code>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as exc:
        log.warning("Could not send fulfillment to buyer %s: %s", buyer_id, exc)

    await message.answer(
        f"✅ Order #{order_id} fulfilled and buyer notified.",
        reply_markup=build_admin_keyboard(),
    )


@router.callback_query(F.data.startswith("admin_refund_"))
@admin_only
async def cb_admin_refund(query: CallbackQuery) -> None:
    order_id = int(query.data.split("_")[-1])
    async with AsyncSessionFactory() as session:
        result_o = await session.execute(select(Order).where(Order.id == order_id))
        order = result_o.scalar_one_or_none()
        if order is None:
            await query.answer("Order not found.", show_alert=True)
            return

        result_p = await session.execute(
            select(Product).where(Product.id == order.product_id)
        )
        p = result_p.scalar_one_or_none()

        if p:
            refund_amount = Decimal(str(p.price))
            await session.execute(
                update(User)
                .where(User.id == order.user_id)
                .values(balance=User.balance + refund_amount)
            )
            await session.execute(
                update(Product).where(Product.id == p.id).values(status="Available")
            )
        await session.execute(
            update(Order).where(Order.id == order_id).values(status="Refunded")
        )
        await session.execute(
            update(Transaction)
            .where(
                Transaction.order_id == order_id,
                Transaction.type == "Purchase",
                Transaction.status == "Pending",
            )
            .values(status="Refunded")
        )
        await session.commit()
        buyer_id = order.user_id

    try:
        await query.bot.send_message(
            buyer_id,
            f"↩️ <b>Order #{order_id} refunded.</b>\n"
            f"${p.price:.2f if p else 0} USDT has been returned to your balance.",
            parse_mode=ParseMode.HTML,
        )
    except Exception as exc:
        log.warning("Could not notify buyer %s of refund: %s", buyer_id, exc)

    await query.message.edit_text(
        f"↩️ Order #{order_id} refunded successfully.",
        reply_markup=build_admin_keyboard(),
    )


# ── Broadcast ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_broadcast")
@admin_only
async def cb_admin_broadcast(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await state.set_state(AdminBroadcast.message)
    await query.message.edit_text(
        "📢 <b>Broadcast Message</b>\n\nSend the message you want to broadcast to all users:",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminBroadcast.message)
@admin_only
async def fsm_broadcast(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with AsyncSessionFactory() as session:
        rows = await session.execute(select(User.id))
        user_ids = [r[0] for r in rows.fetchall()]

    sent = 0
    failed = 0
    for uid in user_ids:
        try:
            await message.bot.send_message(uid, message.text)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(
        f"📢 Broadcast complete.\n✅ Sent: {sent}\n❌ Failed: {failed}",
        reply_markup=build_admin_keyboard(),
    )


# ── /tip command ──────────────────────────────────────────────────────────────

@router.message(Command("tip"))
@admin_only
async def cmd_tip(message: Message) -> None:
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer(
            "❌ Usage: <code>/tip @username amount</code>\n"
            "Example: <code>/tip @john 5.00</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    target_str = parts[1].lstrip("@")
    try:
        amount = Decimal(parts[2])
        if amount <= 0:
            raise ValueError
    except (ValueError, InvalidOperation):
        await message.answer(
            "❌ Invalid amount. Must be a positive number like <code>5.00</code>.",
            parse_mode=ParseMode.HTML,
        )
        return

    async with AsyncSessionFactory() as session:
        try:
            uid_int = int(target_str)
            result = await session.execute(select(User).where(User.id == uid_int))
        except ValueError:
            result = await session.execute(
                select(User).where(User.username == target_str)
            )

        target_user = result.scalar_one_or_none()
        if target_user is None:
            await message.answer(
                f"❌ User <b>{target_str}</b> not found in the bot database.",
                parse_mode=ParseMode.HTML,
            )
            return

        await session.execute(
            update(User)
            .where(User.id == target_user.id)
            .values(balance=User.balance + amount)
        )
        txn = Transaction(
            user_id=target_user.id, type="Tip",
            amount=amount, status="Completed",
        )
        session.add(txn)
        await session.commit()
        recipient_id = target_user.id
        display_name = (
            f"@{target_user.username}" if target_user.username else str(target_user.id)
        )

    await message.answer(
        f"✅ Tipped <b>${amount:.2f} USDT</b> to {display_name} successfully.",
        parse_mode=ParseMode.HTML,
    )
    try:
        await message.bot.send_message(
            recipient_id,
            f"🎁 <b>You received a tip of ${amount:.2f} USDT</b> from the admin!\n"
            f"Your balance has been updated.",
            parse_mode=ParseMode.HTML,
        )
    except TelegramAPIError as exc:
        log.warning("Could not notify tip recipient %s: %s", recipient_id, exc)


# ── /help command (admin) ─────────────────────────────────────────────────────

@router.message(Command("help"))
@admin_only
async def cmd_help(message: Message) -> None:
    await message.answer(
        "🔐 <b>Admin Commands &amp; Usage</b>\n\n"
        "<b>Commands:</b>\n"
        "/admin – Open the Admin Panel\n"
        "/tip @username amount – Add balance to a user\n"
        "/setbal @username amount – Set exact balance for a user\n"
        "/remove +phonenumber – Delete a number and all its data\n"
        "/help – Show this help message\n\n"
        "<b>Admin Panel Features:</b>\n"
        "➕ <b>Add Number</b> – Add a new virtual number to inventory\n"
        "📦 <b>View Inventory</b> – Browse and manage all numbers\n"
        "📋 <b>Pending Orders</b> – Fulfill or refund pending orders\n"
        "👥 <b>Users</b> – Browse all users (paginated) with details\n"
        "🔍 <b>Search User</b> – Find a user by Telegram ID or username\n"
        "📢 <b>Broadcast</b> – Send a message to all users\n\n"
        "<b>User detail options:</b>\n"
        "🚫 Ban / ✅ Unban – Ban or unban a user\n"
        "💰 Deposits – View all deposits for a user\n"
        "📦 Purchases – View all purchases with OTP status\n\n"
        "<b>Notes:</b>\n"
        "• /setbal can use @username or numeric Telegram ID\n"
        "• /tip adds to existing balance; /setbal sets exact amount\n"
        "• /remove permanently deletes the number and its session string",
        parse_mode=ParseMode.HTML,
    )


# ── /remove command ───────────────────────────────────────────────────────────

@router.message(Command("order"))
@admin_only
async def cmd_order(message: Message) -> None:
    """Show details of a specific premium order."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: <code>/order ORDER_ID</code>", parse_mode=ParseMode.HTML)
        return
    order_ref = parts[1].strip().upper()
    async with AsyncSessionFactory() as session:
        res = await session.execute(select(PremiumOrder).where(PremiumOrder.order_ref == order_ref))
        prem_order = res.scalar_one_or_none()
    if prem_order is None:
        await message.answer(f"❌ Order <code>{order_ref}</code> not found.", parse_mode=ParseMode.HTML)
        return
    flag = get_country_flag(prem_order.country)
    dt = prem_order.created_at.strftime("%Y-%m-%d %H:%M") if prem_order.created_at else "N/A"
    text = (
        f"📌 <b>Order:</b> <code>{prem_order.order_ref}</code>\n"
        f"👤 <b>User ID:</b> {prem_order.user_id}\n"
        f"🌍 <b>Country:</b> {flag} {prem_order.country.title()}\n"
        f"💵 <b>Price:</b> ${prem_order.price:.2f} USDT\n"
        f"📊 <b>Status:</b> {prem_order.status}\n"
        f"⏰ <b>Created:</b> {dt}"
    )
    kb = None
    if prem_order.status == "Pending":
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Confirm", callback_data=f"prem_admin_confirm_{order_ref}"), 'success', "5206607081334906820"),
            apply_button_style(InlineKeyboardButton(text="Decline", callback_data=f"prem_admin_decline_{order_ref}"), 'danger', "5416041192905265756"),
        ]])
    await message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)


@router.message(Command("orders"))
@admin_only
async def cmd_orders(message: Message) -> None:
    """List all premium orders (pending first)."""
    async with AsyncSessionFactory() as session:
        res = await session.execute(
            select(PremiumOrder).order_by(
                PremiumOrder.status,
                PremiumOrder.created_at.desc()
            )
        )
        all_orders = res.scalars().all()
    if not all_orders:
        await message.answer("No premium orders found.")
        return
    lines = ["<b>Premium Orders</b>\n"]
    for o in all_orders[:50]:
        dt = o.created_at.strftime("%m-%d") if o.created_at else "N/A"
        lines.append(f"• <code>{o.order_ref}</code> | UID:{o.user_id} | {o.country.title()} | {o.status} | {dt}")
    await message.answer("\n".join(lines), parse_mode=ParseMode.HTML)


@router.message(Command("remove"))
@admin_only
async def cmd_remove(message: Message) -> None:
    """Delete a phone number and all associated data from the bot."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ Usage: <code>/remove +phonenumber</code>\n"
            "Example: <code>/remove +919876543210</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    phone_number = parts[1].strip()

    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(Product).where(Product.phone_number == phone_number)
        )
        product = result.scalar_one_or_none()

        if product is None:
            await message.answer(
                f"❌ Number <code>{phone_number}</code> not found in the database.",
                parse_mode=ParseMode.HTML,
            )
            return

        pid = product.id

        # Remove associated orders and their transactions
        ord_rows = await session.execute(
            select(Order).where(Order.product_id == pid)
        )
        orders = ord_rows.scalars().all()
        for order in orders:
            await session.execute(
                delete(Transaction).where(Transaction.order_id == order.id)
            )
        await session.execute(delete(Order).where(Order.product_id == pid))

        # Delete the product (session_string is stored in the product row)
        await session.execute(delete(Product).where(Product.id == pid))
        await session.commit()

    # Stop any running OTP listener for this product
    await otp_manager.stop_product(pid)

    await message.answer(
        f"✅ <b>Number Removed</b>\n\n"
        f"📱 <code>{phone_number}</code> and all associated data "
        f"(session string, orders, transactions) have been permanently deleted.",
        parse_mode=ParseMode.HTML,
    )


# ── /setbal command ───────────────────────────────────────────────────────────

@router.message(Command("setbal"))
@admin_only
async def cmd_setbal(message: Message) -> None:
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer(
            "❌ Usage: <code>/setbal @username amount</code>\n"
            "or:      <code>/setbal user_id amount</code>\n"
            "Example: <code>/setbal @john 10.00</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    target_str = parts[1].lstrip("@")
    try:
        amount = Decimal(parts[2])
        if amount < 0:
            raise ValueError
    except (ValueError, InvalidOperation):
        await message.answer(
            "❌ Invalid amount. Must be a non-negative number like <code>10.00</code>.",
            parse_mode=ParseMode.HTML,
        )
        return

    async with AsyncSessionFactory() as session:
        try:
            uid_int = int(target_str)
            result = await session.execute(select(User).where(User.id == uid_int))
        except ValueError:
            result = await session.execute(
                select(User).where(User.username == target_str)
            )

        target_user = result.scalar_one_or_none()
        if target_user is None:
            await message.answer(
                f"❌ User <b>{target_str}</b> not found in the bot database.",
                parse_mode=ParseMode.HTML,
            )
            return

        old_balance = Decimal(str(target_user.balance))
        await session.execute(
            update(User).where(User.id == target_user.id).values(balance=amount)
        )
        txn = Transaction(
            user_id=target_user.id, type="AdminSetBalance",
            amount=amount, status="Completed",
        )
        session.add(txn)
        await session.commit()
        display_name = (
            f"@{target_user.username}" if target_user.username else str(target_user.id)
        )
        recipient_id = target_user.id

    await message.answer(
        f"✅ Balance updated for {display_name}.\n"
        f"Old: <b>${old_balance:.2f}</b> → New: <b>${amount:.2f} USDT</b>",
        parse_mode=ParseMode.HTML,
    )
    try:
        await message.bot.send_message(
            recipient_id,
            f"💰 <b>Your balance has been updated by an admin.</b>\n"
            f"New balance: <b>${amount:.2f} USDT</b>",
            parse_mode=ParseMode.HTML,
        )
    except TelegramAPIError as exc:
        log.warning("Could not notify setbal recipient %s: %s", recipient_id, exc)


# ── Admin: User Management ────────────────────────────────────────────────────

async def _show_admin_user_detail(message: Message, user_id: int) -> None:
    """Helper: render user detail card (used by detail callback, ban/unban, search)."""
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        u = result.scalar_one_or_none()
        if u is None:
            await message.edit_text("❌ User not found.", reply_markup=build_admin_keyboard())
            return

        dep_rows = await session.execute(
            select(Transaction).where(
                Transaction.user_id == user_id, Transaction.type == "Deposit",
            )
        )
        deposits = dep_rows.scalars().all()
        total_deposited = sum(Decimal(str(d.amount)) for d in deposits)

        ord_rows = await session.execute(
            select(Order).where(Order.user_id == user_id, Order.status == "Completed")
        )
        purchases = ord_rows.scalars().all()

    ban_btn = (
        apply_button_style(InlineKeyboardButton(text="Unban", callback_data=f"admin_unban_{user_id}"), 'success', "5206607081334906820")
        if u.is_banned
        else apply_button_style(InlineKeyboardButton(text="Ban", callback_data=f"admin_ban_{user_id}"), 'danger', "5276032951342088188")
    )
    joined = u.created_at.strftime("%Y-%m-%d") if u.created_at else "N/A"
    await message.edit_text(
        f"<tg-emoji emoji-id='5319175438268913255'>👤</tg-emoji> <b>User Details</b>\n\n"
        f"ID: <code>{u.id}</code>\n"
        f"Username: @{u.username or 'N/A'}\n"
        f"<tg-emoji emoji-id='5409048419211682843'>💰</tg-emoji> Balance: <b>${u.balance:.2f} USDT</b>\n"
        f"Total Deposited: <b>${total_deposited:.2f} USDT</b>\n"
        f"Purchases: <b>{len(purchases)}</b>\n"
        f"Referred by: {u.referred_by or 'None'}\n"
        f"Joined: {joined}\n"
        f"Status: {'<tg-emoji emoji-id=\"5276032951342088188\">🚫</tg-emoji> Banned' if u.is_banned else '<tg-emoji emoji-id=\"5206607081334906820\">✅</tg-emoji> Active'}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [ban_btn],
            [
                apply_button_style(InlineKeyboardButton(
                    text="Deposits",
                    callback_data=f"admin_user_deposits_{user_id}",
                ), 'primary', "5409048419211682843"),
                apply_button_style(InlineKeyboardButton(
                    text="Purchases",
                    callback_data=f"admin_user_purchases_{user_id}",
                ), 'primary', "5406683434124859552"),
            ],
            [apply_button_style(InlineKeyboardButton(
                text="Adjust Discount",
                callback_data=f"admin_set_user_discount_{user_id}",
            ), 'primary', "5427168083074628963")],
            [apply_button_style(InlineKeyboardButton(text="Back to Users", callback_data="admin_users_0"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("admin_users_"))
@admin_only
async def cb_admin_users(query: CallbackQuery) -> None:
    await query.answer()
    page = int(query.data.split("_")[-1])
    async with AsyncSessionFactory() as session:
        rows = await session.execute(select(User).order_by(User.id))
        users = rows.scalars().all()

    if not users:
        await query.message.edit_text("👥 No users found.", reply_markup=build_admin_keyboard())
        return

    total_pages = (len(users) + PAGE_SIZE - 1) // PAGE_SIZE
    page_users = users[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]

    buttons = [
        [apply_button_style(InlineKeyboardButton(
            text=(
                f"{'🚫 ' if u.is_banned else ''}"
                f"{('@' + u.username) if u.username else str(u.id)}"
                f" (ID: {u.id})"
            ),
            callback_data=f"admin_user_detail_{u.id}",
        ), 'primary', "5260343246831237239")]
        for u in page_users
    ]
    nav_row: list[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(
            apply_button_style(InlineKeyboardButton(text="Prev", callback_data=f"admin_users_{page - 1}"), 'primary', "5416041192905265756")
        )
    if page < total_pages - 1:
        nav_row.append(
            apply_button_style(InlineKeyboardButton(text="Next", callback_data=f"admin_users_{page + 1}"), 'primary', "5416117059207572332")
        )
    if nav_row:
        buttons.append(nav_row)
    buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="admin_menu"), 'danger', "5416041192905265756")])

    await query.message.edit_text(
        f"👥 <b>Users</b> (Page {page + 1}/{total_pages}, Total: {len(users)}):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("admin_user_detail_"))
@admin_only
async def cb_admin_user_detail(query: CallbackQuery) -> None:
    await query.answer()
    user_id = int(query.data.split("_")[-1])
    await _show_admin_user_detail(query.message, user_id)


@router.callback_query(F.data.startswith("admin_ban_"))
@admin_only
async def cb_admin_ban(query: CallbackQuery) -> None:
    user_id = int(query.data.split("_")[-1])
    async with AsyncSessionFactory() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(is_banned=True)
        )
        await session.commit()
    await query.answer("🚫 User banned.", show_alert=True)
    await _show_admin_user_detail(query.message, user_id)


@router.callback_query(F.data.startswith("admin_unban_"))
@admin_only
async def cb_admin_unban(query: CallbackQuery) -> None:
    user_id = int(query.data.split("_")[-1])
    async with AsyncSessionFactory() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(is_banned=False)
        )
        await session.commit()
    await query.answer("✅ User unbanned.", show_alert=True)
    await _show_admin_user_detail(query.message, user_id)


@router.callback_query(F.data.startswith("admin_user_deposits_"))
@admin_only
async def cb_admin_user_deposits(query: CallbackQuery) -> None:
    user_id = int(query.data.split("_")[-1])
    async with AsyncSessionFactory() as session:
        rows = await session.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id, Transaction.type == "Deposit")
            .order_by(Transaction.created_at.desc())
        )
        deposits = rows.scalars().all()

    if not deposits:
        await query.answer("No deposits found for this user.", show_alert=True)
        return

    await query.answer()
    lines = [f"💰 <b>Deposits for User {user_id}</b>\n"]
    total = Decimal("0")
    for d in deposits[:MAX_DISPLAY_ITEMS]:
        dt = d.created_at.strftime("%Y-%m-%d %H:%M") if d.created_at else "N/A"
        lines.append(f"• ${d.amount:.2f} – {dt} [{d.status}]")
        total += Decimal(str(d.amount))
    if len(deposits) > MAX_DISPLAY_ITEMS:
        lines.append(f"<i>… and {len(deposits) - MAX_DISPLAY_ITEMS} more</i>")
    lines.append(f"\n<b>Total: ${total:.2f} USDT</b>")

    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(
                text="◀️ Back", callback_data=f"admin_user_detail_{user_id}",
            ), 'danger', "5409048419211682843"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("admin_user_purchases_"))
@admin_only
async def cb_admin_user_purchases(query: CallbackQuery) -> None:
    user_id = int(query.data.split("_")[-1])
    async with AsyncSessionFactory() as session:
        ord_rows = await session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        orders = ord_rows.scalars().all()

        product_ids = [o.product_id for o in orders]
        products: dict[int, Product] = {}
        if product_ids:
            prod_rows = await session.execute(
                select(Product).where(Product.id.in_(product_ids))
            )
            products = {p.id: p for p in prod_rows.scalars().all()}

    if not orders:
        await query.answer("No purchases found for this user.", show_alert=True)
        return

    await query.answer()
    lines = [f"📦 <b>Purchases for User {user_id}</b>\n"]
    for o in orders[:MAX_DISPLAY_ITEMS]:
        p = products.get(o.product_id)
        phone = p.phone_number if p else "N/A"
        country = p.country if p else "N/A"
        otp_status = "✅ OTP received" if (p and p.latest_otp) else "⏳ No OTP yet"
        dt = o.created_at.strftime("%Y-%m-%d") if o.created_at else "N/A"
        lines.append(
            f"• <b>{phone}</b> ({country}) [{o.status}] {otp_status} – {dt}"
        )
    if len(orders) > MAX_DISPLAY_ITEMS:
        lines.append(f"<i>… and {len(orders) - MAX_DISPLAY_ITEMS} more</i>")

    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(
                text="◀️ Back", callback_data=f"admin_user_detail_{user_id}",
            ), 'danger', "5409048419211682843"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


# ── Admin: Search User ────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_search_user")
@admin_only
async def cb_admin_search_user(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await state.set_state(AdminSearchUser.user_input)
    await query.message.edit_text(
        "🔍 <b>Search User</b>\n\nEnter a <b>Telegram ID</b> or <b>@username</b>:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_cancel_search"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "admin_cancel_search")
@admin_only
async def cb_admin_cancel_search(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await state.clear()
    await query.message.edit_text(
        "🔐 <b>Admin Panel</b>",
        reply_markup=build_admin_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminSearchUser.user_input)
@admin_only
async def fsm_search_user(message: Message, state: FSMContext) -> None:
    await state.clear()
    target_str = message.text.strip().lstrip("@")

    async with AsyncSessionFactory() as session:
        try:
            uid_int = int(target_str)
            result = await session.execute(select(User).where(User.id == uid_int))
        except ValueError:
            result = await session.execute(
                select(User).where(User.username == target_str)
            )

        u = result.scalar_one_or_none()
        if u is None:
            await message.answer(
                f"❌ User <b>{target_str}</b> not found in the bot database.",
                reply_markup=build_admin_keyboard(),
                parse_mode=ParseMode.HTML,
            )
            return

        dep_rows = await session.execute(
            select(Transaction).where(
                Transaction.user_id == u.id, Transaction.type == "Deposit",
            )
        )
        deposits = dep_rows.scalars().all()
        total_deposited = sum(Decimal(str(d.amount)) for d in deposits)

        ord_rows = await session.execute(
            select(Order).where(Order.user_id == u.id, Order.status == "Completed")
        )
        purchases = ord_rows.scalars().all()

    ban_btn = (
        apply_button_style(InlineKeyboardButton(text="Unban", callback_data=f"admin_unban_{u.id}"), 'success', "5206607081334906820")
        if u.is_banned
        else apply_button_style(InlineKeyboardButton(text="Ban", callback_data=f"admin_ban_{u.id}"), 'danger', "5276032951342088188")
    )
    joined = u.created_at.strftime("%Y-%m-%d") if u.created_at else "N/A"
    await message.answer(
        f"<tg-emoji emoji-id='5319175438268913255'>👤</tg-emoji> <b>User Details</b>\n\n"
        f"ID: <code>{u.id}</code>\n"
        f"Username: @{u.username or 'N/A'}\n"
        f"<tg-emoji emoji-id='5409048419211682843'>💰</tg-emoji> Balance: <b>${u.balance:.2f} USDT</b>\n"
        f"Total Deposited: <b>${total_deposited:.2f} USDT</b>\n"
        f"Purchases: <b>{len(purchases)}</b>\n"
        f"Referred by: {u.referred_by or 'None'}\n"
        f"Joined: {joined}\n"
        f"Status: {'<tg-emoji emoji-id=\"5276032951342088188\">🚫</tg-emoji> Banned' if u.is_banned else '<tg-emoji emoji-id=\"5206607081334906820\">✅</tg-emoji> Active'}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [ban_btn],
            [
                apply_button_style(InlineKeyboardButton(
                    text="Deposits",
                    callback_data=f"admin_user_deposits_{u.id}",
                ), 'primary', "5409048419211682843"),
                apply_button_style(InlineKeyboardButton(
                    text="Purchases",
                    callback_data=f"admin_user_purchases_{u.id}",
                ), 'primary', "5406683434124859552"),
            ],
            [apply_button_style(InlineKeyboardButton(
                text="Adjust Discount",
                callback_data=f"admin_set_user_discount_{u.id}",
            ), 'primary', "5427168083074628963")],
            [apply_button_style(InlineKeyboardButton(text="Back to Admin", callback_data="admin_menu"), 'danger', "5416041192905265756")],
        ]),
        parse_mode=ParseMode.HTML,
    )


# ── My Purchases (user) ───────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_set_user_discount_"))
@admin_only
async def cb_admin_set_user_discount(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    user_id = int(query.data.split("_")[-1])
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminUserDiscountState.discount_pct)
    await query.message.edit_text(
        f"🏷️ <b>Set Personal Discount for User {user_id}</b>\n\n"
        f"Step 1/2: Enter the <b>discount percentage</b>\n"
        f"Enter <code>0</code> to remove personal discount.\n"
        f"Example: <code>15</code> for 15% discount",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data=f"admin_user_detail_{user_id}"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminUserDiscountState.discount_pct)
@admin_only
async def fsm_user_discount_pct(message: Message, state: FSMContext) -> None:
    try:
        pct = Decimal(message.text.strip().replace("%", ""))
        if pct < 0 or pct >= 100:
            raise ValueError
    except Exception:
        await message.answer(
            "❌ Invalid percentage. Enter 0-99 (e.g. 15):",
            parse_mode=ParseMode.HTML,
        )
        return

    if pct == 0:
        data = await state.get_data()
        target_uid = data["target_user_id"]
        await state.clear()
        async with AsyncSessionFactory() as session:
            await session.execute(
                delete(UserDiscount).where(UserDiscount.user_id == target_uid)
            )
            await session.commit()
        await message.answer(
            f"✅ Personal discount removed for user {target_uid}.",
            reply_markup=build_admin_keyboard(),
            parse_mode=ParseMode.HTML,
        )
        return

    await state.update_data(discount_pct=str(pct))
    await state.set_state(AdminUserDiscountState.min_deposit)
    await message.answer(
        f"✅ Discount: <b>{pct:.0f}%</b>\n\n"
        f"Step 2/2: Enter the <b>minimum deposit amount</b> (in USD)\n"
        f"This discount applies when user has deposited this amount.\n"
        f"Example: <code>0</code> for instant discount regardless of deposits",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminUserDiscountState.min_deposit)
@admin_only
async def fsm_user_discount_min_deposit(message: Message, state: FSMContext) -> None:
    try:
        min_dep = Decimal(message.text.strip().replace("$", ""))
        if min_dep < 0:
            raise ValueError
    except Exception:
        await message.answer("❌ Invalid amount. Enter a non-negative number:", parse_mode=ParseMode.HTML)
        return

    data = await state.get_data()
    pct = Decimal(data["discount_pct"])
    target_uid = data["target_user_id"]
    await state.clear()

    async with AsyncSessionFactory() as session:
        existing_res = await session.execute(
            select(UserDiscount).where(UserDiscount.user_id == target_uid)
        )
        existing = existing_res.scalar_one_or_none()
        if existing:
            await session.execute(
                update(UserDiscount)
                .where(UserDiscount.user_id == target_uid)
                .values(discount_pct=pct, min_deposit=min_dep)
            )
        else:
            ud = UserDiscount(user_id=target_uid, min_deposit=min_dep, discount_pct=pct)
            session.add(ud)
        await session.commit()

    await message.answer(
        f"✅ <b>Personal Discount Set!</b>\n\n"
        f"User {target_uid} will get <b>{pct:.0f}% discount</b> on all purchases "
        f"(min deposit: ${min_dep:.0f}).",
        reply_markup=build_admin_keyboard(),
        parse_mode=ParseMode.HTML,
    )

    try:
        await message.bot.send_message(
            target_uid,
            f"🎉 <b>Special Offer Just For You!</b>\n\n"
            f"🏷️ You've been granted a <b>{pct:.0f}% personal discount</b> on all purchases!\n"
            f"{'This applies to all your purchases.' if min_dep == 0 else f'This applies once you have deposited ${min_dep:.0f}+ in total.'}\n\n"
            f"Start shopping now to enjoy your exclusive discount! 🛒",
            parse_mode=ParseMode.HTML,
        )
    except Exception as exc:
        log.warning("Could not notify user %s of personal discount: %s", target_uid, exc)


@router.callback_query(F.data == "admin_create_gift_code")
@admin_only
async def cb_admin_create_gift_code(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer()
    await state.set_state(AdminCreateGiftCode.amount)
    await query.message.edit_text(
        "🎁 <b>Create Gift Code</b>\n\n"
        "Step 1/3: Enter the <b>amount in USDT</b> to give\n"
        "Example: <code>5.00</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            apply_button_style(InlineKeyboardButton(text="Cancel", callback_data="admin_menu"), 'danger', "5416041192905265756"),
        ]]),
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminCreateGiftCode.amount)
@admin_only
async def fsm_gift_code_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = Decimal(message.text.strip().replace("$", ""))
        if amount <= 0:
            raise ValueError
    except Exception:
        await message.answer("❌ Invalid amount. Enter a positive number like 5.00:", parse_mode=ParseMode.HTML)
        return
    await state.update_data(gift_amount=str(amount))
    await state.set_state(AdminCreateGiftCode.max_claims)
    await message.answer(
        f"✅ Amount: <b>${amount:.2f} USDT</b>\n\n"
        f"Step 2/3: Enter the <b>maximum number of claims</b>\n"
        f"How many users can claim this code?\n"
        f"Example: <code>100</code>",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminCreateGiftCode.max_claims)
@admin_only
async def fsm_gift_code_max_claims(message: Message, state: FSMContext) -> None:
    try:
        max_claims = int(message.text.strip())
        if max_claims <= 0:
            raise ValueError
    except Exception:
        await message.answer("❌ Invalid number. Enter a positive integer like 100:", parse_mode=ParseMode.HTML)
        return
    await state.update_data(max_claims=max_claims)
    await state.set_state(AdminCreateGiftCode.min_buy_volume)
    await message.answer(
        f"✅ Max Claims: <b>{max_claims}</b>\n\n"
        f"Step 3/3: Enter the <b>minimum total buying volume</b> required (in USDT)\n"
        f"Enter <code>0</code> for no requirement.\n"
        f"Example: <code>10</code> means user must have bought $10+ worth",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminCreateGiftCode.min_buy_volume)
@admin_only
async def fsm_gift_code_min_buy_volume(message: Message, state: FSMContext) -> None:
    try:
        min_vol = Decimal(message.text.strip().replace("$", ""))
        if min_vol < 0:
            raise ValueError
    except Exception:
        await message.answer("❌ Invalid amount. Enter 0 or a positive number:", parse_mode=ParseMode.HTML)
        return

    data = await state.get_data()
    amount = Decimal(data["gift_amount"])
    max_claims = data["max_claims"]
    await state.clear()

    code = secrets.token_hex(GIFT_CODE_BYTES).upper()

    async with AsyncSessionFactory() as session:
        gift = GiftCode(
            code=code,
            amount=amount,
            max_claims=max_claims,
            min_buy_volume=min_vol,
        )
        session.add(gift)
        await session.commit()

    min_vol_line = f"🛒 Min Purchase Volume: <b>${min_vol:.2f} USDT</b>" if min_vol > 0 else "🛒 Min Purchase Volume: <b>None</b>"
    await message.answer(
        f"✅ <b>Gift Code Created!</b>\n\n"
        f"🎁 <b>Code:</b> <code>{code}</code>\n"
        f"💰 <b>Amount:</b> ${amount:.2f} USDT per claim\n"
        f"👥 <b>Max Claims:</b> {max_claims}\n"
        f"{min_vol_line}\n\n"
        f"Share this code with users: <code>/claim {code}</code>",
        reply_markup=build_admin_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("claim"))
async def cmd_claim(message: Message) -> None:
    """Claim a gift code."""
    from sqlalchemy import func
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "🎁 <b>Claim Gift Code</b>\n\n"
            "Usage: <code>/claim YOUR_CODE</code>\n\n"
            "Example: <code>/claim WELCOME2024</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    code_input = parts[1].strip().upper()
    user_id = message.from_user.id

    async with AsyncSessionFactory() as session:
        code_res = await session.execute(
            select(GiftCode).where(GiftCode.code == code_input, GiftCode.is_active.is_(True))
        )
        gift_code = code_res.scalar_one_or_none()

        if gift_code is None:
            await message.answer(
                "❌ <b>Invalid Code</b>\n\n"
                "This code doesn't exist or has expired. Please check and try again.",
                parse_mode=ParseMode.HTML,
            )
            return

        if gift_code.claims_count >= gift_code.max_claims:
            await message.answer(
                "❌ <b>Code Exhausted</b>\n\n"
                "This gift code has reached its maximum number of claims.",
                parse_mode=ParseMode.HTML,
            )
            return

        already_res = await session.execute(
            select(GiftCodeClaim).where(
                GiftCodeClaim.code_id == gift_code.id,
                GiftCodeClaim.user_id == user_id,
            )
        )
        if already_res.scalar_one_or_none():
            await message.answer(
                "❌ <b>Already Claimed</b>\n\n"
                "You have already claimed this gift code.",
                parse_mode=ParseMode.HTML,
            )
            return

        if gift_code.min_buy_volume and Decimal(str(gift_code.min_buy_volume)) > 0:
            buy_vol_res = await session.execute(
                select(func.sum(Transaction.amount)).where(
                    Transaction.user_id == user_id,
                    Transaction.type == "Purchase",
                    Transaction.status == "Completed",
                )
            )
            buy_vol = buy_vol_res.scalar() or Decimal(0)
            if Decimal(str(buy_vol)) < Decimal(str(gift_code.min_buy_volume)):
                await message.answer(
                    f"❌ <b>Requirements Not Met</b>\n\n"
                    f"This code requires a minimum purchase volume of "
                    f"<b>${float(gift_code.min_buy_volume):.2f} USDT</b>.\n\n"
                    f"Your current purchase volume: <b>${float(buy_vol):.2f} USDT</b>",
                    parse_mode=ParseMode.HTML,
                )
                return

        amount = Decimal(str(gift_code.amount))
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(balance=User.balance + amount)
        )

        claim = GiftCodeClaim(code_id=gift_code.id, user_id=user_id)
        session.add(claim)

        new_claims = gift_code.claims_count + 1
        updates: dict = {"claims_count": new_claims}
        if new_claims >= gift_code.max_claims:
            updates["is_active"] = False
        await session.execute(
            update(GiftCode).where(GiftCode.id == gift_code.id).values(**updates)
        )

        txn = Transaction(
            user_id=user_id, type="GiftCode",
            amount=amount, tx_hash=code_input, status="Completed",
        )
        session.add(txn)
        await session.commit()

    await message.answer(
        f"🎉 <b>Gift Code Claimed!</b>\n\n"
        f"🎁 Code: <code>{code_input}</code>\n"
        f"💰 Amount Added: <b>${amount:.2f} USDT</b>\n\n"
        f"Your balance has been updated! 🚀",
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "my_purchases")
async def cb_my_purchases(query: CallbackQuery) -> None:
    await query.answer()
    user_id = query.from_user.id
    async with AsyncSessionFactory() as session:
        ord_rows = await session.execute(
            select(Order)
            .where(Order.user_id == user_id, Order.status == "Completed")
            .order_by(Order.created_at.desc())
        )
        orders = ord_rows.scalars().all()

        product_ids = [o.product_id for o in orders]
        products_map: dict[int, Product] = {}
        if product_ids:
            prod_rows = await session.execute(
                select(Product).where(Product.id.in_(product_ids))
            )
            products_map = {p.id: p for p in prod_rows.scalars().all()}

    if not orders:
        await query.message.edit_text(
            "<tg-emoji emoji-id=\"5406683434124859552\">📦</tg-emoji> You haven't purchased any numbers yet.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756"),
            ]]),
        )
        return

    buttons = []
    for o in orders:
        p = products_map.get(o.product_id)
        phone = p.phone_number if p else f"Order #{o.id}"
        otp_icon = "✅" if (p and p.latest_otp) else "⏳"
        buttons.append([apply_button_style(InlineKeyboardButton(
            text=f"{otp_icon} {phone}",
            callback_data=f"purchase_detail_{o.id}",
        ), 'primary', "5406683434124859552")])
    buttons.append([apply_button_style(InlineKeyboardButton(text="Back", callback_data="back_main"), 'danger', "5416041192905265756")])

    await query.message.edit_text(
        "<tg-emoji emoji-id=\"5406683434124859552\">📦</tg-emoji> <b>My Purchases</b>\n\n<tg-emoji emoji-id=\"5206607081334906820\">✅</tg-emoji> = OTP received  <tg-emoji emoji-id=\"5458603043203327669\">⏳</tg-emoji> = Waiting for OTP",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("purchase_detail_"))
async def cb_purchase_detail(query: CallbackQuery) -> None:
    order_id = int(query.data.split("_")[-1])
    user_id = query.from_user.id

    async with AsyncSessionFactory() as session:
        result_o = await session.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        o = result_o.scalar_one_or_none()
        if o is None:
            await query.answer("Order not found.", show_alert=True)
            return

        result_p = await session.execute(
            select(Product).where(Product.id == o.product_id)
        )
        p = result_p.scalar_one_or_none()

    await query.answer()
    if p is None:
        await query.message.edit_text(
            "❌ Product details not found.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                apply_button_style(InlineKeyboardButton(text="My Purchases", callback_data="my_purchases"), 'danger', "5406683434124859552"),
            ]]),
        )
        return

    dt = o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else "N/A"
    if p.latest_otp:
        otp_line = f"<tg-emoji emoji-id=\"5206607081334906820\">✅</tg-emoji> <b>OTP Received:</b> <code>{p.latest_otp}</code>"
        kb_rows = [
            [apply_button_style(InlineKeyboardButton(text="My Purchases", callback_data="my_purchases"), 'danger', "5406683434124859552")],
        ]
    else:
        otp_line = "<tg-emoji emoji-id=\"5458603043203327669\">⏳</tg-emoji> OTP not received yet."
        kb_rows = [
            [apply_button_style(InlineKeyboardButton(text="Get OTP", callback_data=f"getotp_{p.id}"), 'primary', "5449569374065152798")],
            [apply_button_style(InlineKeyboardButton(text="My Purchases", callback_data="my_purchases"), 'danger', "5406683434124859552")],
        ]

    # Session string display – only for Telegram Sessions category
    if p.category == CATEGORY_TELEGRAM_SESSIONS:
        sess_line = "\n" + format_session_full(p.session_string)
    else:
        sess_line = ""
    # 2FA password
    twofa_detail_line = ""
    if p.twofa_password:
        try:
            twofa_plain = decrypt_privkey(p.twofa_password)
            twofa_detail_line = f"\n🔐 <b>2FA Password:</b> <code>{twofa_plain}</code>"
        except Exception:
            pass

    await query.message.edit_text(
        f"<tg-emoji emoji-id=\"5197252827247841976\">📱</tg-emoji> <b>{p.phone_number}</b>\n"
        f"<tg-emoji emoji-id=\"5460755126761312667\">🌍</tg-emoji> Country: {get_country_flag(p.country)} {p.country}\n"
        f"<tg-emoji emoji-id=\"5409048419211682843\">💵</tg-emoji> Price Paid: ${p.price:.2f} USDT\n"
        f"<tg-emoji emoji-id=\"5274055917766202507\">📅</tg-emoji> Purchased: {dt}\n\n"
        f"{otp_line}"
        f"{sess_line}"
        f"{twofa_detail_line}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows),
        parse_mode=ParseMode.HTML,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  BLOCKCHAIN MONITOR (background task)
# ─────────────────────────────────────────────────────────────────────────────

_last_scanned_block: dict[str, int] = {}


def _load_blockchain_state() -> None:
    global _last_scanned_block
    try:
        with open(BLOCKCHAIN_STATE_FILE, "r") as f:
            data = json.load(f)
        if isinstance(data, dict) and all(
            isinstance(k, str) and isinstance(v, int) for k, v in data.items()
        ):
            _last_scanned_block = data
            log.info("Loaded blockchain state (%d wallets).", len(_last_scanned_block))
        else:
            log.warning("blockchain_state.json has unexpected format; ignoring.")
    except FileNotFoundError:
        pass
    except Exception as exc:
        log.warning("Could not load blockchain state: %s", exc)


def _save_blockchain_state() -> None:
    try:
        with open(BLOCKCHAIN_STATE_FILE, "w") as f:
            json.dump(_last_scanned_block, f)
        log.info("Saved blockchain state (%d wallets).", len(_last_scanned_block))
    except Exception as exc:
        log.warning("Could not save blockchain state: %s", exc)


async def blockchain_monitor(bot: Bot) -> None:
    log.info("Blockchain monitor started.")
    while True:
        try:
            await _check_deposits(bot)
        except Exception as exc:
            log.error("Blockchain monitor error: %s", exc, exc_info=True)
        await asyncio.sleep(BLOCKCHAIN_POLL_INTERVAL)


async def _check_deposits(bot: Bot) -> None:
    async with AsyncSessionFactory() as session:
        rows = await session.execute(
            select(
                User.id, User.deposit_wallet_address,
                User.deposit_wallet_privkey, User.referred_by,
            ).where(User.deposit_wallet_address.isnot(None))
        )
        users_data = rows.fetchall()

    if not users_data:
        return

    try:
        latest_block = await w3.eth.block_number
    except Exception as exc:
        log.warning("Could not fetch latest block: %s", exc)
        return

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(USDT_CONTRACT_ADDRESS), abi=USDT_ABI,
    )

    for uid, wallet_addr, wallet_privkey_enc, referred_by in users_data:
        if not wallet_addr:
            continue

        checksum_addr = Web3.to_checksum_address(wallet_addr)
        from_block = _last_scanned_block.get(wallet_addr, max(0, latest_block - 5))
        if from_block >= latest_block:
            continue

        try:
            events = await contract.events.Transfer.get_logs(
                fromBlock=from_block + 1,
                toBlock=latest_block,
                argument_filters={"to": checksum_addr},
            )
        except Exception as exc:
            log.warning("Filter error for %s: %s", wallet_addr, exc)
            _last_scanned_block[wallet_addr] = latest_block
            continue

        _last_scanned_block[wallet_addr] = latest_block

        for evt in events:
            tx_hash = evt["transactionHash"].hex()
            raw_amount = evt["args"]["value"]
            amount_usdt = Decimal(raw_amount) / Decimal(10 ** 18)
            if amount_usdt <= 0:
                continue

            async with AsyncSessionFactory() as session:
                existing = await session.execute(
                    select(Transaction).where(Transaction.tx_hash == tx_hash)
                )
                if existing.scalar_one_or_none():
                    continue

                await session.execute(
                    update(User)
                    .where(User.id == uid)
                    .values(balance=User.balance + amount_usdt)
                )
                txn = Transaction(
                    user_id=uid, type="Deposit",
                    amount=amount_usdt, tx_hash=tx_hash, status="Completed",
                )
                session.add(txn)

                if referred_by:
                    commission = (
                        amount_usdt
                        * Decimal(str(REFERRAL_COMMISSION_PCT))
                        / Decimal(100)
                    )
                    await session.execute(
                        update(User)
                        .where(User.id == referred_by)
                        .values(balance=User.balance + commission)
                    )
                    ref_txn = Transaction(
                        user_id=referred_by, type="ReferralBonus",
                        amount=commission, tx_hash=tx_hash, status="Completed",
                    )
                    session.add(ref_txn)

                await session.commit()

            try:
                await bot.send_message(
                    uid,
                    f"✅ <b>Deposit received!</b>\n"
                    f"Amount: <b>${amount_usdt:.2f} USDT</b> credited to your balance.",
                    parse_mode=ParseMode.HTML,
                )
            except Exception as exc:
                log.warning("Could not notify user %s: %s", uid, exc)

            if wallet_privkey_enc:
                try:
                    privkey = decrypt_privkey(wallet_privkey_enc)
                    await send_bnb(
                        FAUCET_WALLET_ADDRESS,
                        FAUCET_WALLET_PRIVATE_KEY,
                        wallet_addr,
                        GAS_BNB_AMOUNT,
                    )
                    await asyncio.sleep(BNB_CONFIRMATION_WAIT_SECONDS)
                    sweep_hash = await sweep_usdt(wallet_addr, privkey, amount_usdt)
                    log.info(
                        "Swept %s USDT from %s, tx: %s",
                        amount_usdt, wallet_addr, sweep_hash,
                    )
                except (ContractLogicError, Exception) as exc:
                    log.warning("Auto-sweep failed for %s: %s", wallet_addr, exc)


# ─────────────────────────────────────────────────────────────────────────────
#  OXAPAY PAYMENT MONITOR (background task)
# ─────────────────────────────────────────────────────────────────────────────

async def oxapay_payment_monitor(bot: Bot) -> None:
    """Background task to check pending OxaPay payments."""
    log.info("OxaPay payment monitor started.")
    while True:
        try:
            await _check_pending_oxapay_payments(bot)
        except Exception as exc:
            log.error("OxaPay monitor error: %s", exc, exc_info=True)
        await asyncio.sleep(OXAPAY_POLL_INTERVAL)


async def _check_pending_oxapay_payments(bot: Bot) -> None:
    """Check all pending OxaPay payments and process confirmations."""
    async with AsyncSessionFactory() as session:
        # Get all pending payments
        rows = await session.execute(
            select(OxaPayPayment).where(
                OxaPayPayment.status.in_(["Waiting", "Confirming"])
            )
        )
        pending_payments = rows.scalars().all()
    
    if not pending_payments:
        return
    
    for payment in pending_payments:
        try:
            async with aiohttp.ClientSession() as http_session:
                payload = {
                    "merchant": OXAPAY_API_KEY,
                    "trackId": payment.track_id,
                }
                
                async with http_session.post(OXAPAY_INQUIRY_URL, json=payload) as resp:
                    if resp.status != 200:
                        continue
                    
                    data = await resp.json()
                    status = data.get("status", "").lower()
                    
                    if status in ["paid", "confirmed"]:
                        # Payment confirmed! Credit user
                        await _process_oxapay_confirmation(payment, data)
                        
                        # Notify user
                        try:
                            total_credit = Decimal(str(payment.amount)) + Decimal(str(payment.bonus_amount))
                            await bot.send_message(
                                payment.user_id,
                                f"✅ <b>Payment Confirmed!</b>\n\n"
                                f"💵 Amount: <b>${payment.amount:.2f}</b>\n"
                                f"🎁 Bonus: <b>+${payment.bonus_amount:.2f}</b>\n"
                                f"💰 Total Credited: <b>${total_credit:.2f} USDT</b>\n\n"
                                f"Your balance has been updated!",
                                parse_mode=ParseMode.HTML,
                            )
                        except Exception as exc:
                            log.warning("Could not notify user %s: %s", payment.user_id, exc)
                    
                    elif status == "expired":
                        async with AsyncSessionFactory() as session:
                            await session.execute(
                                update(OxaPayPayment)
                                .where(OxaPayPayment.id == payment.id)
                                .values(status="Expired", updated_at=datetime.now(timezone.utc))
                            )
                            await session.commit()
                    
                    elif status == "confirming":
                        async with AsyncSessionFactory() as session:
                            await session.execute(
                                update(OxaPayPayment)
                                .where(OxaPayPayment.id == payment.id)
                                .values(status="Confirming", updated_at=datetime.now(timezone.utc))
                            )
                            await session.commit()
                            
        except Exception as exc:
            log.warning("Error checking OxaPay payment %s: %s", payment.track_id, exc)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

async def main() -> None:
    _load_blockchain_state()
    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    # Start blockchain monitor as a background task
    asyncio.create_task(blockchain_monitor(bot))
    
    # Start OxaPay payment monitor as a background task
    asyncio.create_task(oxapay_payment_monitor(bot))

    # Save blockchain state on graceful shutdown (SIGINT / SIGTERM)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _save_blockchain_state)
        except (NotImplementedError, RuntimeError):
            pass

    log.info("Bot starting…")
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        _save_blockchain_state()
        await otp_manager.shutdown()
        log.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())