import os
from datetime import datetime, timedelta
import requests
from modules.location import get_city_coords
from dotenv import load_dotenv
from langchain.agents import Tool

# Загрузка ключа для парсера временных зон
load_dotenv()
TIME_KEY = os.getenv("TIME_KEY")

def get_current_time(city_name: str = None) -> str:
    """
    Функция для получения времени.
    """
    # Если город не указан
    if not city_name:
        now = datetime.now()
        return f"Сейчас {now.strftime('%H:%M:%S')} (по системному времени)"

    # Получение координат
    coords = get_city_coords(city_name)
    if not coords:
        return f"Извините, я не смог определить город '{city_name}'."

    lat, lon = coords

    # Получаем смещение временной зоны
    response = requests.get(
        "http://api.timezonedb.com/v2.1/get-time-zone",
        params={"key": {TIME_KEY}, "format": "json", "by": "position", "lat": lat, "lng": lon}
    )
    
    if response.status_code != 200:
        return "Произошла ошибка при получении временной зоны."

    data = response.json()
    offset_seconds = data.get("gmtOffset", 0)
    now_utc = datetime.utcnow()
    city_time = now_utc + timedelta(seconds=offset_seconds)

    return f"Сейчас {city_time.strftime('%H:%M:%S')} в городе {city_name}"

# Инициализация Tool (для LangChainBot)
get_time_tool = Tool(
    name = "get_time",
    func = get_current_time,
    description=
    """
    Определяет текущее время. Функция имеет вид: get_current_time(city_name: str = None)
    Данные на вход: пустая строка, если город не указан. Или название города, если город указан.
    Название города вводить обязательно на русском!.
    """
)