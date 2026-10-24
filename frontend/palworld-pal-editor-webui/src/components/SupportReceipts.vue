<script setup>
import { computed, ref, watch } from 'vue'
import { useAppStore } from '@/stores/app'
import receipts from '@/support-receipts.json'

const app = useAppStore()
const t = (key, args = []) => app.getTranslatedText(`Receipts_${key}`, args)
const assetUrl = path => `${import.meta.env.BASE_URL}${path}`
const method = ref('crypto')
const currency = ref('')
const networkId = ref('')
const query = ref('')
const copied = ref('')
const addressInput = ref()
const selectedAsset = computed(() => receipts.assets.find(a => a.symbol === currency.value))
const networks = computed(() => receipts.routes.filter(r => r.asset === currency.value &&
  `${r.networkName} ${r.network} ${r.exchange}`.toLowerCase().includes(query.value.trim().toLowerCase())))
const selected = computed(() => receipts.routes.find(r => r.id === networkId.value && r.asset === currency.value))
watch(currency, () => { networkId.value = ''; query.value = ''; copied.value = '' })
watch([networkId, method], () => { copied.value = '' })
async function copyAddress() {
  const value = method.value === 'bank' ? receipts.bank.account : selected.value?.address
  if (!value) return
  try {
    await navigator.clipboard.writeText(value)
    copied.value = 'Copied'
  } catch {
    addressInput.value?.focus()
    addressInput.value?.select()
    copied.value = 'CopyFallback'
  }
}
</script>

