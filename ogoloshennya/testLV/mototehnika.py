# -*- coding: utf-8 -*-
"""
Збирає Brand + Count зі сторінок rus.mototehnika.ee і пише у results_mototehnika.csv
Працює через реальний браузер (Playwright), щоб обійти захист.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeoutError
import csv
import re

# >>> СЮДИ ДОДАВАЙ СВОЇ URL-и (зі встановленою маркою у фільтрі) <<<
URLS = [
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1096&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA"
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=465&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=197&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=469&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=858&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=731&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1638&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1659&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1307&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1711&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=234&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=441&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=890&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1654&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=4&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1642&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=438&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1708&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=517&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1323&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=633&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=20&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=550&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=724&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=416&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=437&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=359&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1400&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1661&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1216&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=462&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1121&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1322&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=49&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1145&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=434&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=345&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1159&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1157&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=443&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=300&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=301&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=57&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1541&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=347&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1675&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=61&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1200&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=303&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1370&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=377&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1161&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1601&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=475&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=575&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1467&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1100&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=899&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=404&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1077&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1627&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=477&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1754&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1751&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1513&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1389&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=138&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1105&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1187&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1542&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=16&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=257&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=447&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=109&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1683&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1682&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=190&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1431&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=901&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=430&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=659&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1104&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1676&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1628&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=439&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1660&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1404&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1444&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1596&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=41&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1282&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1629&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=570&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1147&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=225&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1439&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=717&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1706&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=442&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=509&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1750&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=585&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1674&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1721&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=33&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
    "https://rus.mototehnika.ee/kasutatud/nimekiri.php?bn=2&a=109&aj=&b=1643&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA",
]

# Селектори під mototehnika
SEL_COUNT = "div.current-range span.label strong"
SEL_BRAND_OPT = 'select[id*="searchParam-cmm-1-make"] option[selected]'
SEL_BRAND_CHIP = '#item-searchParam-cmm-1-make .search-filter'
SEL_BRAND_SPAN = 'span.search-filter'   # як запасний варіант

def clean_brand(s: str) -> str:
    if not s:
        return ""
    s = " ".join(s.replace("\xa0"," ").split())
    s = re.sub(r"\s*легков(ой|ые)\s+автомобил(ь|и)\s*$", "", s, flags=re.I).strip()
    return s

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
        elif page.locator(SEL_BRAND_SPAN).count():
            brand = page.locator(SEL_BRAND_SPAN).first.inner_text().strip()
        elif page.locator(SEL_BRAND_CHIP).count():
            brand = page.locator(SEL_BRAND_CHIP).first.inner_text().strip()
        else:
            brand = re.split(r"[-–|•()]", (page.title() or ""))[0].strip()

        brand = clean_brand(brand)
        if not brand or brand.lower() in ["легковой автомобиль", "все типы"]:
            continue

        print(f"{brand} {count}")
        rows.append([brand, count])

    browser.close()

with open("vuvod/LV_mototehnika.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["Brand", "Count"])
    w.writerows(rows)

print("\n✅ Дані збережено у vuvod/LV_mototehnika.csv")
