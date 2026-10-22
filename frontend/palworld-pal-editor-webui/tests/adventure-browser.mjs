// Optional real-browser acceptance with a mock API; never opens a game save.
// PLAYWRIGHT_MODULE may point to the workspace runtime's installed package.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { createServer } from 'vite';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = fileURLToPath(new URL('../', import.meta.url));
const output = fileURLToPath(new URL('../../../test_outputs/adventure', import.meta.url));
const moduleSource = `
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import axios from 'axios';
import Assistant from '/src/components/AdventureAssistant.vue';
import { useAppStore } from '/src/stores/app.js';
import { useRostersStore } from '/src/stores/rosters.js';
import { useAdventureStore } from '/src/stores/adventure.js';
import '/src/assets/main.css';
const pinia = createPinia();
const app = createApp(Assistant); app.use(pinia);
useAppStore().locale = 'zh-TW';
useRostersStore().activeRosterKey = 'player:fixture';
const item = { id: 'item:PalSphere', key: 'PalSphere', kind: 'item', name: '帕魯球', owned: 3, target: 10, quantity: 7, recipe: '帕魯球', reason: 'supplies', can_apply: true, token: 'item-preview' };
const pal = { id: 'pal:Penguin', key: 'Penguin', kind: 'pal', name: '企丸丸', owned: 0, quantity: 1, level: 8, role: 'Watering', reason: 'captured', can_apply: true, token: 'pal-preview' };
const fixture = window.fixture = { posts: [], added: false, stale: false, empty: false, store: useAdventureStore() };
const advice = () => ({ level: 12, effective_level: 12, tech_count: 14, owned_count: 6, capture_data_available: true, recommendations: fixture.empty ? [] : fixture.added ? [{...pal, reason:'owned', can_apply:false}] : [item, pal] });
axios.defaults.adapter = async config => {
 if (config.method === 'post') {
  fixture.posts.push(JSON.parse(config.data));
  if (fixture.stale) throw { response: { status: 409, data: { error: { code: 'ADVENTURE_STALE' } } } };
  fixture.added = true;
  return { config, status: 200, data: { result: { kind: 'item', name: '帕魯球', quantity: 7 }, inventory: { containers: {} }, advice: advice() }, headers: {} };
 }
 return { config, status: 200, data: advice(), headers: {} };
};
app.mount('#app');
`;
const server = await createServer({
    root, logLevel: 'error', server: { host: '127.0.0.1', port: 0 },
    plugins: [{
        name: 'adventure-test-harness',
        resolveId(id) { if (id === '/__adventure_browser.js') return '\0adventure-test-harness'; },
        load(id) { if (id === '\0adventure-test-harness') return moduleSource; },
        configureServer(server) {
            server.middlewares.use(async (req, res, next) => {
                if (req.url.split('?')[0] !== '/__adventure_browser') return next();
                const html = await server.transformIndexHtml('/__adventure_browser', '<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><div id="app"></div><script type="module" src="/__adventure_browser.js"></script></body></html>');
                res.setHeader('Content-Type', 'text/html');
                res.end(html);
            });
        },
    }],
});
let browser;
try {
    await mkdir(output, { recursive: true });
    await server.listen();
    browser = await chromium.launch({ headless: true, ...(process.env.BROWSER_EXECUTABLE ? { executablePath: process.env.BROWSER_EXECUTABLE } : {}) });
    const page = await browser.newPage({ viewport: { width: 1000, height: 900 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') console.error(message.text()); });
    await page.goto(`http://127.0.0.1:${server.httpServer.address().port}/__adventure_browser`);
    await page.getByRole('heading', { name: '幫一點忙，冒險留給你' }).waitFor();
    const choice = page.getByRole('button', { name: '查看新增內容：帕魯球' });
    await choice.waitFor();
    assert.equal(await page.evaluate(() => window.fixture.posts.length), 0);
    await choice.click();
    await page.getByRole('button', { name: '暫時不要' }).click();
    assert.equal(await page.evaluate(() => window.fixture.posts.length), 0);
    await choice.click();
    await page.screenshot({ path: `${output}/desktop.png`, fullPage: true });
    await page.setViewportSize({ width: 360, height: 900 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
    await page.screenshot({ path: `${output}/mobile.png`, fullPage: true });
    await page.getByRole('button', { name: '套用並新增', exact: true }).click();
    await page.getByText('先使用現有夥伴 · 不必新增', { exact: true }).waitFor();
    assert.equal(await page.evaluate(() => window.fixture.posts.length), 1);
    await page.evaluate(async () => { window.fixture.added = false; window.fixture.stale = true; await window.fixture.store.load('explore', null); });
    await choice.click();
    await page.getByRole('button', { name: '套用並新增', exact: true }).click();
    await choice.waitFor();
    assert.equal(await page.getByRole('button', { name: '套用並新增', exact: true }).count(), 0);
    await page.evaluate(async () => { window.fixture.empty = true; await window.fixture.store.load('explore', null); });
    await page.getByText('目前沒有適合新增的項目。', { exact: false }).waitFor();
    assert.equal(await page.getByRole('button', { name: '查看新增內容', exact: false }).count(), 0);
    assert.deepEqual(errors, []);
    console.log('Browser acceptance passed: opt-in, cancel, apply, stale refresh, empty state, mobile layout. Screenshots:', output);
} finally {
    await browser?.close();
    await server.close();
}
