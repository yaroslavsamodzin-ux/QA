#!/usr/bin/env node
/**
 * qa-toolkit/testdata/autofill.js
 *
 * Проганяє одне поле форми через увесь набір граничних значень і фіксує,
 * як форма відреагувала: валідація браузера, повідомлення про помилку,
 * перехід на іншу сторінку, помилки в консолі.
 *
 * Запуск:
 *   node qa-toolkit/testdata/autofill.js --list                       показати набори
 *   node qa-toolkit/testdata/autofill.js --list email                 показати значення набору
 *   node qa-toolkit/testdata/autofill.js https://site/reg \
 *        --field "#email" --set email --submit "button[type=submit]" --headed
 *
 * Опції:
 *   --field <css>    поле, яке заповнюємо (обовʼязково)
 *   --set <назва>    набір із payloads.json (обовʼязково)
 *   --submit <css>   кнопка відправки; без неї перевіряється лише валідація поля
 *   --error <css>    де шукати текст помилки (типово поширені селектори)
 *   --wait <ms>      пауза після дії (типово 500)
 *   --headed         показати браузер
 *   --storage <f>    storageState.json для авторизації
 *   --out <file.md>  куди зберегти звіт
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const PAYLOADS = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'payloads.json'), 'utf8')
);

const DEFAULT_ERROR_SEL = [
  '[role="alert"]',
  '[aria-invalid="true"] ~ *',
  '.error', '.error-message', '.field-error', '.help-block',
  '.invalid-feedback', '.Mui-error', '.ant-form-item-explain-error',
].join(', ');

function parseArgs(argv) {
  const o = { url: null, field: null, set: null, submit: null, error: null, wait: 500, headed: false, storage: null, out: null, list: undefined };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--list') o.list = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : '*';
    else if (a === '--field') o.field = argv[++i];
    else if (a === '--set') o.set = argv[++i];
    else if (a === '--submit') o.submit = argv[++i];
    else if (a === '--error') o.error = argv[++i];
    else if (a === '--wait') o.wait = Number(argv[++i]);
    else if (a === '--storage') o.storage = argv[++i];
    else if (a === '--out') o.out = argv[++i];
    else if (a === '--headed') o.headed = true;
    else if (a.startsWith('--')) throw new Error(`Невідомий параметр: ${a}`);
    else o.url = a;
  }
  return o;
}

function listSets(which) {
  const names = Object.keys(PAYLOADS).filter((k) => k !== '_meta');
  if (which === '*') {
    console.log('Доступні набори:\n');
    for (const n of names) console.log(`  ${n.padEnd(14)} ${PAYLOADS[n].length} значень`);
    console.log('\nПоказати набір:  --list <назва>');
    return;
  }
  if (!PAYLOADS[which]) {
    console.error(`Немає набору «${which}». Є: ${names.join(', ')}`);
    process.exit(1);
  }
  console.log(`\nНабір «${which}» (${PAYLOADS[which].length}):\n`);
  for (const p of PAYLOADS[which]) {
    console.log(`  [${p.expect.padEnd(6)}] ${JSON.stringify(p.value).slice(0, 70).padEnd(72)} ${p.label}`);
  }
}

/* Чи вважаємо, що форма поскаржилась на значення. */
function rejected(r) {
  return !!(r.validationMessage || r.errorText);
}

function verdict(p, r) {
  if (r.crashed) return { mark: '!', note: 'скрипт впав на цьому значенні' };
  if (p.expect === 'escape') {
    if (r.probeFired) return { mark: 'X', note: 'КОД ВИКОНАВСЯ — інʼєкція проходить' };
    return { mark: '?', note: 'не виконався; перевір очима, як значення виводиться назад' };
  }
  const wasRejected = rejected(r);
  if (p.expect === 'accept' && wasRejected) return { mark: 'X', note: 'валідне значення відхилено' };
  if (p.expect === 'reject' && !wasRejected) return { mark: 'X', note: 'невалідне значення прийнято' };
  return { mark: 'v', note: '' };
}

