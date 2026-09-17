# Foxtrot (new CMS) — профіль продукту для QA

Зібрано 2026-09-14 читанням GitLab `git.foxtrot.ua` (група `new-cms-foxtrot/evinent`).
Оновлювати, коли з'являються нові репозиторії, змінюється процес або стенди.

## Що це

Інтернет-магазин **www.foxtrot.com.ua**. Розробляє команда Evinent (пошти
`@evinent.com`, `@foxteam.digital`, `@rencore.com`), код у приватному GitLab
`git.foxtrot.ua`, група `new-cms-foxtrot/evinent` (group ID 121, «проекты команды
Евинент») — 24 репозиторії. Доступ **тільки через VPN**.

## Мапа репозиторіїв

Активність станом на 14.09.2026. ID — project id для API (`/api/v4/projects/<id>/…`).

### Фронт і сайти

| Репо | ID | Що це | Активність |
|---|---|---|---|
| `foxtrot-site` | 274 | сам сайт, ASP.NET Core MVC — головний репозиторій | щодня |
| `foxtrot-macaron` | 282 | Macaron CMS (контент, банери, статті) | місяць тому |
| `foxtrot-brand` | 462 | бренд-сторінки | 2 місяці |
| `foxtrot-faq` | 489 | FAQ | 3 дні |
| `foxtrot-roulette` | 485 | акційна рулетка | 5 днів |
| `foxtrot-seller` | 519 | кабінет продавця | 2 місяці |
| `foxtrot-ai-generator` | 520 | AI-генерація контенту | тиждень |
| `foxtrot-watcher` | 512 | моніторинг | 8 місяців |

### API та бекенд

| Репо | ID | Що це | Активність |
|---|---|---|---|
| `foxtrot-api` | 476 | новий агрегуючий API, живе релізами («Release 2026 09 11») | щодня |
| `foxtrot-common` | 276 | спільна бібліотека кількох API — зміни тут зачіпають Main/Catalog/Exchange | щодня |
| `foxtrot-api-main` | 280 | основний API | щодня |
| `foxtrot-api-catalog` | 277 | каталог | тиждень |
| `foxtrot-api-cms` | 278 | контент з CMS | 2 дні |
| `foxtrot-api-exchange` | 279 | обмін з зовнішніми системами, фіди, залишки | щодня |
| `foxtrot-api-search` | 506 | пошук | 8 місяців |
| `foxtrot-api-products` | 513 | товари | 5 місяців |
| `foxtrot-api-order` | 469 | замовлення | рік |
| `foxtrot-api-delivery` | 457 | доставка | 8 місяців |
| `foxtrot-api-epayments` | 470 | платежі | 7 місяців |
| `foxtrot-api-faq` | 490 | FAQ | 5 днів |
| `foxtrot-api-roulette` | 486 | рулетка | 5 днів |
| `foxtrot-api-mobile` | 388 | API мобілки, гілка `main` | мертвий з 2022 |
| `foxtrot-cron` | 275 | планові задачі | тиждень |
| `evinent.foxtrot` | 227 | старий моноліт, default branch `develop` | 8 місяців |

Default branch скрізь `master`, крім `evinent.foxtrot` (`develop`) і
`foxtrot-api-mobile` (`main`).

## Стек

- **.NET / ASP.NET Core MVC** — Razor Views, ViewComponents, TagHelpers, Filters;
  фронтова збірка в `foxtrot.site/wwwroot`.
- **Redis** — кеш (окремий інстанс під товари), DataProtection, метадані.
- **Elasticsearch** — дані і логи (`LogType: site` / `foxtrot-site`) → це те, що
  видно в Kibana.
- **Kubernetes + Helm + helmfile**, AWS `eu-central-1`, образи в ECR, ingress ALB
  (internal), сервіс на порту **5000**, health-чек **`/health`**.

## Стенди

