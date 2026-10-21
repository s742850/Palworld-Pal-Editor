<script setup>
import { computed, ref, watch } from 'vue'
import { getGraduationCatalog } from '@/api/players'
import { useAppStore } from '@/stores/app'
import { useBackendStore } from '@/stores/backend'
import { usePlayersStore } from '@/stores/players'
import { useRostersStore } from '@/stores/rosters'
import { useSessionStore } from '@/stores/session'

const app = useAppStore()
const backend = useBackendStore()
const players = usePlayersStore()
const rosters = useRostersStore()
const session = useSessionStore()
const preset = ref('all')
const presets = ref(null)
const pending = ref(false)
const entries = computed(() => presets.value?.[preset.value] || [])
const t = key => app.getTranslatedText(key)
watch(() => rosters.activePlayerUid, async uid => {
  presets.value = null
  if (!uid) return
  const epoch = session.sessionEpoch
  try {
    const reply = await getGraduationCatalog(uid, session.readOptions())
    if (session.isCurrentSession(epoch) && rosters.activePlayerUid === uid) presets.value = reply.presets
  } catch (error) { backend.reportApiFailure(error, 'Operation_Load_Player_Data') }
}, { immediate: true })
const add = async () => {
  pending.value = true
  try { await players.addGraduationKit(preset.value) }
  finally { pending.value = false }
}
</script>

<template>
  <section class="graduation-kit">
    <h2>{{ t('Graduation_Title') }}</h2>
    <p>{{ t('Graduation_Description') }}</p>
    <label for="graduation-preset">{{ t('Graduation_Select') }}</label>
    <div class="graduation-actions">
      <select id="graduation-preset" v-model="preset" :disabled="pending">
        <option v-for="key in ['all', 'combat', 'base', 'mounts', 'core']" :key="key" :value="key">
          {{ t(`Graduation_${key}`) }} · {{ presets?.[key]?.length ?? '…' }}
        </option>
      </select>
      <button type="button" class="editor-button" :disabled="!presets || pending" @click="add">{{ t('Graduation_Add') }}</button>
    </div>
    <p>{{ t('Graduation_Rules') }}</p>
    <ul>
      <li v-for="entry in entries" :key="`${entry.role}-${entry.species}`">
        <strong>{{ entry.name }}</strong> · {{ t(`Graduation_${entry.role}`) }}
      </li>
    </ul>
  </section>
</template>

<style scoped>
.graduation-kit { padding: 1rem; overflow: auto; color: var(--editor-color-text); }
.graduation-kit p { color: var(--editor-color-muted); line-height: 1.7; }
.graduation-actions { display: flex; flex-wrap: wrap; gap: .75rem; margin-top: .5rem; }
.graduation-actions select { padding: .6rem; border: 1px solid var(--editor-color-border); border-radius: .5rem; background: var(--editor-color-control); color: inherit; }
.graduation-kit ul { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: .6rem 1.5rem; padding-left: 1.5rem; }
</style>
