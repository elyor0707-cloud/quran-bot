# database.py

users = {}

def get_surahs():
    return [
        {"number": i, "name": name}
        for i, name in [
            (1,"Fatiha"), (2,"Baqara"), (3,"Imran"), (4,"Nisa"),
            (5,"Maida"), (6,"Anam"), (7,"Araf"), (8,"Anfal"),
            (9,"Tawba"), (10,"Yunus"),
            # ...
            # 🔥 114 gacha to‘liq ro‘yxat bo‘lishi shart
            (114,"Nas")
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

