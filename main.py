import re
import smtplib
import dns.resolver
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message

# 🔹 ضع التوكن هنا أو ضعه في متغير بيئة BOT_TOKEN في Render
API_TOKEN = os.getenv("BOT_TOKEN", "8525848016:AAF8yTVahsO2wjO-Lj84Zx5i0d_yrMQHG54")

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# التحقق من صيغة الايميل
def is_valid_format(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

# MX record
def get_mx(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return str(answers[0].exchange)
    except:
        return None

# SMTP Check
def smtp_check(email):
    if not is_valid_format(email):
        return "❌ صيغة الإيميل غير صحيحة."

    domain = email.split('@')[1]
    mx = get_mx(domain)
    if not mx:
        return "❌ الدومين لا يستقبل بريد (لا يوجد MX)."

    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(mx)
        server.helo("example.com")
        server.mail("check@example.com")
        code, _ = server.rcpt(email)
        server.quit()

        if code in [250, 251]:
            return f"✅ الإيميل موجود فعليًا (SMTP: {code})"
        else:
            return f"❌ الإيميل غير موجود أو مرفوض (SMTP: {code})"
    except Exception as e:
        return f"🚫 خطأ أثناء الاتصال: {e}"

# استقبال الرسائل
@dp.message()
async def handle_message(message: Message):
    email = message.text.strip()
    result = smtp_check(email)
    await message.reply(f"📧 <b>{email}</b>\n\n{result}")

# تشغيل البوت (بديل executor)
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