- **Прод:** https://www.foxtrot.com.ua, статика й фото — https://files.foxtrot.com.ua
- **Дев-стенди динамічні, по розробнику:** `<user>.foxtrot.cloud`. Піднімаються з
  `foxtrot-site/helm`:
  ```
  USER_NAME=academ1c helmfile apply \
    --state-values-set domain="${USER_NAME}.foxtrot.cloud",namespace="${USER_NAME}" \
    --set image.tag=dev_3343
  ```
  `image.tag=dev_NNNN` — номер збірки; коли питають «на якому білді перевіряв»,
  йдеться саме про нього. Kibana живе в тому ж домені `foxtrot.cloud` (VPN).
- **Тестові домени, які сайт розпізнає як тестові** (`CustomSettings.TestSitesUrls`):
  `test.foxtrot.com.ua`, `test1`, `test10`–`test17`, `test22`, `new1`,
  `aws.foxtrot.com.ua`, усе в `.mc.gcf`. На них частина логіки поводиться інакше —
  якщо фіча працює на тестовому домені й не працює на проді (або навпаки), перша
  гіпотеза саме тут.
- **dev-01 — статичний спільний стенд:** https://dev-01.foxtrot.com.ua. Не
  `<user>.foxtrot.cloud`: публічний, за Cloudflare, не за VPN. У
  `CustomSettings.TestSitesUrls` його немає, тобто сайт не вважає його тестовим
  доменом. Логи — в **окремому кластері** (див. нижче).

### Kibana: два кластери, різні мапінги

| Стенди | Kibana | LogType |
|---|---|---|
| динамічні `<user>.foxtrot.cloud` | `foxtrot01-dev-dyn-kibana-g.foxtrot.cloud` (VPN) | `site-foxtrot-<user>`, `api-main-<user>`, … |
| статичний dev-01 | `foxtrot01-dev-kibana-g.foxtrot.local` | `foxtrot-site`, `api-main`, `api-catalog`, `api-cms`, `api-exchange` — **без суфікса** |

Шукати логи dev-01 у dyn-кластері марно: там лежать тільки стенди по розробниках
(9 суфіксів). Індекси в обох — `logstash-*` і `logstash9-*`; корисне майже все в
`logstash9-*`, у `logstash-*` живе `macaron`.

**Рівні логів — лише `Error` і `Warning`.** `Fatal` і `Critical` не існують
(перевірено 2026-09-17 по обох кластерах за 14 днів) — не писати їх у фільтр.

**Помилка — це тільки `level: Error`.** `Warning` у цьому продукті інформаційний:
його десятки тисяч на день у штатному потоці, і сам по собі він нічого не означає.
Фільтр при пошуку збоїв — завжди `level: Error`; у звіт як «помилки» йдуть тільки
вони. Кількість записів `Warning` не називати кількістю помилок.

Водночас `Warning` часто містить **доказ до** `Error`: наприклад збій відправки GA4
фіксується як `Error` (`Execution attempt … Result: '502'`), а куди слалось і що
відповіло — лежить у `Warning` (`CartProviderBase:GA4MeasurementAnalytics … result: …`)
з тим самим `RequestPath` і сусідньою мілісекундою. Тому `Warning` підтягувати як
контекст до знайденого `Error`, а не рахувати окремими дефектами.

**Поле `level` змаплено по-різному:** на dev-01 це text із підполем
(`level.keyword`), на динамічних стендах — уже `keyword` (`level`). Невірний шлях
до поля **не падає з помилкою, а мовчки віддає нуль** — порожній результат тут
означає «не те поле», а не «помилок немає». Перед першим фільтром по рівню
перевіряти мапінг:
`POST /api/console/proxy?path=logstash9-<дата>%2F_mapping%2Ffield%2Flevel&method=GET`.
`fields.LogType` — text в обох, агрегація тільки через `fields.LogType.keyword`.

**Структура документа різна:** на dev-01 є масив `exceptions[]` зі структурованими
`ClassName` / `Message` / `StackTraceString`, а `messageTemplate` часто просто
`Exception occured`. На динамічних стендах стек лежить текстом прямо в `message`.
Тому пошук по винятку має йти і по `message`, і по `exceptions.*`.

