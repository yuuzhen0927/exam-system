<template>
  <div class="page-container">
    <div class="page-header"><h2>练习记录</h2></div>

    <div class="stats-row">
      <div class="stat-item"><span class="stat-num">{{ total }}</span><span class="stat-label">练习次数</span></div>
      <div class="stat-item"><span class="stat-num">{{ totalQuestions }}</span><span class="stat-label">答题总数</span></div>
      <div class="stat-item" :class="overallAccuracy>=80?'pass':overallAccuracy>=60?'warn':'fail'">
        <span class="stat-num">{{ overallAccuracy }}%</span><span class="stat-label">总正确率</span>
      </div>
      <div class="stat-item"><span class="stat-num">{{ formatDuration(totalDuration) }}</span><span class="stat-label">累计用时</span></div>
    </div>

    <div class="search-bar">
      <el-input v-model="searchText" placeholder="搜索科目或练习模式..." clearable size="default">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <div v-if="!filteredRecords.length" class="empty-state">
      <el-empty :description="searchText?'未找到匹配记录':'暂无练习记录，去练习中心开始吧'">
        <el-button v-if="!searchText" type="primary" @click="$router.push('/practice')">去练习</el-button>
      </el-empty>
    </div>

    <div v-else class="records-wrapper">
      <div v-for="r in filteredRecords" :key="r.id" class="record-item" @click="openDetail(r)">
        <div class="ri-bar" :class="accuracyClass(r)"></div>
        <div class="ri-main">
          <div class="ri-top">
            <div class="ri-info">
              <div class="ri-title">{{ r.subject_name || '综合练习' }}</div>
              <div class="ri-tags">
                <el-tag size="small" type="info">{{ modeLabel(r.mode) }}</el-tag>
                <el-tag size="small" v-if="r.question_type">{{ typeLabel(r.question_type) }}</el-tag>
              </div>
            </div>
            <div class="ri-accuracy">
              <div class="ri-pct" :style="{color:accuracyColor(r)}">{{ calcAccuracy(r) }}%</div>
              <div class="ri-count">{{ r.correct_count }} / {{ r.total_count }} 正确</div>
            </div>
          </div>
          <div class="ri-bottom">
            <span class="ri-time">{{ r.created_at?.slice(0,16) }}</span>
            <span class="ri-duration">用时 {{ formatDuration(r.duration_seconds) }}</span>
            
          </div>
        </div>
      </div>
    </div>

    <el-pagination v-if="total > pageSize" v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="loadRecords" style="justify-content:center;margin-top:20px" size="small" />

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="练习详情" width="700px" :close-on-click-modal="true">
      <div v-if="detail" class="detail-wrap">
        <div class="detail-header">
          <span class="dh-subject">{{ detail.subject_name || '综合练习' }} · {{ modeLabel(detail.mode) }}</span>
          <span class="dh-score" :style="{color: accuracyColor(detail)}">{{ detail.correct_count }}/{{ detail.total_count }} ({{ calcAccuracy(detail) }}%)</span>
        </div>
        <div class="detail-list">
          <div v-for="(d, i) in detail.details" :key="i" class="detail-q" :class="{correct: d.is_correct, wrong: !d.is_correct}">
            <div class="dq-header">
              <span class="dq-num">{{ i+1 }}.</span>
              <el-tag size="small" :type="d.is_correct?'success':'danger'">{{ d.is_correct?'正确':'错误' }}</el-tag>
            </div>
            <div class="dq-content">{{ d.content }}</div>
            <div v-if="d.type!=='composite'" class="dq-options">
              <span v-for="o in d.options" :key="o.label" class="dq-opt" :class="{user: o.label===d.user_answer, correct: o.label===d.answer}">{{ o.label }}. {{ o.text }}</span>
            </div>
            <div v-else class="dq-answer">你的答案：{{ d.user_answer || '(未作答)' }}</div>
            <div v-if="!d.is_correct && d.answer" class="dq-correct">正确答案：{{ d.answer }}</div>
            <div v-if="d.explanation" class="dq-explain">{{ d.explanation }}</div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { Search } from '@element-plus/icons-vue'

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const records = ref([])
const page = ref(1)
const pageSize = 20
const total = ref(0)
const searchText = ref('')
const detailVisible = ref(false)
const detail = ref(null)

const filteredRecords = computed(() => {
  if (!searchText.value) return records.value
  const q = searchText.value.toLowerCase()
  return records.value.filter(r =>
    (r.subject_name || '').includes(q) || modeLabel(r.mode).includes(q)
  )
})

const totalQuestions = computed(() => records.value.reduce((s, r) => s + (r.total_count || 0), 0))
const overallAccuracy = computed(() => {
  const sc = records.value.reduce((s, r) => s + (r.correct_count || 0), 0)
  const st = records.value.reduce((s, r) => s + (r.total_count || 0), 0)
  return st ? Math.round((sc / st) * 100) : 0
})
const totalDuration = computed(() => records.value.reduce((s, r) => s + (r.duration_seconds || 0), 0))

