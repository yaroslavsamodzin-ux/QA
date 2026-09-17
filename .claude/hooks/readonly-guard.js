#!/usr/bin/env node
/**
 * PreToolUse hook: «у зовнішніх системах — тільки читання».
 *
 * CLAUDE.md просить не писати в Jira, GitLab і Kibana. Прохання — не гарантія:
 * воно живе в контексті й може загубитись. Цей хук — примус: він бачить кожен
 * виклик інструмента до того, як той виконався, і вирішує allow / ask / deny.
 *
 * Що вміє і чого не вміє (чесно):
 *   - navigate і tabs_create_mcp несуть url → хост відомий точно;
 *   - computer, form_input, javascript_tool несуть лише tabId → хост беремо
 *     з власного стану (tabId → url), який хук веде сам по викликах navigate;
 *   - якщо вкладку відкрив Ярослав руками, хост невідомий → пропускаємо.
 *     Це свідомий компроміс: блокувати невідоме означало б ламати роботу на стендах.
 *
 * Клік на readonly-хості за замовчуванням не блокується, а питається: розгорнути
 * опис задачі, відкрити вкладку MR, ввести запит у Kibana — це читання, і глухий
 * deny зробив би Jira нечитабельною. Режим міняється в readonly-guard.config.json.
 *
 * Конфіг перечитується на кожен виклик.
 */

'use strict';

const fs = require('fs');
const path = require('path');

const HERE = __dirname;
const CONFIG_PATH = path.join(HERE, 'readonly-guard.config.json');
const STATE_PATH = path.join(HERE, '.state', 'tabs.json');

/** Інструменти, що тільки читають сторінку — крізь них нічого не змінюється. */
const READ_ONLY_TOOLS = new Set([
  'read_page', 'get_page_text', 'find', 'read_console_messages',
  'read_network_requests', 'tabs_context_mcp', 'tabs_close_mcp',
  'list_connected_browsers', 'select_browser', 'switch_browser',
  'resize_window', 'gif_creator', 'shortcuts_list',
]);

/** Інструменти, що взаємодіють зі сторінкою: клік, ввід, гарячі клавіші. */
const INTERACTION_TOOLS = new Set(['computer', 'form_input', 'shortcuts_execute']);

/** Інструменти, у яких на readonly-хості легального застосування немає. */
const WRITE_TOOLS = new Set(['file_upload', 'upload_image', 'javascript_tool']);

// ── дрібні помічники ────────────────────────────────────────────────────────

function readJson(file, fallback) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return fallback;
  }
}

function hostOf(url) {
  if (typeof url !== 'string') return null;
  try {
    return new URL(url).hostname.toLowerCase();
  } catch {
    return null;
  }
}

/** Рішення хука. Порожній вихід = «не втручаюсь», далі вирішують звичайні права. */
function respond(decision, reason) {
  if (decision) {
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        permissionDecision: decision,
        permissionDecisionReason: reason,
      },
    }));
  }
  process.exit(0);
}

// ── стан вкладок ────────────────────────────────────────────────────────────

function loadState() {
  const state = readJson(STATE_PATH, {});
  return (state && typeof state === 'object') ? state : {};
}

function rememberTab(tabId, url) {
  if (!url) return;
  const state = loadState();
  if (tabId !== undefined && tabId !== null) state[String(tabId)] = url;
  state.__last = url;
  // Не даємо файлу рости нескінченно: лишаємо 40 останніх вкладок.
  const keys = Object.keys(state).filter((k) => k !== '__last');
  if (keys.length > 40) {
    for (const k of keys.slice(0, keys.length - 40)) delete state[k];
  }
  try {
    fs.mkdirSync(path.dirname(STATE_PATH), { recursive: true });
    fs.writeFileSync(STATE_PATH, JSON.stringify(state));
  } catch {
    // Стан — оптимізація, а не вимога. Не змогли записати — просто працюємо далі.
  }
}

/**
 * Який хост зачіпає виклик. Спершу явний url, далі — запамʼятана вкладка.
 * `__last` свідомо НЕ використовуємо для рішення: у паралельних вкладках він бреше.
 */
