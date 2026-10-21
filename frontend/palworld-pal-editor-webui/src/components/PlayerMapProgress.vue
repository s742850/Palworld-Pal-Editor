<script setup>
import { ref, watch } from 'vue'
import { getMapProgress, updateMapProgress } from '@/api/players'
import { useAppStore } from '@/stores/app'
import { useBackendStore } from '@/stores/backend'
import { useMessagesStore } from '@/stores/messages'
import { useRostersStore } from '@/stores/rosters'
import { useSessionStore } from '@/stores/session'

const app = useAppStore()
const backend = useBackendStore()
const messages = useMessagesStore()
const rosters = useRostersStore()
const session = useSessionStore()
const status = ref(null)
const current = (uid, epoch) => rosters.activePlayerUid === uid && session.isCurrentSession(epoch)
watch(() => rosters.activePlayerUid, async uid => {
  status.value = null
  if (!uid) return
  const epoch = session.sessionEpoch
  try {
    const reply = await getMapProgress(uid, session.readOptions())
    if (current(uid, epoch)) status.value = reply
  } catch (error) {
    if (current(uid, epoch)) backend.reportApiFailure(error, 'Operation_Load_Player_Data')
  }
}, { immediate: true })

const apply = async operation => {
  const uid = rosters.activePlayerUid
  const epoch = session.sessionEpoch
  try {
    const reply = await session.runOperation(() => updateMapProgress(uid, operation))
    if (!current(uid, epoch)) return
    status.value = reply
    messages.showToast('Map_Save_Reminder', 'success')
  } catch (error) {
    backend.reportApiFailure(error, 'Operation_Update_Player')
  }
}
</script>

<template>
  <section class="map-progress">
    <h2>{{ app.getTranslatedText('Map_Title') }}</h2>
    <p>{{ app.getTranslatedText('Map_Description') }}</p>
    <article>
      <h3>{{ app.getTranslatedText('Map_Reveal') }}</h3>
      <button type="button" class="editor-button" :disabled="!status?.fog.available" @click="apply('reveal')">
        {{ app.getTranslatedText('Map_Reveal') }}
      </button>
      <p v-if="status?.fog.reason" role="status">{{ status.fog.reason }}</p>
      <p v-for="map in status?.fog.maps" :key="map.name">{{ map.name }}: {{ map.revealed }} / {{ map.pixels }}</p>
    </article>
    <article>
      <h3>{{ app.getTranslatedText('Map_Travel') }}</h3>
      <button type="button" class="editor-button" :disabled="!status?.travel.available" @click="apply('unlock-travel')">
        {{ app.getTranslatedText('Map_Travel') }}
      </button>
      <p v-if="status?.travel.available">{{ status.travel.unlocked }} / {{ status.travel.total }} · {{ status.catalog }}</p>
      <p v-if="status?.travel.reason" role="status">{{ status.travel.reason }}</p>
    </article>
    <p>{{ app.getTranslatedText('Map_Save_Reminder') }}</p>
  </section>
</template>

<style scoped>
.map-progress { padding: 1rem; overflow: auto; color: var(--editor-color-text); }
.map-progress article { padding: 1rem; margin: .75rem 0; border: 1px solid var(--editor-color-border); border-radius: .75rem; background: var(--editor-color-glass-surface); }
.map-progress p { color: var(--editor-color-muted); }
</style>
