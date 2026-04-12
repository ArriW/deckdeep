// Quick game review — screenshots key scenes and saves them for inspection
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT = 'C:/Users/arrin/stash/deckdeep/scripts/screenshots';
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 720 });

  // Capture console errors
  const errors = [];
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('pageerror', err => errors.push(err.message));

  // ── Start screen ──────────────────────────────────────────────────────────
  await page.goto('http://localhost:8765', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(OUT, '01_start.png') });
  console.log('✓ Start screen');

  // ── Enter map ─────────────────────────────────────────────────────────────
  await page.click('text=New Game');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(OUT, '02_map.png') });
  console.log('✓ Map screen');

  // Click first available node
  const canvas = page.locator('canvas').first();
  const box = await canvas.boundingBox();
  // Click around the center-bottom of the canvas where the first node usually is
  await page.mouse.click(box.x + box.width * 0.5, box.y + box.height * 0.15);
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(OUT, '03_after_node_click.png') });
  console.log('✓ After node click');

  // ── Wait for combat or event ───────────────────────────────────────────────
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(OUT, '04_scene.png') });
  console.log('✓ Scene (combat or event)');

  // ── Try end turn if in combat ─────────────────────────────────────────────
  await page.keyboard.press('e');
  await page.waitForTimeout(2500);
  await page.screenshot({ path: path.join(OUT, '05_after_end_turn.png') });
  console.log('✓ After end turn');

  if (errors.length) {
    console.log('\n⚠ Console errors:');
    errors.forEach(e => console.log('  ', e));
  } else {
    console.log('\n✓ No console errors');
  }

  await browser.close();
  console.log(`\nScreenshots saved to: ${OUT}`);
})();
