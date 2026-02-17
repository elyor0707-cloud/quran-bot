# database.py

users = {}

def get_surahs():
    return [{"number": i} for i in range(1, 115)]

def get_user(user_id):
    if user_id not in users:
        users[user_id] = [user_id, 1, 1]
    return users[user_id]

def update_user(user_id, field, value):
    if user_id not in users:
        users[user_id] = [user_id, 1, 1]

    if field == "current_surah":
        users[user_id][1] = value
    elif field == "current_ayah":
        users[user_id][2] = value

def get_ayah(surah, ayah):
    return {
        "surah_name": f"{surah}-сура",
        "arabic": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "uzbek": "Бисмиллаҳир роҳманир роҳим",
        "total_ayahs": 7
    }