function modeLabel(m) { return { random:'随机练习', memorize:'背题模式', specialty:'专项练习', chapter:'章节练习', wrongbook:'错题重做' }[m] || m }
function typeLabel(t) { return { single:'单选题', multi:'多选题', truefalse:'判断题', composite:'综合题' }[t] || t }
function calcAccuracy(row) {
  if (!row.total_count) return 0
  return Math.round((row.correct_count / row.total_count) * 100)
}
function accuracyColor(row) {
  const p = calcAccuracy(row)
  if (p >= 80) return 'var(--color-success)'
  if (p >= 60) return 'var(--color-warning)'
  return 'var(--color-danger)'
}
function accuracyClass(row) {
  const p = calcAccuracy(row)
  if (p >= 80) return 'good'
  if (p >= 60) return 'ok'
  return 'bad'
}
function formatDuration(s) {
  if (!s || s < 0) return '-'
  const m = Math.floor(s / 60)
  const sec = s % 60
  return m > 0 ? `${m}分${sec}秒` : `${sec}秒`
}

async function loadRecords() {
  try {
    const { data } = await api.get('/practice/records', { params: { page: page.value, page_size: pageSize } })
    records.value = data.items || []
    total.value = data.total || 0
  } catch {}
}

async function retryWrong(row) {
  try {
    const { data } = await api.get('/practice/records/' + row.id + '/wrong-questions')
    if (!data.length) { ElMessage.info('该记录无错题'); return }
    sessionStorage.setItem('practice_session', JSON.stringify({ questions: data, recordId: null, mode: 'wrongbook' }))
    router.push('/practice')
  } catch (e) { ElMessage.error('获取错题失败') }
}

async function openDetail(r) {
  try {
    const { data } = await api.get(`/practice/records/${r.id}/detail`)
    detail.value = data
    detailVisible.value = true
  } catch { ElMessage.error('获取详情失败') }
}

onMounted(() => loadRecords())
</script>

<style scoped>
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); margin-bottom: var(--space-5); }
.stat-item { background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4); text-align: center; box-shadow: var(--shadow-xs); }
.stat-item.pass { background: var(--color-success-light); }
.stat-item.warn { background: var(--color-warning-light); }
.stat-item.fail { background: var(--color-danger-light); }
.stat-num { display: block; font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--gray-900); line-height: 1.2; }
.stat-label { font-size: var(--text-xs); color: var(--gray-500); margin-top: 4px; display: block; }

.search-bar { margin-bottom: var(--space-5); max-width: 360px; }

.records-wrapper { display: flex; flex-direction: column; gap: var(--space-3); }

.record-item {
  display: flex; background: var(--gray-25); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs); overflow: hidden;
}
.ri-bar { width: 4px; flex-shrink: 0; }
.ri-bar.good { background: var(--color-success); }
.ri-bar.ok { background: var(--color-warning); }
.ri-bar.bad { background: var(--color-danger); }

.ri-main { flex: 1; padding: var(--space-4); min-width: 0; }
.ri-top { display: flex; justify-content: space-between; align-items: flex-start; gap: var(--space-4); margin-bottom: var(--space-3); }
.ri-info { flex: 1; min-width: 0; }
.ri-title { font-size: var(--text-base); font-weight: var(--font-semibold); color: var(--gray-900); margin-bottom: var(--space-2); }
.ri-tags { display: flex; gap: 4px; }

.ri-accuracy { text-align: right; flex-shrink: 0; }
.ri-pct { font-size: var(--text-xl); font-weight: var(--font-bold); line-height: 1; margin-bottom: 2px; }
.ri-count { font-size: var(--text-xs); color: var(--gray-500); }

.ri-bottom { display: flex; align-items: center; gap: var(--space-4); font-size: var(--text-xs); color: var(--gray-500); }
.ri-time { flex: 1; }
.ri-duration { color: var(--gray-400); }

@media (max-width: 768px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .ri-main { padding: var(--space-3); }
  .ri-pct { font-size: var(--text-lg); }
  .ri-bottom { flex-wrap: wrap; gap: var(--space-2); }
  .ri-duration { display: none; }
}

/* ===== Detail Dialog ===== */
.detail-wrap { max-height: 60vh; overflow-y: auto; }
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); padding-bottom: var(--space-3); border-bottom: 1px solid var(--gray-100); }
.dh-subject { font-size: var(--text-md); font-weight: var(--font-semibold); color: var(--gray-900); }
.dh-score { font-size: var(--text-lg); font-weight: var(--font-bold); }
.detail-list { display: flex; flex-direction: column; gap: var(--space-3); }
.detail-q { padding: var(--space-3); border-radius: var(--radius-md); border-left: 3px solid var(--gray-200); }
.detail-q.correct { border-left-color: var(--color-success); background: var(--color-success-light); }
.detail-q.wrong { border-left-color: var(--color-danger); background: var(--color-danger-light); }
.dq-header { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-1); }
.dq-num { font-weight: var(--font-bold); font-size: var(--text-sm); }
.dq-content { font-size: var(--text-sm); margin-bottom: var(--space-2); line-height: 1.6; }
.dq-options { display: flex; flex-wrap: wrap; gap: var(--space-1); margin-bottom: var(--space-2); }
.dq-opt { font-size: var(--text-xs); padding: 2px 8px; border-radius: var(--radius-sm); background: var(--gray-50); }
.dq-opt.correct { background: var(--color-success-light); color: var(--color-success); font-weight: var(--font-bold); }
.dq-opt.user:not(.correct) { background: var(--color-danger-light); color: var(--color-danger); text-decoration: line-through; }
.dq-answer { font-size: var(--text-xs); color: var(--gray-600); margin-bottom: var(--space-1); }
.dq-correct { font-size: var(--text-xs); color: var(--color-success); font-weight: var(--font-semibold); margin-bottom: var(--space-1); }
.dq-explain { font-size: var(--text-xs); color: var(--gray-600); background: rgba(255,255,255,0.5); padding: var(--space-2); border-radius: var(--radius-sm); }

</style>
