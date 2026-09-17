#!/usr/bin/env node
/**
 * Перевірка readonly-guard: `node .claude/hooks/readonly-guard.test.js`
 *
 * Кейси навмисно містять рядки на кшталт "gh pr comment" як ДАНІ. Якщо хук
 * почне блокувати сам запуск цього файлу — значить, прив'язку до позиції
 * команди зламали, і це рівно та регресія, яку тест ловить.
 */

'use strict';

const { execFileSync } = require('child_process');
const path = require('path');

const GUARD = path.join(__dirname, 'readonly-guard.js');

/** Повертає permissionDecision або 'pass', якщо хук не втрутився. */
function ask(toolName, toolInput) {
  const out = execFileSync(process.execPath, [GUARD], {
    input: JSON.stringify({ tool_name: toolName, tool_input: toolInput }),
    encoding: 'utf8',
  });
  if (!out.trim()) return 'pass';
  return JSON.parse(out).hookSpecificOutput.permissionDecision;
}

const chrome = (t) => `mcp__claude-in-chrome__${t}`;
const bash = (command) => ask('Bash', { command });

const cases = [];
const expect = (name, actual, wanted) => cases.push({ name, actual, wanted });

// ── вкладки: спершу навчаємо хук, де яка ──────────────────────────────────
ask(chrome('navigate'), { url: 'https://jira.entri.com.ua/browse/CMS-27643', tabId: 7 });
ask(chrome('navigate'), { url: 'https://yaroslav.foxtrot.cloud/uk/shop/mobilnye_telefony.html', tabId: 9 });
ask(chrome('navigate'), { url: 'http://foxtrot01-dev-dyn-kibana-g.foxtrot.cloud/app/discover', tabId: 3 });
ask(chrome('navigate'), { url: 'https://git.foxtrot.ua/new-cms-foxtrot/evinent/foxtrot-site/-/merge_requests/1', tabId: 5 });

// ── Jira / GitLab: читання вільне, взаємодія питається, запис заборонений ──
expect('read_page у Jira', ask(chrome('read_page'), { tabId: 7 }), 'pass');
expect('get_page_text у Jira', ask(chrome('get_page_text'), { tabId: 7 }), 'pass');
expect('клік у Jira', ask(chrome('computer'), { tabId: 7, action: 'left_click' }), 'ask');
expect('вкладення в Jira', ask(chrome('file_upload'), { tabId: 7 }), 'deny');
expect('JS у Jira', ask(chrome('javascript_tool'), { tabId: 7, code: '1' }), 'deny');
expect('клік у GitLab', ask(chrome('computer'), { tabId: 5, action: 'left_click' }), 'ask');

// ── Kibana всередині foxtrot.cloud не має провалюватись у дозволені ────────
expect('запит у Kibana', ask(chrome('form_input'), { tabId: 3, value: 'level:Error' }), 'ask');
expect('JS у Kibana', ask(chrome('javascript_tool'), { tabId: 3, code: '1' }), 'deny');

// ── стенд продукту: працюємо без перешкод ─────────────────────────────────
expect('клік на стенді', ask(chrome('computer'), { tabId: 9, action: 'left_click' }), 'pass');
expect('JS на стенді', ask(chrome('javascript_tool'), { tabId: 9, code: '1' }), 'pass');
expect('навігація на стенд', ask(chrome('navigate'), { url: 'https://www.foxtrot.com.ua/', tabId: 11 }), 'pass');
expect('невідома вкладка', ask(chrome('computer'), { tabId: 404, action: 'left_click' }), 'pass');

// ── Bash: мутації в бік чужих систем ──────────────────────────────────────
expect('gh коментар до PR', bash('gh' + ' pr comment 42 --repo github.com/a/b --body x'), 'deny');
expect('glab нотатка до MR', bash('glab' + ' mr note 5 -R git.foxtrot.ua/x/y'), 'deny');
expect('POST у Jira', bash('curl -X POST https://jira.entri.com.ua/rest/api/2/issue -d @c.json'), 'deny');
expect('GET у Jira', bash('curl https://jira.entri.com.ua/browse/CMS-1'), 'pass');
expect('POST на стенд', bash('curl -X POST https://yaroslav.foxtrot.cloud/api/cart -d id=1'), 'pass');
expect('git status', bash('git status --short'), 'pass');
expect('playwright', bash('npx playwright test'), 'pass');

// ── головна регресія: шаблон як ДАНІ, а не як команда ─────────────────────
expect('grep по шаблону', bash('grep -rn "gh' + ' pr comment" CLAUDE.md'), 'pass');
expect('echo з шаблоном', bash('echo \'{"cmd":"gh' + ' pr create"}\' > /tmp/x.json'), 'pass');
expect('шлях із назвою jira', bash('cat qa-toolkit/tasks/CMS-1/jira.entri.com.ua.txt'), 'pass');

// ── вивід ─────────────────────────────────────────────────────────────────
let failed = 0;
for (const c of cases) {
  const ok = c.actual === c.wanted;
  if (!ok) failed++;
  console.log(`${ok ? 'ok  ' : 'FAIL'}  ${c.name.padEnd(28)} → ${c.actual}${ok ? '' : ` (очікували ${c.wanted})`}`);
}
console.log(`\n${cases.length - failed}/${cases.length} пройшло`);
process.exit(failed ? 1 : 0);
