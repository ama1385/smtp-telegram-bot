import re
import smtplib
import dns.resolver
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart

# ==============================
# BOT TOKEN
# استخدم متغير بيئة في Render
# ضع اسم المتغير BOT_TOKEN
# ==============================
API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ==============================
# التحقق من صيغة الإيميل
# ==============================
def is_valid_format(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

# ==============================
# استعلام DNS MX
# ==============================
def get_mx(domain):
    try:
        answers = dns.resolver.resolve(domain, "MX")
        return str(answers[0].exchange)
    except:
        return None

# ==============================
# SMTP CHECK
# ==============================
def smtp_check(email):
    if not is_valid_format(email):
        return "❌ صيغة الإيميل غير صحيحة."

    domain = email.split("@")[1]
    mx = get_mx(domain)

    if not mx:
        return "❌ الدومين لا يستقبل بريد (لا يوجد MX)."

    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(mx)
        server.helo("example.com")
        server.mail("test@example.com")
        code, _ = server.rcpt(email)
        server.quit()

        if code in [250, 251]:
            return f"✅ الإيميل موجود (SMTP:{code})"
        return f"❌ الإيميل غير موجود (SMTP:{code})"

    except Exception as e:
        return f"⚠️ خطأ أثناء الاتصال: {e}"

# ==============================
# الأوامر ♦
# ==============================
@dp.message(CommandStart())
async def start(message: Message):
    await message.reply("👋 أرسل الإيميل الآن لفحصه عبر SMTP")

@dp.message()
async def handle_email(message: Message):
    email = message.text.strip()
    result = smtp_check(email)
    await message.reply(f"📧 <b>{email}</b>\n\n{result}")

# ==============================
# تشغيل البوت + Fake Web Server لـ Render
# ==============================
async def run_bot():
    print("🚀 Bot is Running...")
    await dp.start_polling(bot)

# Fake web server لخداع Render
import threading
import http.server
import socketserver

def fake_web():
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 10000), Handler) as httpd:
        print("🌍 Fake web server running on port 10000")
        httpd.serve_forever()

threading.Thread(target=fake_web).start()

if __name__ == "__main__":
    asyncio.run(run_bot())
