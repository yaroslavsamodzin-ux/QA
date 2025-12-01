// tests/a11y.axe.spec.js
const { test, expect } = require('@playwright/test');
const { AxeBuilder } = require('@axe-core/playwright');
const fs = require('fs');
const path = require('path');

/* ===== helpers ===== */
const RUN_TS = new Date().toISOString().slice(0,19).replace(/[:T]/g,'-');
const runDir = (project) => path.join('reports', 'a11y', project, RUN_TS);

function ensureDir(dir) { if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true }); }
const slug = s => String(s).replace(/^https?:\/\//, '').replace(/[^\w.-]+/g, '_');

function tipFor(ruleId) {
  switch (ruleId) {
    case 'image-alt': return 'Додайте змістовний alt або role="presentation".';
    case 'color-contrast': return 'Підвищіть контраст до WCAG AA.';
    case 'label':
    case 'aria-input-field-name':
    case 'form-field-multiple-labels': return 'Зв’яжіть поле з <label for> або додайте aria-label.';
    case 'button-name': return 'Кнопка має мати текст або aria-label.';
    case 'link-name': return 'Посилання має мати текст або aria-label.';
    case 'list': return '<ul>/<ol> мають містити тільки <li> напряму.';
    case 'listitem': return '<li> має бути всередині <ul>/<ol>.';
    case 'aria-required-children': return 'ARIA-роль вимагає потрібні дочірні елементи (наприклад, <li> у списках).';
    case 'meta-viewport': return 'Приберіть maximum-scale=1 / дозвольте user-scalable.';
    case 'select-name': return '<select> повинен мати ім’я: <label>, aria-label або aria-labelledby.';
    default: return `Перевірте правило "${ruleId}" за посиланням helpUrl.`;
  }
}

function resetSummary(project) {
  const dir = runDir(project);
  ensureDir(dir);
  const header = `# A11y summary — ${project}\nДата/час: ${RUN_TS}\n\n`;
  fs.writeFileSync(path.join(dir, 'summary.md'), header, 'utf8'); // перезапис
}

async function saveReport(project, pageUrl, data) {
  const dir = runDir(project);
  ensureDir(dir);
  const base = `${slug(pageUrl)}`;

  // JSON (детальний)
  fs.writeFileSync(path.join(dir, `${base}.json`), JSON.stringify(data, null, 2), 'utf8');

  // короткий Markdown-summary (append)
  const list = data.violations || [];
  const lines = [];
  lines.push(`### ${pageUrl}`);
  lines.push(`- **serious/critical** порушень: **${list.length}**`);
  list.slice(0, 8).forEach(v => {
    lines.push(`  - \`${v.id}\` — ${v.help} → ${tipFor(v.id)} (${v.nodes?.length ?? 0} ел.)`);
  });
  lines.push('');
  fs.appendFileSync(path.join(dir, 'summary.md'), lines.join('\n'), 'utf8');
}

/* ===== main test ===== */
test('A11y smoke: головна + каталог + 1 PDP (wcag2a/aa, serious/critical)', async ({ page, baseURL }, testInfo) => {
  const project = testInfo.project?.name || 'default';

  // чистий summary для цього прогону
  resetSummary(project);

  // Працюємо навіть без конфіга
  const effectiveBase = process.env.BASE_URL || baseURL || 'https://automoto.com.lv';
  const isLV = String(effectiveBase).includes('automoto.com.lv');
  const catalogPath = isLV ? '/ru/bu-avto' : '/car';

  const targets = ['/', catalogPath];

  // Знайдемо справжній PDP-лінк у каталозі (а не підкаталог)
  await page.goto(new URL(catalogPath, effectiveBase).toString(), { waitUntil: 'domcontentloaded' });

  // зберемо всі абсолютні href і відфільтруємо PDP-кандидати
  const origin = new URL(effectiveBase).origin;
  const hrefs = await page.$$eval('a[href]', as => as.map(a => a.href));
  const candidates = hrefs
    .filter(u => u.startsWith(origin))
    .filter(u => /\/detail\//i.test(u) || /\d/.test(new URL(u).pathname))      // є цифри або /detail/
    .filter(u => !/\/(Europe|latviya|region|city)\b/i.test(u))                 // відкинути регіони
    .filter(u => !/\/(car|ru\/bu-avto)\/?$/i.test(u));                         // відкинути корінь каталогу

  const pdpUrl = candidates[0];
  if (pdpUrl) targets.push(pdpUrl);

  // ENV-настройки
  //   A11Y_IGNORE=meta-viewport,list  (ігнорувати правила)
  //   A11Y_THRESHOLD=0                (падати якщо >0)
  const IGNORE_RULES = (process.env.A11Y_IGNORE || '')
    .split(',').map(s => s.trim()).filter(Boolean);
  const thEnv = process.env.A11Y_THRESHOLD;

  for (const t of targets) {
    const url = t.startsWith('http') ? t : new URL(t, effectiveBase).toString();
    await page.goto(url, { waitUntil: 'domcontentloaded' });

    const axe = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    const filtered = (axe.violations || []).filter(v =>
      ['serious','critical'].includes(String(v.impact || '').toLowerCase()) &&
      !IGNORE_RULES.includes(v.id)
    );

    await saveReport(project, url, { url, violations: filtered });

    if (thEnv !== undefined) {
      const THRESHOLD = Number.isNaN(Number(thEnv)) ? 0 : Number(thEnv);
      expect(
        filtered.length,
        `Serious/Critical A11y (${filtered.length}) > ${THRESHOLD}: ${url}`
      ).toBeLessThanOrEqual(THRESHOLD);
    } else {
      console.log(`[a11y] ${project} ${url} serious/critical: ${filtered.length}`);
    }
  }
});
