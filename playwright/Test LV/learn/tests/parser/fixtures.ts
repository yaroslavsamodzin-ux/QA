import { test as base, expect } from '@playwright/test';
import { chromium } from 'playwright-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

chromium.use(StealthPlugin());

export const test = base.extend({
    browser: [async ({}, use) => {
        const browser = await chromium.launch({ headless: false });
        await use(browser as any);
        await browser.close();
    }, { scope: 'worker' }],
});

export { expect };
