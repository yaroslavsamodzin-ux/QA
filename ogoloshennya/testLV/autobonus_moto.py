import requests
from bs4 import BeautifulSoup
import csv

urls = [
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=596&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",   
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=1359&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=601&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=870&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=1272&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=1115&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=1053&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=608&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=609&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=610&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C,",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=616&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=620&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=622&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=624&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=626&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=628&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=1270&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=1265&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=635&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=877&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=879&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=880&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=648&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=652&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=886&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=656&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=659&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
    "https://www.autobonus.lt/moto/poisk/?search=1&cat=3&ord=date&asc=desc&collapsrch=1&ussearch=&saveusersearch=1&ma=653&mo=-1&bo=-1&cool=-1&v1=-1&v2=-1&da=-1&cnt=&ci=&p1=&p2=&y1=-1&y2=-1&ord=date&asc=desc&doSearch=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C",
]

results = []

for url in urls:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    # кількість
    count_el = soup.select_one("span.result-count")
    count = count_el.get_text(strip=True).strip("()") if count_el else "?"

    
    # бренд з <h1>, очищений від "Легковые автомобили"
    h1_el = soup.select_one("h1")
    brand = h1_el.get_text(strip=True) if h1_el else "?"
    brand = brand.replace("Мотоциклы", "").strip()
    
    print(f"{brand} {count}")
    results.append([brand, count])


# збереження у CSV
with open("LV_autobonus_moto.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["Brand", "Count"])  # заголовки
    writer.writerows(results)

print("\n✅ Дані збережено у LV_autobonus_moto.csv")
