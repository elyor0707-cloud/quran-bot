# database.py

users = {}

def get_surahs():
    return [
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
