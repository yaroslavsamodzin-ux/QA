# Postman-колекції

## «Фокстрот» — одна колекція для Postman і для Claude

Джерело правди — тека **`Фокстрот/`** (формат Postman Local: YAML, по файлу на запит).
Postman бачить її через `.postman/resources.yaml` (`localResources → ../Фокстрот`), Claude запускає її
Postman CLI. Що змінив у застосунку — те й запускається з термінала, і навпаки; диф видно в git.

| Тека | Що там |
|---|---|
| `Dynamic` | samodzin.*.foxtrot.cloud: токени, джоби, AI-описи |
| `Stage` | stage.*.foxtrot.local (через RDP/VPN) |
| `kviatkovska`, `osipov`, `shutov` | dyn-стенди колег |

### Логіни й паролі

У запитах — лише змінні: `{{api_login}}`, `{{api_password}}` (apiConsumer, api-exchange) і
`{{ai_login}}`, `{{ai_password}}` (ai-consumer, api-catalog). Значення — у
**`local.postman_environment.json`**, він у `.gitignore` і нікуди не комітиться.

- **Postman:** Import → `local.postman_environment.json` → вибрати оточення «Фокстрот local» справа вгорі.
  Нові облікові дані додавай у це оточення (або Vault), не в заголовок запиту.
- **Термінал / Claude:**
  ```
  postman collection run "PostmanCollection/Фокстрот" -e "PostmanCollection/local.postman_environment.json" -i "Токен мій"
  ```
  `-i` — назва запиту або теки. **Усю колекцію не запускати:** частина запитів стартує джоби на стендах.

### Правила

- Пароль, токен, телефон, cookie — тільки в оточення. Перед комітом: `grep -rn "password: [^\"]" PostmanCollection/Фокстрот`
  має бути порожнім.
- Назва запиту = ім'я файлу; `/` у назві Postman замінює на `_`.
- Старий `Фокстрот.postman_collection.json` прибрано 13.10.2026 — усе з нього перенесено в теку
  (у т.ч. 4 запити, яких бракувало в `Фокстрот_CLOD`).

## Інші файли

- `Postman extendet Yaroslav Samodzin/` — навчальна колекція (теж YAML, теж у `resources.yaml`).
- `Prod.env.json`, `ENVforREG.json` — оточення для старих JSON-колекцій.
- `newman/`, `report.html`, `node_modules/` — newman і його звіти для JSON-колекцій (`PostmanTests/`, задачні
  колекції в `qa-toolkit/tasks/<KEY>/api/`).
