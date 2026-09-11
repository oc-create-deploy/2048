import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({
  viewport: { width: 1320, height: 2868 },
  deviceScaleFactor: 1,
  colorScheme: 'light',
});

await page.goto('http://127.0.0.1:8080', { waitUntil: 'networkidle' });
await page.waitForTimeout(1800);
await mkdir('app-store-screenshots', { recursive: true });

async function capture(name) {
  await page.screenshot({
    path: `app-store-screenshots/${name}.png`,
    fullPage: false,
    omitBackground: false,
  });
}

await capture('01-classic-board');

for (const key of [
  'ArrowLeft', 'ArrowDown', 'ArrowRight', 'ArrowUp',
  'ArrowLeft', 'ArrowDown', 'ArrowLeft', 'ArrowUp',
  'ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp',
]) {
  await page.keyboard.press(key);
  await page.waitForTimeout(260);
}
await capture('02-smooth-gameplay');

for (const key of [
  'ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp',
  'ArrowLeft', 'ArrowDown', 'ArrowRight', 'ArrowUp',
  'ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp',
  'ArrowLeft', 'ArrowDown', 'ArrowRight', 'ArrowUp',
]) {
  await page.keyboard.press(key);
  await page.waitForTimeout(260);
}
await capture('03-build-your-best-score');

await browser.close();
