import os
from flask import Flask, request
import telebot
import google.generativeai as genai

# 🔐 این بار کلیدها را مستقیم در کد نمی‌نویسیم؛ سرور رندر خودش این‌ها را پنهانی می‌خواند
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
RENDER_WEBHOOK_URL = os.environ.get('RENDER_WEBHOOK_URL') 

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

app = Flask(__name__)

SYSTEM_PROMPT = """
اسم تو «آنتونی» است. تو دستیار شخصی، باوفا و دست‌راست «ممد» هستی.
لحنت باید کاملاً رفیقانه، صمیمی، لوتی، مشتی و باحال باشه.
همیشه یادت باشه رئیس تو ممده. اگر کسی ازت درباره خودت یا ممد پرسید، با تعصب جواب بده.
جواب‌ها رو کوتاه و جذاب نگه دار.
"""

@app.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_WEBHOOK_URL + '/' + TELEGRAM_BOT_TOKEN)
    return "آنتونی بیدار و آماده است!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ارادت رفیق! من آنتونی هستم، دستیار ممد. امرت رو بگو! 😉")

@bot.message_handler(func=lambda message: True)
def chat_with_antoni(message):
    user_text = message.text.lower()
    bot.send_chat_action(message.chat.id, 'typing')
    
    identity_keywords = ["تو کی هستی", "اسمت چیه", "خودتو معرفی کن", "کی هستی", "اسم تو چیه"]
    if any(keyword in user_text for keyword in identity_keywords):
        bot.reply_to(message, "من آنتونی، دستیار ممد هستم! مخلص شما. 😉")
        return

    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nکاربر گفت: {message.text}\nپاسخ در نقش آنتونی:"
        response = model.generate_content(full_prompt)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "مغزم یه لحظه رگ به رگ شد داداش! 😅")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
