const { test, expect } = require('@playwright/test');
// Важно: для stealth используем playwright-extra
const { chromium } = require('playwright-extra'); 
const stealth = require('puppeteer-extra-plugin-stealth')();

chromium.use(stealth);

test.describe('Мои рабочие тесты со Stealth', () => {
  let browser;
  let context;
  let page;

  test.beforeEach(async () => {
    // Запускаем stealth-браузер вручную перед каждым тестом
    browser = await chromium.launch({ headless: true });
    context = await browser.newContext();
    page = await context.newPage();
  });

  test.afterEach(async () => {
    // Закрываем браузер после каждого теста
    await browser.close();
  });

  test('Мой рабочий тест №1', async () => {
    // Пишите ваш обычный рабочий код, используя переменную page
    await page.goto('https://automoto.com.lv/ru');
    
    // Ваши проверки (expect работают как обычно)
    await expect(page.locator('h1')).toBeVisible();
  });
});