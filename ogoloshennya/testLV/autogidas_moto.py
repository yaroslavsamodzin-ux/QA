# -*- coding: utf-8 -*-
# autogidas_batch.py
# Збирає Brand + Count зі сторінок autogidas.lt і пише у autogidas_brands_counts.csv

import re
import csv
import time
from pathlib import Path
from typing import Tuple, Optional, List
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── НАЛАШТУВАННЯ ───────────────────────────────────────────────────────────────
URLS: List[str] = [
    # <<< СЮДИ ДОДАВАЙ СТОРІНКИ >>>
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Yamaha&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Honda&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Kawasaki&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Kita&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Suzuki&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Harley-Davidson&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=CFMOTO&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Piaggio&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Segway&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Aprilia&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=ABM&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=AGM&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=ATM&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=ATV&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Adly&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Aodes&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Apollo&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=BMW&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=BRIXTON&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Barton&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Bashan&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Benelli&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Beta&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Blata&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Buell&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=CPI&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Cagiva&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Can-Am&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=City-bike&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Cooper&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Daelim&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Delta&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Derbi&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Dinli&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Dniepr&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Ducati&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=E-RIDE&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Electron&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Gas+Gas&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Gilera&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Goes&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Hummer&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Husqvarna&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Hyosung&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Indian&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Izh&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Jawa&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Jincheng&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Jinlun&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Junak&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=KMT+MOTORS&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=KSR&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=KTM&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Kayo&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Keeway&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Kinroad&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Kymco&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Lexmoto&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Lifan&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Linhai&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=MBP&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=MTT&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=MZ&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Magpower&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Malaguti&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Masai&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Mash&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Mikilon&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Mosca&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Moto+Guzzi&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Moto+Morini&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Motowell&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Motron&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=NECO&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=NSU&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=ODES&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Orcal&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Pegasus&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Peugeot&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Pitmoto&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Polaris&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=QJMOTOR&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Qingqi&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Quad&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Rieju&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Royal+Enfield&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Ryga&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=SMC&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=SWM&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=SYM&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Sachs&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Sherco&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Ski+Doo&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Stels&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Super+SOCO&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=TGB&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=TNT&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Triton&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Triumph&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Ural&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=VOGE&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Vespa&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Victory&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=X-Moto&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Xstar&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=ZNEN&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Zeeho&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Zero&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
    "https://autogidas.lt/ru/skelbimai/motociklai/?f_1%5B0%5D=Zongshen&f_model_14%5B0%5D=&f_215=&f_216=&f_41=&f_42=&f_133=&f_134=&f_376=",
]
CSV_PATH = "LV_autogidas_moto.csv"
HEADLESS = True           # якщо антибот заважає — постав False
REQUEST_DELAY = 0.0       # пауза між URL, щоб швидше (можеш 0.0..1.0)
MAX_TIMEOUT = 60_000      # мс
INCLUDE_URL = False       # True → додасть у CSV третю колонку URL
QUIET = False              # True → мінімальний вивід у консоль
# ───────────────────────────────────────────────────────────────────────────────

def accept_cookies(page) -> None:
    sels = [
        "#onetrust-accept-btn-handler",
        "button:has-text('Sutinku')", "button:has-text('Piekrītu')",
        "button:has-text('Соглас')",  "button:has-text('Accept')",
        "button:has-text('OK')",
    ]
    for s in sels:
        try:
            loc = page.locator(s).first
            if loc.is_visible():
                loc.click()
                break
        except Exception:
            pass

def digits_int(text: Optional[str]) -> int:
    m = re.search(r"\d[\d\s]*", text or "")
    return int(m.group(0).replace(" ", "")) if m else 0

def extract_brand_from_h1(page) -> str:
    # прибираємо (2973) у вкладеному <span class="ads-total"> з H1
    page.evaluate("""() => {
        document.querySelectorAll('h1.title span.ads-total').forEach(s=>s.remove());
    }""")
    t = (page.locator("h1.title").first.text_content() or "").strip()
    # відсікаємо службові слова
    return re.split(r"\s+(Мотоциклы|Automobiliai|Авто)\b", t)[0].strip()

def process_url(page, url: str) -> Tuple[str, int]:
    # швидше, ніж networkidle
    page.goto(url, wait_until="domcontentloaded", timeout=MAX_TIMEOUT)
    accept_cookies(page)

    # чекаємо не 60 сек, а максимум 5
    page.wait_for_selector("h1.title", timeout=5000)

    # ads-total може бути невидимий — чекаємо появу в DOM
    ads = page.locator("span.ads-total").first
    ads.wait_for(state="attached", timeout=5000)
    count = digits_int(ads.text_content())

    # бренд з чіпа активного фільтра; якщо нема — з H1
    brand = (page.locator("#active-filters-wrapper .filter-value")
             .first.text_content() or "").strip()
    if not brand:
        brand = extract_brand_from_h1(page)

    return brand, count

def main():
    rows: List[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context(
            locale="ru-RU",
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"),
            viewport={"width": 1366, "height": 900},
            ignore_https_errors=True,
        )
        page = ctx.new_page()

        for url in URLS:
            try:
                brand, count = process_url(page, url)
                row = {"Brand": brand, "Count": count}
                if INCLUDE_URL:
                    row["URL"] = url
                rows.append(row)
                if not QUIET:
                    # короткий вивід; або прибери цей print, якщо треба повна тиша
                    print(f"{brand} {count}" + (f";{url}" if INCLUDE_URL else ""))
            except PWTimeout:
                # збережемо артефакти для дебагу конкретного URL
                Path("debug.html").write_text(page.content(), encoding="utf-8")
                page.screenshot(path="debug.png", full_page=True)
                if not QUIET:
                    print("TIMEOUT → збережено debug.html / debug.png")
            except Exception as e:
                if not QUIET:
                    print(f"ERROR: {e}")

            time.sleep(REQUEST_DELAY)

        browser.close()

    # запис у CSV (крапка з комою)
    fieldnames = ["Brand", "Count"] + (["URL"] if INCLUDE_URL else [])
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    if not QUIET:
        print(f"\n✅ Дані збережено у {CSV_PATH}")

if __name__ == "__main__":
    main()
