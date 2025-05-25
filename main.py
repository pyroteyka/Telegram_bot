import telebot
from telebot import types
import json
import random
import requests
from bs4 import BeautifulSoup
from config import *

bot = telebot.TeleBot(TOKEN)

# 🔹 Заголовки для сайта
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# 🔹 Загрузка категорий
def load_recipes():
    with open("recipes.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["recipes"]

# 🔹 Получение всех ссылок на рецепты из категории
def get_recipes_from_category(category_url):
    try:
        response = requests.get(category_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        recipe_links = []
        for link in links:
            href = link["href"]
            if href.startswith("/recepty/") and len(href) > 20:
                full_url = "https://eda.ru" + href
                recipe_links.append(full_url)

        return list(set(recipe_links))
    except Exception as e:
        print(f"⚠️ Ошибка при получении ссылок из категории: {e}")
        return []

# 🔹 Получение одного конкретного рецепта по ссылке
def get_recipe_details(recipe_url):
    try:
        response = requests.get(recipe_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        name = soup.find("h1").get_text(strip=True)
        ingredients = [item.get_text(strip=True) for item in soup.find_all("span", class_="emotion-15im4d2")]
        instructions = " ".join([step.get_text(strip=True) for step in soup.find_all("p", class_="emotion-19d62wq")])

        return {
            "name": name,
            "url": recipe_url,
            "ingredients": ingredients,
            "instructions": instructions
        }
    except Exception as e:
        print(f"❌ Ошибка при парсинге рецепта: {e}")
        return None

# 🔹 Стартовая команда
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    recipes = load_recipes()

    for recipe in recipes:
        markup.add(types.KeyboardButton(recipe["name"]))

    bot.send_message(message.chat.id, "👋 Привет! Выбери категорию рецепта:", reply_markup=markup)

# 🔹 Обработка выбора категории
@bot.message_handler(content_types=['text'])
def handle_text(message):
    categories = load_recipes()
    selected = next((cat for cat in categories if cat["name"] == message.text), None)

    if not selected:
        bot.send_message(message.chat.id, "❌ Категория не найдена. Пожалуйста, выбери из списка.")
        return

    recipe_links = get_recipes_from_category(selected["url"])
    if not recipe_links:
        bot.send_message(message.chat.id, "⚠️ Не удалось найти рецепты в этой категории.")
        return

    chosen_url = random.choice(recipe_links)
    recipe = get_recipe_details(chosen_url)

    if not recipe:
        bot.send_message(message.chat.id, "⚠️ Не удалось загрузить рецепт. Попробуй ещё раз.")
        return

    # 🔹 Формирование ответа
    recipe_text = f"🍽 *{recipe['name']}*\n\n🔗 [Ссылка на рецепт]({recipe['url']})\n\n🍴 *Ингредиенты:*\n"
    recipe_text += "\n".join([f"- {ing}" for ing in recipe["ingredients"]])
    recipe_text += f"\n\n👨‍🍳 *Приготовление:*\n{recipe['instructions']}"

    bot.send_message(message.chat.id, recipe_text, parse_mode="Markdown", disable_web_page_preview=True)

# 🔹 Запуск бота
bot.polling(none_stop=True)