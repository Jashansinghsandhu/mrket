"""
Telegram Session Generator Bot
==============================
A fully functional Telegram bot that guides users through creating
a Pyrogram session string.

HOW TO RUN:
    pip install aiogram==3.25.0 pyrogram tgcrypto
    python session_bot.py

SETUP:
    Replace 'YOUR_BOT_TOKEN_HERE' with a token from @BotFather.
"""

import asyncio
import logging
import re
from typing import Dict

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from pyrogram import Client
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    SessionPasswordNeeded,
)

# Configuration
BOT_TOKEN = "8538104557:AAH-WPtnwbhnRgQVA0veNTwQuJpfImhBEWA"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

router = Router()

# Global dictionary to hold active Pyrogram clients during the login flow
active_clients: Dict[int, Client] = {}


class SessionGen(StatesGroup):
    api_id = State()
    api_hash = State()
    phone = State()
    otp = State()
    password = State()


async def cleanup_client(user_id: int):
    """Safely disconnect and remove a user's Pyrogram client."""
    client = active_clients.pop(user_id, None)
    if client:
        try:
            if client.is_connected:
                await client.disconnect()
        except Exception as e:
            log.warning(f"Error disconnecting client for {user_id}: {e}")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await cleanup_client(message.from_user.id)
    
    welcome_text = (
        "👋 <b>Welcome to the Session Generator Bot!</b>\n\n"
        "I will help you create a Pyrogram session string securely.\n\n"
        "<b>Before we begin, you need your Telegram API credentials:</b>\n"
        "1. Go to <a href='https://my.telegram.org/apps'>my.telegram.org/apps</a>\n"
        "2. Log in with your Telegram account.\n"
        "3. Copy your <b>API ID</b> and <b>API Hash</b>.\n\n"
        "When you are ready, send /generate to start."
    )
    await message.answer(welcome_text, disable_web_page_preview=True)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await cleanup_client(message.from_user.id)
    await message.answer("🚫 Process cancelled. Send /generate to start over.")


@router.message(Command("generate"))
async def cmd_generate(message: Message, state: FSMContext):
    await state.clear()
    await cleanup_client(message.from_user.id)
    
    await state.set_state(SessionGen.api_id)
    await message.answer(
        "Let's get started. You can type /cancel at any time.\n\n"
        "Please send me your <b>API ID</b> (numbers only):"
    )


@router.message(SessionGen.api_id)
async def process_api_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ API ID must contain only numbers. Please try again:")
        return
        
    await state.update_data(api_id=int(message.text))
    await state.set_state(SessionGen.api_hash)
    await message.answer("✅ Good. Now send me your <b>API Hash</b>:")


@router.message(SessionGen.api_hash)
async def process_api_hash(message: Message, state: FSMContext):
    await state.update_data(api_hash=message.text.strip())
    await state.set_state(SessionGen.phone)
    await message.answer(
        "✅ Great. Now send the <b>Phone Number</b> of the account you want to log into.\n\n"
        "Include the country code (e.g., <code>+1234567890</code>):"
    )


@router.message(SessionGen.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip().replace(" ", "")
    data = await state.get_data()
    
    msg = await message.answer("⏳ Connecting to Telegram and requesting OTP...")
    
    # Initialize Pyrogram Client in memory
    client = Client(
        name=f"session_{message.from_user.id}",
        api_id=data["api_id"],
        api_hash=data["api_hash"],
        in_memory=True
    )
    
    try:
        await client.connect()
        sent_code = await client.send_code(phone)
        
        # Store client and code hash for the next step
        active_clients[message.from_user.id] = client
        await state.update_data(phone=phone, phone_code_hash=sent_code.phone_code_hash)
        
        await state.set_state(SessionGen.otp)
        await msg.edit_text(
            "✅ <b>OTP Sent!</b>\n\n"
            "Check your Telegram app for the login code.\n\n"
            "⚠️ <b>CRITICAL:</b> Telegram deletes messages containing codes to prevent phishing.\n"
            "You <b>MUST</b> send the code with spaces between the numbers.\n"
            "Example: If your code is <code>12345</code>, send it as <code>1 2 3 4 5</code>"
        )
        
    except ApiIdInvalid:
        await msg.edit_text("❌ The API ID or API Hash is invalid. /generate to restart.")
        await client.disconnect()
        await state.clear()
    except Exception as e:
        await msg.edit_text(f"❌ Error requesting code: <code>{str(e)}</code>\n/generate to restart.")
        await client.disconnect()
        await state.clear()


@router.message(SessionGen.otp)
async def process_otp(message: Message, state: FSMContext):
    # Remove spaces or dashes the user added to bypass Telegram's filter
    otp = re.sub(r"[^0-9]", "", message.text)
    
    if len(otp) != 5:
        await message.answer("❌ Code must be exactly 5 digits (e.g., 1 2 3 4 5). Try again:")
        return

    data = await state.get_data()
    client = active_clients.get(message.from_user.id)
    
    if not client or not client.is_connected:
        await message.answer("❌ Connection lost. Please type /generate to start over.")
        await state.clear()
        return

    msg = await message.answer("⏳ Verifying code...")

    try:
        await client.sign_in(
            phone_number=data["phone"],
            phone_code_hash=data["phone_code_hash"],
            phone_code=otp
        )
        
        # If we reach here, sign in was successful without 2FA!
        session_string = await client.export_session_string()
        await cleanup_client(message.from_user.id)
        await state.clear()
        
        await msg.edit_text(
            "🎉 <b>Authentication Successful!</b>\n\n"
            "Here is your session string. <b>Keep it secure!</b>\n\n"
            f"<code>{session_string}</code>"
        )
        
    except SessionPasswordNeeded:
        # User has 2FA enabled
        await state.set_state(SessionGen.password)
        await msg.edit_text("🔐 This account has Two-Step Verification enabled.\n\nPlease send your password:")
        
    except PhoneCodeInvalid:
        await msg.edit_text("❌ The code you entered is incorrect. Please try typing it again (with spaces):")
        
    except PhoneCodeExpired:
        await msg.edit_text("❌ The code has expired. Type /generate to start over.")
        await cleanup_client(message.from_user.id)
        await state.clear()
        
    except Exception as e:
        await msg.edit_text(f"❌ Error during sign in: <code>{str(e)}</code>\n/generate to restart.")
        await cleanup_client(message.from_user.id)
        await state.clear()


@router.message(SessionGen.password)
async def process_password(message: Message, state: FSMContext):
    client = active_clients.get(message.from_user.id)
    password = message.text.strip()
    
    if not client or not client.is_connected:
        await message.answer("❌ Connection lost. Please type /generate to start over.")
        await state.clear()
        return

    msg = await message.answer("⏳ Verifying password...")

    try:
        await client.check_password(password)
        session_string = await client.export_session_string()
        
        await cleanup_client(message.from_user.id)
        await state.clear()
        
        # Delete the user's message containing the password for security
        try:
            await message.delete()
        except:
            pass
            
        await msg.edit_text(
            "🎉 <b>Authentication Successful!</b>\n\n"
            "Here is your session string. <b>Keep it secure!</b>\n\n"
            f"<code>{session_string}</code>"
        )
        
    except Exception as e:
        await msg.edit_text("❌ Incorrect password. Please try again or type /cancel.")


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    
    log.info("Session Generator Bot started.")
    try:
        await dp.start_polling(bot)
    finally:
        # Cleanup any lingering connections on shutdown
        for uid in list(active_clients.keys()):
            await cleanup_client(uid)

if __name__ == "__main__":
    asyncio.run(main())