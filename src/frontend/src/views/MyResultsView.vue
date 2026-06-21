<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:#fef3c7;color:#d97706"><el-icon size="22"><Trophy /></el-icon></div>
        <div><h2>我的成绩</h2><p class="ph-sub">查看所有考试成绩记录</p></div>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon" style="background:#e8f0fe;color:var(--color-primary)"><el-icon size="20"><Document /></el-icon></div>
        <div class="stat-info"><span class="stat-num">{{ results.length }}</span><span class="stat-label">考试次数</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:var(--color-success-light);color:var(--color-success)"><el-icon size="20"><CircleCheck /></el-icon></div>
        <div class="stat-info"><span class="stat-num">{{ passCount }}</span><span class="stat-label">通过次数</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:var(--color-danger-light);color:var(--color-danger)"><el-icon size="20"><WarningFilled /></el-icon></div>
        <div class="stat-info"><span class="stat-num">{{ results.length - passCount }}</span><span class="stat-label">未通过</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#ede9fe;color:#7c3aed"><el-icon size="20"><TrendCharts /></el-icon></div>
        <div class="stat-info"><span class="stat-num">{{ avgScore }}</span><span class="stat-label">平均分</span></div>
      </div>
    </div>

    <!-- Search -->
    <div class="toolbar">
      <el-input v-model="searchText" placeholder="搜索考试名称..." clearable size="default" style="max-width:300px">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <div v-if="!filteredResults.length" class="empty-wrap"><el-empty description="暂无考试记录" /></div>

    <div v-else class="results-grid">
      <div v-for="r in filteredResults" :key="r.id" class="result-card" @click="goDetail(r)">
        <div class="rc-header">
          <div class="rc-title">{{ r.exam_title || '考试' }}</div>
          <el-tag v-if="r.manual_score === null && r.manual_score !== 0" type="warning" size="small" effect="plain">待人工评分</el-tag><el-tag v-else :type="r.passed ? 'success' : 'danger'" size="small" effect="plain">{{ r.passed ? '通过' : '未通过' }}</el-tag>
        </div>
        <div class="rc-score-row">
          <div v-if="r.manual_score === null" class="rc-score pending">待评分</div><div v-else class="rc-score" :class="r.passed ? 'pass' : 'fail'">{{ (r.auto_score ?? 0) + (r.manual_score ?? 0) }}</div><div class="rc-score-label">/ {{ r.total_score || 100 }} 分</div>
        </div>
        <div class="rc-meta">
          <span v-if="r.mode === 'formal'"><el-icon><Warning /></el-icon> 正式考试</span>
          <span v-else><el-icon><Document /></el-icon> 模拟考试</span>
          <span v-if="r.finished_at">{{ r.finished_at?.slice(0, 16).replace('T', ' ') }}</span>
          <span v-if="r.tab_switches > 0" style="color:var(--color-danger)">切屏 {{ r.tab_switches }} 次</span>
        </div>
        <div class="rc-actions">
          <el-button size="small" type="primary" text @click.stop="goReview(r)">查看详情</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { Trophy, Document, CircleCheck, WarningFilled, TrendCharts, Search, Warning } from '@element-plus/icons-vue'

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const results = ref([])
const searchText = ref('')

const passCount = computed(() => results.value.filter(r => r.passed).length)
const avgScore = computed(() => {
  if (!results.value.length) return '0'
  const sum = results.value.reduce((a, r) => a + (r.auto_score || 0), 0)
  return (sum / results.value.length).toFixed(1)
})

const filteredResults = computed(() => {
  if (!searchText.value) return results.value
  const q = searchText.value.toLowerCase()
  return results.value.filter(r => (r.exam_title || '').toLowerCase().includes(q))
})

onMounted(async () => {
  try {
    const { data } = await api.get('/exams/my-results')
    results.value = data.items || data || []
  } catch {
    results.value = []
  }
})

function goDetail(r) { router.push(`/review/${r.id}`) }
function goReview(r) { router.push(`/review/${r.id}`) }
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-4); gap: var(--space-3); flex-wrap: wrap; }
.ph-left { display: flex; align-items: center; gap: var(--space-3); }
.ph-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }

.stats-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: var(--space-3); margin-bottom: var(--space-4); }
.stat-card {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); border: 1px solid var(--gray-100);
  display: flex; align-items: center; gap: var(--space-3);
}
.stat-icon { width: 44px; height: 44px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-info { display: flex; flex-direction: column; }
.stat-num { font-size: 22px; font-weight: 700; color: var(--gray-900); line-height: 1.2; }
.stat-label { font-size: 12px; color: var(--gray-500); margin-top: 2px; }

.toolbar { margin-bottom: var(--space-4); }
.empty-wrap { padding: 60px 0; }

.results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--space-3); }
.result-card {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); border: 1px solid var(--gray-100);
  cursor: pointer; transition: all 0.2s;
}
.result-card:hover { box-shadow: var(--shadow-sm); transform: translateY(-1px); }
.rc-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-3); }
.rc-title { font-size: 15px; font-weight: 600; color: var(--gray-900); }
.rc-score-row { display: flex; align-items: baseline; gap: 4px; margin-bottom: var(--space-2); }
.rc-score { font-size: 32px; font-weight: 700; line-height: 1; }
.rc-score.pass { color: var(--color-success); }
.rc-score.fail { color: var(--color-danger); }.rc-score.pending { color: var(--color-warning, #e6a23c); font-size: 20px; }
.rc-score-label { font-size: 14px; color: var(--gray-400); }
.rc-meta { display: flex; gap: var(--space-3); font-size: 12px; color: var(--gray-500); margin-bottom: var(--space-2); flex-wrap: wrap; }
.rc-meta span { display: flex; align-items: center; gap: 4px; }
.rc-actions { display: flex; justify-content: flex-end; }

@media (max-width: 768px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .results-grid { grid-template-columns: 1fr; }
}
</style>
