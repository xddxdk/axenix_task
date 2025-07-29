import requests
import os
import json
from dotenv import load_dotenv
from langchain.agents import Tool

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Системный промпт
system_prompt = """
Ты — парсер пользовательских запросов.
Твоя задача — извлекать параметры из текста и возвращать результат строго в формате JSON.

Формат:
{
    "action": "get_weather" или "get_time", иначе null,
    "date": дата в формате YYYY-MM-DD или null, если не указана,
    "location": город как строка (только на русском языке) или null, если не указан
}

Правила:
Если вопрос про время - укажи "get_time", если про погоду - "get_weather", иначе null.
Location может быть только городом, селом, насленным пунктом и т.д.
Если пользователь не указал дату или город, заполни их значением null.
Если в action ты указал get_time, то в date и location должны быть null.
Если вопрос не про время или погоду, то везде ставь null.
Не добавляй пояснений. Отвечай только JSON. Не используй markdown.

Примеры:
Вопрос: "Какая погода была в Казани 25 октября 2024 года?"
Ответ: {
    "action": "get_weather",
    "date": "2024-10-25",
    "location": "Казань"
}

Вопрос: "Какая сейчас погода?"
Ответ: {
    "action": "get_weather",
    "date": null,
    "location": null
}

Вопрос: "Сколько будет 5+5?"
Ответ: {
    "action": null,
    "date": null,
    "location": null
}

Вопрос: "Сколько время?"
Ответ: {
    "action": "get_time",
    "date": null,
    "location": null
}
"""

# Функция парсера
def parse_user_query(user_input: str) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://localhost",  # для OpenRouter
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "qwen/qwen3-8b:free",  # быстрая и дешёвая для таких задач
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.1
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )
        
    result = response.json()
    content = result["choices"][0]["message"]["content"].strip()

    try:
        parsed = json.loads(content)
    except Exception as e:
        raise ValueError(f"Ошибка парсинга JSON: {e}\nОтвет модели:\n{content}")

    return parsed

# Оборачиваем вывод с parse_user_query для LangChain
def parser_tool_func(text: str) -> str:
    result = parse_user_query(text)
    a, d, l = result["action"], result["date"], result["location"]
    if a == "get_weather" and (not d or not l):
        return "Пожалуйста, уточните дату и город."
    if a == "get_time":
        return f"ACTION: get_time | LOCATION: {l or 'null'}"
    if a == "get_weather":
        return f"ACTION: get_weather | LOCATION: {l} | DATE: {d}"
    return "Я могу отвечать только на вопросы о погоде или времени."

# Инициализация Tool
parser_tool = Tool(
    name = "QueryParser",
    func = parser_tool_func,
    description=
    """
    Преобразует подготовленные данные в JSON. JSON содержит "action", "date", "location"
    """
)