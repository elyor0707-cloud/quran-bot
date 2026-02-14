import requests
import os
import sqlite3
import random
import stripe
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# ======================
# CONFIG
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")
STRIPE_SECRET = os.getenv("STRIPE_SECRET")

stripe.api_key = STRIPE_SECRET

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ======================
# DATABASE
# ======================

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    ayah_progress INTEGER DEFAULT 1,
    premium INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT ayah_progress,premium,score FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return 1,0,0
    return row

def add_score(user_id, points):
    cursor.execute("UPDATE users SET score=score+? WHERE user_id=?", (points,user_id))
    conn.commit()

def activate_premium(user_id):
    cursor.execute("UPDATE users SET premium=1 WHERE user_id=?", (user_id,))
    conn.commit()

# ======================
# MENUS
# ======================

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add("📖 Бугунги оят")
main_keyboard.add("🧠 Тест режими")
main_keyboard.add("📊 Leaderboard")
main_keyboard.add("📜 Сертификат")
main_keyboard.add("📚 Грамматика")
main_keyboard.add("💳 Premium")

# ======================
# TEST SYSTEM
# ======================

arabic_letters = ["ا","ب","ت","ث","ج","ح","خ","د","ذ","ر","ز","س","ش","ص","ض","ط","ظ","ع","غ","ف","ق","ك","ل","م","ن","ه","و","ي"]

tests = {}

@dp.message_handler(lambda m: m.text=="🧠 Тест режими")
async def start_test(message: types.Message):
    tests[message.from_user.id] = {"score":0,"count":0}
    await ask_question(message)

async def ask_question(message):
    letter = random.choice(arabic_letters)
    tests[message.from_user.id]["correct"] = letter
    tests[message.from_user.id]["count"] += 1
    await message.answer(f"{tests[message.from_user.id]['count']}/10\nБу қайси ҳарф?\n\n{letter}")

@dp.message_handler(lambda m: m.from_user.id in tests and m.text!="🏠 Бош меню")
async def check_answer(message: types.Message):
    user_test = tests[message.from_user.id]

    if message.text.strip()==user_test["correct"]:
        user_test["score"] +=1
        await message.answer("✅ Тўғри")
    else:
        await message.answer(f"❌ Нотўғри. Жавоб: {user_test['correct']}")

    if user_test["count"]<10:
        await ask_question(message)
    else:
        final_score = user_test["score"]
        add_score(message.from_user.id, final_score*10)

        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("🏠 Бош меню")

        await message.answer(
            f"🏁 Тест тугади!\n\nНатижа: {final_score}/10\nБалл: {final_score*10}",
            reply_markup=kb
        )

        del tests[message.from_user.id]

# ======================
# HOME
# ======================

@dp.message_handler(lambda m: m.text=="🏠 Бош меню")
async def back_home(message: types.Message):
    if message.from_user.id in tests:
        del tests[message.from_user.id]
    await message.answer("🏠 Бош меню", reply_markup=main_keyboard)

# ======================
# LEADERBOARD
# ======================

@dp.message_handler(lambda m: m.text=="📊 Leaderboard")
async def leaderboard(message: types.Message):
    cursor.execute("SELECT user_id,score FROM users ORDER BY score DESC LIMIT 10")
    rows = cursor.fetchall()

    text="🏆 ТОП 10\n\n"
    for i,row in enumerate(rows,1):
        text+=f"{i}. {row[0]} — {row[1]} балл\n"

    await message.answer(text)

# ======================
# CERTIFICATE (Professional PDF)
# ======================

@dp.message_handler(lambda m: m.text=="📜 Сертификат")
async def generate_certificate(message: types.Message):

    filename="certificate.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)

    elements = []

    style = ParagraphStyle(
        name='Normal',
        fontSize=22,
        textColor=colors.darkblue
    )

    elements.append(Paragraph("QURAN LEARNING CERTIFICATE", style))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"User ID: {message.from_user.id}", style))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Successfully completed test module.", style))

    doc.build(elements)

    with open(filename,"rb") as f:
        await message.answer_document(f)

# ======================
# PREMIUM (Stripe Checkout)
# ======================

@dp.message_handler(lambda m: m.text=="💳 Premium")
async def premium_payment(message: types.Message):

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data':{
                'currency':'usd',
                'product_data':{'name':'Quran Premium'},
                'unit_amount':3000,
            },
            'quantity':1,
        }],
        mode='payment',
        success_url='https://example.com/success',
        cancel_url='https://example.com/cancel',
    )

    await message.answer(f"💳 Тўлов учун ҳавола:\n{session.url}")

# ======================
# GRAMMAR
# ======================

@dp.message_handler(lambda m: m.text=="📚 Грамматика")
async def grammar_menu(message: types.Message):

    text = """
📚 Араб грамматикаси:

1️⃣ Ҳаракатлар (фатҳа, касра, дамма)
2️⃣ Танвин
3️⃣ Сукун
4️⃣ Шадда
5️⃣ Исм ва феъл фарқи
6️⃣ Жумла тузилиши
"""

    await message.answer(text)

# ======================
# RUN
# ======================

if __name__=="__main__":
    executor.start_polling(dp, skip_updates=True)