function resolveHost(toolInput) {
  const direct = hostOf(toolInput.url);
  if (direct) return { host: direct, certain: true };

  const tabId = toolInput.tabId ?? toolInput.tab_id;
  if (tabId !== undefined && tabId !== null) {
    const known = hostOf(loadState()[String(tabId)]);
    if (known) return { host: known, certain: true };
  }
  return { host: null, certain: false };
}

// ── класифікація хоста ──────────────────────────────────────────────────────

/**
 * readonlyHosts перевіряємо ПЕРШИМИ: Kibana живе на foxtrot.cloud, тобто
 * всередині дозволеного домену стендів, і зворотний порядок її б розблокував.
 */
function classify(host, config) {
  if (!host) return null;
  for (const entry of config.readonlyHosts || []) {
    if (entry.match && host.includes(String(entry.match).toLowerCase())) return entry;
  }
  return null;
}

// ── Bash: записи через CLI та HTTP ──────────────────────────────────────────

/**
 * Шаблони прив'язані до ПОЗИЦІЇ КОМАНДИ: початок рядка або після ; && || | $( ` .
 * Без цього хук блокував би сам себе — `grep "gh pr comment" CLAUDE.md` і будь-яку
 * згадку шаблона в тексті аргумента. Перевірено на собі.
 */
const CMD_START = String.raw`(?:^|[\n;|&]|\$\(|` + '`' + String.raw`)\s*`;

const BASH_WRITE_PATTERNS = [
  { re: new RegExp(CMD_START + String.raw`gh\s+(?:pr|issue|release)\s+(?:comment|review|create|close|edit|merge|delete|ready|reopen|lock|unlock)\b`), what: 'gh — зміна стану PR/issue' },
  { re: new RegExp(CMD_START + String.raw`gh\s+api\b[^|;&]*-X\s*(?:POST|PUT|PATCH|DELETE)\b`, 'i'), what: 'gh api з мутуючим методом' },
  { re: new RegExp(CMD_START + String.raw`glab\s+(?:mr|issue)\s+(?:create|note|approve|merge|close|update)\b`), what: 'glab — зміна стану MR/issue' },
  { re: new RegExp(CMD_START + String.raw`curl\b[^|;&]*\s-X\s*(?:POST|PUT|PATCH|DELETE)\b`, 'i'), what: 'curl з мутуючим методом' },
  { re: new RegExp(CMD_START + String.raw`curl\b[^|;&]*\s(?:--data|--data-raw|--data-binary|--form|-d\s|-F\s)`), what: 'curl з тілом запиту' },
  // PowerShell-еквіваленти curl: Invoke-WebRequest / Invoke-RestMethod та їхні аліаси.
  { re: new RegExp(CMD_START + String.raw`(?:Invoke-WebRequest|Invoke-RestMethod|iwr|irm|wget)\b[^|;&]*-Method\s+(?:POST|PUT|PATCH|DELETE)\b`, 'i'), what: 'PowerShell-запит з мутуючим методом' },
  { re: new RegExp(CMD_START + String.raw`(?:Invoke-WebRequest|Invoke-RestMethod|iwr|irm)\b[^|;&]*-(?:Body|InFile|Form)\b`, 'i'), what: 'PowerShell-запит з тілом' },
];

function checkBash(command, config) {
  if (typeof command !== 'string') return null;

  const hit = BASH_WRITE_PATTERNS.find((p) => p.re.test(command));
  if (!hit) return null;

  // Мутуючий запит сам собою не заборонений — заборонений він у бік чужої системи.
  const targets = (config.readonlyHosts || []).filter(
    (e) => e.match && command.toLowerCase().includes(String(e.match).toLowerCase())
  );
  if (targets.length === 0) return null;

  const names = targets.map((t) => t.label || t.match).join(', ');
  return `${hit.what} у бік ${names}. CLAUDE.md: у зовнішніх системах — тільки читання. `
       + 'Підготуй текст і віддай Ярославу — публікує він сам.';
}

