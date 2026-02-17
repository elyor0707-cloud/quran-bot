import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        current_surah INTEGER DEFAULT 1,
        current_ayah INTEGER DEFAULT 1,
        block_start INTEGER DEFAULT 1,
        block_end INTEGER DEFAULT 10,
        block_passed INTEGER DEFAULT 0,
        total_score INTEGER DEFAULT 0,
        premium INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memorization_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        surah INTEGER,
        start_ayah INTEGER,
        end_ayah INTEGER,
        passed INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voice_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        surah INTEGER,
        ayah INTEGER,
        accuracy REAL,
        feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()


def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return get_user(user_id)

    return user


def update_user(user_id, field, value):
    cursor.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
    conn.commit()
