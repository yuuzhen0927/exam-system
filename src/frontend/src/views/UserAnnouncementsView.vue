<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:var(--color-warning-light);color:var(--color-warning)"><el-icon size="22"><Bell /></el-icon></div>
        <div><h2>公告通知</h2><p class="ph-sub">共 {{ items.length }} 条公告</p></div>
      </div>
    </div>

    <div v-if="!items.length" class="empty-wrap">
      <el-empty description="暂无公告" />
    </div>

    <div v-else class="ann-list">
      <div v-for="a in items" :key="a.id" class="ann-item" :class="{ pinned: a.is_pinned }">
        <div class="ann-item-header">
          <el-tag v-if="a.is_pinned" type="danger" size="small" effect="dark">置顶</el-tag>
          <span class="ann-item-title">{{ a.title }}</span>
          <span class="ann-item-date">{{ new Date(a.created_at).toLocaleDateString('zh-CN') }}</span>
        </div>
        <div class="ann-item-content">{{ a.content }}</div>
        <div v-if="a.created_by" class="ann-item-meta">发布者：{{ a.created_by }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Bell } from '@element-plus/icons-vue'

import { ref, onMounted } from 'vue'
import api from '../api'

const items = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/announcements', { params: { published_only: true, page_size: 50 } })
    items.value = data.items || data || []
  } catch {}
})
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-4); }
.ph-left { display: flex; align-items: center; gap: var(--space-3); }
.ph-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }
.empty-wrap { padding: 60px 0; }

.ann-list { display: flex; flex-direction: column; gap: var(--space-3); }
.ann-item {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: 20px;
  border: 1px solid var(--gray-100); transition: all 0.2s;
}
.ann-item:hover { border-color: var(--color-primary); box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.ann-item.pinned { border-left: 4px solid var(--color-danger); background: #fef2f2; }
.ann-item-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.ann-item-title { font-weight: 700; font-size: 16px; color: var(--gray-900); flex: 1; }
.ann-item-date { font-size: 13px; color: var(--gray-400); white-space: nowrap; }
.ann-item-content { font-size: 14px; color: var(--gray-600); line-height: 1.8; white-space: pre-wrap; word-break: break-word; }
.ann-item-meta { margin-top: 12px; font-size: 12px; color: var(--gray-400); }

@media (max-width: 768px) {
  .ann-item { padding: 16px; }
  .ann-item-title { font-size: 15px; }
}
</style>