// ── MCP-сервери зовнішніх систем ────────────────────────────────────────────

/**
 * Конектор до Jira чи GitLab пише напряму: ні браузера, ні шелла в цьому шляху немає.
 * Тому тут свідомо fail-closed: пропускаємо лише те, чиє імʼя явно читає.
 * Повертає причину блокування або null.
 */
function checkMcpTool(fullName, config) {
  const m = /^mcp__([^_]+(?:[^_]|_(?!_))*)__(.+)$/.exec(fullName);
  if (!m) return null;

  const [, server, tool] = m;
  const serverLc = server.toLowerCase();

  const known = (config.mcpExternalServers || []).find((s) => serverLc.includes(String(s).toLowerCase()));
  if (!known) return null;

  const toolLc = tool.toLowerCase();
  const reads = config.mcpReadVerbs || [];
  if (reads.some((v) => toolLc.includes(String(v).toLowerCase()))) return null;

  return `${fullName} — запис у зовнішню систему (${known}). CLAUDE.md: там тільки читання. `
       + 'Якщо ця тулза насправді читає, додай її дієслово в mcpReadVerbs у '
       + '.claude/hooks/readonly-guard.config.json.';
}

// ── головне ─────────────────────────────────────────────────────────────────

function main() {
  let payload;
  try {
    payload = JSON.parse(fs.readFileSync(0, 'utf8'));
  } catch {
    respond(null); // Не зрозуміли вхід — не наша справа блокувати.
  }

  const config = readJson(CONFIG_PATH, null);
  if (!config) respond(null); // Немає конфігу — охорона вимкнена, а не «блокуй усе».

  const fullName = payload.tool_name || '';
  const toolInput = payload.tool_input || {};

  // PowerShell — окремий інструмент із тим самим полем `command`. На Windows він
  // основний, тому матчити лише Bash означало б лишити двері відчиненими.
  if (fullName === 'Bash' || fullName === 'PowerShell') {
    const reason = checkBash(toolInput.command, config);
    respond(reason ? 'deny' : null, reason);
  }

  if (!fullName.startsWith('mcp__claude-in-chrome__')) {
    const reason = checkMcpTool(fullName, config);
    respond(reason ? 'deny' : null, reason);
  }
  const tool = fullName.slice('mcp__claude-in-chrome__'.length);

  // navigate / tabs_create — самі по собі читання, але це наше єдине джерело
  // знання про те, що у вкладці лежить. Запамʼятовуємо і пропускаємо.
  if (tool === 'navigate' || tool === 'tabs_create_mcp') {
    rememberTab(toolInput.tabId ?? toolInput.tab_id, toolInput.url);
    respond(null);
  }

  if (READ_ONLY_TOOLS.has(tool)) respond(null);

  const { host } = resolveHost(toolInput);
  const entry = classify(host, config);
  if (!entry || entry.mode === 'off') respond(null);

  const label = entry.label || entry.match;

  if (WRITE_TOOLS.has(tool)) {
    const mode = config.uploadsAndScripts === 'ask' ? 'ask' : 'deny';
    respond(mode,
      `${tool} на ${label} (${host}) — це запис у зовнішню систему. `
      + 'Читати сторінку треба через read_page / get_page_text. '
      + 'CLAUDE.md: у Jira, GitLab і Kibana — тільки читання.');
  }

  if (INTERACTION_TOOLS.has(tool)) {
    if (entry.mode === 'deny') {
      respond('deny',
        `Взаємодія зі сторінкою ${label} (${host}) заблокована режимом "deny". `
        + 'Читай через read_page / get_page_text; змінити режим — '
        + '.claude/hooks/readonly-guard.config.json.');
    }
    respond('ask',
      `${label} (${host}) — система «тільки читання». Дія ${tool} допустима, `
      + 'лише якщо це читання: розгорнути опис, відкрити вкладку, ввести запит у Kibana. '
      + 'Якщо це коментар, статус, лейбл, апрув чи збереження — відмов.');
  }

  respond(null);
}

main();