<template>
  <section class="receipts" aria-labelledby="receipts-title">
    <header class="receipts-header">
      <div>
        <span class="eyebrow">{{ t('Maintainer') }}</span>
        <h3 id="receipts-title">{{ t('Title') }}</h3>
        <p>{{ t('Recipient') }} <a href="https://github.com/s742850/Palworld-Pal-Editor" target="_blank" rel="noopener noreferrer">s742850</a></p>
      </div>
      <span class="receipt-badge">{{ t('Optional') }}</span>
    </header>
    <div class="method-switch" role="group" :aria-label="t('Method')">
      <button type="button" :aria-pressed="method === 'crypto'" @click="method = 'crypto'">{{ t('Crypto') }}</button>
      <button type="button" :aria-pressed="method === 'bank'" @click="method = 'bank'">{{ t('Bank') }}</button>
    </div>

    <div v-if="method === 'crypto'" class="receipt-layout">
      <div class="receipt-steps">
        <h4><span class="step">1</span>{{ t('ChooseAsset') }}</h4>
        <div class="currency-grid" role="group" :aria-label="t('ChooseAsset')">
          <button v-for="asset in receipts.assets" :key="asset.symbol" type="button"
            :aria-pressed="currency === asset.symbol" @click="currency = asset.symbol">
            <img :src="assetUrl(asset.icon)" :alt="asset.symbol" class="receipt-icon">
            <span><strong>{{ asset.symbol }}</strong><small>{{ asset.name }}</small></span>
          </button>
        </div>
        <h4><span class="step">2</span>{{ t('ChooseNetwork') }}</h4>
        <p v-if="!currency" class="muted">{{ t('ChooseAssetFirst') }}</p>
        <template v-else>
          <input v-model="query" class="network-search" type="search" :placeholder="t('Search')" :aria-label="t('Search')">
          <div class="network-list" role="group" :aria-label="t('ChooseNetwork')">
            <button v-for="route in networks" :key="route.id" type="button"
              :aria-pressed="networkId === route.id" @click="networkId = route.id">
              <img :src="assetUrl(route.networkIcon)" :alt="route.networkName" class="receipt-icon">
              <span><strong>{{ route.networkName }}</strong><small>{{ route.exchange }} · {{ t('MinimumShort') }} {{ route.minimumInclusive ? '≥' : '>' }} {{ route.minimum }} {{ route.asset }}</small></span>
              <span v-if="networkId === route.id" class="selected-check" aria-hidden="true">✓</span>
            </button>
            <p v-if="!networks.length" class="muted">{{ t('NoResults') }}</p>
          </div>
        </template>
      </div>

      <article v-if="selected" class="receipt-detail" aria-live="polite">
        <div class="receipt-selection">
          <img :src="assetUrl(selectedAsset.icon)" :alt="selected.asset" class="receipt-icon">
          <div><h4>{{ selected.asset }}</h4><span>{{ selected.networkName }}</span></div>
          <img :src="assetUrl(selected.networkIcon)" :alt="selected.networkName" class="receipt-icon">
        </div>
        <p class="recipient-note">{{ t('Maintainer') }} · s742850 · {{ selected.exchange }}</p>
        <img :src="assetUrl(selected.qr)" :alt="t('QrAlt', [selected.asset, selected.networkName])" class="receipt-qr">
        <p class="network-warning">{{ t('NetworkWarning', [selected.asset, selected.networkName]) }}</p>
        <p v-if="selected.asset === 'BTC' && ['bsc', 'ethereum'].includes(selected.network)" class="network-warning">{{ t(selected.network === 'ethereum' ? 'WrappedBbtc' : 'WrappedBtcb') }}</p>
        <p v-if="selected.asset === 'USDC' && ['optimism', 'polygon'].includes(selected.network)" class="network-warning">{{ t('NativeUsdc') }}</p>
        <label for="crypto-receipt-address">{{ t('Address') }}</label>
        <textarea id="crypto-receipt-address" ref="addressInput" readonly rows="3" :value="selected.address" @focus="$event.target.select()" />
        <button type="button" class="copy-button" @click="copyAddress">{{ t('Copy') }}</button>
        <p role="status" class="copy-status">{{ copied ? t(copied) : '' }}</p>
        <dl>
          <div><dt>{{ t('Minimum') }}</dt><dd>{{ selected.minimumInclusive ? '≥' : '>' }} {{ selected.minimum }} {{ selected.asset }}</dd></div>
          <div v-if="selected.contract"><dt>{{ t(selected.network === 'near' ? 'Contract' : 'ContractSuffix') }}</dt><dd>{{ selected.network === 'near' ? '' : '…' }}{{ selected.contract }}</dd></div>
        </dl>
        <p class="muted small">{{ t('Snapshot', [receipts.asOf]) }}</p>
      </article>
      <div v-else class="receipt-empty">
        <span class="empty-mark" aria-hidden="true">QR</span>
        <h4>{{ t('ChooseNetworkFirst') }}</h4>
        <p>{{ t('EmptyDescription') }}</p>
      </div>
    </div>

    <article v-else class="bank-receipt">
      <div>
        <h4>{{ t('BankName') }} <span class="receipt-badge">TWD</span></h4>
        <p class="recipient-note">{{ t('Maintainer') }} · s742850</p>
        <dl>
          <div><dt>{{ t('BankCode') }}</dt><dd>{{ receipts.bank.code }}</dd></div>
          <div><dt>{{ t('Branch') }}</dt><dd>{{ t('BranchName') }} ({{ receipts.bank.branch }})</dd></div>
        </dl>
        <label for="bank-receipt-account">{{ t('Account') }}</label>
        <input id="bank-receipt-account" ref="addressInput" readonly :value="receipts.bank.account" @focus="$event.target.select()">
        <button type="button" class="copy-button" @click="copyAddress">{{ t('CopyAccount') }}</button>
        <p role="status" class="copy-status">{{ copied ? t(copied) : '' }}</p>
        <p class="muted">{{ t('BankHint') }}</p>
      </div>
      <img :src="assetUrl(receipts.bank.qr)" :alt="t('BankQrAlt')" class="receipt-qr">
    </article>
  </section>
</template>

