import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, Poll
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class TestState(StatesGroup):
    in_test = State()
    waiting_answer = State()

# Test savollari
ALL_QUESTIONS = [
    # Alifbo savollari
    {"q": "ب harfining nomi nima?", "opts": ["Alif", "Ba", "Ta", "Sa"], "a": 1, "cat": "alphabet"},
    {"q": "ع harfi qanday talaffuz qilinadi?", "opts": ["oddiy 'a'", "tomoqdan 'a'", "burun 'a'", "og'ir 'a'"], "a": 1, "cat": "alphabet"},
    {"q": "Qancha arab harfi mavjud?", "opts": ["26", "28", "30", "32"], "a": 1, "cat": "alphabet"},
    {"q": "Arab yozuvi qaysi tomonga o'qiladi?", "opts": ["Chapdan o'ngga", "O'ngdan chapga", "Yuqoridan pastga", "Istalgan tomonga"], "a": 1, "cat": "alphabet"},
    {"q": "ص harfi qaysi tovushni ifodalaydi?", "opts": ["oddiy s", "sh", "og'ir s", "z"], "a": 2, "cat": "alphabet"},
    {"q": "Fatha haraki qanday ovoz beradi?", "opts": ["i", "u", "a", "tovushsiz"], "a": 2, "cat": "alphabet"},
    {"q": "Shadda nima?", "opts": ["Uzaytirish belgisi", "Ikkilantirish belgisi", "Sukun belgisi", "Yo'q belgisi"], "a": 1, "cat": "alphabet"},
    {"q": "ق va ك harflarining farqi nima?", "opts": ["Farqi yo'q", "ق - orqa tomog'dan, ك - oldindan", "ك - orqa tomog'dan, ق - oldindan", "Faqat shakli farq qiladi"], "a": 1, "cat": "alphabet"},

    # Tajvid savollari
    {"q": "Izhоr qoidasida nun sakin qanday aytiladi?", "opts": ["Yashirinadi", "Aniq aytiladi", "Ikkilanadi", "Gunnali aytiladi"], "a": 1, "cat": "tajwid"},
    {"q": "Iqlab qoidasi qaysi harf oldida qo'llaniladi?", "opts": ["با", "تا", "با", "ما"], "a": 0, "cat": "tajwid"},
    {"q": "Gunna qancha harakat davom etadi?", "opts": ["1", "2", "3", "4"], "a": 1, "cat": "tajwid"},
    {"q": "Qalqala harflari yod olish uchun qaysi so'z ishlatiladi?", "opts": ["YAMNALAVUN", "QUTB JAD", "IKHFA", "IDGHAM"], "a": 1, "cat": "tajwid"},
    {"q": "Madd tabiiy necha harakat uzunlikda?", "opts": ["1", "2", "4", "6"], "a": 1, "cat": "tajwid"},
    {"q": "Idgom ma'al gunna harflari qaysilar?", "opts": ["ر ل", "ب ت", "ي ن م و", "أ ه ع ح"], "a": 2, "cat": "tajwid"},
    {"q": "Lam shamsiy nima?", "opts": ["Lam aniq aytiladi", "Lam yashirinadi", "Lam ikkilanadi", "Lam o'qilmaydi"], "a": 1, "cat": "tajwid"},
    {"q": "Vaqf majburiy belgisi qaysi?", "opts": ["ج", "ط", "م", "ز"], "a": 2, "cat": "tajwid"},

    # Grammatika savollari
    {"q": "Arabchada sifat otdan qayerda keladi?", "opts": ["Oldin", "Keyin", "Istalgan joyda", "Jumlaning boshida"], "a": 1, "cat": "grammar"},
    {"q": "أَنَا olmoshi nima ma'noni bildiradi?", "opts": ["Sen", "U", "Men", "Biz"], "a": 2, "cat": "grammar"},
    {"q": "Muannath otlarning asosiy belgisi nima?", "opts": ["ي", "و", "ة", "ا"], "a": 2, "cat": "grammar"},
    {"q": "Mozi zamoni qaysi zamonga to'g'ri keladi?", "opts": ["Hozirgi zamon", "O'tgan zamon", "Kelasi zamon", "Buyruq mayli"], "a": 1, "cat": "grammar"},
    {"q": "كِتَابَان nima ma'noni bildiradi?", "opts": ["Kitob", "Kitoblar", "Ikki kitob", "Katta kitob"], "a": 2, "cat": "grammar"},
    {"q": "نَحنُ olmoshi nima ma'noni bildiradi?", "opts": ["Men", "Sen", "Biz", "Ular"], "a": 2, "cat": "grammar"},
]

def get_test_keyboard(question_idx: int, total: int):
    builder = InlineKeyboardBuilder()
    q = ALL_QUESTIONS[question_idx]
    
    for i, opt in enumerate(q['opts']):
        builder.button(text=opt, callback_data=f"test_ans_{question_idx}_{i}")
    
    builder.button(text="❌ Testni to'xtatish", callback_data="test_stop")
    builder.adjust(1)
    
    return builder.as_markup()

