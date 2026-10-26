import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ВСТАВЬТЕ СЮДА ВАШ ТОКЕН МЕЖДУ КАВЫЧКАМИ
TOKEN = "8810434439:AAEKstgiobq57G7dioP5Z6CgNG9__Nk8_K4"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Простая база данных игроков в памяти (сбросится при перезапуске сервера)
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

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
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
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="⛵ В гавань", callback_url="dummy", callback_data="harbor"))
    builder.add(types.InlineKeyboardButton(text="🏝️ Искать остров", callback_url="dummy", callback_data="find_island"))
    builder.adjust(2)
    
    await message.answer(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "harbor")
async def go_harbor(callback: types.CallbackQuery):
    p = get_player(callback.from_user.id, callback.from_user.username)
    text = f"⛵ **Вы в гавани.** Здесь можно усилить армию.\n💰 Золото: {p['gold']}"
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Купить солдата (10💰)", callback_url="dummy", callback_data="buy_soldier"))
    builder.add(types.InlineKeyboardButton(text="Купить пушку (30💰)", callback_url="dummy", callback_data="buy_cannon"))
    builder.add(types.InlineKeyboardButton(text="Назад", callback_url="dummy", callback_data="main_menu"))
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "buy_soldier")
async def buy_soldier(callback: types.CallbackQuery):
    p = get_player(callback.from_user.id, callback.from_user.username)
    if p['gold'] >= 10:
        p['gold'] -= 10
        p['soldiers'] += 1
        await callback.answer("Вы наняли 1 солдата! ⚔️")
    else:
        await callback.answer("Недостаточно золота! ❌")
    await go_harbor(callback)

@dp.callback_query(F.data == "buy_cannon")
async def buy_cannon(callback: types.CallbackQuery):
    p = get_player(callback.from_user.id, callback.from_user.username)
    if p['gold'] >= 30:
        p['gold'] -= 30
        p['cannons'] += 1
        await callback.answer("Отлита новая пушка! 💣")
    else:
        await callback.answer("Недостаточно золота! ❌")
    await go_harbor(callback)

@dp.callback_query(F.data == "main_menu")
async def go_main(callback: types.CallbackQuery):
    p = get_player(callback.from_user.id, callback.from_user.username)
    text = (
        f"💰 Золото: {p['gold']}\n"
        f"⛵ Корабли: {p['ships']}\n"
        f"⚔️ Солдаты: {p['soldiers']}\n"
        f"💣 Пушки: {p['cannons']}\n"
        f"🏝️ Острова: {p['islands']}"
    )
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="⛵ В гавань", callback_url="dummy", callback_data="harbor"))
    builder.add(types.InlineKeyboardButton(text="🏝️ Искать остров", callback_url="dummy", callback_data="find_island"))
    builder.adjust(2)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "find_island")
async def find_island(callback: types.CallbackQuery):
    p = get_player(callback.from_user.id, callback.from_user.username)
    if p['ships'] < 1:
        await callback.answer("У вас нет кораблей для экспедиции! ❌")
        return
        
    text = "🏝️ **Обнаружен неизведанный остров!**\nЗащита форта: 15 силы.\n\nОтправить флот на штурм?"
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="⚔️ Атаковать!", callback_url="dummy", callback_data="attack_island"))
    builder.add(types.InlineKeyboardButton(text="🏳️ Отступить", callback_url="dummy", callback_data="main_menu"))
    builder.adjust(1)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "attack_island")
async def attack_island(callback: types.CallbackQuery):
    p = get_player(callback.from_user.id, callback.from_user.username)
    
    # Очень простая формула боя: пушка дает 5 силы, солдат 1 силу
    army_power = (p['cannons'] * 5) + p['soldiers']
    enemy_power = 15
    
    if army_power >= enemy_power:
        p['islands'] += 1
        p['gold'] += 50
        # Небольшие потери при штурме
        if p['soldiers'] > 2: p['soldiers'] -= 2
        text = "🎉 **Победа!**\nВаша артиллерия разбила стены форта, а пехота захватила остров!\n\n💰 Награда: +50 золота."
    else:
        if p['soldiers'] > 4: p['soldiers'] -= 4
        text = "💥 **Поражение!**\nЗащитники форта потопили лодки десанта. Вы отступили с потерями."
        
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="В главное меню", callback_url="dummy", callback_data="main_menu"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

import asyncio
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

async def on_startup(bot: Bot):
    asyncio.create_task(dp.start_polling(bot))

def main():
    app = web.Application()
    app.on_startup.append(lambda a: on_startup(bot))
    web.run_app(app, host="0.0.0.0", port=10000)

if __name__ == "__main__":
    main()

