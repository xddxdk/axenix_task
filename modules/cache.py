import sqlite3

DB_PATH = 'city_cache.db'

# Функция создания БД
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS city_cache (
            city_id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT(50),
            latitude REAL(8),
            longitude REAL(8)
        )
    ''')
    conn.commit()
    conn.close()

# Функция извлечения координат
def get_cached_coords(city_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT latitude, longitude FROM city_cache WHERE city_name = ?', (city_name.lower(),))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result  # (lat, lon)
    return None

# Функция внесения данных
def cache_coords(city_name, lat, lon):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO city_cache (city_name, latitude, longitude) VALUES (?, ?, ?)',
        (city_name.lower(), lat, lon)
    )
    conn.commit()
    conn.close()