async function run() {
  const o = parseArgs(process.argv.slice(2));
  if (o.list !== undefined) return listSets(o.list);

  if (!o.url || !o.field || !o.set) {
    console.error('Потрібні: <url> --field <css> --set <назва>.  Довідка: --list');
    process.exit(1);
  }
  const payloads = PAYLOADS[o.set];
  if (!payloads) {
    console.error(`Немає набору «${o.set}». Є: ${Object.keys(PAYLOADS).filter((k) => k !== '_meta').join(', ')}`);
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: !o.headed });
  const ctx = await browser.newContext({
    storageState: o.storage || undefined,
    ignoreHTTPSErrors: true,
  });
  const page = await ctx.newPage();

  let probeFired = false;
  page.on('console', (m) => {
    if (m.text().includes('qa-xss-probe')) probeFired = true;
  });
  page.on('dialog', async (d) => { probeFired = true; await d.dismiss(); });

  const rows = [];
  console.log(`\nПоле ${o.field} — набір «${o.set}» (${payloads.length} значень)\n`);

  for (const p of payloads) {
    const r = { consoleErrors: 0 };
    probeFired = false;
    const errs = [];
    const onErr = (m) => { if (m.type() === 'error') errs.push(m.text().slice(0, 120)); };
    page.on('console', onErr);

    try {
      await page.goto(o.url, { waitUntil: 'load', timeout: 45000 });
      const field = page.locator(o.field).first();
      await field.waitFor({ state: 'visible', timeout: 10000 });

      await field.fill('');
      await field.fill(p.value);
      await field.blur().catch(() => {});
      await page.waitForTimeout(o.wait);

      const urlBefore = page.url();

      if (o.submit) {
        await page.locator(o.submit).first().click({ timeout: 10000 }).catch(() => {});
        await page.waitForTimeout(o.wait + 400);
      }

      r.navigated = page.url() !== urlBefore;
      r.validationMessage = await field
        .evaluate((el) => (el.checkValidity && !el.checkValidity() ? el.validationMessage : ''))
        .catch(() => '');

      const errLoc = page.locator(o.error || DEFAULT_ERROR_SEL);
      const errCount = await errLoc.count().catch(() => 0);
      for (let i = 0; i < Math.min(errCount, 5); i++) {
        const el = errLoc.nth(i);
        if (await el.isVisible().catch(() => false)) {
          const t = (await el.innerText().catch(() => '')).trim();
          if (t) { r.errorText = t.slice(0, 120); break; }
        }
      }
      r.probeFired = probeFired;
    } catch (e) {
      r.crashed = true;
      r.errorText = String(e).split('\n')[0].slice(0, 120);
    }

    page.off('console', onErr);
    r.consoleErrors = errs.length;
    r.consoleSample = errs[0] || '';

    const v = verdict(p, r);
    rows.push({ p, r, v });
    console.log(
      `  ${v.mark} [${p.expect.padEnd(6)}] ${JSON.stringify(p.value).slice(0, 46).padEnd(48)} ` +
        `${(r.validationMessage || r.errorText || (r.navigated ? 'форма відправилась' : 'без реакції')).slice(0, 50)}`
    );
  }

  await browser.close();

  const md = render(o, rows);
  const outFile = o.out || path.join(__dirname, 'out', `${o.set}-${Date.now()}.md`);
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  fs.writeFileSync(outFile, md);

  const bad = rows.filter((x) => x.v.mark === 'X').length;
  const unknown = rows.filter((x) => x.v.mark === '?').length;
  console.log(`\nЗвіт: ${outFile}`);
  console.log(`Розбіжностей: ${bad}. Потребує ручної перевірки: ${unknown}.`);
}

function render(o, rows) {
  const L = [];
  L.push(`# Перевірка поля \`${o.field}\` — набір «${o.set}»`, ``);
  L.push(`Сторінка: ${o.url}`, `Час: ${new Date().toLocaleString('uk-UA')}`, ``);
  L.push(`| | Значення | Що це | Очікували | Реакція форми |`);
  L.push(`|:-:|---|---|:-:|---|`);
  for (const { p, r, v } of rows) {
    const reaction =
      r.validationMessage ? `валідація: ${r.validationMessage}` :
      r.errorText ? `помилка: ${r.errorText}` :
      r.navigated ? 'форма відправилась' : 'без реакції';
    const val = JSON.stringify(p.value).replace(/\|/g, '\\|').slice(0, 60);
    L.push(`| ${v.mark} | \`${val}\` | ${p.label} | ${p.expect} | ${reaction.replace(/\|/g, '\\|')} |`);
  }
  L.push(``, `Позначки: \`v\` збіглося з очікуванням · \`X\` розбіжність · \`?\` треба глянути очима · \`!\` скрипт впав`, ``);

  const bad = rows.filter((x) => x.v.mark === 'X');
  if (bad.length) {
    L.push(`## Розбіжності (${bad.length})`, ``);
    for (const { p, r, v } of bad) {
      L.push(`- \`${JSON.stringify(p.value).slice(0, 60)}\` (${p.label}) — ${v.note}. ` +
             `Реакція: ${r.validationMessage || r.errorText || 'жодної'}`);
    }
    L.push(``);
  }
  const unknown = rows.filter((x) => x.v.mark === '?');
  if (unknown.length) {
    L.push(`## Перевірити очима (${unknown.length})`, ``,
      `Значення прийнялись. Треба подивитись, як вони **виводяться назад** — у списку,`,
      `в картці, в листі, в експорті CSV. Саме там проявляється погана санітизація.`, ``);
    for (const { p } of unknown) L.push(`- \`${JSON.stringify(p.value).slice(0, 60)}\` — ${p.label}`);
    L.push(``);
  }
  return L.join('\n');
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