<style scoped>
.receipts { grid-column: 1 / -1; min-width: 0; border: 1px solid var(--editor-color-border); border-radius: 16px; padding: 24px; background: var(--editor-color-surface); color: var(--editor-color-text); }
.receipts-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.eyebrow { font-size: .75rem; letter-spacing: .08em; color: var(--editor-color-primary); }
h3 { font-size: 1.35rem; margin: 6px 0 10px; }
h4 { font-size: 1rem; margin: 0 0 12px; }
p { line-height: 1.6; margin: 6px 0 12px; }
a { color: var(--editor-color-focus); }
.receipt-badge { font-size: .75rem; padding: 5px 9px; border: 1px solid var(--editor-color-border); border-radius: 20px; white-space: nowrap; }
button, input, textarea { font: inherit; color: inherit; border: 1px solid var(--editor-color-border); border-radius: 9px; background: var(--editor-color-control); box-sizing: border-box; }
button { cursor: pointer; }
button:hover { border-color: var(--editor-color-focus); background: var(--editor-color-control-hover); }
button:focus-visible, input:focus-visible, textarea:focus-visible { outline: 2px solid var(--editor-color-focus); outline-offset: 3px; }
button[aria-pressed="true"] { border-color: var(--editor-color-primary); background: color-mix(in srgb, var(--editor-color-primary) 14%, var(--editor-color-control)); }
.method-switch { display: flex; gap: 8px; margin: 14px 0 24px; }
.method-switch button { padding: 12px 18px; }
.receipt-layout { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 24px; align-items: start; }
.receipt-steps { min-width: 0; }
.step { display: inline-grid; place-items: center; width: 25px; height: 25px; background: var(--editor-color-control); border-radius: 50%; margin-right: 9px; font-size: .8rem; }
.currency-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 24px; }
.currency-grid button, .network-list button { display: flex; align-items: center; gap: 10px; text-align: left; padding: 12px; min-width: 0; }
.receipt-icon { width: 34px; height: 34px; padding: 3px; border-radius: 50%; background: #fff; flex-shrink: 0; object-fit: contain; box-sizing: border-box; }
strong, small { display: block; }
small { font-size: .72rem; opacity: .7; margin-top: 4px; }
.network-search { padding: 11px 12px; width: 100%; margin-bottom: 8px; }
.network-list { display: flex; flex-direction: column; gap: 6px; max-height: 320px; overflow-y: auto; padding: 3px; }
.network-list button { width: 100%; min-height: 64px; }
.selected-check { margin-left: auto; color: var(--editor-color-primary); }
.receipt-detail, .receipt-empty { border: 1px solid var(--editor-color-border); border-radius: 12px; padding: 20px; min-width: 0; background: color-mix(in srgb, var(--editor-color-control) 40%, transparent); }
.receipt-selection { display: flex; align-items: center; gap: 10px; }
.receipt-selection h4 { margin: 0 0 3px; }
.receipt-selection > img:last-child { margin-left: auto; width: 26px; height: 26px; }
.receipt-selection span, .recipient-note { font-size: .8rem; }
.recipient-note { opacity: .75; margin: 12px 0; }
.receipt-qr { display: block; width: min(240px, 100%); height: auto; margin: 18px auto; border-radius: 10px; background: white; }
.network-warning { padding: 10px 12px; border-left: 3px solid #e3b65b; background: rgb(227 182 91 / 9%); font-size: .8rem; }
label { display: block; font-size: .8rem; margin: 12px 0 7px; }
textarea, .bank-receipt input { display: block; width: 100%; padding: 10px; font-family: ui-monospace, monospace; font-size: .85rem; line-height: 1.55; resize: none; overflow-wrap: anywhere; }
.copy-button { width: 100%; padding: 12px; margin-top: 8px; background: var(--editor-color-primary); color: var(--editor-color-background); border-color: var(--editor-color-primary); font-weight: 600; }
.copy-button:hover { background: var(--editor-color-primary-hover); }
.copy-status { font-size: .8rem; min-height: 1.3em; margin: 6px 0; }
dl { font-size: .8rem; margin: 12px 0; }
dl > div { display: flex; justify-content: space-between; gap: 14px; padding: 6px 0; }
dt { opacity: .7; }
dd { text-align: right; margin: 0; overflow-wrap: anywhere; }
.muted { opacity: .7; }
.small { font-size: .72rem; }
.receipt-empty { display: grid; place-content: center; text-align: center; min-height: 330px; }
.receipt-empty p { opacity: .65; font-size: .9rem; }
.empty-mark { display: grid; place-items: center; width: 64px; height: 64px; margin: 0 auto 18px; border: 2px dashed var(--editor-color-border); border-radius: 12px; opacity: .6; }
.bank-receipt { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 24px; align-items: center; }
@media (max-width: 650px) { .receipts { padding: 16px; } .receipt-layout, .bank-receipt { grid-template-columns: 1fr; } .receipts-header { flex-wrap: wrap; } .receipt-empty { min-height: 170px; } .method-switch button { flex: 1; padding: 12px 8px; } }
</style>
