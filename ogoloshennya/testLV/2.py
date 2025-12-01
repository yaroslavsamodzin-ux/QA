import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import random
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Налаштування ---
OUTPUT_DIR = Path("vuvod")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "LV_autobonus_avto.csv"

# Якщо у вас є легальний проксі (комерційний, дозволений провайдером),
# ви можете передати його як словник у функцію fetch_all (див. приклад нижче).
# НЕ використовуйте для обходу блокувань або іншої неправомірної активності.
# proxies = {"http": "http://user:pass@proxy.example:3128", "https": "http://..."}
proxies = None  # <-- залиште None або вставте тут словник з проксі

# Список User-Agent для "природнішого" вигляду запитів (використовуйте відповідально)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/16.4 Safari/605.1.15",
]

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,uk;q=0.8,en-US;q=0.7,en;q=0.6",
    # 'Referer' можна задати, якщо потрібно
}

# Retry strategy
RETRY_STRATEGY = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)

# --- URLs (ваш список) ---
urls = [
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&ma=792&doSearch=1",   
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&1&ma=791&doSearch=1",    
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&ma=795&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=790&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1063&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1273&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=789&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=788&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=787&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=786&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1563&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=785&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=784&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=783&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1942&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=782&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1232&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=781&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=780&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=779&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1941&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=866&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=778&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=777&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=776&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=775&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1937&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=774&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=773&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1541&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=772&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=728&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=771&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=770&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=769&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=768&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=767&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1542&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=766&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=765&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=764&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=762&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=761&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=760&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1546&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=759&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=758&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=756&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1062&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=755&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=754&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=753&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=752&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1543&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=751&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=750&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1938&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=749&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=748&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=747&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1696&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1940&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=746&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=745&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=744&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=743&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=742&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=741&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=740&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=739&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=738&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=794&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=737&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1162&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=736&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1251&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=735&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=734&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1636&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=727&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=733&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=732&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1274&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1544&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=731&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1545&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1231&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=730&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=729&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1230&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=763&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=796&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1160&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1255&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1229&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
    "https://www.autobonus.lt/avto/poisk/?search=1&cat=1&collapsrch=1&ussearch=&saveusersearch=1&ma=1169&mo=-1&bo=-1&fu=-1&ge=-1&p1=&p2=&y1=-1&y2=-1&doSearch=1",
]

def make_session(proxies=None):
    """Повертає requests.Session з підключеним Retry/Adapter та опціональними проксі."""
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=RETRY_STRATEGY)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    if proxies:
        session.proxies.update(proxies)
    return session

def fetch_page(session, url, timeout=15):
    """Завантажує сторінку з базовими заголовками і обробляє помилки."""
    headers = DEFAULT_HEADERS.copy()
    headers["User-Agent"] = random.choice(USER_AGENTS)
    try:
        resp = session.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.RequestException as e:
        # Логування помилок — можна писати у файл або друкувати
        print(f"[ERROR] {url} -> {e}")
        return None

def parse_brand_count(html):
    """Парсить бренд (h1) і кількість (span.result-count). Повертає (brand, count)."""
    if not html:
        return "?", "?"
    soup = BeautifulSoup(html, "html.parser")

    # кількість
    count_el = soup.select_one("span.result-count")
    count = count_el.get_text(strip=True).strip("()") if count_el else "?"

    # бренд з <h1>, очищений від "Легковые автомобили" (або інших підрядків)
    h1_el = soup.select_one("h1")
    brand = h1_el.get_text(strip=True) if h1_el else "?"
    brand = brand.replace("Легковые автомобили", "").strip()
    return brand, count

def fetch_all(urls, proxies=None, min_delay=1.0, max_delay=3.0):
    session = make_session(proxies=proxies)
    results = []
    for i, url in enumerate(urls, start=1):
        print(f"[{i}/{len(urls)}] Fetching: {url}")
        html = fetch_page(session, url)
        brand, count = parse_brand_count(html)
        print(f"  -> {brand} | {count}")
        results.append([brand, count])

        # Рандомна пауза щоб зменшити навантаження
        sleep_time = random.uniform(min_delay, max_delay)
        time.sleep(sleep_time)

    return results

def save_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Brand", "Count"])
        writer.writerows(rows)
    print(f"\n✅ Дані збережено у {path}")

if __name__ == "__main__":
    # Якщо хочете використовувати проксі — передайте сюди словник proxies (див. вище)
    rows = fetch_all(urls, proxies=proxies, min_delay=1.5, max_delay=4.0)
    save_csv(rows, OUTPUT_FILE)
