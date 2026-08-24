// Layout regression test for the published course page.
//
//   npm i playwright   (browser already present: /opt/pw-browsers/chromium)
//   ./assemble.sh && node test-layout.mjs
//
// Guards the two bugs that shipped once already:
//   1. a bare `1fr` grid track refusing to shrink below min-content, so a
//      long inline <code> pushed the page wider than the phone;
//   2. an over-broad `code { white-space: normal }` collapsing every code
//      block onto one line.
import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const ALL = Array.from({length:24},(_,i)=>'l'+(i+1));
let fails = 0;
for (const w of [320, 390, 430, 1440]) {
  const ctx = await b.newContext({ viewport: { width: w, height: 900 } });
  const p = await ctx.newPage();
  await p.addInitScript((ids) => localStorage.setItem('ccpath-v1',
    JSON.stringify({ done: ids, at: 'l1' })), ALL);
  await p.goto('file://' + process.cwd() + '/course.html');
  await p.waitForTimeout(500);
  const issues = [];
  for (let i = 0; i < 24; i++) {
    if (w <= 960) { await p.locator('#btn-menu').click(); await p.waitForTimeout(150); }
    await p.locator('.nav-l').nth(i).click(); await p.waitForTimeout(260);
    const r = await p.evaluate(() => {
      const pre = document.querySelector('.ex pre');
      return {
        t: document.querySelector('h2.lesson-t').innerText.slice(0, 20),
        over: document.documentElement.scrollWidth - innerWidth,
        // A multi-line source block must still render multiple lines.
        preLines: pre ? pre.innerText.split('\n').length : null,
        preWhite: pre ? getComputedStyle(pre.querySelector('code') || pre).whiteSpace : null,
      };
    });
    if (r.over > 1) issues.push(`L${i+1} overflow +${r.over}`);
    if (r.preLines !== null && r.preLines < 2) issues.push(`L${i+1} code block collapsed to 1 line`);
    if (r.preWhite && !r.preWhite.startsWith('pre')) issues.push(`L${i+1} pre white-space=${r.preWhite}`);
  }
  console.log(`${String(w).padStart(4)}px : ${issues.length ? issues.join(' | ') : '24/24 lessons OK (fit + code blocks intact)'}`);
  fails += issues.length;
  await ctx.close();
}
console.log(fails === 0 ? '\nPASS' : `\n${fails} ISSUES`);
await b.close();
