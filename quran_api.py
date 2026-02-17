import requests

BASE_URL = "https://api.alquran.cloud/v1"

def get_surahs():
    r = requests.get(f"{BASE_URL}/surah").json()
    return r["data"]

def get_ayah(surah, ayah):
    r = requests.get(
    f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/editions/quran-tajweed,uz.sodik",
    timeout=10
).json()

    arabic = r['data'][0]['text']
    uzbek = r['data'][1]['text']
    surah_name = r['data'][0]['surah']['englishName']
    total_ayahs = r['data'][0]['surah']['numberOfAyahs']

    return {
        "arabic": arabic,
        "uzbek": uzbek,
        "surah_name": surah_name,
        "total_ayahs": total_ayahs
    }
