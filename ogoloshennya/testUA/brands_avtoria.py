import requests
import json

def fetch_marks():
    url = "https://auto.ria.com/api/categories/1/marks/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print("❌ Помилка при запиті:", e)
        return

    # Перевіряємо структуру відповіді
    if not isinstance(data, list):
        print("❌ Неочікуваний формат відповіді")
        return

    # Записуємо в txt
    with open("autoria_marks.txt", "w", encoding="utf-8") as f:
        for item in data:
            mark_id = item.get("value")
            mark_name = item.get("name")
            if mark_id and mark_name:
                f.write(f"{mark_id} ; {mark_name}\n")

    print(f"✅ Успішно збережено {len(data)} марок у 'autoria_marks.txt'")

if __name__ == "__main__":
    fetch_marks()
