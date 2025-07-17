# -- coding: utf-8 --
import telebot
from telebot import types

API_TOKEN = '7970630915:AAGqux51ZMO6mxQEavG9svrMTG2CqgWLTSw'
ADMIN_ID = 6736058580
MAIN_CHANNEL = "@cod_NR"

bot = telebot.TeleBot(API_TOKEN)
user_states = {}
pending_vasete = {}
discount_users = set()
gold_users = set()
order_history = {}

def is_user_member(user_id):
    try:
        status = bot.get_chat_member(MAIN_CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

def main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛒 سفارش سی پی", "📦 ثبت نام در کلن")
    markup.row("💰 کد تخفیف", "🛡 واسطه‌گری")
    markup.row("☕ همکاری", "💸 دونیت", "🌐 DNS")
    markup.row("🎥 رکوردر بدون لگ", "🎁 دریافت سی پی رایگان")
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "باسلام 👋\nمن ربات هوشمند NR هستم...", reply_markup=main_menu_markup())

# سفارش سی پی
@bot.message_handler(func=lambda m: m.text == "🛒 سفارش سی پی")
def order_cp(message):
    if not is_user_member(message.chat.id):
        bot.send_message(message.chat.id,
            "❗️ لطفاً ابتدا در کانال‌های زیر عضو شوید:\n\n"
            "📢 تلگرام: @cod_NR\n"
            "📺 یوتیوب: https://www.youtube.com/@cod_NR_callofduty\n"
            "📸 اینستاگرام: https://www.instagram.com/c0d_nr?igsh")
        return

    markup = types.InlineKeyboardMarkup()
    cp_options = [
        ("80cp", 70), ("160cp", 140), ("240cp", 210), ("320cp", 280),
        ("420cp", 475), ("500cp", 535), ("580cp", 620), ("660cp", 700),
        ("740cp", 770), ("880cp", 855), ("960cp", 875), ("1040cp", 953)
    ]
    for cp, price in cp_options:
        if message.from_user.id in discount_users:
            price = max(0, price - 30)
        btn_text = f"{cp}={price}هزار تومان"
        markup.add(types.InlineKeyboardButton(text=btn_text, callback_data=f"cp_{cp.replace('cp','')}:{price}"))
    markup.add(types.InlineKeyboardButton("کد تخفیف 💰", callback_data="cp_discount_code"))
    bot.send_message(message.chat.id, "یکی از پکیج‌های زیر را انتخاب کنید:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cp_"))
def handle_cp_selection(call):
    data = call.data.replace("cp_", "")
    if data == "discount_code":
        user_states[call.message.chat.id] = "awaiting_discount"
        bot.send_message(call.message.chat.id, "لطفاً کد تخفیف مورد نظر خود را وارد کنید:")
    else:
        cp, price = data.split(":")
        user_states[f"{call.message.chat.id}_cp_amount"] = cp
        user_states[f"{call.message.chat.id}_cp_price"] = price
        bot.send_message(call.message.chat.id,
            "لطفاً اطلاعات مورد نیاز برای سفارش را ارسال کنید.\n"
            "شماره کارت جهت واریز: 6219861940763880 (خالصی)")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "awaiting_discount")
def handle_discount_code(message):
    code = message.text.strip()
    user_states.pop(message.chat.id, None)
    if code == "amirsabrikmx00NR":
        gold_users.add(message.from_user.id)
        bot.send_message(message.chat.id, "✅ شما در اکانت‌های طلایی قرار گرفتید.")
    elif code.lower() == "nr is great":
        discount_users.add(message.from_user.id)
        bot.send_message(message.chat.id, "✅ کد تخفیف ۳۰ هزارتومانی فعال شد.")
        order_cp(message)
    else:
        bot.send_message(message.chat.id, "کد در حال بررسی است ✅")
        bot.send_message(ADMIN_ID, f"کد تخفیف جدید:\n{code}\nاز طرف: @{message.from_user.username or 'ندارد'}")

