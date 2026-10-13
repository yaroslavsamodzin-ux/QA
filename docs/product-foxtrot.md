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
- **Що залито на динамічний стенд — Jenkins** `dev/deploy-dyn-env-paralell`
  (https://deploy.foxtrot.ua/job/dev/job/deploy-dyn-env-paralell/), збірки підписані
  `#NNNNN deployed-<user>`. Гілки й коміти кожного сервісу — тільки читанням через
  `<build>/api/json?tree=actions[parameters[name,value],lastBuiltRevision[SHA1,branch[name]],remoteUrls]`:
  параметр `SITE` = гілка сайту, `DEPLOY_*` = які сервіси перевикладались. Сторінка
  `/parameters/` значень у тексті не показує. Номер цієї збірки й коміт іти у звіт.
- **Тестові домени, які сайт розпізнає як тестові** (`CustomSettings.TestSitesUrls`):
  `test.foxtrot.com.ua`, `test1`, `test10`–`test17`, `test22`, `new1`,
  `aws.foxtrot.com.ua`, усе в `.mc.gcf`. На них частина логіки поводиться інакше —
  якщо фіча працює на тестовому домені й не працює на проді (або навпаки), перша
  гіпотеза саме тут.
- **dev-01 — статичний спільний стенд:** https://dev-01.foxtrot.com.ua. Не
  `<user>.foxtrot.cloud`: публічний, за Cloudflare, не за VPN. У
  `CustomSettings.TestSitesUrls` його немає, тобто сайт не вважає його тестовим
  доменом. Логи — в **окремому кластері** (див. нижче).

### Джоби стенду — через колекцію «Фокстрот»

Тека `PostmanCollection/Фокстрот/` (YAML, з 13.10.2026 — спільна для Postman і Claude) тримає запуски
джоб по стендах. Ендпоінт api-exchange вимагає Bearer-токен, який видає окремий запит тієї ж колекції:

```
GET http://<user>.api-exchange.foxtrot.cloud/v0/authentication/token
    заголовки login / password = {{api_login}} / {{api_password}} з local.postman_environment.json
GET http://<user>.api-exchange.foxtrot.cloud/v1/1/job/services_redis/execute
    Authorization: Bearer <token>
    -> {"resultMessage":"Updated N services records."}
```

Без токена ендпоінт джоби віддає **401** — на **будь-яку** назву джоби, тож перевірити
існування джоби без токена неможливо. Назви джоб — у `foxtrot-api-exchange`,
`BusinessLayer/Providers/JobExecutionProvider.cs` (напр. `rests` → `RestsJob`,
`products`). Токен короткоживучий: брати свіжий перед кожним запуском
(`qa-toolkit/tasks/CMS-25396/run-job.js <job> <user>` робить обидва кроки). Прогін `services_redis` на повному стенді
займає ~1 секунду.

**БД динамічних стендів — `foxtrot01-dev-shared` / `foxtrot_dev`, не стейдж.** Вона спільна
для всіх `<user>.foxtrot.cloud`, тож запуск джоби з одного стенда переписує дані всім. Читати:
`python qa-toolkit/db/pg.py -t dev "..."` (без `-t` — стейдж `fox_stage_current`, де за розкладом
о :22 і :52 крутиться `rests` зі старим кодом стейджу). Стейдж годиться лише як базова лінія
«без фіксу», результат перевірки — тільки з `foxtrot_dev`. На 30.09.2026 у `foxtrot_dev` є
`backup_current_202609280953_01`, тобто дані туди заливали зі стейдж-бекапу 28.09.

**`rests` відповідає `Job rests failed` → спершу конфіг стенда.** 30.09.2026 на samodzin
причина була `defaultCityId ('0')` у `CityRepository.GetCitiesStoragesRelationships`: на стенді
не заданий `RestsJobSettings:CityId` (у `appsettings.json` master він `11`). Відповідь API
причини не каже, вона є лише в Kibana (`exceptions.Message`).

**`restslogs` — хто читає** (30.09.2026, CMS-25396): крім самої `RestsJob` (через
`foxtrot-common` `RestsAdapterBase`, перезапис усієї таблиці `BulkCopyAsync(..., true)`),
лише процедури БД `update_wishlist()` і `update_comparisons_list()`. Вони видаляють з
обраного й порівнянь товари без ціни, без залишку і без `lastdate` за 30 днів. Облікові дані сервісного акаунта лежать у колекції — у звіти,
баг-репорти й цей файл їх не переносити.

### Kibana: два кластери, різні мапінги

| Стенди | Kibana | LogType |
|---|---|---|
| динамічні `<user>.foxtrot.cloud` | `foxtrot01-dev-dyn-kibana-g.foxtrot.cloud` (VPN) | `site-foxtrot-<user>`, `api-main-<user>`, … |
| статичний dev-01 | `foxtrot01-dev-kibana-g.foxtrot.local` | `foxtrot-site`, `api-main`, `api-catalog`, `api-cms`, `api-exchange` — **без суфікса** |

Шукати логи dev-01 у dyn-кластері марно: там лежать тільки стенди по розробниках
(9 суфіксів). Індекси в обох — `logstash-*` і `logstash9-*`; корисне майже все в
`logstash9-*`, у `logstash-*` живе `macaron`.

**LogType api-exchange пишеться з крапками:** `foxtrot.api.exchange.<user>`, а 01.10.2026 на samodzin і yatsun траплявся вже `foxtrot.api-exchange-<user>` — шукати `fields.LogType:*exchange*<user>*`,
тоді як сайт — `site-foxtrot-<user>`, а каталог — `api-catalog-<user>`. Через це
`fields.LogType:*exchange*` мовчки віддає нуль і виглядає як «джоба не логується»
(перевірено 23.09.2026 на CMS-27181). Логи джоб надійніше шукати за текстом:
`message:*Job*` або `message:*has been executed*`.

**Запит у Discover без кліків — через URL.** Dyn-кластер відкривається по `http://` (на `https://`
curl мовчки таймаутить), дата-в'ю `logstash*` має id `aee7f12d-a673-4b83-8a93-f32ff9600304`.
Готовий шаблон, який ставить і фільтр, і період за один `navigate`:
`http://foxtrot01-dev-dyn-kibana-g.foxtrot.cloud/app/discover#/?_g=(time:(from:now-30m,to:now))&_a=(dataSource:(dataViewId:aee7f12d-a673-4b83-8a93-f32ff9600304,type:dataView),query:(language:kuery,query:'level:Error and fields.LogType:*samodzin*'),sort:!(!('@timestamp',desc)))`
Результат читати через `get_page_text` — він віддає розгорнуті документи зі стеком, `_id` і `_index`;
скріншот тут гірший, бо таблиця дрібна. `javascript_tool` на Kibana блокує readonly-hook, і це не
заважає: URL + `get_page_text` закривають усі потреби читання.

**Переглянуті товари (кука `ft_recently`, CMS-27500, 11.10.2026).** Кука HttpOnly: зі скрипта не видно і не
перезаписати, поки вона є. Очистити штатно — «Видалити всі товари» на `/uk/account/lookedgoods`
(`/uk/lookedgoods/removeallfromlookedgoods`), після цього скриптова `ft_recently=_<classId>%3A<id>_…` читається
сервером (останній у куці = перший у блоці). Блок головної — AJAX `/uk/home/getrecentlylookedgoodsblock`
(skip 0, take 20, sync true), догрузка по одній — `GetMainPageLookedGoodsLoad?skip=N`. Кука з `classId ≤ 0` дає 500.

Kibana dev-01 — так само по `http://`, дата-в'ю `bcccf430-4cbb-4ac1-82ee-bc5d7c62d734` (дав Ярослав
11.10.2026, CMS-27500): `http://foxtrot01-dev-kibana-g.foxtrot.local/app/discover#/?_g=(time:(from:now-15m,to:now))&_a=(dataSource:(dataViewId:bcccf430-4cbb-4ac1-82ee-bc5d7c62d734,type:dataView),query:(language:kuery,query:''),sort:!(!('@timestamp',desc)))`

