"""
📖 Tajvid kitobi bo'limi
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

TAJWID_RULES = [
    {
        "id": "izhaar",
        "name": "Izhor",
        "arabic": "الإظهار",
        "short": "Aniq o'qish",
        "desc": (
            "Izhor — aniq, ravshan talaffuz qilish demak.\n\n"
            "<b>📌 Qoida:</b> Nun sokin (نْ) yoki tanvin (ـً ـٍ ـٌ) dan keyin bo'g'iz harflari kelsa, "
            "nun aniq o'qiladi, idgom yoki ixfo bo'lmaydi.\n\n"
            "<b>Bo'g'iz harflari (6 ta):</b>\n"
            "<code>ء ه ع ح غ خ</code>\n\n"
            "<b>📝 Misollar:</b>\n"
            "<code>مَنْ آمَنَ</code> — man AAMANA (nun aniq)\n"
            "<code>عَلِيمٌ حَكِيمٌ</code> — tanvin aniq\n\n"
            "<b>🎵 Eslab qolish:</b> «Aniq» — bo'g'izdan chiqadigan harflar oldida nun aniq!"
        )
    },
    {
        "id": "idgham",
        "name": "Idgom",
        "arabic": "الإدغام",
        "short": "Qo'shib o'qish",
        "desc": (
            "Idgom — nun sokin yoki tanvinni keyingi harfga «eritish» — qo'shib o'qish.\n\n"
            "<b>📌 Idgom harflari (6 ta):</b>\n"
            "<code>ي ر م ل و ن</code> (yarmalu + vun)\n\n"
            "<b>2 turi:</b>\n"
            "1. <b>Gunna bilan</b> (ي و ن م) — burun tovushi bilan\n"
            "2. <b>Gunnasiz</b> (ل ر) — to'g'ridan qo'shiladi\n\n"
            "<b>📝 Misollar:</b>\n"
            "<code>مَن يَقُولُ</code> — man + ya → mayya-qulu\n"
            "<code>مِن رَبِّهِم</code> — min + ra → mirrab-bihim\n\n"
            "<b>⚠️ Istisnolar:</b> قِنْوَانٌ، بُنْيَانٌ — bir so'zda bo'lsa, idgom yo'q."
        )
    },
    {
        "id": "iqlab",
        "name": "Iqlab",
        "arabic": "الإقلاب",
        "short": "Almashtirib o'qish",
        "desc": (
            "Iqlab — nun sokin yoki tanvinni «mim»ga almashtirish.\n\n"
            "<b>📌 Qoida:</b> Nun sokin / tanvindan keyin «ب» (bo) kelsa, "
            "nun «م» (mim)ga aylanadi va burun bilan gunna qilinadi.\n\n"
            "<b>📝 Misollar:</b>\n"
            "<code>مَن بَخِلَ</code> — mam-baxila\n"
            "<code>سَمِيعٌ بَصِيرٌ</code> — samiim-basir\n\n"
            "<b>🎵 Eslab qolish:</b> «Nun + Bo = Mim + Gunna» — faqat bitta harf iqlab uchun!"
        )
    },
    {
        "id": "ikhfa",
        "name": "Ixfo",
        "arabic": "الإخفاء",
        "short": "Yashirib o'qish",
        "desc": (
            "Ixfo — nun sokinni yashirish: to'liq aytmay, «burun»ga o'tkazib o'qish.\n\n"
            "<b>📌 Ixfo harflari (15 ta):</b>\n"
            "<code>ت ث ج د ذ ز س ش ص ض ط ظ ف ق ك</code>\n\n"
            "<b>📝 Misollar:</b>\n"
            "<code>مَن كَفَرَ</code> — man~kafara (yashirib)\n"
            "<code>عَلِيمٌ قَدِيرٌ</code> — alii~qadir\n\n"
            "<b>🎵 Eslab qolish:</b> Izhor + Idgom + Iqlab harflari olib tashlansa, "
            "qolgan 15 ta harf ixfo uchun!"
        )
    },
    {
        "id": "madd",
        "name": "Madd",
        "arabic": "المد",
        "short": "Cho'zib o'qish",
        "desc": (
            "Madd — harfni cho'zib o'qish. O'lchov birligi — «harakat» (1 harakat ≈ 1 son).\n\n"
            "<b>📌 Madd harflari:</b> <code>ا و ي</code>\n\n"
            "<b>Turlari:</b>\n"
            "• <b>Tabi'iy (Asl madd)</b> — 2 harakat: <code>قَالَ / قِيلَ / يَقُولُ</code>\n"
            "• <b>Muttasil</b> — bir so'zda madd + hamza — 4-5 harakat\n"
            "• <b>Munfasil</b> — alohida so'zlarda — 4-5 harakat\n"
            "• <b>Lazim</b> — sukun yoki tashdid oldida — 6 harakat (shart)\n\n"
            "<b>📝 Misollar:</b>\n"
            "<code>الضَّالِّينَ</code> — 6 harakat (lazim)\n"
            "<code>جَاءَ</code> — 4-5 harakat (muttasil)"
        )
    },
    {
        "id": "gunna",
        "name": "Gunna",
        "arabic": "الغنة",
        "short": "Burun tovushi",
        "desc": (
            "Gunna — burun orqali chiqadigan tovush. 2 harakat ushlanadi.\n\n"
            "<b>📌 Gunna harflari:</b> <code>ن م</code> (nun va mim)\n\n"
            "<b>Qachon gunna bo'ladi?</b>\n"
            "• Mim/Nun tashdid bo'lganda: <code>إِنَّ / أَمَّا</code>\n"
            "• Idgom gunna bilan bo'lganda\n"
            "• Ixfo va iqlobda\n\n"
            "<b>📝 Misollar:</b>\n"
            "<code>إِنَّ اللَّهَ</code> — nun tashdid, 2 harakat gunna\n"
            "<code>ثُمَّ</code> — mim tashdid, 2 harakat gunna"
        )
    },
    {
        "id": "qalqala",
        "name": "Qalqala",
        "arabic": "القلقلة",
        "short": "Titratib o'qish",
        "desc": (
            "Qalqala — harfni to'xtab, tebranib o'qish.\n\n"
            "<b>📌 Qalqala harflari (5 ta):</b>\n"
            "<code>ق ط ب ج د</code>\n"
            "Yodlash: «QUTBA'JID» yoki «قُطبُ جَدٍّ»\n\n"
            "<b>2 darajasi:</b>\n"
            "• Kichik qalqala — so'z o'rtasida sukun\n"
            "• Katta qalqala — so'z oxirida waqf (to'xtatish)\n\n"
            "<b>📝 Misollar:</b>\n"
            "<code>يَقُولُ</code> — qof sukun → qalqala\n"
            "<code>الْفَلَقِ</code> — oxirda waqf → katta qalqala"
        )
    },
    {
        "id": "lam",
        "name": "Lam qoidalari",
        "arabic": "أحكام اللام",
        "short": "Shamsiya va qamariya",
        "desc": (
            "«Al» (الـ) artikli — 2 xil o'qiladi:\n\n"
            "<b>1. Shamsiya لام شمسية</b>\n"
            "Lam o'qilmaydi, keyingi harf tashdid bo'ladi:\n"
            "<code>الشَّمْس، الرَّحْمَن، النَّاس</code>\n\n"
            "<b>Shamsiya harflari (14 ta):</b>\n"
            "<code>ت ث د ذ ر ز س ش ص ض ط ظ ل ن</code>\n\n"
            "<b>2. Qamariya لام قمرية</b>\n"
            "Lam aniq o'qiladi:\n"
            "<code>الْقَمَر، الْكِتَاب، الْحَمْد</code>\n\n"
            "<b>Qamariya harflari (14 ta):</b>\n"
            "<code>ء ب ج ح خ ع غ ف ق ك م و ه ي</code>\n\n"
            "<b>🎵 Eslab qolish:</b> Shamsiya — quyosh harflari (lam «eriydi»). "
            "Qamariya — oy harflari (lam aniq)."
        )
    },
]

def get_tajwid_list_keyboard():
    builder = InlineKeyboardBuilder()
    for rule in TAJWID_RULES:
        builder.button(
            text=f"📌 {rule['name']} ({rule['arabic']}) — {rule['short']}",
            callback_data=f"tajwid_{rule['id']}"
        )
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(1)
    return builder.as_markup()

def get_tajwid_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Tajvid ro'yxati", callback_data="menu_tajwid")
    builder.button(text="🏠 Bosh menyu", callback_data="menu_main")
    builder.adjust(2)
    return builder.as_markup()

@router.callback_query(F.data == "menu_tajwid")
async def tajwid_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📖 <b>Tajvid kitobi — 8 asosiy qoida</b>\n\n"
        "Tajvid — Qur'onni to'g'ri va go'zal o'qish ilmi.\n"
        "Har bir qoidani bosing va batafsil o'rganing 👇",
        reply_markup=get_tajwid_list_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r"^tajwid_(.+)$"))
async def show_tajwid_rule(callback: CallbackQuery):
    rule_id = callback.data.split("_", 1)[1]
    rule = next((r for r in TAJWID_RULES if r["id"] == rule_id), None)
    if not rule:
        await callback.answer("Qoida topilmadi!")
        return

    text = (
        f"📖 <b>{rule['name']} ({rule['arabic']})</b>\n"
        f"<i>{rule['short']}</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{rule['desc']}"
    )

    await callback.message.edit_text(text, reply_markup=get_tajwid_back_keyboard())
    await callback.answer()
