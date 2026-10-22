import { ref } from 'vue';
import { defineStore } from 'pinia';
import { getAdventureAdvice, applyAdventureAdvice } from '../api/players.js';
import { useSessionStore } from './session.js';
import { useBackendStore } from './backend.js';
import { usePlayersStore } from './players.js';
import { playerRosterKey, useRostersStore } from './rosters.js';
import { useMessagesStore } from './messages.js';

export const useAdventureStore = defineStore('adventure', () => {
    const session = useSessionStore();
    const backend = useBackendStore();
    const players = usePlayersStore();
    const rosters = useRostersStore();
    const messages = useMessagesStore();
    const advice = ref(null);
    const loading = ref(false);
    const pending = ref(false);
    const failed = ref(false);
    let serial = 0;
    let context = null;

    function clear() {
        serial += 1;
        context = null;
        advice.value = null;
        loading.value = false;
        failed.value = false;
    }

    const current = (uid, epoch, ticket) => ticket === serial
        && session.isCurrentSession(epoch) && rosters.activePlayerUid === uid;

    async function load(goal, ceiling) {
        const uid = rosters.activePlayerUid;
        const epoch = session.sessionEpoch;
        const ticket = ++serial;
        context = null;
        advice.value = null;
        failed.value = false;
        if (!uid) { loading.value = false; return; }
        loading.value = true;
        try {
            const reply = await getAdventureAdvice(uid, goal, ceiling, session.readOptions());
            if (!current(uid, epoch, ticket)) return;
            advice.value = reply;
            context = { uid, epoch, ticket, goal, ceiling };
        } catch (error) {
            if (!current(uid, epoch, ticket)) return;
            failed.value = true;
            backend.reportApiFailure(error, 'Operation_Load_Player_Data');
        } finally {
            if (current(uid, epoch, ticket)) loading.value = false;
        }
    }

    async function apply(row) {
        const active = context;
        if (pending.value || !active || !current(active.uid, active.epoch, active.ticket)
            || !row?.can_apply || !advice.value?.recommendations.some(r => r.id === row.id && r.token === row.token)) return false;
        pending.value = true;
        try {
            return await session.runOperation(async () => {
                let reply;
                try {
                    reply = await applyAdventureAdvice(active.uid, {
                        goal: active.goal, ceiling: active.ceiling,
                        recommendationId: row.id, token: row.token,
                    });
                } catch (error) {
                    if (current(active.uid, active.epoch, active.ticket)) {
                        if (error.code === 'ADVENTURE_STALE') {
                            messages.showToast('Adventure_Stale');
                            await load(active.goal, active.ceiling);
                        } else backend.reportApiFailure(error, 'Operation_Update_Player');
                    }
                    return false;
                }
                if (!current(active.uid, active.epoch, active.ticket)) return false;
                players.inventory = reply.inventory;
                advice.value = reply.advice;
                messages.showToast('Adventure_Added', 'success', [reply.result.name, reply.result.quantity]);
                if (reply.result.kind === 'pal') {
                    // A refresh failure must not turn a successful addition into
                    // a retry of the write. The returned advice already removes it.
                    try {
                        await rosters.loadRosters();
                        if (current(active.uid, active.epoch, active.ticket)) {
                            await rosters.loadRosterPals(playerRosterKey(active.uid));
                        }
                    } catch (error) {
                        backend.reportApiFailure(error, 'Operation_Load_Player_Data');
                    }
                }
                return true;
            });
        } finally { pending.value = false; }
    }

    return { advice, loading, pending, failed, load, apply, clear };
});
