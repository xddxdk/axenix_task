import requests
from datetime import datetime
from modules.location import get_city_coords
from langchain.tools import Tool

def get_weather(city_name: str, date: str) -> str:
    """
    Получает погоду в городе на указанную дату (в формате YYYY-MM-DD).
    Возвращает строку: "Температура в этот день была ...°C ночью и ... °C днем."
    """
    # Проверка: дата не в будущем
    today = datetime.today().date()
    query_date = datetime.strptime(date, "%Y-%m-%d").date()
    if query_date >= today:
        return "Я могу подсказать только погоду в прошлом. Выберите прошедшую дату."

    # Получение координат
    coords = get_city_coords(city_name)
    if not coords:
        return f"Извините, я не смог определить город '{city_name}'."

    lat, lon = coords
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date,
        "end_date": date,
        "daily": "temperature_2m_min,temperature_2m_max",
        "timezone": "auto"
    }

    resp = requests.get(url, params=params)
    data = resp.json()

    temps_min = data.get("daily", {}).get("temperature_2m_min", [None])[0]
    temps_max = data.get("daily", {}).get("temperature_2m_max", [None])[0]

    if temps_min is None or temps_max is None:
        return "Не удалось получить данные о погоде на эту дату."

    return f"Температура в этот день была {temps_min:.1f}°C ночью и {temps_max:.1f}°C днем."

# Функция-обертка для Langhain Tool
def get_weather_single_arg(query: str) -> str:
    """Парсит строку вида 'Город, YYYY-MM-DD' и вызывает get_weather()"""
    try:
        city_name, date = query.split(", ")
        return get_weather(city_name, date)
    except:
        return "Ошибка: используйте формат 'Город, YYYY-MM-DD'"
    
# Создаем инструмент
get_weather_tool = Tool(
    name="get_weather",
    func=get_weather_single_arg,
    description=
    """
    Определяет погоду в конкретном городе в конкретную дату (в прошлом). 
    Формат ввода: 'Город, YYYY-MM-DD'
    Название города в функцию подается обязательно на русском.
    """
)