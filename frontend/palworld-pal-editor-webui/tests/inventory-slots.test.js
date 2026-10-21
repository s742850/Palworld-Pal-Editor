import assert from 'node:assert/strict';
import test, { after } from 'node:test';
import { createPinia, setActivePinia } from 'pinia';
import { closeVueServer, loadVueModule, renderVue } from './vue-render.js';

globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
after(closeVueServer);

async function renderSlot(slot, editable = true) {
    const pinia = createPinia();
    setActivePinia(pinia);
    const { default: component } = await loadVueModule('/src/components/InventoryItemSlot.vue');
    return renderVue(component, { pinia, props: { slot, editable, label: 'Test slot' } });
}

test('unknown stored items remain deletable even without a catalog icon', async () => {
    const html = await renderSlot({ static_id: 'UnknownFromNewerGame', count: 5 });
    assert.match(html, /class="slot-clear"/);
    assert.match(html, /Clear slot/);
});

test('empty slots expose an add affordance and readonly slots disable editing', async () => {
    assert.match(await renderSlot({ static_id: null, count: 0 }), /class="empty-slot-add"/);
    const html = await renderSlot({ static_id: 'Wood', count: 1 }, false);
    assert.match(html, /class="item-slot-button" disabled/);
    assert.doesNotMatch(html, /class="slot-clear"/);
});
