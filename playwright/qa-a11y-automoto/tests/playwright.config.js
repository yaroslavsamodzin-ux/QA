// playwright.config.js
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'automoto.lv',
      use: {
        baseURL: 'https://automoto.com.lv',
      },
    },
  ],
});