## Робочий процес у GitLab

- **Jira-префікси задач:** `CMS-` (сайт/CMS) і `FMA-` (мобільний застосунок/API).
- **Назва MR:** `[#CMS-27678] Update order details` (іноді без `#`).
- **Гілка:** `CMS-15490_ura_new_popup` або `CMS-14072-update-img-pdp` — номер задачі
  попереду, далі назва через `_` чи `-`.
- **Ціль:** `master`. Merge method — merge commit, squash `default_on`, гілка
  видаляється після мержу.
- **Обсяг:** ~196 відкритих MR, 9 334 змержених — потік великий, рев'ю точкове.
- **CI:** у старих репо (274–282) jobs вимкнені; у нових (`foxtrot-api`,
  `foxtrot-faq`, `foxtrot-roulette`, `foxtrot-ai-generator`) — увімкнені.

### Мітки MR — це і є процес QA

| Мітка | Значення |
|---|---|
| `Reviewed` | код-рев'ю пройдено |
| `Code_Review_Failed` | рев'ю не пройдено |
| `On_Testing` | віддано на тестування |
| `QA_Approved` | QA підтвердив |
| `Need_Fix` | знайдено дефект, повернуто розробнику |
| `Db_changed` | є зміни БД — на стенді потрібна міграція |
| `Conf_changed` | змінено конфіг — стенд треба переналаштувати |
| `NuGet_changed` | оновлені пакети — потрібен повний ребілд |
| `Api-Main`, `Api-Catalog`, `Api-Exchange` | на MR у `foxtrot-common`: які API зачіпає зміна |
| `Release` | реліз-MR |

`Db_changed` / `Conf_changed` / `NuGet_changed` — прямий сигнал, що просто
задеплоїти гілку мало: без міграції чи конфігу фіча не підніметься, і «не працює»
виявиться не багом.

### Одна задача = кілька MR

Типово зміна розповзається по репозиторіях. Приклад `[#CMS-25040] Damaged products
added` — одночасно 5 MR: `foxtrot-site`, `foxtrot-common`, `foxtrot-api-main`,
`foxtrot-api-exchange`, `foxtrot-api-catalog`. Перед рев'ю або тестуванням завжди
перевіряти, чи немає ще MR по тій самій задачі, інакше рев'ю неповне, а стенд
зібраний наполовину. Зручний пошук — список MR групи з номером задачі в рядку пошуку.

## Розробники

Пучач Юрій (`Puhach-Yu`), Грицаченко Андрій (`Andrii_Hrytsachenko`), Котовський
Денис, Вужинський Іван, Джага Михайло, Malikov Oleksiy (`Alex`), Bolsunovskyi
Andrii, Mykhailo Shapoval, Taras Vynar.

## Функціонал — звідки беруться області тестування

Каталог і лістинг, PDP з відгуками й фото, пошук, порівняння, обране, переглянуті
товари, кошик і його прев'ю, чекаут, оплата (Tranzzo, monobank, ПриватБанк «оплата
частинами»), електронний чек, доставка, Foxclub і персональні бонуси, Outlet,
акції та спецпропозиції, подарункові картки, «Знайшли дешевше» (NicePrice),
Trade-in (Breezy), відеоконсультації (TokBox/OpenTok), чат (Kwizbot), підтримка
нечуючих, QR-автентифікація, реферальна програма, ідеї подарунків до свят.

Авторизація: телефон + код, Google, Apple, Facebook; reCAPTCHA v2.

### Конкретика, корисна для граничних значень

- **Мови:** `uk` (id 1, дефолт) і `ru` (id 3) — перевіряти обидві версії сторінки.
- **Дозволені коди мобільних:** 38097, 38039, 38050, 38066, 38095, 38099, 38063,
  38093, 38073, 38067, 38068, 38096, 38098, 38091, 38092, 38094. Решта має
  відхилятися формою.
