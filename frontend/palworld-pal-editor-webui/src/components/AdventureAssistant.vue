<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { useAdventureStore } from '@/stores/adventure'
import { useAppStore } from '@/stores/app'
import { useRostersStore } from '@/stores/rosters'
import { useSessionStore } from '@/stores/session'
import { MAX_LEVEL } from '@/game-limits'

const app = useAppStore()
const rosters = useRostersStore()
const session = useSessionStore()
const adventure = useAdventureStore()
const goal = ref('explore')
const ceiling = ref(null)
const selected = ref(null)
const t = (key, args = []) => app.getTranslatedText(`Adventure_${key}`, args)
const busy = computed(() => adventure.loading || adventure.pending || session.operationPending)
const ceilings = [...new Set([10, 20, 30, MAX_LEVEL])].sort((a, b) => a - b)
watch([() => rosters.activePlayerUid, () => session.sessionEpoch, () => app.locale, goal, ceiling], () => {
  selected.value = null
  adventure.load(goal.value, ceiling.value)
}, { immediate: true })
watch(() => adventure.advice, () => { selected.value = null })
onUnmounted(() => adventure.clear())
const apply = async () => {
  const row = selected.value
  if (row && !busy.value) await adventure.apply(row)
  selected.value = null
}
</script>

<template>
  <section class="adventure-assistant" :aria-busy="busy">
    <header class="adventure-heading">
      <span class="adventure-eyebrow">{{ t('Title') }}</span>
      <h2>{{ t('Heading') }}</h2>
      <p>{{ t('Description') }}</p>
    </header>
    <div class="adventure-controls">
      <label for="adventure-goal">{{ t('Goal') }}
        <select id="adventure-goal" v-model="goal" :disabled="busy">
          <option v-for="value in ['explore', 'combat', 'base', 'mounts']" :key="value" :value="value">{{ t(value) }}</option>
        </select>
      </label>
      <label for="adventure-ceiling">{{ t('Ceiling') }}
        <select id="adventure-ceiling" v-model="ceiling" :disabled="busy">
          <option :value="null">{{ t('Automatic') }}</option>
          <option v-for="value in ceilings" :key="value" :value="value">{{ t('UpTo', [value]) }}</option>
        </select>
      </label>
      <button type="button" class="editor-button" :disabled="busy" @click="adventure.load(goal, ceiling)">{{ t('Refresh') }}</button>
    </div>
    <p class="adventure-note">{{ t('CeilingHint') }}</p>
    <p v-if="adventure.loading" role="status">{{ t('Loading') }}</p>
    <p v-else-if="adventure.failed" role="status">{{ t('Failed') }}</p>
    <template v-else-if="adventure.advice">
      <div class="adventure-progress">
        <strong>{{ t('Progress', [adventure.advice.level, adventure.advice.effective_level]) }}</strong>
        <p>{{ t('Evidence', [adventure.advice.tech_count, adventure.advice.owned_count]) }}</p>
        <p v-if="!adventure.advice.capture_data_available">{{ t('MissingCaptures') }}</p>
      </div>
      <p v-if="!adventure.advice.recommendations.length" class="adventure-empty" role="status">{{ t('Empty') }}</p>
      <div class="adventure-cards">
        <article v-for="row in adventure.advice.recommendations" :key="row.id" class="adventure-card">
          <span class="adventure-eyebrow">{{ t(row.kind === 'item' ? 'Supplies' : 'Partner') }}</span>
          <h3>{{ row.name }}</h3>
          <template v-if="row.kind === 'item'">
            <p>{{ t('ItemReason', [row.recipe]) }}</p>
            <strong class="adventure-change">{{ t('Stock', [row.owned, row.target, row.quantity]) }}</strong>
          </template>
          <template v-else>
            <p>{{ t(`Reason_${row.reason}`, [row.required_tech]) }}</p>
            <p>{{ t('Role', [t(`Role_${row.role}`)]) }}</p>
            <p v-if="row.gear">{{ t('Gear', [row.gear]) }}</p>
            <strong v-if="row.can_apply" class="adventure-change">{{ t('PalChange', [row.level]) }}</strong>
          </template>
          <div v-if="selected?.id === row.id" class="adventure-confirm" role="group" :aria-label="t('Confirm')">
            <strong>{{ t('Confirm') }}</strong>
            <p>{{ t(row.kind === 'item' ? 'ConfirmItem' : 'ConfirmPal', [row.name, row.quantity, row.level]) }}</p>
            <div class="adventure-confirm-actions">
              <button type="button" class="editor-button" :disabled="busy" @click="apply">{{ t('Apply') }}</button>
              <button type="button" class="editor-button" :disabled="busy" @click="selected = null">{{ t('Cancel') }}</button>
            </div>
          </div>
          <button v-else-if="row.can_apply" type="button" class="editor-button adventure-choose" :disabled="busy" :aria-label="`${t('Choose')}：${row.name}`" @click="selected = row">{{ t('Choose') }}</button>
          <span v-else class="adventure-owned">{{ t(row.reason === 'technology' ? 'TechRequired' : 'UseExisting') }}</span>
        </article>
      </div>
    </template>
    <footer class="adventure-footer">
      <p>{{ t('Rules') }}</p>
      <p>{{ t('SaveHint') }}</p>
    </footer>
  </section>
</template>

<style scoped>
.adventure-assistant { padding: 1.25rem; overflow: auto; color: var(--editor-color-text); }
.adventure-heading h2 { margin: .5rem 0; font-size: 1.5rem; }
.adventure-assistant p { color: var(--editor-color-muted); line-height: 1.7; }
.adventure-eyebrow { font-size: .8rem; color: var(--editor-color-muted); }
.adventure-controls { display: flex; flex-wrap: wrap; gap: 1rem; align-items: end; margin-top: 1.25rem; }
.adventure-controls label { display: grid; gap: .5rem; flex: 1 1 12rem; }
.adventure-controls select { width: 100%; min-height: 2.75rem; padding: .6rem; border: 1px solid var(--editor-color-border); border-radius: .6rem; background: var(--editor-color-control); color: inherit; font: inherit; }
.adventure-note { font-size: .85rem; }
.adventure-progress { padding: 1rem; margin: 1.25rem 0; border-radius: .75rem; background: var(--editor-color-glass-surface); border: 1px solid var(--editor-color-border); }
.adventure-progress p { margin-bottom: 0; }
.adventure-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 17rem), 1fr)); gap: 1rem; }
.adventure-card { min-width: 0; padding: 1.1rem; border: 1px solid var(--editor-color-border); border-radius: .9rem; background: var(--editor-color-glass-surface); overflow-wrap: anywhere; }
.adventure-card h3 { margin: .5rem 0; }
.adventure-change { display: block; margin: 1rem 0; }
.adventure-confirm { border-top: 1px solid var(--editor-color-border); padding-top: 1rem; margin-top: 1rem; }
.adventure-confirm-actions { display: flex; gap: .5rem; flex-wrap: wrap; }
.adventure-choose { margin-top: .5rem; }
.adventure-owned { display: block; margin-top: 1rem; color: var(--editor-color-muted); }
.adventure-footer { margin-top: 1.5rem; border-top: 1px solid var(--editor-color-border); font-size: .85rem; }
.adventure-empty { padding: 1rem 0; }
</style>
