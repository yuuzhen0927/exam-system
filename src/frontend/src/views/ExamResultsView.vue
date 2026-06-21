<template>
  <div class="page-container">
    <div class="page-header"><h2>成绩查询</h2></div>

    <div class="toolbar">
      <el-input v-model="searchText" placeholder="搜索姓名或用户名..." clearable size="default" style="max-width:280px">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filterPassed" clearable placeholder="筛选状态" style="width:110px" size="default">
        <el-option label="全部" value="" />
        <el-option label="通过" value="1" />
        <el-option label="未通过" value="0" />
      </el-select>
      <el-select v-model="filterCheating" clearable placeholder="作弊" style="width:100px" size="default">
        <el-option label="是" value="1" />
        <el-option label="否" value="0" />
      </el-select>
    </div>

    <div v-if="!filteredItems.length" class="empty-state">
      <el-empty :description="searchText||filterPassed||filterCheating?'未找到匹配结果':'暂无成绩数据'" />
    </div>

    <div v-else class="result-grid">
      <div v-for="item in filteredItems" :key="item.id" class="result-card" :class="{passed: item.passed, failed: !item.passed, cheating: item.is_cheating}">
        <div class="rc-avatar" :style="{background: avatarColor(item.fullname || item.username)}">
          {{ (item.fullname || item.username || '?')[0].toUpperCase() }}
        </div>
        <div class="rc-body">
          <div class="rc-name">{{ item.fullname || item.username }}</div>
          <div class="rc-username">@{{ item.username }}</div>
          <div class="rc-tags">
            <el-tag :type="item.passed?'success':'danger'" size="small">{{ item.passed?'通过':'未过' }}</el-tag>
            <el-tag v-if="item.is_cheating" type="danger" size="small">作弊</el-tag>
          </div>
        </div>
        <div class="rc-scores">
          <div class="rc-score-row">
            <span class="rc-score-label">自动</span>
            <span class="rc-score-val">{{ item.auto_score ?? '-' }}</span>
          </div>
          <div class="rc-score-row">
            <span class="rc-score-label">人工</span>
            <span class="rc-score-val">{{ item.manual_score != null ? item.manual_score : '-' }}</span>
          </div>
          <div class="rc-time">{{ item.finished_at?.slice(0,16) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Search } from '@element-plus/icons-vue'

import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const items = ref([])
const searchText = ref('')
const filterPassed = ref('')
const filterCheating = ref('')

const filteredItems = computed(() => {
  let list = items.value
  if (searchText.value) {
    const q = searchText.value.toLowerCase()
    list = list.filter(i => (i.fullname||'').toLowerCase().includes(q) || (i.username||'').toLowerCase().includes(q))
  }
  if (filterPassed.value !== '') list = list.filter(i => i.passed === (filterPassed.value === '1'))
  if (filterCheating.value !== '') list = list.filter(i => i.is_cheating === (filterCheating.value === '1'))
  return list
})

const avatarColors = ['#4f6ef7','#22c55e','#f59e0b','#ef4444','#8b5cf6','#ec4899','#06b6d4','#f97316','#84cc16','#6366f1']
function avatarColor(name) {
  let hash = 0
  for (let i = 0; i < (name||'').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return avatarColors[Math.abs(hash) % avatarColors.length]
}

onMounted(async () => {
  const { data } = await api.get(`/exams/${route.params.id}/results`)
  items.value = data.items || []
})
</script>

<style scoped>
.toolbar { display: flex; gap: 8px; margin-bottom: var(--space-4); flex-wrap: wrap; }
.result-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-3); }
.result-card {
  display: flex; gap: var(--space-3);
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); border-left: 4px solid var(--gray-200);
  transition: box-shadow var(--transition-fast);
}
.result-card:hover { box-shadow: var(--shadow-sm); }
.result-card.passed { border-left-color: var(--color-success); }
.result-card.failed { border-left-color: var(--color-danger); }
.result-card.cheating { background: var(--gray-25)5f5; }

.rc-avatar {
  width: 44px; height: 44px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: var(--font-bold); font-size: 16px; flex-shrink: 0;
}
.rc-body { flex: 1; min-width: 0; }
.rc-name { font-weight: var(--font-semibold); font-size: var(--text-base); color: var(--gray-900); }
.rc-username { font-size: var(--text-xs); color: var(--gray-400); margin: 2px 0 6px; }
.rc-tags { display: flex; gap: 4px; flex-wrap: wrap; }

.rc-scores { text-align: right; flex-shrink: 0; min-width: 80px; }
.rc-score-row { display: flex; justify-content: flex-end; gap: 6px; margin-bottom: 2px; }
.rc-score-label { font-size: var(--text-xs); color: var(--gray-400); }
.rc-score-val { font-size: var(--text-md); font-weight: var(--font-bold); color: var(--gray-900); }
.rc-time { font-size: var(--text-xs); color: var(--gray-400); margin-top: 6px; }

@media (max-width: 768px) {
  .result-grid { grid-template-columns: 1fr; }
  .result-card { padding: var(--space-3); }
}
</style>
