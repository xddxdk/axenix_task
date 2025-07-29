import requests
from modules.cache import get_cached_coords, cache_coords

def get_city_coords(city_name: str):
    """Получить координаты города через кэш или API"""
    cached = get_cached_coords(city_name)
    if cached:
        return cached

    url = "https://geocoding-api.open-meteo.com/v1/search"
    response = requests.get(url, params={"name": city_name, "count": 1, "language": "ru", "format": "json"})

    data = response.json()
    results = data.get("results")
    if not results:
        return None

    lat = results[0]["latitude"]
    lon = results[0]["longitude"]

    # кешируем
    cache_coords(city_name, lat, lon)
    return lat, lon