**`foxtrot-ai-generator` у Kibana.** У dyn-кластері його записи мають `fields.type: ai-generator`
і `MachineName` локальних машин розробників (`DESKTOP-…`), тобто це локальні запуски, а не стенд.
Пишеться лише рівень `Warning`+ (`MinimumLevel.Warning()`). Відхилені повідомлення стріму
(`naming data was not found` тощо) **в лог не потрапляють** — лише в Redis (DLQ, history, лічильник
Rejected). Під час генерації на стейджі 25.09.2026 у dyn-кластері за 2 години нуль записів; Kibana
dev-01 (`foxtrot.local`) просить логін — де логує стейдж-інстанс генератора, ще не з'ясовано.
Пошук запуску сервісу: `message:"worker starting as consumer" or message:"Consumer group"`.

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

### Прод: логи, кошик у шапці, ліміти (30.09.2026)

- **Серверні логи проду є — у третій Kibana `https://logs.foxtrot.ua`** (знайдено 13.10.2026 на
  CMS-28048; запис вище про «тільки дев-кластери» був хибний). Дата-в'ю `Logs9` = id
  `39174ea1-1c53-470b-91a9-aea0b172e8a6`, `fields.LogType: api-main` без суфікса, у сусідніх записах
  `prod.api-main.foxtrot.local`. **Поле `exceptions` там не шукається через KQL:**
  `exceptions.ClassName:"…"` і вільний текст по стеку дають 0 навіть на документ, що точно є
  (у перегляді документа поле з іконкою ⚠). Шукати за `level`, `fields.LogType`, `fields.MachineName`
  і часом, потім відкривати документ. Обхід для підрахунку: **Inspect → Response → Copy to clipboard**
  віддає сирі 500 документів з `exceptions`, далі `Get-Clipboard` у файл і групування Python-ом (CMS-28048:
  так знайшлось, що 478 з 500 — одна помилка). Мобільний API там пишеться як `fields.type: api-foxtrot`
  (не `fields.LogType`); його `HttpService:GetAsync Url:"…"` містить шлях виклику api-main з `customerId`.
  **Увага:** у Warning `api-foxtrot` відкритим текстом лежать телефони з SMS-кодами й refresh-токени —
  такі відповіді не зберігати у файли, буфер після копіювання чистити. Консоль і мережа браузера лишаються для фронтових помилок;
  сторонній шум там — `[GSI_LOGGER] FedCM` від Google One Tap.
