#!/usr/bin/env node
/**
 * qa-toolkit/responsive/responsive.js
 *
 * Проганяє сторінку по всіх розширеннях і сам шукає проблеми верстки:
 *   - горизонтальний скрол + конкретні елементи, які вилазять за екран
 *   - обрізаний текст (ellipsis / overflow hidden)
 *   - тач-таргети менші за 44px на мобільних ширинах
 *   - биті картинки
 *   - помилки в консолі та запити 4xx/5xx під час завантаження
 *
 * Запуск:
 *   node qa-toolkit/responsive/responsive.js https://example.com
 *   node qa-toolkit/responsive/responsive.js https://a.com https://b.com --set mobile
 *   node qa-toolkit/responsive/responsive.js https://example.com --viewports 360,768,1440
 *   node qa-toolkit/responsive/responsive.js https://example.com --storage auth.json --headed
 *
 * Результат: папка зі скріншотами + report.md + report.json
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const MAX_ITEMS = 15; // скільки проблем одного типу показувати в звіті

// ---------------------------------------------------------------- аргументи

function parseArgs(argv) {
  const opts = {
    urls: [],
    set: 'all',
    viewports: null,
    out: null,
    wait: 800,
    headed: false,
    storage: null,
    shots: true,
    timeout: 45000,
    tapMin: 24, // WCAG 2.2 AA (2.5.8); постав 44 для AAA
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--set') opts.set = argv[++i];
    else if (a === '--viewports') opts.viewports = argv[++i];
    else if (a === '--out') opts.out = argv[++i];
    else if (a === '--wait') opts.wait = Number(argv[++i]);
    else if (a === '--timeout') opts.timeout = Number(argv[++i]);
    else if (a === '--tap-min') opts.tapMin = Number(argv[++i]);
    else if (a === '--storage') opts.storage = argv[++i];
    else if (a === '--headed') opts.headed = true;
    else if (a === '--no-shots') opts.shots = false;
    else if (a.startsWith('--')) throw new Error(`Невідомий параметр: ${a}`);
    else opts.urls.push(a);
  }
  if (!opts.urls.length) {
    console.error(`
Вкажи хоча б один URL.

  node qa-toolkit/responsive/responsive.js <url> [url2 ...] [опції]

Опції:
  --set mobile|tablet|desktop|all   набір розширень (типово all)
  --viewports 360,768,1440          свої ширини замість набору
  --out <dir>                       куди класти звіт
  --wait <ms>                       пауза після завантаження (типово 800)
  --timeout <ms>                    таймаут навігації (типово 45000)
  --tap-min <px>                    мін. розмір тач-таргета (типово 24 = WCAG AA)
  --storage <file.json>             storageState Playwright для авторизації
  --headed                          показати браузер
  --no-shots                        без скріншотів, тільки аналіз
`);
    process.exit(1);
  }
  return opts;
}

function resolveViewports(opts) {
  const cfg = JSON.parse(
    fs.readFileSync(path.join(__dirname, 'viewports.json'), 'utf8')
  );
  if (opts.viewports) {
    return opts.viewports.split(',').map((w) => {
      const width = Number(w.trim());
      if (!width) throw new Error(`Погана ширина: ${w}`);
      return {
        name: `${width}`,
        width,
        height: width < 600 ? 800 : 900,
        mobile: width <= 640,
      };
    });
  }
  if (opts.set === 'all') return [...cfg.mobile, ...cfg.tablet, ...cfg.desktop];
  if (!cfg[opts.set]) throw new Error(`Невідомий набір: ${opts.set}`);
  return cfg[opts.set];
}

// ------------------------------------------------- аналіз усередині сторінки

/* Виконується в контексті браузера. Повертає тільки серіалізовані дані. */
function auditPage([limit, tapMin]) {
  const cssPath = (el) => {
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && parts.length < 4) {
      let part = node.tagName.toLowerCase();
      if (node.id) {
        parts.unshift(`${part}#${node.id}`);
        break;
      }
      const cls = (node.getAttribute('class') || '')
        .trim()
        .split(/\s+/)
        .filter(Boolean)
        .slice(0, 2)
        .join('.');
      if (cls) part += `.${cls}`;
      parts.unshift(part);
      node = node.parentElement;
    }
    return parts.join(' > ');
  };

  const visible = (el, rect) => {
    if (rect.width === 0 && rect.height === 0) return false;
    const st = getComputedStyle(el);
    return (
      st.display !== 'none' &&
      st.visibility !== 'hidden' &&
      Number(st.opacity) !== 0
    );
  };

  const snippet = (el) => (el.innerText || el.textContent || '').trim().slice(0, 70);

  /* Текст «тільки для скрінрідера» та skip-лінки — навмисно сховані,
     це не баг верстки. Відсіюємо, щоб не засмічувати звіт. */
  const srOnly = (el, rect, st) => {
    if (rect.width <= 1 || rect.height <= 1) return true;
    if (/inset\(\s*50%/.test(st.clipPath || '')) return true;
    if ((st.clip || '').replace(/\s/g, '') === 'rect(0px,0px,0px,0px)') return true;
    return false;
  };

  const vw = document.documentElement.clientWidth;
  const docW = Math.max(
    document.documentElement.scrollWidth,
    document.body ? document.body.scrollWidth : 0
  );

  const all = Array.from(document.querySelectorAll('body *'));

  // 1. елементи, що вилазять за правий/лівий край
  const overflowers = [];
  for (const el of all) {
    const r = el.getBoundingClientRect();
    if (!visible(el, r)) continue;
    const st = getComputedStyle(el);
    if (srOnly(el, r, st)) continue;
    if (st.position === 'fixed') continue; // модалки/хедери рахуємо окремо
    const overRight = r.right - vw;
    if (overRight > 1 || r.left < -1) {
      overflowers.push({
        sel: cssPath(el),
        overflowPx: Math.round(overRight > 1 ? overRight : -r.left),
        side: overRight > 1 ? 'right' : 'left',
        width: Math.round(r.width),
        text: snippet(el),
      });
    }
  }
  // лишаємо найглибші/найгірші, прибираючи батьків тих самих проблем
  overflowers.sort((a, b) => b.overflowPx - a.overflowPx);

  // 2. обрізаний текст
  const truncated = [];
  for (const el of all) {
    const r = el.getBoundingClientRect();
    if (!visible(el, r)) continue;
    const txt = snippet(el);
    if (!txt) continue;
    const hasElementChildren = el.children.length > 0;
    const st = getComputedStyle(el);
    if (srOnly(el, r, st)) continue;
    /* Якщо видимий бокс майже нульовий — текст сховали навмисно
       (іконкова кнопка з підписом для скрінрідера), а не обрізали. */
    if (el.clientWidth < 24 || el.clientHeight < 8) continue;
    const hidesX = /hidden|clip|ellipsis/.test(st.overflowX + st.textOverflow);
    const hidesY = /hidden|clip/.test(st.overflowY);
    const clamped = st.webkitLineClamp && st.webkitLineClamp !== 'none';
    if (hidesX && el.scrollWidth > el.clientWidth + 1 && !hasElementChildren) {
      truncated.push({
        sel: cssPath(el),
        axis: 'x',
        cutPx: el.scrollWidth - el.clientWidth,
        text: txt,
      });
    } else if (
      hidesY &&
      !clamped &&
      el.scrollHeight > el.clientHeight + 2 &&
      !hasElementChildren
    ) {
      truncated.push({
        sel: cssPath(el),
        axis: 'y',
        cutPx: el.scrollHeight - el.clientHeight,
        text: txt,
      });
    }
  }
  truncated.sort((a, b) => b.cutPx - a.cutPx);

  // 3. малі тач-таргети
  const tapSel = 'a, button, input, select, textarea, [role="button"], [onclick]';
  const tinyTargets = [];
  for (const el of Array.from(document.querySelectorAll(tapSel))) {
    const r = el.getBoundingClientRect();
    if (!visible(el, r)) continue;
    const st = getComputedStyle(el);
    if (srOnly(el, r, st)) continue;
    // WCAG 2.5.8 виключає посилання всередині рядка тексту
    if (el.tagName === 'A' && (st.display === 'inline' || st.display === 'contents')) continue;
    if (r.width < tapMin || r.height < tapMin) {
      tinyTargets.push({
        sel: cssPath(el),
        size: `${Math.round(r.width)}x${Math.round(r.height)}`,
        text: snippet(el) || el.getAttribute('aria-label') || '',
      });
    }
  }

  // 4. биті картинки
  const brokenImages = Array.from(document.images)
    .filter((img) => {
      if (!img.complete || img.naturalWidth !== 0) return false;
      const raw = img.getAttribute('src');
      // порожній src резолвиться в URL сторінки — це лези-завантаження, не бита картинка
      if (!raw || !raw.trim()) return false;
      if ((img.currentSrc || img.src) === location.href) return false;
      return true;
    })
    .map((img) => ({ sel: cssPath(img), src: (img.currentSrc || img.src || '').slice(0, 120) }));

  return {
    viewportWidth: vw,
    documentWidth: docW,
    hasHScroll: docW > vw + 1,
    overflowScrollPx: Math.max(0, docW - vw),
    overflowers: overflowers.slice(0, limit),
    overflowersTotal: overflowers.length,
    truncated: truncated.slice(0, limit),
    truncatedTotal: truncated.length,
    tinyTargets: tinyTargets.slice(0, limit),
    tinyTargetsTotal: tinyTargets.length,
    brokenImages: brokenImages.slice(0, limit),
    brokenImagesTotal: brokenImages.length,
  };
}

