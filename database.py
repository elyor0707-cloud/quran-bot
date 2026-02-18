# database.py

users = {}

def get_surahs():
    return [
        {"number": i, "name": name}
        for i, name in [
            (1,"Fatiha"),
            (2,"Baqara"),
            (3,"Ali Imran"),
            (4,"Nisa"),
            (5,"Maida"),
            (6,"Anam"),
            (7,"Araf"),
            (8,"Anfal"),
            (9,"Tawba"),
            (10,"Yunus"),
            (11,"Hud"),
            (12,"Yusuf"),
            (13,"Rad"),
            (14,"Ibrahim"),
            (15,"Hijr"),
            (16,"Nahl"),
            (17,"Isra"),
            (18,"Kahf"),
            (19,"Maryam"),
            (20,"Taha"),
            (21,"Anbiya"),
            (22,"Hajj"),
            (23,"Muminun"),
            (24,"Nur"),
            (25,"Furqan"),
            (26,"Shuara"),
            (27,"Naml"),
            (28,"Qasas"),
            (29,"Ankabut"),
            (30,"Rum"),
            (31,"Luqman"),
            (32,"Sajda"),
            (33,"Ahzab"),
            (34,"Saba"),
            (35,"Fatir"),
            (36,"Yasin"),
            (37,"Saffat"),
            (38,"Sad"),
            (39,"Zumar"),
            (40,"Ghafir"),
            (41,"Fussilat"),
            (42,"Shura"),
            (43,"Zukhruf"),
            (44,"Dukhan"),
            (45,"Jathiya"),
            (46,"Ahqaf"),
            (47,"Muhammad"),
            (48,"Fath"),
            (49,"Hujurat"),
            (50,"Qaf"),
            (51,"Dhariyat"),
            (52,"Tur"),
            (53,"Najm"),
            (54,"Qamar"),
            (55,"Rahman"),
            (56,"Waqia"),
            (57,"Hadid"),
            (58,"Mujadila"),
            (59,"Hashr"),
            (60,"Mumtahana"),
            (61,"Saff"),
            (62,"Jumuah"),
            (63,"Munafiqun"),
            (64,"Taghabun"),
            (65,"Talaq"),
            (66,"Tahrim"),
            (67,"Mulk"),
            (68,"Qalam"),
            (69,"Haqqa"),
            (70,"Maarij"),
            (71,"Nuh"),
            (72,"Jinn"),
            (73,"Muzzammil"),
            (74,"Muddathir"),
            (75,"Qiyamah"),
            (76,"Insan"),
            (77,"Mursalat"),
            (78,"Naba"),
            (79,"Naziat"),
            (80,"Abasa"),
            (81,"Takwir"),
            (82,"Infitar"),
            (83,"Mutaffifin"),
            (84,"Inshiqaq"),
            (85,"Buruj"),
            (86,"Tariq"),
            (87,"Ala"),
            (88,"Ghashiya"),
            (89,"Fajr"),
            (90,"Balad"),
            (91,"Shams"),
            (92,"Layl"),
            (93,"Duha"),
            (94,"Sharh"),
            (95,"Tin"),
            (96,"Alaq"),
            (97,"Qadr"),
            (98,"Bayyina"),
            (99,"Zalzala"),
            (100,"Adiyat"),
            (101,"Qaria"),
            (102,"Takathur"),
            (103,"Asr"),
            (104,"Humaza"),
            (105,"Fil"),
            (106,"Quraysh"),
            (107,"Maun"),
            (108,"Kawthar"),
            (109,"Kafirun"),
            (110,"Nasr"),
            (111,"Masad"),
            (112,"Ikhlas"),
            (113,"Falaq"),
            (114,"Nas"),
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

