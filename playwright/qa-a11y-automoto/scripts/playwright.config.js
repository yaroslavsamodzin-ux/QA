const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  reporter: [['html', { outputFolder: 'playwright-report', open: 'never' }], ['list']],
  timeout: 60_000,
  use: {
    ignoreHTTPSErrors: true,
    headless: true,
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'automoto.lv', use: { baseURL: 'https://automoto.com.lv' } },
    { name: 'automoto.ua', use: { baseURL: 'https://automoto.ua' } },
  ],
});
