
import { makeBrowser, saveSiteCsv, loadBrands, acceptCookiesIfPresent } from './common.js';
import auto24lv from './sites/auto24lv.js';

const sites = [ auto24lv /*, add more later */ ];

(async () => {
  const headless = (process.env.HEADED ?? '1') !== '0';
  const brands = loadBrands('./brands.json');
  const { browser, page } = await makeBrowser(headless);

  for (const site of sites) {
    try {
      console.log(`\n[RUN ] ${site.key} → ${site.url}`);
      const rows = await site.scrape(page, brands);
      await saveSiteCsv(site.key, rows);
    } catch (e) {
      console.error(`[FAIL] ${site.key}:`, e.message);
    }
  }

  await browser.close();
})();