- **Шапка кошика малюється з `localStorage`** (`foxtrot-cart-state-v1`, `foxtrot-cart-count-v1`), а
  не з сервера. Правда про кошик — `GET /uk/cart/cartitems?getFullData=true` (`isEmptyBasket`,
  `cartProducts`). Розбіжність шапки й кошика спершу звіряти з цим запитом.
- **Cloudflare** перед продом: десятки скриптових запитів за хвилини → 429 і challenge.
- `/health` на проді публічний (`Healthy`).
- Таймери акцій: `data-end` без часового поясу (`2026-09-30T23:59:59`).

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

**Порівняння: хто кличе які ендпоінти api-main** (13.10.2026, CMS-28048). Сайт
(`foxtrot.site/Classes/Providers/CompareProvider.cs`) ходить лише в `add-product`,
`remove-product`, `remove-category-products`, `remove-all-products`, `all-products-ids`, тобто
картки товарів збирає сам. `all-products` і `category-products` кличе тільки новий API
`foxtrot-api` (`BusinessLayer/Providers/ComparisonProvider.cs`, `api/v1/comparison`, `[Authorize]`)
— бекенд мобільного застосунку. Баг у `all-products` через UI сайту не відтворити.
На динамічному стенді `foxtrot-api` є лише тоді, коли збірка з `DEPLOY_API = true`
(у #11260 його не було, `samodzin.api.foxtrot.cloud` не резолвиться).

Порівняння на сайті (samodzin, 13.10.2026): `ExternalCustomer = true`, рядки — у
`externalcustomercomparisons` (`customerid`, `classid`, `catalogobjectid`, `datein`). Ендпоінти сайту:
`POST /uk/products/addtocomparelist` (`classId`, `objectId`), `DELETE /uk/compare/remove`,
`DELETE /uk/compare/removeall`, `GET /uk/compare/getcomparingproductids`. Сторінка `/uk/compare` відкривається на
категорії, куди додавали останньою. **Після виходу з акаунта гість бачить список акаунта** (копія в гостьовому
сховищі; гостьові зміни в БД акаунта не пишуться) — на проді не звірено, питання CMS-28048 q2.

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

### Класи товарів у БД: `cc_<class>` і `cc_<class>_`

Товари зберігаються не в одній таблиці, а **по таблиці на клас товару**. Ім'я
таблиці збирається з `classes.uniquename`: клас ноутбуків — `noutbuki`, отже
`cc_noutbuki` (базові поля: `id`, `ft_url`, `uniquename`) і `cc_noutbuki_` з
суфіксом `_` — локалізації (`id`, `languageid`, `naimenovanie`). `id` товару
збігається з `productcommonrelations.goodid`.

Наслідок для коду: запит до класу можна побудувати тільки конкатенацією імені
таблиці, тож у сервісах трапляється інтерпольований SQL (`cc_{className}`).
Наслідок для QA: щоб знайти дані по всіх класах, потрібен згенерований
`union all` по `classes` — див. `qa-toolkit/tasks/CMS-27767/queries.sql`.

Назва товару має два джерела: старе `productcommonrelations.goodtitle` і
`cc_<class>_.naimenovanie` за локаллю. Локалей у таблиці **три**, не дві:
`1` — укр, `3` — рос, а також `2` (у `cc_noutbuki_` це 19 938 рядків), яку
сервіси з парою «дефолтна + запасна» не використовують.

**Порожніх `naimenovanie` в базі немає** — заміряно 18.09.2026 на `cc_noutbuki_`:
32 500 рядків UA, 32 512 RU, 19 938 для локалі 2, і в усіх трьох `with_name`
дорівнює `rows_total`. Тобто `nullif(naimenovanie, '')` на практиці ніколи не
спрацьовує, а fallback на іншу локаль вмикається тільки там, де **рядка
локалізації взагалі немає** (у ноутбуках це десятки товарів на 32 тисячі).
Замір: `qa-toolkit/tasks/CMS-27767/evidence/noutbuki-locales-2026-09-18.txt`.

### Подарунки до товару: `packages` type 7 (13.10.2026, стейдж)

- **Подарунок = пакет `packages.packagetypeid = 7`**: головний товар у `mainobjectclassid/mainobjectid`,
  подарунок — рядок у `packagesobjects` (`minorobjectclassid/minorobjectid`, `minorobjectprice` —
  номінальна ціна подарунка, не нуль). `title` має формат
  `<specialofferid>_<externalspecialofferid>_<кодГоловного>_<кодПодарунка>`, з нього береться акція.
- **В одному пакеті type 7 завжди рівно один подарунок** (7 737 пакетів, жодного з двома).
  Кілька пакетів однієї акції — це варіанти вибору (напр. навушники двох кольорів до OPPO).
  Товар у двох різних подарункових акціях — це теж два окремі пакети; чи падають обидва
  подарунки в одне замовлення, з БД не видно (не перевірено ні в коді, ні в кошику).
- **«Товар + 2 подарунки в одне замовлення» одним пакетом у БД немає** — ні на стейджі, ні в
  спільній dev-БД (13.10.2026): кілька minor-товарів буває лише в type 23 (комплекти). Єдиний
  type 23 з подарунком — 2157529: комплект Electrolux 7136783 (прихований) + мультипіч 7130668 за 1 грн.
- **Інші типи — не подарунки:** 23 — комплекти «пральна + сушильна» (кілька minor-товарів
  за повною ціною), 10 і 4 — масові пакети (купуй разом / знижки).
- Таблиця `giftproducts` (89 кодів) — лише перелік товарів «подарункового фонду», більшість
  уже без запису в `productcommonrelations`; для пошуку подарунків вона не годиться.
- Готовий запит: `qa-toolkit/db/queries/products-with-two-gifts.sql`. Найчастіше два
  подарунки дають акції 42467 «GIFTA» і 43976 «GIFTAB» (пляшки GUSTO 6885340 і 6885344).

### Описи товарів для AI: `description-scroll` (CMS-28140, 01.10.2026)

- **Ендпоінт** `GET /v0/38044/{lang}/products/ai/description-scroll` у `foxtrot-api-catalog`,
  NDJSON-потік `{"Key","Value"}`. Bearer-токен з роллю `ai` бере запит «Токен for
  ai-consumer api catalog» (Postman → `MY`, логін і пароль у заголовках). На динамічному
  стенді хост — `<user>.api-catalog.foxtrot.cloud`, api-exchange — `<user>.api-exchange.foxtrot.cloud`.
  Токен api-exchange api-catalog не приймає (401 «signature key was not found»).
  Перший сегмент шляху (`38044`) ігнорується — будь-яке значення, навіть `abc`, дає ті самі дані.
- **Джерело — тільки Redis**: ключі `pd:{lang}:{code}` (ручний `cc_<class>_.description`)
  і `pdai:{lang}:{code}` (`cc_<class>_.ai_description`). Число в ключі — **`code`**, а не `id`.
  Колонка `ai_description` є в 730 класах. Окрема таблиця `productaidescriptions`
  (`id`, `classid`, `languageid`, `text`) — інше джерело, з кешем не збігається.
- **Мови в AI-описах — 1 і 3.** Запит на мову 2 дає 200 з порожнім потоком.
- **Обсяг:** мова 1 — 179 тис. рядків і 907 МБ, повне вивантаження через VPN триває близько 500 с.
  Python + `requests` зі `stream=True` проходить потік без проблем; `get_page_text`/браузер — ні.
- **У кеш потрапляють не всі товари:** невидимі — ніколи; з видимих — лише частина
  (за якою ознакою, невідомо: не ціна, не залишки, не `allgoodsforsearch`). Тому звіряти
  треба відповідь з БД за `code`, а не очікувати повного збігу кількості.
- **Кеш `pd:`/`pdai:` пише джоба `descriptions`** (`DescriptionsJob`, api-exchange):
  `GET http://<user>.api-exchange.foxtrot.cloud/v1/1/job/descriptions/execute`, токен «Токен мій»
  (`qa-toolkit/tasks/CMS-25396/run-job.js descriptions <user>`). На yatsun 29.09: «Updated 502029
  description records. Updated 535 reviews summary records». На samodzin 01.10 падала з 500
  `Value cannot be null. (Parameter 'configuration')` у `ProductsRedisService..ctor`: у конфігу
  api-exchange стенда немає підключення до products-Redis. Це конфіг стенда, а не баг.
  Поки джоба не пройде, тексти в кеші можуть відставати від БД.
- **Джерело джоби — функція БД `getpoductdescriptionsfunc(languageid)`** → `code, description, ai_description`:
  класи з `isservice = false`, `visible`, `code > 0`, без записів у `catalogobjectsattributeslinks`.
  Правило (аналітик, 01.10.2026): **ручний опис у пріоритеті** — `pdai` пишеться лише товарам без ручного, як і на сайті.
  Джоба пише рівно `f(1) + f(3)` записів (01.10: 502 029), а у відповіді на samodzin щоразу бракувало ~60 тис.,
  причому різних між запусками. Причина (02.10.2026, тімлід): Redis динамічних стендів `dev-dyn-valkey` — спільний, **1 GB**,
  ключі витісняються. На стейджі втрат немає. Повноту кешу описів перевіряти на стейджі, а не на динамічному стенді.
  Звіряти треба з `getpoductdescriptionsfunc`, а не з категорійними таблицями.
- **Обрив потоку клієнтом пишеться в Kibana як Error** (`OperationCanceledException`
  з `ProductProvider`). Це наслідок власних обірваних запитів, а не дефект — звіряти час з `_id`.

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

### Чекаут: два шаблони і які ендпойнти смикає UI

- Мовний префікс в URL — **`/uk/`**, не `/ua/`. Кошик — `/uk/cart`, чекаут —
  `/uk/cart/checkout`.
- Два незалежні шаблони: звичайний (`Views/Checkout/Index.cshtml` + партіал
  `_CheckoutItems.cshtml`) і спліт (`Views/Checkout/Splitted/IndexSplitted.cshtml` +
  `_CheckoutItemsSplitted.cshtml`). Обидва рендерять товари через `_CheckoutItem.cshtml`.
  Зміна в блоці товарів майже завжди має зачепити обидва — перевіряти окремо.
- **Дії з товарами на чекауті НЕ перерендерять партіал товарів.** Перевірено 21.09.2026
  інструментуванням XHR:
  - зміна кількості → `GET /uk/cart/updatecart`
  - видалення товару → `GET /uk/cart/deletefromorder`
  - зміна міста → `GET /uk/cart/loadcities`
  - після кожної — `POST /uk/checkout/getdeliverytypes` і
    `POST /uk/checkout/recalculatecheckout`

  DOM правиться на місці, тож стан, який тримається на CSS-класах (згорнутий/розгорнутий
  блок товарів), після цих дій не скидається. `CheckoutController.GetOrderedProducts`
  (повертає `PartialView("_CheckoutItems")`) з цих сценаріїв не викликається — він має
  параметр `promocode`, а поля промокоду на самому чекауті немає, воно лише в кошику.
- Блок товарів — `#products-block`, він же `.checkout-tovar-list.hide-for-mobile.slot`.
  Згорнутий стан = клас `collapse-product` (CSS у
  `wwwroot/src/templates/pages/checkout/new-design.scss`, мініатюри 48×48, на
  `max-width:769px` — 43×43).
- Видалення товару має **два** варіанти розмітки: `.checkout-tovar__remove` (десктоп,
  іконка-хрестик) і `.checkout-tovar__remove_mob` (мобілка, текст «Видалити»;
  для зв'язки товар+послуга — «Видалити все»). Перевіряти обидва.

### Мобільний таббар і каталог: дві реалізації (CMS-25439, 07.10.2026)

На мобілці (< 1024 px) нижній таббар «Головна · Каталог · Кошик · Обране · Меню» існує у **двох незалежних
версіях** — фікс в одній не діє на іншу:

| | Стара | Нова |
|---|---|---|
| Таббар | `#mobileFooterSection` у `Views/Shared/_Layout.cshtml` | `#mobileBottonMenu`, кнопка `#catalogBtn` |
| Каталог | `.footer-fixed-mobile-catalog-container` у `#mobile-footer-catalog`, логіка — `mobile-menu.js` `toggleMobileCatalog()` | `#headerCatalog.mobile-catalog` (плитки категорій, довантажується 2–3 с) |
| Блокування фону | з CMS-25439: `html.is-mobile-catalog-open` → `overflow:hidden` до 1023 px | `body.scroll-locked` (position fixed, `top: -Ypx`, позиція відновлюється) |
| Де (07.10.2026) | головна, `/uk/actions`, `/uk/stores`, `/uk/cart.html`, `/ru/` | лістинг, картка товару, пошук, `/uk/actions/<id>`, `nice_price` |

- ☰ у мобільній шапці — `.header__main-catalog-trigger` (`header.js`, `catalogTrigger`): клікає таббар, тобто той
  самий `toggleMobileCatalog`. `.js-open-catalog-mb` — це **десктопна** кнопка «Каталог товарів», на мобілці 0×0.
- Пункт «Меню» в таббарі відкриває `#js-mobile-menu` з власним блокуванням `body.mm-body--open`; пункт «Каталог
  товарів» усередині меню на мобілці схований — каталог звідти не відкрити. Меню перекриває таббар.
- Відкриття «Меню» і попапа входу скидає прокрутку сторінки на 0 (помічено на samodzin, з продом не звіряли).
- На `/uk/cart/checkout` таббара немає.

### Десктопний «Каталог товарів»: дві реалізації (CMS-25449, 12.10.2026)

| | Стара шапка (головна, `/uk/cart.html`, `/ru/`) | Нова шапка (лістинг, PDP, пошук, акції) |
|---|---|---|
| Розмітка | `#js-catalog-list` / `.catalog__category`, активне меню — `.catalog_active` | `Views/Shared/Components/MainMenuNew/Default.cshtml`, `#headerCatalog.active` → `.header-fixed-inner` |
| JS | `wwwroot/src/scripts/header.js` (`setUpMainCatalog`, `setUpHomePageMainCatalog`) | `wwwroot/new/src/js/layout/header.js` |
| SCSS | `wwwroot/src/templates/components/header/header.scss` | `wwwroot/new/src/scss/header.scss` |

Фікс в одній не діє на іншу, але MR часто правлять обидві — дивитись diff за обома шляхами. На головній
каталог — бічна колонка поруч зі слайдером, тому будь-яка зміна висоти `.catalog_active` б'є по першому екрану.
Повний diff MR без тяжкої сторінки Changes: `.../merge_requests/<N>.diff`.

### Події eSputnik / Softcube (CMS-28186, 12.10.2026)

- Заглушка `eS` визначається інлайном у `<head>`; кожен виклик іде через `eS.c(arguments)` — обгортка
  `eS.c` бачить усі `eS('sendEvent', …)` з payload. Мережа: POST `esputnik.com/site-events/api/v1/webevent`
  (подія, `GeneralInfo.eventName`) і `/webcontact` (ідентифікатори). Тіло CustomerData у webevent містить
  лише `user_name` — email і телефон скрипт вирізає й шле через webcontact, **раз за сесію**.
  Часті виклики (~1 с) скрипт схлопує в один запит. Дев-стенд шле в той самий siteId `8D3869C`, orgId 5179.
- Нові сторінки: `wwwroot/new/src/js/components/ecommerce-sc.js` (до CMS-28186 — `ecommerceSc.js`), шина
  `MessageBus`: `scStatusCart` ← cart, `scAddToWishlist` ← favorites, `signInToEs` ← auth-popup (окремий чанк),
  `scSearchRequest` і `scCustomerData` — **без публікатора**. При завантаженні: CategoryPage (лістинг, з
  `#main[data-category-title]`), ProductPage (PDP), CustomerData з `#userInfo`/thank-you/профілю.
- Старі сторінки: `wwwroot/src/scripts/softcube-events.js`, шлють `PageView` явно; головна — ще `MainPage`
  з `undefined`. `signInToEs` старий вхід публікував ще до CMS-28186.
- Чекаут: телефон у `#Phone` — без «38» («+38» — окремий селектор країни); власний payload замовлення
  (`localStorage._requestsDetails.customer.phone`) — у форматі `380…`.
- Виклики на **завантаженні** сторінки звичайним хуком не зловити (defer-скрипти вже відпрацювали), iframe
  стенд забороняє. Робочий спосіб — popup того ж домену по реальному кліку + цикл через `MessageChannel`
  в opener (не троттлиться), обгорнути `popup.eS.c`, щойно з'явилась заглушка
  (`qa-toolkit/tasks/CMS-28186/evidence/capture-pageload.js`, опис — `…/2026-10-12_pageload_anon.md`).

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

### Пагінація по розділах сайту (перевірено 2026-10-07, CMS-28000)

- **Каталог** (категорії, фільтр-, тег-сторінки) — `?page=N`, контролер `ProductBaseController`.
  SEO-правила в `CheckSeoRules`: `page=1` і `page<1` → 301 на чисту URL, `Page` → 301 на `page`,
  `page` за межами → 302 на категорію, `page=0` → 404 (перевірка до SEO-правил).
- **Акції `/uk/actions`, корпблог** — «Показати ще» через AJAX (`data-page`, `/uk/article/getmorearticle`),
  `?page` в URL ігнорується.
- **Black Friday, nice_price, outlet, бренди** — усі товари в HTML, «Показати ще N товарів» розкриває
  на клієнті без запитів; `?page` ігнорується, з параметром сторінка `noindex` + canonical на чисту.
- **Пошук** — `/uk/search?query=…`; запит, що збігається з категорією (`iphone`), дає 302 на неї.
- **Слабке місце — класи `MetaTags`**: `ProductsIndexPage.GetTitle` і `SpecialOfferBlackFridayPage.Generate`
  роблять `Convert.ToInt32(Query["page"])` по сирому рядку → 500 на дублі `page` чи нечисловому значенні,
  навіть коли контролер уже все обробив. А сторінка 500 після цього рендериться порожньою (Http50x-лейаут
  повторно викликає MetaTags і падає з NRE). Новий параметр URL — перевіряти й тут.
- **Портали `/uk/portal-*.html`** — `PortalController` → `PortalProvider.GetPortalByCategory(category, page)`
  кидає `ArgumentOutOfRangeException` на page ≤ 0 → 500 (прод теж, 2026-10-07). Інші значення page → 301 на чисту.
- **Outlet-категорії `/uk/outlet/shop/<cat>.html`** — свій контролер: `page≤0` → 404, `page` за межами → 302 на
  *портал*, а не на outlet-категорію.
- **Головна й регіональні головні (`/uk/shop/lvov.html`)** — `HomeController.IndexAsync` робить
  `Query.ContainsKey(Settings.RefererIdQueryParameter)`; якщо параметр не заданий у конфігу стенда — 500 на будь-який
  query (так на samodzin 2026-10-07, прод 200). «500 на головній з utm» на стенді — спершу конфіг.
- Повний перелік шаблонів сторінок — у sitemap проду (`/sitemap.xml` → `sitemap_<тип>.xml`: brands, holidays,
  black_friday, otzyvy, portals_<місто>, filters_<місто>, main_regional, tags, skriytaya_kategoriya). На
  динамічних стендах sitemap немає (404).

### Головна: ajax-блоки і кука переглянутих (CMS-27500, 13.10.2026)
- Блоки головної (`.ajax-block` з `data-url` у base64, напр. `#recently-looked-goods`) підвантажуються **лише після
  реальної прокрутки** колесом. `scrollTo()` і `scrollIntoView()` зі скрипта їх не запускають — блок лишається порожнім
  `div` висотою 0, і це виглядає як «блоку немає». Кадр знімати після `computer scroll`, а не після скриптової прокрутки.
- Перегляд картки товару сервер записує в **HttpOnly** `ft_recently`. Після цього `document.cookie = "ft_recently=…"`
  стару куку не перекриває, і наступні заміри йдуть на зміненому наборі. Перед кожною підстановкою куки чистити
  `DELETE /uk/lookedgoods/removeallfromlookedgoods` (той самий запит, що робить кнопка «Видалити всі товари»; confirm немає).
- Для залогіненого блок зливає куку з БД («Ви переглядали N товарів»), тож гостьові кейси з кукою на залогіненій
  сесії не перевірити. Вихід: `/uk/account/singout`.
