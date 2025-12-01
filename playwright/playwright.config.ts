import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './Test LV',   // твоя директорія з тестами
  testMatch: ['**/*.ts'],         // щоб підхоплював усі .ts
});
