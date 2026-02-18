# database.py

users = {}

def get_surahs():
    return [
        {"number": i, "name": name}
        for i, name in [
        {"number": 1, "name": "Fatiha"},
        {"number": 2, "name": "Baqara"},
        {"number": 3, "name": "Imran"},
        {"number": 4, "name": "Nisa"},
        {"number": 5, "name": "Maida"},
        {"number": 6, "name": "Anam"},
        {"number": 7, "name": "Araf"},
        {"number": 8, "name": "Anfal"},
        {"number": 9, "name": "Tawba"},
        {"number": 10, "name": "Yunus"},
        {"number": 11, "name": "Hud"},
        {"number": 12, "name": "Yusuf"},
        {"number": 13, "name": "Rad"},
        {"number": 14, "name": "Ibrahim"},
        {"number": 15, "name": "Hijr"},
        {"number": 16, "name": "Nahl"},
        {"number": 17, "name": "Isro"},
        {"number": 18, "name": "Kahf"},
        {"number": 19, "name": "Maryam"},
        {"number": 20, "name": "Toha"},
        {"number": 21, "name": "Anbiya"},
        {"number": 22, "name": "Hajj"},
        {"number": 23, "name": "Muminun"},
        {"number": 24, "name": "Nur"},
        {"number": 25, "name": "Furqan"},
        {"number": 26, "name": "Shuaro"},
        {"number": 27, "name": "Naml"},
        {"number": 28, "name": "Qasas"},
        {"number": 29, "name": "Ankabut"},
        {"number": 30, "name": "Rum"},
        {"number": 31, "name": "Luqmon"},
        {"number": 32, "name": "Sajda"},
        {"number": 33, "name": "Ahzob"},
        {"number": 34, "name": "Saba"},
        {"number": 35, "name": "Fatir"},
        {"number": 36, "name": "Yasin"},
        {"number": 37, "name": "Saffat"},
        {"number": 38, "name": "Sod"},
        {"number": 39, "name": "Zumar"},
        {"number": 40, "name": "Ghafir"},
        {"number": 41, "name": "Fussilat"},
        {"number": 42, "name": "Shuro"},
        {"number": 43, "name": "Zukhruf"},
        {"number": 44, "name": "Dukhan"},
        {"number": 45, "name": "Jasiya"},
        {"number": 46, "name": "Ahqof"},
        {"number": 47, "name": "Muhammad"},
        {"number": 48, "name": "Fath"},
        {"number": 49, "name": "Hujurat"},
        {"number": 50, "name": "Qof"},
        {"number": 51, "name": "Zariyat"},
        {"number": 52, "name": "Tur"},
        {"number": 53, "name": "Najm"},
        {"number": 54, "name": "Qamar"},
        {"number": 55, "name": "Rahman"},
        {"number": 56, "name": "Waqia"},
        {"number": 57, "name": "Hadid"},
        {"number": 58, "name": "Mujodala"},
        {"number": 59, "name": "Hashr"},
        {"number": 60, "name": "Mumtahana"},
        {"number": 61, "name": "Saff"},
        {"number": 62, "name": "Juma"},
        {"number": 63, "name": "Munafiqun"},
        {"number": 64, "name": "Taghabun"},
        {"number": 65, "name": "Talaq"},
        {"number": 66, "name": "Tahrim"},
        {"number": 67, "name": "Mulk"},
        {"number": 68, "name": "Qalam"},
        {"number": 69, "name": "Haqqah"},
        {"number": 70, "name": "Maarij"},
        {"number": 71, "name": "Nuh"},
        {"number": 72, "name": "Jinn"},
        {"number": 73, "name": "Muzzammil"},
        {"number": 74, "name": "Muddassir"},
        {"number": 75, "name": "Qiyamah"},
        {"number": 76, "name": "Insan"},
        {"number": 77, "name": "Mursalat"},
        {"number": 78, "name": "Naba"},
        {"number": 79, "name": "Naziat"},
        {"number": 80, "name": "Abasa"},
        {"number": 81, "name": "Takwir"},
        {"number": 82, "name": "Infitar"},
        {"number": 83, "name": "Mutaffifin"},
        {"number": 84, "name": "Inshiqoq"},
        {"number": 85, "name": "Buruj"},
        {"number": 86, "name": "Tariq"},
        {"number": 87, "name": "Ala"},
        {"number": 88, "name": "Ghashiya"},
        {"number": 89, "name": "Fajr"},
        {"number": 90, "name": "Balad"},
        {"number": 91, "name": "Shams"},
        {"number": 92, "name": "Layl"},
        {"number": 93, "name": "Duha"},
        {"number": 94, "name": "Sharh"},
        {"number": 95, "name": "Tin"},
        {"number": 96, "name": "Alaq"},
        {"number": 97, "name": "Qadr"},
        {"number": 98, "name": "Bayyina"},
        {"number": 99, "name": "Zalzala"},
        {"number": 100, "name": "Adiyat"},
        {"number": 101, "name": "Qoria"},
        {"number": 102, "name": "Takathur"},
        {"number": 103, "name": "Asr"},
        {"number": 104, "name": "Humaza"},
        {"number": 105, "name": "Fil"},
        {"number": 106, "name": "Quraysh"},
        {"number": 107, "name": "Maun"},
        {"number": 108, "name": "Kawthar"},
        {"number": 109, "name": "Kafirun"},
        {"number": 110, "name": "Nasr"},
        {"number": 111, "name": "Masad"},
        {"number": 112, "name": "Ikhlas"},
        {"number": 113, "name": "Falaq"},
        {"number": 114, "name": "Nas"},
    ]

    ]




def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "current_surah": 1,
            "current_ayah": 1
        }
    return users[user_id]

def update_user(user_id, field, value):
    if user_id not in users:
        get_user(user_id)

    users[user_id][field] = value


def get_ayah(surah, ayah):
    # TEST VERSION (кейин API'га улаймиз)
    return {
        "surah_name": f"{surah}-сура",
        "arabic": f"Оят {ayah} арабча матн",
        "uzbek": f"Оят {ayah} ўзбекча таржима",
        "total_ayahs": 7
    }
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

