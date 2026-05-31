import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("money.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")
conn.commit()


def get_balance(user_id):
    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO users VALUES (?, ?)", (user_id, 0))
        conn.commit()
        return 0
    return row[0]


def add_money(user_id, amount):
    bal = get_balance(user_id)
    new_bal = bal + amount
    cur.execute("UPDATE users SET balance=? WHERE user_id=?", (new_bal, user_id))
    conn.commit()


@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    get_balance(msg.from_user.id)
    await msg.answer("бот запущен")


@dp.message_handler(commands=["balance"])
async def balance(msg: types.Message):
    bal = get_balance(msg.from_user.id)
    await msg.answer(f"баланс: {bal}")


@dp.message_handler(commands=["add"])
async def add(msg: types.Message):
    if msg.from_user.id == int(os.getenv("ADMIN_ID")):
        try:
            _, user_id, amount = msg.text.split()
            add_money(int(user_id), int(amount))
            await msg.answer("добавлено")
        except:
            await msg.answer("пример: /add 123456 20")


executor.start_polling(dp)