@bot.message_handler(func=lambda m: user_states.get(f"{m.chat.id}_cp_amount"))
def receive_cp_order(message):
    cp = user_states.pop(f"{message.chat.id}_cp_amount", "نامشخص")
    price_raw = user_states.pop(f"{message.chat.id}_cp_price", "0").replace("هزار تومان", "").strip()
    try:
        price = int(price_raw)
    except:
        price = 0
    if message.from_user.id in discount_users:
        price = max(0, price - 30)
    price_text = f"{price} هزار تومان (با تخفیف)" if message.from_user.id in discount_users else f"{price} هزار تومان"
    bot.send_message(message.chat.id, f"✅ سفارش شما ثبت شد.\nقیمت نهایی: {price_text}", reply_markup=main_menu_markup())
    report = (
        f"🛒 سفارش جدید:\nمقدار: {cp}\nقیمت: {price_text}\n"
        f"{message.text}\nID: {message.from_user.id}"
        f"{' (طلایی)' if message.from_user.id in gold_users else ''}\n"
        f"یوزرنیم: @{message.from_user.username or 'ندارد'}"
    )
    bot.send_message(ADMIN_ID, report)
    order_history.setdefault(message.from_user.id, []).append(report)

@bot.message_handler(func=lambda m: m.text == "📦 ثبت نام در کلن")
def handle_register_clan(message):
    bot.send_message(message.chat.id,
        "باسلام 👋\nبرای ثبت نام در یکی از بهترین کلن‌های ایران، به آیدی زیر پیام دهید و علت پیام را توضیح دهید:\n\n@cod_amir_NR")

@bot.message_handler(func=lambda m: m.text == "☕ همکاری")
def handle_collaboration(message):
    user_states[message.chat.id] = "awaiting_collab_info"
    bot.send_message(message.chat.id,
        "لطفاً اطلاعات زیر را وارد کنید:\n"
        "نام، سن، تخصص شما (مثل تبلیغات، طراحی، پاسخ‌گویی...) و آیدی تلگرام")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "awaiting_collab_info")
def receive_collab_info(message):
    user_states.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "✅ اطلاعات شما با موفقیت دریافت شد.")
    bot.send_message(ADMIN_ID,
        f"📩 همکاری جدید:\n{message.text}\n"
        f"از @{message.from_user.username or 'ندارد'} | ID: {message.from_user.id}")

@bot.message_handler(func=lambda m: m.text == "💸 دونیت")
def handle_donate(message):
    bot.send_message(message.chat.id,
        "💸 شماره کارت جهت دونیت:\n`6219 8619 4076 3880`\nبه نام خالصی بنهنگی", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🌐 DNS")
def handle_dns(message):
    bot.send_message(message.chat.id,
        "🌐 برای بهبود پینگ از اپ زیر استفاده کنید:\n"
        "https://play.google.com/store/apps/details?id=com.appplanex.dnschanger")

@bot.message_handler(func=lambda m: m.text == "🎥 رکوردر بدون لگ")
def handle_recorder(message):
    bot.send_message(message.chat.id,
        "🎥 دانلود رکوردر بدون لگ:\nhttps://play.google.com/store/apps/details?id=com.hecorat.screenrecorder.free")

@bot.message_handler(func=lambda m: m.text == "🎁 دریافت سی پی رایگان")
def handle_free_cp(message):
    if not is_user_member(message.chat.id):
        bot.send_message(message.chat.id,
            "❗️ لطفاً ابتدا در کانال‌های زیر عضو شوید:\n\n"
            "📢 تلگرام: @cod_NR\n"
            "📺 یوتیوب: https://www.youtube.com/@cod_NR_callofduty\n"
            "📸 اینستاگرام: https://www.instagram.com/c0d_nr?igsh")
        return

    bot.send_message(message.chat.id,
        "🎁 برای دریافت سی پی رایگان وارد لینک زیر شوید و ۲ نفر با دعوت شما ثبت‌نام کنند:\n"
        "https://milli.gold/app/home\n\n"
        "کد دعوت: `milli-sfr2d`\n\n"
        "سپس اسکرین‌شات ثبت‌نام را برای مدیر ربات ارسال کنید.",
        parse_mode="Markdown")

bot.infinity_polling()
