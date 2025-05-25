import requests
from bs4 import BeautifulSoup
import json
import random
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def load_categories():
    with open("recipes.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["recipes"]  # [{'name': ..., 'url': ...}, ...]

def get_recipes_from_category(category_url):
    response = requests.get(category_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)

    recipe_links = []
    for link in links:
        href = link["href"]
        if href.startswith("/recepty/") and len(href) > 20:
            recipe_links.append("https://eda.ru" + href)

    return list(set(recipe_links))

def get_recipe_details(recipe_url):
    try:
        response = requests.get(recipe_url, headers=HEADERS)
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
        print(f"❌ Ошибка при парсинге {recipe_url}: {e}")
        return None

def main():
    final_recipes = []
    categories = load_categories()

    for category in categories:
        print(f"\n🔎 Категория: {category['name']}")
        links = get_recipes_from_category(category["url"])

        if not links:
            print("⚠️ Не найдено рецептов в категории.")
            continue

        random_url = random.choice(links)
        print(f"📥 Случайный рецепт: {random_url}")

        recipe = get_recipe_details(random_url)
        if recipe:
            final_recipes.append(recipe)
            print(f"✅ Добавлен: {recipe['name']}")
            time.sleep(random.uniform(1.0, 2.0))  # пауза для вежливости
        else:
            print("⚠️ Не удалось распарсить рецепт.")

    with open("parsed_recipes.json", "w", encoding="utf-8") as f:
        json.dump({"recipes": final_recipes}, f, ensure_ascii=False, indent=4)

    print(f"\n🍽 Готово! Сохранено рецептов: {len(final_recipes)}")

if __name__ == "__main__":
    main()