@router.callback_query(F.data == "menu_test")
async def test_menu(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Umumiy test (20 savol)", callback_data="test_start_all")
    builder.button(text="🔤 Alifbo testi", callback_data="test_start_alphabet")
    builder.button(text="📖 Tajvid testi", callback_data="test_start_tajwid")
    builder.button(text="📚 Grammatika testi", callback_data="test_start_grammar")
    builder.button(text="⬅️ Asosiy menyu", callback_data="menu_main")
    builder.adjust(1)
    
    await callback.message.edit_text(
        "✅ <b>Test bo'limi</b>\n\n"
        "Bilimingizni tekshiring! Qaysi testni topshirmoqchisiz?",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("test_start_"))
async def start_test(callback: CallbackQuery, state: FSMContext):
    cat = callback.data.replace("test_start_", "")
    
    if cat == "all":
        questions = random.sample(ALL_QUESTIONS, min(20, len(ALL_QUESTIONS)))
    else:
        filtered = [q for q in ALL_QUESTIONS if q['cat'] == cat]
        questions = random.sample(filtered, min(10, len(filtered)))
    
    await state.set_state(TestState.in_test)
    await state.update_data(
        questions=questions,
        current=0,
        score=0,
        wrong=[]
    )
    
    q = questions[0]
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(q['opts']):
        builder.button(text=opt, callback_data=f"test_ans_0_{i}")
    builder.button(text="❌ To'xtatish", callback_data="test_stop")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"📝 <b>Test boshlandi!</b>\n\n"
        f"<b>Savol 1/{len(questions)}:</b>\n\n"
        f"{q['q']}",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("test_ans_"))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    q_idx = int(parts[2])
    ans_idx = int(parts[3])
    
    data = await state.get_data()
    questions = data['questions']
    score = data['score']
    wrong = data['wrong']
    
    current_q = questions[q_idx]
    correct = ans_idx == current_q['a']
    
    if correct:
        score += 1
        feedback = "✅ To'g'ri!"
    else:
        feedback = f"❌ Noto'g'ri! To'g'ri javob: <b>{current_q['opts'][current_q['a']]}</b>"
        wrong.append(current_q)
    
    next_idx = q_idx + 1
    
    if next_idx >= len(questions):
        # Test tugadi
        await state.clear()
        
        total = len(questions)
        percentage = (score / total) * 100
        
        if percentage >= 80:
            emoji = "🏆"
            result = "Ajoyib natija!"
        elif percentage >= 60:
            emoji = "👍"
            result = "Yaxshi natija!"
        elif percentage >= 40:
            emoji = "📚"
            result = "Ko'proq o'rganish kerak"
        else:
            emoji = "💪"
            result = "Tushunmagan joylarga qaytib o'rganaylik"
        
        wrong_text = ""
        if wrong:
            wrong_text = "\n\n<b>Noto'g'ri javoblar:</b>\n"
            for w in wrong[:5]:
                wrong_text += f"• {w['q']}\n  → {w['opts'][w['a']]}\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Qayta test topshirish", callback_data="menu_test")
        builder.button(text="⬅️ Asosiy menyu", callback_data="menu_main")
        builder.adjust(1)
        
        await callback.message.edit_text(
            f"{emoji} <b>Test yakunlandi!</b>\n\n"
            f"<b>Natija:</b> {score}/{total} ({percentage:.0f}%)\n"
            f"<b>Baho:</b> {result}"
            f"{wrong_text}",
            reply_markup=builder.as_markup()
        )
    else:
        await state.update_data(current=next_idx, score=score, wrong=wrong)
        
        next_q = questions[next_idx]
        builder = InlineKeyboardBuilder()
        for i, opt in enumerate(next_q['opts']):
            builder.button(text=opt, callback_data=f"test_ans_{next_idx}_{i}")
        builder.button(text="❌ To'xtatish", callback_data="test_stop")
        builder.adjust(1)
        
        await callback.message.edit_text(
            f"{feedback}\n\n"
            f"<b>Savol {next_idx + 1}/{len(questions)}:</b>\n\n"
            f"{next_q['q']}",
            reply_markup=builder.as_markup()
        )
    
    await callback.answer()

@router.callback_query(F.data == "test_stop")
async def stop_test(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Qayta boshlash", callback_data="menu_test")
    builder.button(text="⬅️ Asosiy menyu", callback_data="menu_main")
    builder.adjust(1)
    
    await callback.message.edit_text(
        "❌ <b>Test to'xtatildi.</b>\n\nIstalgan vaqt qayta boshlashingiz mumkin!",
        reply_markup=builder.as_markup()
    )
    await callback.answer()
