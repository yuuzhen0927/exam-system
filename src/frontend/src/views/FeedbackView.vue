<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:var(--color-success-light);color:var(--color-success)"><el-icon><ChatLineSquare /></el-icon></div>
        <div><h2>题目反馈</h2><p class="ph-sub">学员提交的题目疑问与纠错</p></div>
      </div>
    </div>

    <div class="filter-bar">
      <el-input v-model="searchText" placeholder="搜索反馈内容..." clearable class="fb-search">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="statusFilter" placeholder="状态" clearable @change="load" style="min-width:110px">
        <el-option label="待处理" value="pending" /><el-option label="已采纳" value="accepted" /><el-option label="已拒绝" value="rejected" />
      </el-select>
    </div>

    <div v-if="!filteredItems.length" class="empty-wrap"><el-empty description="暂无反馈" /></div>

    <div v-else class="fb-grid">
      <div v-for="r in filteredItems" :key="r.id" class="fb-card" :class="'fb-' + r.status">
        <div class="fb-top">
          <div class="fb-tags">
            <el-tag size="small" :type="r.type==='doubt'?'warning':'danger'">{{ r.type === 'doubt' ? '疑问' : '纠错' }}</el-tag>
            <el-tag size="small" :type="r.status==='pending'?'warning':r.status==='accepted'?'success':'danger'" effect="plain">{{ statusLabel(r.status) }}</el-tag>
          </div>
          <span class="fb-time">{{ r.created_at?.substring(0, 10) }}</span>
        </div>
        <div class="fb-user">{{ r.username }}</div>
        <div v-if="r.question_content" class="fb-question">题目: {{ r.question_content?.substring(0, 60) }}{{ r.question_content?.length > 60 ? '...' : '' }}</div>
        <div class="fb-body">{{ r.content }}</div>
        <div v-if="r.status === 'pending'" class="fb-btns">
          <el-button size="small" type="success" @click="reply(r, 'accepted')">采纳</el-button>
          <el-button size="small" type="danger" @click="reply(r, 'rejected')">拒绝</el-button>
        </div>
        <div v-else class="fb-result">{{ r.replied_by }} · {{ r.updated_at?.substring(0, 10) }}</div>
      </div>
    </div>

    <div v-if="total > 20" class="page-pagination">
      <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="prev,next" @current-change="load" size="small" />
    </div>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, ChatLineSquare } from '@element-plus/icons-vue'

import { ref, computed, onMounted } from 'vue'
import api from '../api'

const items = ref([])
const total = ref(0)
const page = ref(1)
const statusFilter = ref('pending')
const searchText = ref('')

const filteredItems = computed(() => {
  if (!searchText.value) return items.value
  const q = searchText.value.toLowerCase()
  return items.value.filter(r => (r.content || '').toLowerCase().includes(q) || (r.question_content || '').toLowerCase().includes(q))
})

onMounted(load)

async function load() {
  const params = { page: page.value, page_size: 20 }
  if (statusFilter.value) params.status = statusFilter.value
  const { data } = await api.get('/feedback', { params })
  items.value = data.items; total.value = data.total
}

async function reply(row, status) {
  await api.put(`/feedback/${row.id}/reply`, { reply: status === 'accepted' ? '已采纳' : '已拒绝', status })
  row.status = status
  ElMessage.success('已处理')
}

function statusLabel(s) { return { pending: '待处理', accepted: '已采纳', rejected: '已拒绝' }[s] || s }
</script>

<style scoped>
.page-header { margin-bottom: var(--space-4); }
.ph-left { display: flex; align-items: center; gap: var(--space-3); }
.ph-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }

.filter-bar { display: flex; gap: var(--space-2); margin-bottom: var(--space-4); align-items: center; }
.fb-search { max-width: 280px; flex: 1; min-width: 150px; }
.empty-wrap { padding: 60px 0; }

.fb-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: var(--space-3); }
.fb-card {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); border: 1px solid var(--gray-100);
  transition: all 0.2s; display: flex; flex-direction: column; gap: var(--space-2);
}
.fb-card:hover { box-shadow: var(--shadow-sm); }
.fb-card.fb-accepted { border-left: 3px solid #22c55e; }
.fb-card.fb-rejected { border-left: 3px solid #ef4444; opacity: 0.6; }
.fb-top { display: flex; justify-content: space-between; align-items: center; }
.fb-tags { display: flex; gap: 6px; }
.fb-time { font-size: 12px; color: var(--gray-400); }
.fb-user { font-weight: 600; font-size: 13px; color: var(--gray-900); }
.fb-question { font-size: 13px; color: var(--gray-600); background: var(--gray-50); padding: 8px 12px; border-radius: var(--radius-md); }
.fb-body { font-size: 14px; line-height: 1.6; color: var(--gray-800); }
.fb-btns { display: flex; gap: 8px; padding-top: var(--space-2); border-top: 1px solid var(--gray-100); }
.fb-result { font-size: 12px; color: var(--gray-500); text-align: right; }

.page-pagination { margin-top: var(--space-4); display: flex; justify-content: center; }

@media (max-width: 768px) {
  .filter-bar { flex-direction: column; }
  .fb-search { max-width: 100%; }
  .fb-grid { grid-template-columns: 1fr; }
}
</style>
