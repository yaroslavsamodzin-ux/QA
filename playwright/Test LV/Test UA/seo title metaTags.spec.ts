import { test, expect, Page } from '@playwright/test';

test.describe('SEO: Renault Modus 2005 (Dnepr)', () => {
  const URL = 'https://new.automoto.ua/renault-modus-2005-dnepr-dnepropetrovsk-68384908.html';

  test('Dynamic Title check', async ({ page }) => {
  const title = await page.title();

  // Витягуємо рік (4 цифри)
  const yearMatch = title.match(/\b(19|20)\d{2}\b/);
  const year = yearMatch ? yearMatch[0] : '';

  // Витягуємо бренд + модель (припустимо, перші два слова після "Купити/Купить")
  const brandModelMatch = title.match(/(?:Купити|Купить)\s+([A-Za-zА-Яа-яёЁЇІЄҐ]+)\s+([A-Za-zА-Яа-яёЁЇІЄҐ]+)/u);
  const brand = brandModelMatch ? brandModelMatch[1] : '';
  const model = brandModelMatch ? brandModelMatch[2] : '';

  // Перевірки
  expect(title).toMatch(/(Купити|Купить)/u);   // має бути одне з двох слів
  expect(year).not.toBe('');
  expect(brand).not.toBe('');
  expect(model).not.toBe('');

  // Додатково можемо перевірити структуру
  console.log(`Brand: ${brand}, Model: ${model}, Year: ${year}`);
});
});