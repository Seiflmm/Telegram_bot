import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from googletrans import Translator, LANGUAGES
import random
import time

TOKEN = '7794687491:AAEiYCZXIabvrmCfwe0a1f6sH6n85HV1OSQ'
bot = telebot.TeleBot(TOKEN, threaded=False, parse_mode='HTML')
translator = Translator()

user_states = {}

# Dictionary mapping language codes to flag emojis
LANGUAGE_FLAGS = {
    'en': '🇬🇧', 'es': '🇪🇸', 'fr': '🇫🇷', 'de': '🇩🇪', 'it': '🇮🇹', 'pt': '🇵🇹',
    'ru': '🇷🇺', 'ja': '🇯🇵', 'ko': '🇰🇷', 'zh-cn': '🇨🇳', 'ar': '🇸🇦', 'hi': '🇮🇳',
    'bn': '🇧🇩', 'id': '🇮🇩', 'tr': '🇹🇷', 'th': '🇹🇭', 'vi': '🇻🇳', 'nl': '🇳🇱',
    'pl': '🇵🇱', 'sv': '🇸🇪', 'fi': '🇫🇮', 'no': '🇳🇴', 'da': '🇩🇰', 'cs': '🇨🇿',
    'el': '🇬🇷', 'he': '🏁', 'fa': '🇮🇷'
}

def get_flag(lang_code):
    return LANGUAGE_FLAGS.get(lang_code, '🏁')

def create_language_keyboard(page=0, items_per_page=8):
    keyboard = InlineKeyboardMarkup(row_width=2)
    sorted_languages = sorted(LANGUAGES.items(), key=lambda x: x[1])
    start = page * items_per_page
    end = start + items_per_page
    current_page_languages = sorted_languages[start:end]
    
    for code, name in current_page_languages:
        flag = get_flag(code)
        keyboard.add(InlineKeyboardButton(f"{flag} {name.capitalize()}", callback_data=f"lang_{code}"))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{page-1}"))
    if end < len(sorted_languages):
        nav_buttons.append(InlineKeyboardButton("المزيد من اللغات   ➡️", callback_data=f"page_{page+1}"))
    
    keyboard.row(*nav_buttons)
    return keyboard

def create_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton("🔄 بدء ترجمة جديدة"))
    keyboard.add(KeyboardButton("🎲 ترجمة عشوائية"), KeyboardButton("📊 إحصائيات"))
    keyboard.add(KeyboardButton("ℹ️ المساعدة"))
    return keyboard
# Part 2: Updated message handlers and callback functions

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        user_states[message.from_user.id] = {'translations': 0}
        welcome_text = (
            "مرحبًا بك في بوت الترجمة المطور! 🌍✨\n\n"
            "لبدء الترجمة، انقر على '🔄 بدء ترجمة جديدة'.\n"
            "لتجربة ترجمة عشوائية، جرب '🎲 ترجمة عشوائية'.\n"
            "لمعرفة إحصائيات استخدامك، اختر '📊 إحصائيات'.\n"
            "للمساعدة، انقر على 'ℹ️ المساعدة'.\n\n"
            "هيا بنا نبدأ رحلة الترجمة! 🚀"
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=create_main_menu())
    except Exception as e:
        print(f"Error in send_welcome: {e}")
        restart_bot()

@bot.message_handler(func=lambda message: message.text == "ℹ️ المساعدة")
def show_help(message):
    try:
        help_text = (
            "ℹ️ *المساعدة:*\n\n"
            "هذا البوت يتيح لك ترجمة النصوص بين العديد من اللغات المختلفة. "
            "يمكنك البدء بترجمة جديدة باستخدام خيار '🔄 بدء ترجمة جديدة'.\n\n"
            "إذا أردت تجربة الترجمة العشوائية، اختر '🎲 ترجمة عشوائية' وسنقوم باختيار لغات عشوائية لك.\n\n"
            "لعرض إحصائيات استخدامك وعدد الترجمات التي قمت بها، اختر '📊 إحصائيات'.\n\n"
            "بعد كل ترجمة، ستجد زر 'نسخ النص المترجم' لنسخ الترجمة بسهولة.\n\n"
            "إذا واجهت أي مشكلة، لا تتردد في الاتصال بنا عبر حسابنا على تلغرام الموجود في وصف البوت."
        )
        bot.send_message(message.chat.id, help_text, parse_mode='Markdown')
    except Exception as e:
        print(f"Error in show_help: {e}")
        restart_bot()

