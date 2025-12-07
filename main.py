import re
import smtplib
import dns.resolver
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
import os

# ✅ استبدل هذا بتوكن بوتك
API_TOKEN = os.getenv("BOT_TOKEN", "8525848016:AAF8yTVahsO2wjO-Lj84Zx5i0d_yrMQHG54")

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ✅ التحقق من صيغة الإيميل
def is_valid_format(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

# ✅ جلب MX record
def get_mx(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return str(answers[0].exchange)
    except:
        return None

# ✅ فحص SMTP مباشر
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

# ✅ أمر /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 أرسل لي أي إيميل، وسأتحقق هل هو موجود فعليًا أم لا عن طريق SMTP.")

# ✅ كل رسالة نصية تعتبر إيميل
@dp.message(F.text)
async def handle_email(message: Message):
    email = message.text.strip()
    result = smtp_check(email)
    await message.answer(f"📧 <b>{email}</b>\n\n{result}")

# ✅ تشغيل البوت
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
