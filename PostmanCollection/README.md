# Postman-колекції

## «Фокстрот» — одна колекція для Postman і для Claude

Джерело правди — тека **`postman/collections/Фокстрот/`** (формат Postman Local: YAML, по файлу на запит).
Postman показує в панелі Collections лише теки з `postman/collections/` — колекцію поза нею він не бачить
і через Import зробить копію (так з'явився дубль `Фокстрот-1`). У `.postman/resources.yaml` тека прив'язана
до хмарної колекції «Фокстрот» (`cloudResources`). Claude запускає її
Postman CLI. Що змінив у застосунку — те й запускається з термінала, і навпаки; диф видно в git.

| Тека | Що там |
|---|---|
| `Dynamic` | samodzin.*.foxtrot.cloud: токени, джоби, AI-описи |
| `Stage` | stage.*.foxtrot.local (через RDP/VPN) |
| `kviatkovska`, `osipov`, `shutov` | dyn-стенди колег |
| `CMS-28048 порівняння` | api-main samodzin, порівняння: P/N/R/C-кейси, K1 (контроль), V1–V9 (невалідні значення). Змінні `cmp_*` і `token_api_main` — у змінних колекції; P4b очищає порівняння клієнта |

### Логіни й паролі

У запитах — лише змінні: `{{api_login}}`, `{{api_password}}` (apiConsumer, api-exchange) і
`{{ai_login}}`, `{{ai_password}}` (ai-consumer, api-catalog). Значення — у
**`local.postman_environment.json`**, він у `.gitignore` і нікуди не комітиться.

- **Postman:** Import → `local.postman_environment.json` → вибрати оточення «Фокстрот local» справа вгорі.
  Нові облікові дані додавай у це оточення (або Vault), не в заголовок запиту.
- **Термінал / Claude:**
  ```
  postman collection run "PostmanCollection/postman/collections/Фокстрот" -e "PostmanCollection/local.postman_environment.json" -i "Токен мій"
  ```
  `-i` — назва запиту або теки. **Усю колекцію не запускати:** частина запитів стартує джоби на стендах.
  Postman CLI 1.31 **не читає змінні колекції** з `.resources/definition.yaml` (застосунок — читає): їх треба
  передати `--env-var key=value`, напр. для папки CMS-28048:
  `--env-var cmp_base=http://samodzin.api-main.foxtrot.cloud --env-var cmp_customerId=<id> --env-var cmp_classId=22281`.

### Правила

- Пароль, токен, телефон, cookie — тільки в оточення. Перед комітом: `grep -rn "password: [^\"]" PostmanCollection/postman/collections/Фокстрот`
  має бути порожнім.
- Назва запиту = ім'я файлу; `/` у назві Postman замінює на `_`.
- Старий `Фокстрот.postman_collection.json` прибрано 13.10.2026 — усе з нього перенесено в теку
  (у т.ч. 4 запити, яких бракувало в `Фокстрот_CLOD`).

## Інші файли

- `Postman extendet Yaroslav Samodzin/` — навчальна колекція (теж YAML, теж у `resources.yaml`).
- `Prod.env.json`, `ENVforREG.json` — оточення для старих JSON-колекцій.
- `newman/`, `report.html`, `node_modules/` — newman і його звіти для JSON-колекцій (`PostmanTests/`, задачні
  колекції в `qa-toolkit/tasks/<KEY>/api/`).
