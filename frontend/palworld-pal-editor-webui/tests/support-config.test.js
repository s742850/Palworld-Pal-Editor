import assert from 'node:assert/strict';
import test from 'node:test';
import { parseSupportConfig } from '../src/support-config.js';

test('support links are disabled until configured and reject executable or credential URLs', () => {
    assert.equal(parseSupportConfig(), null);
    for (const url of ['javascript:alert(1)', 'data:text/html,bad', 'http://example.com', 'https://user:password@example.com', 'invalid']) {
        assert.equal(parseSupportConfig({ VITE_SUPPORT_URL: url }), null);
    }
});

test('support link preserves public recipient and network labels', () => {
    assert.deepEqual(parseSupportConfig({
        VITE_SUPPORT_URL: 'https://example.com/pay',
        VITE_SUPPORT_NAME: 'My fork', VITE_SUPPORT_NETWORK: 'USDT / TRC20',
    }), { url: 'https://example.com/pay', address: '', asset: '', name: 'My fork', network: 'USDT / TRC20' });
});

test('an address requires explicit currency and network, without wallet access', () => {
    const env = { VITE_SUPPORT_ADDRESS: '0x' + '1'.repeat(40) };
    assert.equal(parseSupportConfig(env), null);
    const config = parseSupportConfig({ ...env, VITE_SUPPORT_ASSET: 'USDT', VITE_SUPPORT_NETWORK: 'Ethereum (ERC20)' });
    assert.equal(config.address, env.VITE_SUPPORT_ADDRESS);
    assert.equal(config.url, null);
});
