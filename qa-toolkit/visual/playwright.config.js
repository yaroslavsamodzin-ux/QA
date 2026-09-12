// Конфіг для візуальної регресії (qa-toolkit/visual/visual.spec.js).
// Порівняння скріншотів вбудоване в @playwright/test — зайвих пакетів не треба.
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: __dirname,
  testMatch: 'visual.spec.js',
  timeout: 90_000,
  fullyParallel: true,
  workers: process.env.CI ? 2 : 4,
  reporter: [['list'], ['html', { outputFolder: `${__dirname}/report`, open: 'never' }]],
  outputDir: `${__dirname}/test-results`,
  snapshotPathTemplate: `${__dirname}/baseline/{arg}{ext}`,
  expect: {
    toHaveScreenshot: {
      // дрібний антиаліасинг і субпіксельні зсуви ігноруємо
      maxDiffPixelRatio: 0.01,
      threshold: 0.2,
      animations: 'disabled',
      scale: 'css',
    },
  },
  use: {
    ignoreHTTPSErrors: true,
    storageState: process.env.QA_STORAGE || undefined,
  },
});
