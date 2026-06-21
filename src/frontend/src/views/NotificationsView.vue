<template>
  <div class="page-root">
    <div class="page-header">
      <h2>通知中心</h2>
      <el-button v-if="items.length" size="small" @click="markAllRead">全部已读</el-button>
    </div>
    <div v-if="loading" class="empty-hint">加载中...</div>
    <div v-else-if="!items.length" class="empty-hint">暂无通知</div>
    <div v-else class="notif-list">
      <div v-for="n in items" :key="n.id" class="notif-card" :class="{unread: !n.is_read}" @click="markRead(n)">
        <div class="notif-icon" :class="n.type">{{ iconMap[n.type] || '📢' }}</div>
        <div class="notif-body">
          <div class="notif-title">{{ n.title }}</div>
          <div class="notif-content">{{ n.content }}</div>
          <div class="notif-time">{{ n.created_at?.slice(0,16) }}</div>
        </div>
        <span v-if="!n.is_read" class="unread-dot"></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const items = ref([])
const loading = ref(true)
const iconMap = { announcement: '📢', exam_remind: '📝', cert_issued: '🎓', feedback_reply: '💬', system: '🔔' }

onMounted(async () => { try {
  const { data } = await api.get('/notifications', { params: { page_size: 50 } })
  items.value = (data.data?.items || data.items || [])
} catch {} loading.value = false })

async function markRead(n) {
  if (n.is_read) return
  try { await api.put(`/notifications/${n.id}/read`); n.is_read = true } catch {}
}
async function markAllRead() {
  try { await api.put('/notifications/read-all'); items.value.forEach(n => n.is_read = true) } catch {}
}
</script>

<style scoped>
.page-root { max-width: 800px; margin: 0 auto; padding: var(--space-4); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); }
.empty-hint { text-align: center; padding: 48px 0; color: var(--gray-500); }
.notif-list { display: flex; flex-direction: column; gap: 12px; }
.notif-card { display: flex; align-items: flex-start; gap: 12px; padding: 16px; background: var(--gray-25); border-radius: 8px; cursor: pointer; transition: background .2s; position: relative; }
.notif-card:hover { background: var(--gray-50); }
.notif-card.unread { background: var(--color-primary-light); border-left: 3px solid var(--color-primary); }
.notif-icon { font-size: 24px; flex-shrink: 0; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; background: var(--gray-50); border-radius: 50%; }
.notif-body { flex: 1; min-width: 0; }
.notif-title { font-weight: 600; margin-bottom: 4px; }
.notif-content { font-size: 13px; color: var(--gray-600); margin-bottom: 4px; }
.notif-time { font-size: 12px; color: var(--gray-400); }
.unread-dot { width: 8px; height: 8px; background: var(--color-primary); border-radius: 50%; flex-shrink: 0; margin-top: 8px; }
</style>
