# database.py

# Foydalanuvchilar ma'lumotlari
USERS = {}

# Suralar ro‘yxati
SURAH_LIST = [
    {"number": i + 1, "name": name} for i, name in enumerate([
        "Fatiha","Baqara","Ali Imran","Nisa","Maida","Anam","Araf","Anfal","Tawba","Yunus",
        "Hud","Yusuf","Rad","Ibrahim","Hijr","Nahl","Isra","Kahf","Maryam","Taha",
        "Anbiya","Hajj","Muminun","Nur","Furqan","Shuara","Naml","Qasas","Ankabut","Rum",
        "Luqman","Sajda","Ahzab","Saba","Fatir","Yasin","Saffat","Sad","Zumar","Ghafir",
        "Fussilat","Shura","Zukhruf","Dukhan","Jathiya","Ahqaf","Muhammad","Fath","Hujurat","Qaf",
        "Dhariyat","Tur","Najm","Qamar","Rahman","Waqia","Hadid","Mujadila","Hashr","Mumtahana",
        "Saff","Jumuah","Munafiqun","Taghabun","Talaq","Tahrim","Mulk","Qalam","Haqqa","Maarij",
        "Nuh","Jinn","Muzzammil","Muddathir","Qiyamah","Insan","Mursalat","Naba","Naziat","Abasa",
        "Takwir","Infitar","Mutaffifin","Inshiqaq","Buruj","Tariq","Ala","Ghashiya","Fajr","Balad",
        "Shams","Layl","Duha","Sharh","Tin","Alaq","Qadr","Bayyina","Zalzala","Adiyat",
        "Qaria","Takathur","Asr","Humaza","Fil","Quraysh","Maun","Kawthar","Kafirun","Nasr",
        "Masad","Ikhlas","Falaq","Nas"
    ])
]

def get_surahs():
    return SURAH_LIST

def get_user(user_id):
    if user_id not in USERS:
        USERS[user_id] = {
            "user_id": user_id,
            "current_surah": 1,
            "current_ayah": 1,
            "is_premium": False,
            "last_surah": None,
            "last_ayah": None,
            "last_page": None
        }
    return USERS[user_id]

def update_user(user_id, key, value):
    user = get_user(user_id)
    user[key] = value
    USERS[user_id] = user

def get_premium_users():
    return [u for u in USERS.values() if u.get("is_premium", False)]

# Progress funksiyalari
def update_progress(user_id, surah, ayah):
    update_user(user_id, "last_surah", surah)
    update_user(user_id, "last_ayah", ayah)

def get_progress(user_id):
    user = get_user(user_id)
    return user.get("last_surah"), user.get("last_ayah")

def update_page_progress(user_id, page):
    update_user(user_id, "last_page", page)

def get_page_progress(user_id):
    user = get_user(user_id)
    return user.get("last_page")
