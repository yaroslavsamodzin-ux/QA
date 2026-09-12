# qa-toolkit

Набір інструментів під щоденне ручне тестування. Кожен пункт має слеш-команду —
Claude сам знає, коли її брати, але можна викликати й напряму.

| Команда | Що робить |
|---|---|
| `/qa-android` | тестування на реальному Android-телефоні |
| `/qa-watch` | стежить за консоллю й мережею, поки ти тестуєш руками |
| `/qa-bug` | збирає готовий баг-репорт під Jira |
| `/qa-checklist` | чекліст із задачі Jira як інтерактивна сторінка |
| `/qa-run` | прогнати чекліст і скласти звіт про тестування |
| `/qa-responsive` | верстка на всіх розширеннях + візуальна регресія |
| `/qa-testdata` | граничні дані й автопрогін форм |
| `/qa-trace` | звʼязує UI з логами Kibana та відповідями API |

---

## Швидкий старт

### Верстка на всіх ширинах

```bash
node qa-toolkit/responsive/responsive.js https://стенд/сторінка
```

Дає `report.md` зі списком проблем і скріншоти кожної ширини.
Ширини налаштовуються у `responsive/viewports.json`.

### Візуальна регресія

```bash
set QA_URLS=https://стенд/a,https://стенд/b
npx playwright test --config qa-toolkit/visual/playwright.config.js --update-snapshots  # еталон
npx playwright test --config qa-toolkit/visual/playwright.config.js                      # після деплою
npx playwright show-report qa-toolkit/visual/report
```

### Прогін поля через граничні значення

```bash
node qa-toolkit/testdata/autofill.js --list
node qa-toolkit/testdata/autofill.js https://стенд/reg --field "#email" --set email --submit "button[type=submit]"
```

### Android

```powershell
powershell -ExecutionPolicy Bypass -File qa-toolkit\android\setup.ps1   # один раз
powershell -ExecutionPolicy Bypass -File qa-toolkit\android\adb.ps1 devices
powershell -ExecutionPolicy Bypass -File qa-toolkit\android\adb.ps1 open https://стенд
powershell -ExecutionPolicy Bypass -File qa-toolkit\android\adb.ps1 audit
```

---

## Структура

```
qa-toolkit/
  responsive/
    responsive.js      аудит верстки на N ширинах
    viewports.json     набори розширень
  visual/
    visual.spec.js     візуальна регресія
    playwright.config.js
    baseline/          еталонні скріншоти (комітяться)
  testdata/
    payloads.json      граничні значення з очікуваною реакцією
    autofill.js        автопрогін поля через набір
  android/
    setup.ps1          встановлення adb
    adb.ps1            команди під тестування
  bug/out/             скріншоти й GIF до баг-репортів
```

Згенеровані папки (`report/`, `out/`, `test-results/`) у git не потрапляють —
див. `qa-toolkit/.gitignore`.

---

## Вимоги

- **Node + Playwright** — уже в репо (`@playwright/test` 1.57.0). Браузери:
  `npx playwright install chromium`, якщо скрипт скаржиться на відсутній executable.
- **adb** — ставиться скриптом `android/setup.ps1` у `%LOCALAPPDATA%\platform-tools`,
  без прав адміністратора і без root на телефоні.
- **newman** — уже встановлений глобально, для колекцій із `PostmanCollection/`.
- **VPN** — обовʼязковий для Kibana.

## Особливості середовища

Скрипти `.ps1` мають бути збережені **у UTF-8 з BOM** — Windows PowerShell 5.1
інакше читає кирилицю як ANSI і падає на парсингу. Якщо редагуєш їх і зʼявились
`ParserError` з абракадаброю — причина саме в цьому:

```powershell
$p = "qa-toolkit\android\adb.ps1"
$c = Get-Content -Raw -Encoding UTF8 $p
[System.IO.File]::WriteAllText($p, $c, (New-Object System.Text.UTF8Encoding $true))
```
