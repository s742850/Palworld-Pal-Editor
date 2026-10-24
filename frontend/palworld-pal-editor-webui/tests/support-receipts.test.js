import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import test from 'node:test';
import { translate, GAME_LANGUAGES } from '../src/i18n/index.js';

const data = JSON.parse(readFileSync(new URL('../src/support-receipts.json', import.meta.url)));
const evidence = JSON.parse(readFileSync(new URL('./fixtures/support-receipts-evidence.json', import.meta.url)));
const source = (batch, photo) => evidence.sources.find(s => s.batch === batch && s.photo === photo);

test('all 40 crypto screenshots map to 35 distinct coin/network/address routes', () => {
    assert.equal(evidence.sources.length, 41);
    assert.equal(data.routes.length, 35);
    assert.equal(new Set(data.routes.map(r => `${r.asset}:${r.network}:${r.address}`)).size, 35);
    assert.equal(new Set(data.routes.map(r => r.id)).size, 35);
    assert.deepEqual(Object.fromEntries(data.assets.map(a => [a.symbol, data.routes.filter(r => r.asset === a.symbol).length])),
        { USDT: 18, USDC: 7, BTC: 4, ETH: 6 });
    const covered = new Set(data.routes.map(r => `${r.source.batch}:${r.source.photo}`));
    for (const duplicate of evidence.duplicates) {
        assert.equal(source(duplicate.batch, duplicate.photo).payload, source(duplicate.batch, duplicate.duplicateOf).payload);
        assert.ok(covered.has(`${duplicate.batch}:${duplicate.duplicateOf}`));
        covered.add(`${duplicate.batch}:${duplicate.photo}`);
    }
    for (const item of evidence.sources.filter(s => !(s.batch === 1 && s.photo === 24))) {
        assert.ok(covered.has(`${item.batch}:${item.photo}`));
    }
});

test('every receiving address matches its decoded source QR and all coin/network/QR images are local', () => {
    for (const route of data.routes) {
        assert.equal(route.address, source(route.source.batch, route.source.photo).payload);
        assert.ok(Number(route.minimum) > 0);
        assert.ok(['Binance', 'Kraken'].includes(route.exchange));
        for (const asset of [route.qr, route.networkIcon]) {
            assert.ok(existsSync(new URL(`../public/${asset}`, import.meta.url)), asset);
        }
    }
    for (const asset of data.assets) assert.ok(existsSync(new URL(`../public/${asset.icon}`, import.meta.url)));
});

test('shared EVM addresses do not imply unprovided coin/network support', () => {
    const matching = data.routes.filter(r => r.address === data.routes.find(r => r.id === 'usdt-ethereum').address);
    assert.ok(matching.length > 15);
    assert.equal(data.routes.some(r => r.id === 'usdt-base'), false);
    assert.equal(data.routes.some(r => r.id === 'usdc-tron'), false);
    assert.notEqual(data.routes.find(r => r.id === 'btc-bitcoin').address, data.routes.find(r => r.id === 'btc-segwit').address);
});

test('CTBC bank code and zero-prefixed account match the provided TWQR payload', () => {
    const payload = decodeURIComponent(source(1, 24).payload);
    const params = new URL(payload).searchParams;
    assert.equal(params.get('D5'), data.bank.code);
    assert.equal(params.get('D6'), data.bank.account.padStart(16, '0'));
    assert.equal(data.bank.account, '026540649002');
    assert.ok(existsSync(new URL(`../public/${data.bank.qr}`, import.meta.url)));
});

test('attribution and payment instructions are available in every supported locale', () => {
    for (const locale of Object.keys(GAME_LANGUAGES)) {
        assert.match(translate(locale, 'Receipts_Intro'), /_connlost.*KrisCris.*s742850/);
        assert.match(translate(locale, 'Receipts_OriginalPayment', ['PayPal']), /_connlost/);
        const warning = translate(locale, 'Receipts_NetworkWarning', ['USDT', 'Tron']);
        assert.ok(warning.includes('USDT') && warning.includes('Tron'));
        assert.ok(!warning.includes('{{'));
    }
});
