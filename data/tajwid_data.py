# Tajvid qoidalari

TAJWID_RULES = [
    {
        "id": 1,
        "name": "Izhор (إظهار)",
        "arabic": "إظهار",
        "category": "Nun sakin va tanvin qoidalari",
        "description": "Nun sakin (نْ) yoki tanvin (ً ٍ ٌ) dan keyin bo'g'iz harflari (أ ه ع ح غ خ) kelsa, nun ovozi aniq va to'liq talaffuz qilinadi.",
        "letters": ["أ", "ه", "ع", "ح", "غ", "خ"],
        "letter_names": ["Hamza", "Ha", "Ayn", "Ha", "Gayn", "Xa"],
        "rule_name": "Izhоr - Aniq talaffuz",
        "example_arabic": "مَنْ أَمَنَ",
        "example_transliteration": "man āmana",
        "example_meaning": "kim imon keltirdi",
        "tip": "💡 Eslab qoling: Bo'g'iz harflari oldidan nun SAKINni to'liq aytasiz, gunnasiz!",
        "color": "🟢"
    },
    {
        "id": 2,
        "name": "Idgom (إدغام)",
        "arabic": "إدغام",
        "category": "Nun sakin va tanvin qoidalari",
        "description": "Nun sakin yoki tanvindan keyin 6 ta harf kelsa birlashtirish: (ي ر م ل و ن). Ikki xil: gunna bilan (ي ن م و) va gunnasiz (ر ل).",
        "letters": ["ي", "ر", "م", "ل", "و", "ن"],
        "subtypes": [
            {
                "name": "Idgom ma'al gunna (gunnali)",
                "letters": ["ي", "ن", "م", "و"],
                "description": "Nun harflari - burun tovushi bilan birlashtirish"
            },
            {
                "name": "Idgom bila gunna (gunnasiz)",
                "letters": ["ر", "ل"],
                "description": "Ra va Lam - burunsiz birlashtirish"
            }
        ],
        "example_arabic": "مِن يَقول",
        "example_transliteration": "miy yaqūl",
        "example_meaning": "kim aytsa",
        "tip": "💡 Eslab qoling: YAMNALAVUN (يَمنَلَوُن) - 6 harfni shu so'z bilan yod oling!",
        "color": "🔵"
    },
    {
        "id": 3,
        "name": "Iqlab (إقلاب)",
        "arabic": "إقلاب",
        "category": "Nun sakin va tanvin qoidalari",
        "description": "Nun sakin yoki tanvindan keyin Ba (ب) harfi kelsa, nun 'mim' ga aylanadi va gunna qilinadi.",
        "letters": ["ب"],
        "letter_names": ["Ba"],
        "example_arabic": "مِن بَعد",
        "example_transliteration": "mim baʿd",
        "example_meaning": "keyin",
        "tip": "💡 Eslab qoling: Faqat BA harfi oldida IQLAB - nun MIM ga aylanadi!",
        "color": "🟡"
    },
    {
        "id": 4,
        "name": "Ixfo (إخفاء)",
        "arabic": "إخفاء",
        "category": "Nun sakin va tanvin qoidalari",
        "description": "Nun sakin yoki tanvindan keyin qolgan 15 ta harf kelsa, nun yashirinadi va burun tovushi (gunna) bilan talaffuz qilinadi.",
        "letters": ["ت", "ث", "ج", "د", "ذ", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ف", "ق", "ك"],
        "example_arabic": "مِن تَحت",
        "example_transliteration": "min taḥt",
        "example_meaning": "ostidan",
        "tip": "💡 Eslab qoling: 15 ta harf - Izhоr, Idgom va Iqlab harflaridan tashqari qolganlar!",
        "color": "🟠"
    },
    {
        "id": 5,
        "name": "Madd (مَد)",
        "arabic": "مَد",
        "category": "Madd qoidalari",
        "description": "Madd - cho'zish demakdir. Madd harflari (ا و ي) bilan birga keladi.",
        "types": [
            {
                "name": "Madd tabiiy (طبيعي)",
                "description": "Asosiy madd - 2 harakat uzunligi",
                "duration": "2 harakat",
                "example": "قَالَ - قِيلَ - يَقُول"
            },
            {
                "name": "Madd muttasil (متصل)",
                "description": "Bir so'zda madd va hamza - 4-5 harakat",
                "duration": "4-5 harakat",
                "example": "جَاءَ - شَاءَ"
            },
            {
                "name": "Madd munfasil (منفصل)",
                "description": "Ikki so'zda madd va hamza - 4-5 harakat",
                "duration": "4-5 harakat",
                "example": "إِنَّا أَعطَيناك"
            },
            {
                "name": "Madd lazim (لازم)",
                "description": "Sukun bilan madd - 6 harakat",
                "duration": "6 harakat",
                "example": "وَلَا الضَّالِّين"
            }
        ],
        "tip": "💡 Eslab qoling: Madd = cho'zish. Hamza yoki sukun kelsa, cho'zimni uzaytirasiz!",
        "color": "🟣"
    },
    {
        "id": 6,
        "name": "Gunna (غنة)",
        "arabic": "غنة",
        "category": "Harflar xususiyatlari",
        "description": "Burun tovushi - Nun (ن) va Mim (م) harflarida mavjud bo'lib, 2 harakat davom etadi.",
        "letters": ["ن", "م"],
        "cases": [
            "Shaddalangan Nun (نّ)",
            "Shaddalangan Mim (مّ)",
            "Iqlab holida",
            "Ixfo holida",
            "Idgom ma'al gunna holida"
        ],
        "example_arabic": "إِنَّ - ثُمَّ",
        "tip": "💡 Eslab qoling: Gunna = burun tovushi. NUN va MIM harflarida paydo bo'ladi!",
        "color": "🔴"
    },
    {
        "id": 7,
        "name": "Qalqala (قلقلة)",
        "arabic": "قلقلة",
        "category": "Harflar xususiyatlari",
        "description": "Titroq tovush - 5 ta harf sukun holida kelganda titrab talaffuz qilinadi.",
        "letters": ["ق", "ط", "ب", "ج", "د"],
        "memory_word": "قُطُب جَد (QUTB JAD)",
        "levels": [
            {"name": "Kichik qalqala", "description": "So'z o'rtasida sukun"},
            {"name": "O'rta qalqala", "description": "So'z oxirida sukun (vaqf qilinganda)"},
            {"name": "Katta qalqala", "description": "So'z oxirida shadda + vaqf"}
        ],
        "example_arabic": "يَخلُق - الحَق",
        "tip": "💡 Eslab qoling: QUTB JAD (قُطُب جَد) - 5 harfni shu ibora bilan yod oling!",
        "color": "🟤"
    },
    {
        "id": 8,
        "name": "Lam ta'rif qoidalari",
        "arabic": "لام التعريف",
        "category": "Lam qoidalari",
        "description": "ال (al-) artiklining ikki xil o'qilishi: Qamariy (oy) va Shamsiy (quyosh)",
        "types": [
            {
                "name": "Lam qamariy (قمرية)",
                "description": "Lam aniq aytiladi - 14 ta harf oldida",
                "letters": ["أ", "ب", "ج", "ح", "خ", "ع", "غ", "ف", "ق", "ك", "م", "و", "ه", "ي"],
                "memory_word": "ابغ حجك وخف عقيمه",
                "example": "اَلْكِتَاب = al-kitāb"
            },
            {
                "name": "Lam shamsiy (شمسية)",
                "description": "Lam yashirinadi - 14 ta harf oldida",
                "letters": ["ت", "ث", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ل", "ن"],
                "example": "اَلشَّمس = ash-shams (emas al-shams!)"
            }
        ],
        "tip": "💡 Eslab qoling: Quyosh (شمس) harflarida Lam yashirinadi, Oy (قمر) harflarida - aytiladi!",
        "color": "⭐"
    },
]

# Vaqf (to'xtatish) belgilari
WAQF_SIGNS = [
    {"sign": "م", "name": "Vaqf lazim", "description": "To'xtash majburiy"},
    {"sign": "ط", "name": "Vaqf mutlaq", "description": "To'xtash yaxshi"},
    {"sign": "ج", "name": "Vaqf jaiz", "description": "To'xtash mumkin"},
    {"sign": "ز", "name": "Vaqf mujawwaz", "description": "To'xtash ruxsat"},
    {"sign": "ص", "name": "Vaqf murakhkhas", "description": "To'xtash yaxshi emas lekin mumkin"},
    {"sign": "لا", "name": "Vaqf mamnu", "description": "To'xtash mumkin emas"},
    {"sign": "قلى", "name": "To'xtash afzal", "description": "To'xtash davom etishdan yaxshi"},
    {"sign": "صلى", "name": "Davom afzal", "description": "Davom to'xtashdan yaxshi"},
]
