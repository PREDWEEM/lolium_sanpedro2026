const { chromium } = require('playwright');

(async () => {
  const url = process.env.STREAMLIT_URL;
  if (!url) throw new Error('Defina STREAMLIT_URL con la aplicación de San Pedro.');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  console.log(`Visitando ${url}...`);
  await page.goto(url, { waitUntil: 'networkidle' });
  const wakeUpButton = page.locator('button:has-text("Wake up")');
  if (await wakeUpButton.isVisible()) {
    await wakeUpButton.click();
    await page.waitForTimeout(5000);
  }
  await browser.close();
})();
