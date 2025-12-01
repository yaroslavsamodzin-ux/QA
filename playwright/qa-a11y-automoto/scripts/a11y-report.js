// scripts/a11y-report.js
const fs = require('fs');
const path = require('path');

function readJSONFiles(jsonFiles) {
  const rows = [];
  for (const filePath of jsonFiles) {
    const j = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const url = j.url;
    for (const v of (j.violations || [])) {
      rows.push({
        url,
        rule: v.id,
        impact: v.impact || '',
        count: (v.nodes || []).length,
        help: v.help || ''
      });
    }
  }
  return rows;
}

function toCSV(rows) {
  const header = 'url,rule,impact,count,help\n';
  const esc = (s) => `"${String(s ?? '').replace(/"/g, '""')}"`;
  return header + rows.map(r => [
    esc(r.url),
    esc(r.rule),
    esc(r.impact),
    r.count,
    esc(r.help)
  ].join(',')).join('\n');
}

const project = process.argv[2]; // automoto.lv | automoto.ua
if (!project) {
  console.error('Usage: node scripts/a11y-report.js <projectName>');
  process.exit(1);
}

const base = path.join('reports', 'a11y', project);
if (!fs.existsSync(base)) {
  console.error('Not found:', base, '\nСпочатку запусти тести, щоб зʼявився reports/a11y/<project>/...');
  process.exit(1);
}

// Зчитуємо вміст папки проекту: можуть бути як підпапки-прогони, так і "плоскі" JSON-файли
const entries = fs.readdirSync(base, { withFileTypes: true });

// 1) Варіант із папками прогонів
const runDirs = entries
  .filter(e => e.isDirectory() && /^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}$/.test(e.name))
  .map(e => e.name)
  .sort();

let jsonFiles = [];
let outDir = base;

if (runDirs.length > 0) {
  // беремо найновішу папку прогону
  const lastRun = runDirs[runDirs.length - 1];
  const jsonDir = path.join(base, lastRun);
  outDir = jsonDir;
  jsonFiles = fs.readdirSync(jsonDir)
    .filter(f => f.endsWith('.json'))
    .map(f => path.join(jsonDir, f));
} else {
  // 2) Плоский режим: вибираємо JSON-и тільки з останнім таймстемп-префіксом у назві
  const flatJson = entries
    .filter(e => e.isFile() && e.name.endsWith('.json'))
    .map(e => path.join(base, e.name));

  if (flatJson.length === 0) {
    console.error('У', base, 'не знайдено JSON-звітів.');
    process.exit(1);
  }

  // Файли мають вигляд: 2025-09-15-11-02-27__automoto.com.lv_ru_bu-avto_latviya.json
  // Групуємо за префіксом до "__" і беремо найновіший.
  const groups = {};
  for (const p of flatJson) {
    const name = path.basename(p);
    const prefix = name.split('__')[0]; // "2025-09-15-11-02-27"
    (groups[prefix] ||= []).push(p);
  }
  const latestPrefix = Object.keys(groups).sort().pop();
  jsonFiles = groups[latestPrefix];
  outDir = base; // збережемо CSV поруч
}

if (jsonFiles.length === 0) {
  console.error('Немає JSON-файлів для агрегування.');
  process.exit(1);
}

const rows = readJSONFiles(jsonFiles);
const csv = toCSV(rows);
const outPath = path.join(outDir, 'aggregated.csv');
fs.writeFileSync(outPath, csv, 'utf8');
console.log(`Saved: ${outPath}\nRows: ${rows.length}`);