@bot.message_handler(func=lambda message: message.text == "📊 إحصائيات")
def show_statistics(message):
    try:
        user_id = message.from_user.id
        translations = user_states.get(user_id, {}).get('translations', 0)
        stats_text = (
            f"📊 إحصائيات استخدامك:\n\n"
            f"🔢 عدد الترجمات: {translations}\n"
            f"🏆 المستوى: {get_user_level(translations)}\n\n"
            f"واصل الترجمة لتحسين مستواك! 💪"
        )
        bot.send_message(message.chat.id, stats_text)
    except Exception as e:
        print(f"Error in show_statistics: {e}")
        restart_bot()

@bot.message_handler(func=lambda message: message.text == "🔄 بدء ترجمة جديدة")
def start_new_translation(message):
    try:
        user_states[message.from_user.id] = user_states.get(message.from_user.id, {})
        user_states[message.from_user.id]['step'] = 'select_source_lang'
        bot.send_message(
            message.chat.id,
            "حسنًا، لنبدأ بترجمة جديدة! 👍\n\nأولاً، اختر اللغة التي ستكتب بها النص (لغة المصدر):",
            reply_markup=create_language_keyboard()
        )
    except Exception as e:
        print(f"Error in start_new_translation: {e}")
        restart_bot()

@bot.message_handler(func=lambda message: message.text == "🎲 ترجمة عشوائية")
def random_translation(message):
    try:
        user_id = message.from_user.id
        user_states[user_id] = user_states.get(user_id, {})
        user_states[user_id]['source_lang'] = random.choice(list(LANGUAGES.keys()))
        user_states[user_id]['target_lang'] = random.choice(list(LANGUAGES.keys()))
        user_states[user_id]['step'] = 'wait_for_text'
        
        source_flag = get_flag(user_states[user_id]['source_lang'])
        target_flag = get_flag(user_states[user_id]['target_lang'])
        bot.send_message(
            message.chat.id,
            f"تم اختيار لغات عشوائية لك:\n"
            f"📤 من: {source_flag} {LANGUAGES[user_states[user_id]['source_lang']].capitalize()}\n"
            f"📥 إلى: {target_flag} {LANGUAGES[user_states[user_id]['target_lang']].capitalize()}\n\n"
            f"الآن، أرسل لي النص الذي تريد ترجمته!"
        )
    except Exception as e:
        print(f"Error in random_translation: {e}")
        restart_bot()

@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def callback_page(call):
    try:
        page = int(call.data.split('_')[1])
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_language_keyboard(page))
    except Exception as e:
        print(f"Error in callback_page: {e}")
        restart_bot()

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def callback_language(call):
    try:
        lang_code = call.data.split('_')[1]
        user_id = call.from_user.id
        
        if user_states[user_id]['step'] == 'select_source_lang':
            user_states[user_id]['source_lang'] = lang_code
            flag = get_flag(lang_code)
            bot.answer_callback_query(call.id, f"تم اختيار {flag} {LANGUAGES[lang_code].capitalize()} كلغة المصدر")
            bot.edit_message_text(
                f"ممتاز! لقد اخترت {flag} {LANGUAGES[lang_code].capitalize()} كلغة المصدر. 👍\n\n"
                "الآن، اختر اللغة التي تريد الترجمة إليها (لغة الهدف):",
                call.message.chat.id, call.message.message_id, reply_markup=create_language_keyboard()
            )
            user_states[user_id]['step'] = 'select_target_lang'
        elif user_states[user_id]['step'] == 'select_target_lang':
            user_states[user_id]['target_lang'] = lang_code
            source_lang = user_states[user_id]['source_lang']
            source_flag = get_flag(source_lang)
            target_flag = get_flag(lang_code)
            bot.answer_callback_query(call.id, f"تم اختيار {target_flag} {LANGUAGES[lang_code].capitalize()} كلغة الهدف")
            bot.edit_message_text(
                f"رائع! لقد أكملت إعداد الترجمة:\n\n"
                f"📤 من: {source_flag} {LANGUAGES[source_lang].capitalize()}\n"
                f"📥 إلى: {target_flag} {LANGUAGES[lang_code].capitalize()}\n\n"
                f"الآن، أرسل لي النص الذي تريد ترجمته من {LANGUAGES[source_lang].capitalize()} "
                f"إلى {LANGUAGES[lang_code].capitalize()}.",
                call.message.chat.id, call.message.message_id
            )
            user_states[user_id]['step'] = 'wait_for_text'
    except Exception as e:
        print(f"Error in callback_language: {e}")
        restart_bot()

