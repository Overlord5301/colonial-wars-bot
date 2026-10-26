import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# ВСТАВЬТЕ СЮДА ВАШ ТОКЕН ИЗ BOTFATHER ВНУТРЬ КАВЫЧЕК
TOKEN = "8810434439:AAEKstgiobq57G7dioP5Z6CgNG9__Nk8_K4"

bot = telebot.TeleBot(TOKEN)

players = {}

def get_player(user_id, username):
    if user_id not in players:
        players[user_id] = {
            "name": username or "Капитан",
            "gold": 100,
            "ships": 1,
            "soldiers": 10,
            "cannons": 2,
            "islands": 0
        }
    return players[user_id]

def get_main_menu_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⛵ В гавань", callback_data="harbor"),
        InlineKeyboardButton("🏝️ Искать остров", callback_data="find_island")
    )
    return markup

@bot.message_handler(commands=['start'])
def cmd_start(message):
    p = get_player(message.from_user.id, message.from_user.username)
    text = (
        f"🏴‍☠️ **Приветствуем, Капитан {p['name']}!** 🏴‍☠️\n\n"
        f"Вы прибыли в Новый Свет. Ваша цель — колонизировать острова!\n\n"
        f"💰 Золото: {p['gold']}\n"
        f"⛵ Корабли: {p['ships']}\n"
        f"⚔️ Солдаты: {p['soldiers']}\n"
        f"💣 Пушки (Артиллерия): {p['cannons']}\n"
        f"🏝️ Захвачено островов: {p['islands']}"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    p = get_player(call.from_user.id, call.from_user.username)
    
    if call.data == "main_menu":
        text = (
            f"💰 Золото: {p['gold']}\n"
            f"⛵ Корабли: {p['ships']}\n"
            f"⚔️ Солдаты: {p['soldiers']}\n"
            f"💣 Пушки: {p['cannons']}\n"
            f"🏝️ Острова: {p['islands']}"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=get_main_menu_keyboard())
        
    elif call.data == "harbor":
        text = f"⛵ **Вы в гавани.** Здесь можно усилить армию.\n💰 Золото: {p['gold']}"
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Купить солдата (10💰)", callback_data="buy_soldier"),
            InlineKeyboardButton("Купить пушку (30💰)", callback_data="buy_cannon"),
            InlineKeyboardButton("Назад", callback_data="main_menu")
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "buy_soldier":
        if p['gold'] >= 10:
            p['gold'] -= 10
            p['soldiers'] += 1
            bot.answer_callback_query(call.id, "Вы наняли 1 солдата! ⚔️")
        else:
            bot.answer_callback_query(call.id, "Недостаточно золота! ❌")
        text = f"⛵ **Вы в гавани.** Здесь можно усилить армию.\n💰 Золото: {p['gold']}"
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Купить солдата (10💰)", callback_data="buy_soldier"),
            InlineKeyboardButton("Купить пушку (30💰)", callback_data="buy_cannon"),
            InlineKeyboardButton("Назад", callback_data="main_menu")
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "buy_cannon":
        if p['gold'] >= 30:
            p['gold'] -= 30
            p['cannons'] += 1
            bot.answer_callback_query(call.id, "Отлита новая пушка! 💣")
        else:
            bot.answer_callback_query(call.id, "Недостаточно золота! ❌")
        text = f"⛵ **Вы в гавани.** Здесь можно усилить армию.\n💰 Золото: {p['gold']}"
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Купить солдата (10💰)", callback_data="buy_soldier"),
            InlineKeyboardButton("Купить пушку (30💰)", callback_data="buy_cannon"),
            InlineKeyboardButton("Назад", callback_data="main_menu")
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "find_island":
        text = "🏝️ **Обнаружен неизведанный остров!**\nЗащита форта: 15 силы.\n\nОтправить флот на штурм?"
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("⚔️ Атаковать!", callback_data="attack_island"),
            InlineKeyboardButton("🏳️ Отступить", callback_data="main_menu")
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif call.data == "attack_island":
        army_power = (p['cannons'] * 5) + p['soldiers']
        enemy_power = 15
        
        if army_power >= enemy_power:
            p['islands'] += 1
            p['gold'] += 50
            if p['soldiers'] > 2: p['soldiers'] -= 2
            text = "🎉 **Победа!**\nВаша артиллерия разбила стены форта, а пехота захватила остров!\n\n💰 Награда: +50 золота."
        else:
            if p['soldiers'] > 4: p['soldiers'] -= 4
            text = "💥 **Поражение!**\nЗащитники форта потопили лодки десанта. Вы отступили с потерями."
            
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("В главное меню", callback_data="main_menu"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

class TinyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), TinyServer)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    print("Бот успешно запущен и готов к колонизации!")
    bot.infinity_polling()