// ------------------------------------------------------------------- прогін

async function run() {
  const opts = parseArgs(process.argv.slice(2));
  const viewports = resolveViewports(opts);

  const stamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const outDir = opts.out || path.join(__dirname, 'report', stamp);
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ headless: !opts.headed });
  const results = [];

  for (const url of opts.urls) {
    for (const vp of viewports) {
      const ctx = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        isMobile: vp.mobile,
        hasTouch: vp.mobile,
        deviceScaleFactor: vp.mobile ? 2 : 1,
        storageState: opts.storage || undefined,
        ignoreHTTPSErrors: true,
      });
      const page = await ctx.newPage();

      const consoleErrors = [];
      const badRequests = [];
      page.on('console', (m) => {
        if (m.type() === 'error') consoleErrors.push(m.text().slice(0, 200));
      });
      page.on('pageerror', (e) => consoleErrors.push(`[pageerror] ${String(e).slice(0, 200)}`));
      page.on('response', (r) => {
        if (r.status() >= 400) badRequests.push(`${r.status()} ${r.url().slice(0, 140)}`);
      });
      page.on('requestfailed', (r) => {
        const f = r.failure();
        badRequests.push(`FAILED ${(f && f.errorText) || ''} ${r.url().slice(0, 140)}`);
      });

      const entry = { url, viewport: vp.name, width: vp.width };
      const label = `${url} @ ${vp.width}px`;

      try {
        await page.goto(url, { waitUntil: 'load', timeout: opts.timeout });
        await page.waitForTimeout(opts.wait);
        try {
          await page.waitForLoadState('networkidle', { timeout: 5000 });
        } catch { /* сторінка з постійним поллінгом — не критично */ }

        const audit = await page.evaluate(auditPage, [MAX_ITEMS, opts.tapMin]);
        Object.assign(entry, audit);

        if (opts.shots) {
          const safe = url.replace(/[^a-z0-9]+/gi, '_').slice(0, 50);
          const file = path.join(outDir, `${safe}__${vp.name}.png`);
          await page.screenshot({ path: file, fullPage: true });
          entry.screenshot = path.basename(file);
        }
        console.log(
          `  ${entry.hasHScroll ? 'X' : 'v'} ${label} — ` +
            `overflow:${entry.overflowersTotal} обрізано:${entry.truncatedTotal} ` +
            `дрібні:${entry.tinyTargetsTotal} биті-img:${entry.brokenImagesTotal}`
        );
      } catch (e) {
        entry.error = String(e).split('\n')[0].slice(0, 200);
        console.log(`  ! ${label} — ${entry.error}`);
      }

      entry.consoleErrors = consoleErrors.slice(0, MAX_ITEMS);
      entry.consoleErrorsTotal = consoleErrors.length;
      entry.badRequests = [...new Set(badRequests)].slice(0, MAX_ITEMS);
      entry.badRequestsTotal = badRequests.length;
      results.push(entry);

      await ctx.close();
    }
  }

  await browser.close();

  fs.writeFileSync(
    path.join(outDir, 'report.json'),
    JSON.stringify({ generatedAt: new Date().toISOString(), results }, null, 2)
  );
  const md = renderMarkdown(results, outDir, opts.tapMin);
  fs.writeFileSync(path.join(outDir, 'report.md'), md);

  console.log(`\nЗвіт: ${path.join(outDir, 'report.md')}`);
  const problems = results.filter(hasProblems).length;
  console.log(
    problems
      ? `Проблеми знайдено на ${problems} з ${results.length} комбінацій.`
      : `Чисто на всіх ${results.length} комбінаціях.`
  );
}

