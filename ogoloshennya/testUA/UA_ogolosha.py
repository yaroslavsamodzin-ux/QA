import requests
from bs4 import BeautifulSoup
import time
import csv

# ======== СПИСОК МАРОК ========
brands = [
    "acura","alfa-romeo","audi","bentley","bmw","brilliance","buick","byd","cadillac",
    "chery","chevrolet","chrysler","citroen","dacia","daewoo","daihatsu","dodge",
    "ferrari","fiat","ford","geely","gmc","great-wall","honda","hummer","hyundai",
    "infiniti","isuzu","jac","jaguar","jeep","kia","lancia","land-rover","lexus","lifan",
    "lincoln","maybach","mazda","mercedes-benz","mercury","mini","mitsubishi","nissan",
    "opel","peugeot","pontiac","porsche","renault","rolls-royce","rover","saab","seat",
    "skoda","smart","ssang-yong","subaru","suzuki","tesla","toyota","volkswagen","volvo",
    "moskvich-azlk","zaz","gaz","vaz","uaz","drugaja-model"
]

BASE_URL = "https://ogolosha.ua/transport/legkovye-avtomobili/"

headers = {"User-Agent": "Mozilla/5.0"}

results = []

# ======== ПРОХОДИМО ПО ВСІХ МАРКАХ ========
for brand in brands:
    url = f"{BASE_URL}{brand}/"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Знаходимо кількість
        strong = soup.select_one("strong.total-ads span.blue-span")
        count = strong.text.strip() if strong else "0"

        results.append((brand, count))
        print(f"{brand}: {count}")

    except Exception as e:
        print(f"{brand} -> ERROR: {e}")
        results.append((brand, "error"))

    time.sleep(1)  # щоб не блокували


# ======== ЗБЕРІГАЄМО У ФАЙЛ ========
outfile = "vuvod/UA_ogolosha.csv"

with open(outfile, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["Brand", "Count"])   # заголовок
    writer.writerows(results)              # усі пари (brand, count)

print(f"\n✅ Готово! Результати збережено у {outfile} ({len(results)} рядків)")