- **Фото у відгуку:** до 5 файлів, ≤ 5 МБ кожен, лише `image/jpeg` і `image/png`.
- **«Знайшли дешевше»:** до 3 зображень, ≤ 5 МБ, jpeg/png; посилання приймаються
  лише з доменів `foxtrot.ua` і `foxtrot.com.ua`.
- **Фото товару на мобільному:** максимум 20.
- **Мітки на картці товару:** максимум 3.
- **Санітизація HTML:** у конфізі великий список заборонених конструкцій
  (`ForbiddenStatements`: усі `on*`-хендлери, `javascript:`, `document.cookie`,
  `alert`, `@import`) — готовий набір для перевірок на XSS у полях, що приймають
  розмітку.

## Автотести, які вже є в продуктовому репо

`foxtrot-site/foxtrot.tests/AutoTestFoxtrotSite` — C#, **Selenium 3.141 + NUnit і
MSTest**, `netcoreapp3.1`, `chromedriver.exe` лежить у репо. Області: `Baskets`,
`Footer`, `HeaderComponents`, `ListingPage`, `MainPage`, `Outlet`,
`ProductCatalog`, `Sitemap`, `StocksPages`. `AppSettings.json` — `BaseUrl` вказує
на **прод** (`https://www.foxtrot.com.ua`), логін і пароль порожні.
Поряд `foxtrot.tests/LodingTests` і `load-tests.foxtrot.site` — навантажувальні.

Стек 2020 року, .NET Core 3.1 давно EOL. Для нових перевірок наш Playwright у
`D:\QA` практичніший.

## Куди дивитись у коді

- Контролери, в'юхи, компоненти сайту — `foxtrot.site/Controllers`, `/Views`,
  `/ViewComponents`, `/TagHelpers`.
- Бізнес-логіка — `BusinessLayer/` (окремо в `foxtrot-site` і в `foxtrot-api`).
- **Прапорці фіч** — `foxtrot.site/appsettings.json`, секція `CustomSettings`:
  `EnableGtm`, `EnablePersonalBonuses`, `EnableQrAuthentication`,
  `CancelOrderByClient`, `DisableDefaultDeliveries`, `EnableMenuEncryption`,
  `EnableVerificationCallMeCheckbox` (з датами старту/кінця) тощо. Вимкнений
  прапорець на стенді — часта причина «фіча не працює», перевіряти перед заведенням
  бага.
- **Очікувані meta robots** — `SeoSettings.MetaRobotsPages`: майже все
  `noindex, nofollow`, `index, follow` лише для `Stores_Index` і
  `Stores_LoadForSelectedCity`. Готовий еталон для SEO-перевірок.
- Схема API — `foxtrot-site/docs/foxtrot_apis_v0.json`.
- Деплой — `foxtrot-site/helm/helmfile.yaml` і `helm/foxtrot-site/values.yaml`.

## Як читати файли GitLab без клієнта

API і сирі файли віддають JSON, на якому переглядач Chrome спотикається (у конфігах
є коментарі). Робочий спосіб — сторінка blob із затримкою:

```
https://git.foxtrot.ua/<група>/<репо>/-/blob/master/<шлях>?plain=1
```
відкрити, зачекати ~3 с, забрати текст сторінки. Списки (проєкти, мітки, гілки,
дерево) зручніше через API: `/api/v4/groups/121/projects?simple=true`,
`/api/v4/groups/121/labels`, `/api/v4/projects/<id>/repository/tree?ref=master&path=<шлях>`.

## Застереження

`foxtrot.site/appsettings.json` у `master` містить бойові секрети: паролі сервісних
акаунтів API, приватний ключ Apple, secret'и Google/Facebook/Twitter, секретний
ключ reCAPTCHA. **Не переносити їх у баг-репорти, чеклісти, скріншоти й у цей
файл.** Якщо потрібне значення для перевірки — брати з конфігу стенда на місці.