function hasProblems(r) {
  return !!(
    r.error ||
    r.hasHScroll ||
    r.truncatedTotal ||
    r.tinyTargetsTotal ||
    r.brokenImagesTotal ||
    r.consoleErrorsTotal ||
    r.badRequestsTotal
  );
}

// -------------------------------------------------------------------- звіт

function renderMarkdown(results, outDir, tapMin) {
  const L = [];
  L.push(`# Звіт по верстці`, ``, `Згенеровано: ${new Date().toLocaleString('uk-UA')}`, ``);

  L.push(`## Зведення`, ``);
  L.push(`| URL | Ширина | H-скрол | Вилазить | Обрізано | Дрібні тапи | Биті img | JS-помилки | 4xx/5xx |`);
  L.push(`|---|---:|:---:|---:|---:|---:|---:|---:|---:|`);
  for (const r of results) {
    if (r.error) {
      L.push(`| ${r.url} | ${r.width} | — | — | — | — | — | — | помилка |`);
      continue;
    }
    L.push(
      `| ${r.url} | ${r.width} | ${r.hasHScroll ? `**+${r.overflowScrollPx}px**` : 'ок'} ` +
        `| ${r.overflowersTotal} | ${r.truncatedTotal} | ${r.tinyTargetsTotal} ` +
        `| ${r.brokenImagesTotal} | ${r.consoleErrorsTotal} | ${r.badRequestsTotal} |`
    );
  }
  L.push(``);

  for (const r of results) {
    if (!hasProblems(r)) continue;
    L.push(`---`, ``, `## ${r.url} — ${r.width}px (${r.viewport})`, ``);
    if (r.screenshot) L.push(`Скріншот: \`${r.screenshot}\``, ``);
    if (r.error) {
      L.push(`**Сторінка не відкрилась:** \`${r.error}\``, ``);
      continue;
    }

    if (r.hasHScroll) {
      L.push(
        `### Горизонтальний скрол: +${r.overflowScrollPx}px`,
        ``,
        `Документ ${r.documentWidth}px при вікні ${r.viewportWidth}px.`,
        ``
      );
    }
    if (r.overflowersTotal) {
      L.push(`### Вилазить за екран (${r.overflowersTotal})`, ``);
      for (const o of r.overflowers) {
        L.push(`- \`${o.sel}\` — на ${o.overflowPx}px за ${o.side === 'right' ? 'правий' : 'лівий'} край, ширина ${o.width}px${o.text ? ` — «${o.text}»` : ''}`);
      }
      L.push(``);
    }
    if (r.truncatedTotal) {
      L.push(`### Обрізаний текст (${r.truncatedTotal})`, ``);
      for (const t of r.truncated) {
        L.push(`- \`${t.sel}\` — сховано ${t.cutPx}px по ${t.axis === 'x' ? 'ширині' : 'висоті'} — «${t.text}»`);
      }
      L.push(``);
    }
    if (r.tinyTargetsTotal) {
      L.push(`### Тач-таргети < ${tapMin}px (${r.tinyTargetsTotal})`, ``);
      for (const t of r.tinyTargets) {
        L.push(`- \`${t.sel}\` — ${t.size}${t.text ? ` — «${t.text}»` : ''}`);
      }
      L.push(``);
    }
    if (r.brokenImagesTotal) {
      L.push(`### Биті картинки (${r.brokenImagesTotal})`, ``);
      for (const b of r.brokenImages) L.push(`- \`${b.sel}\` — ${b.src}`);
      L.push(``);
    }
    if (r.consoleErrorsTotal) {
      L.push(`### Помилки в консолі (${r.consoleErrorsTotal})`, ``);
      for (const c of r.consoleErrors) L.push(`- \`${c}\``);
      L.push(``);
    }
    if (r.badRequestsTotal) {
      L.push(`### Невдалі запити (${r.badRequestsTotal})`, ``);
      for (const b of r.badRequests) L.push(`- \`${b}\``);
      L.push(``);
    }
  }

  L.push(`---`, ``, `Скріншоти лежать поруч: \`${outDir}\``, ``);
  return L.join('\n');
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
