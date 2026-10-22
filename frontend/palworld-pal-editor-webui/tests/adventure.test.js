import assert from 'node:assert/strict';
import test, { afterEach } from 'node:test';
import axios from 'axios';
import { createPinia, setActivePinia } from 'pinia';
import { useAdventureStore } from '../src/stores/adventure.js';
import { useRostersStore } from '../src/stores/rosters.js';
import { useSessionStore } from '../src/stores/session.js';
import { usePlayersStore } from '../src/stores/players.js';
import { translate } from '../src/i18n/index.js';
import en from '../src/i18n/en.js';

globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
const originalAdapter = axios.defaults.adapter;
afterEach(() => { axios.defaults.adapter = originalAdapter; });
const row = { id: 'item:PalSphere', token: 'preview', can_apply: true, name: 'Pal Sphere', quantity: 7 };
const advice = { recommendations: [row] };
const response = (config, data) => ({ config, data, status: 200, statusText: 'OK', headers: {} });
function setup() {
    setActivePinia(createPinia());
    const rosters = useRostersStore();
    rosters.activeRosterKey = 'player:one';
    return { store: useAdventureStore(), rosters, session: useSessionStore(), players: usePlayersStore() };
}

test('reading advice makes no write; explicit apply uses only the confirmed recommendation', async () => {
    const { store, players } = setup();
    const calls = [];
    axios.defaults.adapter = async config => {
        calls.push(config);
        return response(config, config.method === 'get' ? advice : {
            advice: { recommendations: [] }, inventory: { containers: {} },
            result: { kind: 'item', name: 'Pal Sphere', quantity: 7 },
        });
    };
    await store.load('explore', null);
    assert.equal(calls.length, 1);
    assert.equal(calls[0].method, 'get');
    assert.equal(await store.apply({ ...row, token: 'forged' }), false);
    assert.equal(calls.length, 1);
    assert.equal(await store.apply(row), true);
    assert.deepEqual(JSON.parse(calls[1].data), {
        goal: 'explore', ceiling: null, recommendationId: row.id, token: row.token,
    });
    assert.deepEqual(players.inventory, { containers: {} });
    assert.equal(await store.apply(row), false);
    assert.equal(calls.length, 2);
});

test('a late read cannot replace a newer goal or player', async () => {
    const { store, rosters } = setup();
    const resolve = [];
    axios.defaults.adapter = config => new Promise(done => resolve.push(data => done(response(config, data))));
    const old = store.load('base', null);
    const fresh = store.load('combat', 10);
    resolve[1]({ recommendations: [], goal: 'combat' });
    await fresh;
    resolve[0](advice);
    await old;
    assert.equal(store.advice.goal, 'combat');
    const other = store.load('explore', null);
    rosters.activeRosterKey = 'player:two';
    resolve[2](advice);
    await other;
    assert.equal(store.advice, null);
});

test('double-click is one request and a changed session cannot receive its result', async () => {
    const { store, session, players } = setup();
    let finish;
    let writes = 0;
    axios.defaults.adapter = config => config.method === 'get'
        ? Promise.resolve(response(config, advice))
        : new Promise(done => { writes++; finish = () => done(response(config, {
            advice: { recommendations: [] }, inventory: { wrong: true }, result: { kind: 'item' },
        })); });
    await store.load('explore', null);
    const first = store.apply(row);
    assert.equal(await store.apply(row), false);
    assert.equal(writes, 1);
    session.sessionEpoch += 1;
    finish();
    assert.equal(await first, false);
    assert.equal(players.inventory, null);
    assert.equal(session.operationPending, false);
});

test('stale confirmation refreshes suggestions without repeating the write', async () => {
    const { store } = setup();
    const methods = [];
    axios.defaults.adapter = async config => {
        methods.push(config.method);
        if (config.method === 'post') throw { response: { status: 409, data: { error: { code: 'ADVENTURE_STALE' } } } };
        return response(config, advice);
    };
    await store.load('explore', 10);
    assert.equal(await store.apply(row), false);
    assert.deepEqual(methods, ['get', 'post', 'get']);
    assert.equal(store.pending, false);
});

test('all adventure labels translate in Chinese and fall back in other locales', () => {
    for (const key of Object.keys(en).filter(k => k.startsWith('Adventure_'))) {
        for (const locale of ['zh-TW', 'zh-CN', 'ja', 'en']) {
            assert.notEqual(translate(locale, key), 'I18N_MISSING');
        }
    }
});

test('a Pal addition refreshes the player roster without repeating a successful write', async () => {
    const { store, rosters } = setup();
    const pal = { ...row, id: 'pal:Penguin' };
    const calls = [];
    axios.defaults.adapter = async config => response(config, config.method === 'get'
        ? { recommendations: [pal] }
        : { advice: { recommendations: [] }, inventory: {}, result: { kind: 'pal', name: 'Pengullet', quantity: 1 } });
    rosters.loadRosters = async () => calls.push('rosters');
    rosters.loadRosterPals = async key => calls.push(key);
    await store.load('base', null);
    assert.equal(await store.apply(pal), true);
    assert.deepEqual(calls, ['rosters', 'player:one']);
    assert.equal(await store.apply(pal), false);
});
