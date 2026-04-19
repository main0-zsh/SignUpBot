import aiogram
import json
from aiogram import Bot, Dispatcher, types
import asyncio
import dotenv
import os
import sqlalchemy
from aiogram.enums import ParseMode
import groq
from database import engine, SessionLocal, Base
from models import User
from requests import add_user, delete_user
from aiogram.filters import Command

dotenv.load_dotenv()
BOT_TOKEN = os.getenv("bot_token")
AI_KEY = os.getenv("ai_key")

Base.metadata.create_all(bind=engine)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def json_load():
    try:
        with open('user.json', 'r') as f:
            users = json.load(f)
        return users
    except FileNotFoundError:
        return {}

def json_save(users):
    with open('user.json', 'w') as f:
        json.dump(users, f, indent=4)
    
users=json_load()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {
            "state": None,
            "name": None,
            "phone": None,
            "date": None
        }
        json_save(users)
        await message.reply("""
<b>Привет! Я бот для записи в барбершоп.</b>
Я помогу тебе выбрать удобное время для посещения нашего барбершопа и запишу тебя на прием.
Напиши /register, чтобы начать процесс записи.
Если у тебя возникнут вопросы, не стесняйся обращаться ко мне!
        """, parse_mode=ParseMode.HTML)
    else:
        await message.reply("Приветсвуем вас снова!")
        if users[user_id]["state"] == "awaiting_name" or users[user_id]["state"] == "awaiting_phone" or users[user_id]["state"] == "awaiting_date":
            users[user_id]["state"] = None
            users[user_id]["name"] = None
            users[user_id]["phone"] = None
            users[user_id]["date"] = None
            json_save(users)
            await message.reply("Ваши данные были сброшены. Запишитесь заново введя /register.")
        elif users[user_id]["state"] == "finished":
            await message.reply("Вы уже записаны. Если хотите записаться снова, введите /register.")

@dp.message(Command("register"))
async def register_command(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {
            "state": None,
            "name": None,
            "phone": None,
            "date": None
        }
        json_save(users)
    
    if users[user_id]["state"]=="finished":
        await message.reply("Вы уже завершили процесс регистрации.")
        return
    
    if users[user_id]["state"] is not None:
        await message.reply("Вы уже начали процесс регистрации. Я сброшу ваши данные и мы начнем регистрацию заново.")
        users[user_id]["state"] = None
        users[user_id]["name"] = None
        users[user_id]["phone"] = None
        users[user_id]["date"] = None
        json_save(users)
    
    users[user_id]["state"] = "awaiting_name"
    json_save(users)
    await message.reply("Пожалуйста, введите ваше имя.")
    
@dp.message(Command("cancel"))
async def cancel_command(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id in users:
        users[user_id]["state"] = None
        users[user_id]["name"] = None
        users[user_id]["phone"] = None
        users[user_id]["date"] = None
        json_save(users)
        delete_user(int(user_id))
        await message.reply("Регистрация отменена. Ваши данные удалены. Введите /register для начала процесса регистрации.")
        delete_user(int(user_id))
    else:
        users[user_id] = {
            "state": None,
            "name": None,
            "phone": None,
            "date": None
        }
        json_save(users)
        await message.reply("Вас нет в базе данных. Я вас добавил, так что можете начинать регестрацию, введя /register.")
    
@dp.message(Command("mydata"))
async def mydata_command(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id in users and users[user_id]["state"] == "finished":
        await message.reply(f"""
*Ваши данные*:\n
    *Имя*: {users[user_id]['name']}\n
    *Телефон*: {users[user_id]['phone']}\n
    *Дата*: {users[user_id]['date']}
""", parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply("Вы не зарегистрированы или не завершили процесс регистрации.")

@dp.message()
async def handle_message(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {
            "state": None,
            "name": None,
            "phone": None,
            "date": None
        }
        json_save(users)
    
    if users[user_id]["state"] == "awaiting_name":
        users[user_id]["name"] = message.text
        users[user_id]["state"] = "awaiting_phone"
        json_save(users)
        await message.reply("Спасибо! Теперь введите ваш номер телефона.")
    elif users[user_id]["state"] == "awaiting_phone":
        users[user_id]["phone"] = message.text
        users[user_id]["state"] = "awaiting_date"
        json_save(users)
        await message.reply("Отлично! Теперь введите желаемую дату и время для записи (например, 2024-07-01 15:00).")
    elif users[user_id]["state"] == "awaiting_date":
        users[user_id]["date"] = message.text
        users[user_id]["state"] = "finished"
        json_save(users)
        await message.reply(f"Спасибо за регистрацию, {users[user_id]['name']}! Вы записаны на {users[user_id]['date']}. Мы свяжемся с вами по номеру {users[user_id]['phone']} для подтверждения записи.")
        add_user(tg_id=int(user_id), name=users[user_id]["name"], phone=users[user_id]["phone"], date=users[user_id]["date"])
    else:
        await message.reply("Пожалуйста, начните процесс регистрации, введя /register.")
    
if __name__ == "__main__":
    print("Бот запущен...")
    asyncio.run(dp.start_polling(bot))
    print("Бот остановлен.")    