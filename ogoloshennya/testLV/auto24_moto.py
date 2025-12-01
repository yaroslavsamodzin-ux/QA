# -*- coding: utf-8 -*-
"""
Збирає Brand + Count зі сторінок rus.auto24.lv і пише у results_auto24.csv
Працює через реальний браузер (Playwright), щоб обійти Cloudflare/anti-bot.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeoutError
import csv
import re
from time import sleep

URLS = [
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1096&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1230&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=465&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=197&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=469&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=858&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=731&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1638&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1307&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1711&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1711&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=441&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=890&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1654&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=4&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1642&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=438&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1708&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=517&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1323&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=633&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=20&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=550&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=724&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=416&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=437&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=359&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1400&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1661&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1216&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=462&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1121&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1322&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=49&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1145&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=345&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1159&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1157&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=443&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=300&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=300&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=57&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1541&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=347&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1675&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=61&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1200&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=303&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1370&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=377&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1161&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1601&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=475&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=575&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1467&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1125&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1100&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=899&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=404&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1077&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1627&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=477&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1754&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1751&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1513&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1389&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=138&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1105&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1187&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1542&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=16&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=257&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=447&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=109&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1683&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1682&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=190&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1431&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=901&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=430&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=659&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1104&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1676&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1628&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=439&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1660&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1404&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1444&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1596&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=41&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1282&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1629&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=570&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1147&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=225&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1439&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1440&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=717&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1706&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=442&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=509&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1750&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=585&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1674&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1721&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=33&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.auto24.lv/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1643&ab=0&ae=1&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
]

SEL_COUNT = "div.current-range span.label strong"
SEL_BRAND_OPT = 'select[id*="searchParam-cmn-1-make"] option[selected]'
SEL_BRAND_CHIP = '#item-searchParam-cmn-1-make .search-filter'

def clean_brand(s: str) -> str:
    if not s:
        return ""
    # нормалізуємо пробіли
    s = " ".join(s.replace("\xa0", " ").split())

    # прибираємо "мототехника"/"мототехніка" як суфікс у кінці або окреме слово
    s = re.sub(r"\s*\(?\s*мототехник[аи]\s*\)?\s*$", "", s, flags=re.I)  # наприкінці
    s = re.sub(r"\bмототехник[аи]\b", "", s, flags=re.I)                 # будь-де

    # фінальна зачистка пробілів
    return s.strip()


def digits(s: str) -> str:
    m = re.search(r"\d+", s or "")
    return m.group(0) if m else "?"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36")
    )

    rows = []
    for url in URLS:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        if "Attention Required" in page.content():
            print("Марка: ? | Кількість: ? (Cloudflare)")
            continue

        # Count
        count = digits(page.locator(SEL_COUNT).first.inner_text()) if page.locator(SEL_COUNT).count() else "?"

        # Brand
        if page.locator(SEL_BRAND_OPT).count():
            brand = page.locator(SEL_BRAND_OPT).first.inner_text().strip()
        elif page.locator(SEL_BRAND_CHIP).count():
            brand = page.locator(SEL_BRAND_CHIP).first.inner_text().strip()
        else:
            brand = re.split(r"[-–|•()]", (page.title() or ""))[0].strip()
        brand = clean_brand(brand)
        if not brand:  # пропускаємо “Легковой автомобиль”
            continue

        print(f"{brand} {count}")
        rows.append([brand, count])

    browser.close()

with open("LV_auto24_moto.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Brand", "Count"])
            w.writerows(rows)

print("\n✅ Дані збережено у LV_auto24_moto.csv")