# Part 3: Updated translation function with copy button

@bot.message_handler(func=lambda message: True)
def translate_text(message):
    user_id = message.from_user.id
    if user_id not in user_states or user_states[user_id].get('step') != 'wait_for_text':
        bot.reply_to(message, "عذرًا، يبدو أنك لم تقم بإعداد الترجمة بعد. الرجاء النقر على '🔄 بدء ترجمة جديدة' للبدء.")
        return

    source_lang = user_states[user_id]['source_lang']
    target_lang = user_states[user_id]['target_lang']
    text_to_translate = message.text

    try:
        translated = translator.translate(text_to_translate, src=source_lang, dest=target_lang)
        user_states[user_id]['translations'] = user_states[user_id].get('translations', 0) + 1
        source_flag = get_flag(source_lang)
        target_flag = get_flag(target_lang)
        
        response = (
            f"🔤 النص الأصلي ({source_flag} {LANGUAGES[source_lang].capitalize()}):\n{text_to_translate}\n\n"
            f"🔡 الترجمة ({target_flag} {LANGUAGES[target_lang].capitalize()}):\n{translated.text}\n\n"
            f"✅ تمت الترجمة بنجاح! عدد ترجماتك الآن: {user_states[user_id]['translations']}\n\n"
            f"هل تريد ترجمة نص آخر بنفس إعدادات اللغة؟ ما عليك سوى إرساله مباشرة!\n"
            f"أو يمكنك النقر على '🔄 بدء ترجمة جديدة' لتغيير اللغات."
        )
        
        # Create inline keyboard with copy button
        copy_keyboard = InlineKeyboardMarkup()
        copy_keyboard.add(InlineKeyboardButton("نسخ النص المترجم", callback_data=f"copy_{message.message_id}"))
        
        # Store the translated text in user_states for later copying
        user_states[user_id]['last_translation'] = translated.text
        
        bot.reply_to(message, response, reply_markup=copy_keyboard)
    except Exception as e:
        print(f"Error in translate_text: {e}")
        restart_bot()

@bot.callback_query_handler(func=lambda call: call.data.startswith('copy_'))
def copy_translation(call):
    try:
        user_id = call.from_user.id
        translated_text = user_states[user_id]['last_translation']
        
        # Update the button text
        copy_keyboard = InlineKeyboardMarkup()
        copy_keyboard.add(InlineKeyboardButton("✅ تم نسخ النص بنجاح", callback_data="dummy"))
        
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=copy_keyboard
        )
        
        # Send the copied text as a separate message
        bot.answer_callback_query(call.id, "تم نسخ النص المترجم!")
        bot.send_message(call.message.chat.id, f"\n\n{translated_text}")
    except Exception as e:
        print(f"Error in copy_translation: {e}")
        restart_bot()

# Part 4: Utility functions and main loop

def get_user_level(translations):
    if translations == 0:
        return "مبتدئ"
    elif translations < 10:
        return "متوسط"
    elif translations < 50:
        return "متقدم"
    else:
        return "خبير"

def restart_bot():
    time.sleep(5)
    print("إعادة تشغيل البوت...")
    try:
        bot.polling()
    except Exception as e:
        print(f"Error in restart_bot: {e}")
        restart_bot()

# Main loop
if __name__ == "__main__":
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"Main polling error: {e}")
            restart_bot() 
