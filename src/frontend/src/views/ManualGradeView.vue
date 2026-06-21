<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:var(--color-danger-light);color:var(--color-danger)"><el-icon size="22"><Checked /></el-icon></div>
        <div><h2>人工批改</h2><p class="ph-sub">{{ grading ? '批改详情' : pendingCount + ' 份待批改' }}</p></div>
      </div>
      <el-button v-if="grading" @click="backToList">返回列表</el-button>
    </div>

    <!-- Pending List -->
    <template v-if="!grading">
      <div v-if="!pendings.length" class="empty-wrap"><el-empty description="暂无待批改试卷" /></div>
      <div v-else class="pend-grid">
        <div v-for="p in pendings" :key="p.id" class="pend-card">
          <div class="pc-top">
            <span class="pc-title">{{ p.exam_title }}</span>
            <el-tag type="warning" size="small">待批改</el-tag>
          </div>
          <div class="pc-info">
            <span>{{ p.fullname || p.username }}</span>
            <span>自动得分: {{ p.auto_score }}</span>
            <span>满分: {{ p.total_score }}</span>
          </div>
          <div class="pc-actions">
            <el-button type="primary" size="small" @click="openGrading(p)">开始批改</el-button>
          </div>
        </div>
      </div>
      <div v-if="pTotal > 20" style="text-align:center;margin-top:16px">
        <el-pagination v-model:current-page="pPage" :total="pTotal" :page-size="20" layout="total,prev,next" @current-change="loadPending" size="small" />
      </div>
    </template>

    <!-- Grading Detail -->
    <template v-if="grading">
      <div class="grading-info">
        <span>考生: {{ gradingDetail.username }}</span>
        <span>自动得分: {{ gradingDetail.auto_score }}</span>
        <span>每题分值: {{ gradingDetail.per_question_score }}</span>
      </div>
      <div class="quick-bar">
        <el-button size="small" @click="scoreAll">全部满分</el-button>
        <el-button size="small" @click="scoreKeyword">匹配评分</el-button>
        <span class="quick-hint">匹配评分：学生答案含参考答案关键词即得满分</span>
      </div>
      <div v-for="q in gradingDetail.questions" :key="q.question_id" class="gq-block">
        <div class="gq-label">{{ q.content }}</div>
        <div class="gq-ref">参考答案: {{ q.reference_answer }}</div>
        <div class="gq-user">学生答案: {{ q.user_answer || '（未作答）' }}</div>
        <div v-if="q.explanation" class="gq-explain">解析: {{ q.explanation }}</div>
        <div class="gq-score-row">
          <span>评分:</span>
          <el-input-number v-model="scores[q.question_id]" :min="0" :max="gradingDetail.per_question_score" :step="1" size="small" />
          <span class="gq-max">/ {{ gradingDetail.per_question_score }} 分</span>
        </div>
      </div>
      <div class="grade-actions">
        <el-button @click="backToList">取消</el-button>
        <el-button type="primary" @click="submitGrading" :loading="submitting">提交评分</el-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Checked } from '@element-plus/icons-vue'

import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api'

const pendings = ref([])
const pPage = ref(1)
const pTotal = ref(0)
const grading = ref(null)
const gradingDetail = ref({ questions: [], auto_score: 0, total_score: 0, per_question_score: 10 })
const scores = reactive({})
const submitting = ref(false)

const pendingCount = computed(() => pTotal.value)

onMounted(() => loadPending())

async function loadPending() {
  try {
    const { data } = await api.get('/exams/pending-grading', { params: { page: pPage.value, page_size: 20 } })
    pendings.value = data.items || []; pTotal.value = data.total || 0
  } catch {}
}

async function openGrading(row) {
  try {
    const { data } = await api.get(`/exams/results/${row.id}/detail`)
    gradingDetail.value = { ...row, ...data, username: row.fullname || row.username }
    gradingDetail.value.per_question_score = row.per_question_score || 20
    Object.keys(scores).forEach(k => delete scores[k])
    for (const q of data.questions) { scores[q.question_id] = 0 }
    grading.value = row.id
  } catch (e) { ElMessage.error(e.response?.data?.detail || '加载失败') }
}

function backToList() { grading.value = null }

function scoreAll() {
  const max = gradingDetail.value.per_question_score || 20
  for (const q of gradingDetail.value.questions) { scores[q.question_id] = max }
  ElMessage.success('已全部满分')
}

function scoreKeyword() {
  const max = gradingDetail.value.per_question_score || 20
  for (const q of gradingDetail.value.questions) {
    const ref = (q.reference_answer || '').trim()
    const user = (q.user_answer || '').trim()
    if (!ref || !user) { scores[q.question_id] = 0; continue }
    const keywords = ref.split(/[,，。；\s]+/).filter(k => k.length >= 2)
    const matchCount = keywords.filter(k => user.includes(k)).length
    const ratio = keywords.length ? matchCount / keywords.length : 0
    scores[q.question_id] = Math.round(max * ratio)
  }
  ElMessage.success('已按关键词匹配评分')
}

async function submitGrading() {
  submitting.value = true
  try {
    const payload = {}
    for (const q of gradingDetail.value.questions) { payload[q.question_id] = scores[q.question_id] || 0 }
    await api.post(`/exams/results/${grading.value}/grade`, payload)
    ElMessage.success('批改完成')
    grading.value = null
    loadPending()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally { submitting.value = false }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-4); gap: var(--space-3); flex-wrap: wrap; }
.ph-left { display: flex; align-items: center; gap: var(--space-3); }
.ph-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }
.empty-wrap { padding: 60px 0; }

.pend-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--space-3); }
.pend-card {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); border: 1px solid var(--gray-100);
}
.pc-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-2); }
.pc-title { font-size: 15px; font-weight: 600; color: var(--gray-900); }
.pc-info { display: flex; gap: var(--space-3); font-size: 12px; color: var(--gray-500); margin-bottom: var(--space-3); }
.pc-actions { display: flex; justify-content: flex-end; }

.grading-info { display: flex; gap: var(--space-4); font-size: 13px; color: var(--gray-600); margin-bottom: var(--space-3); flex-wrap: wrap; }
.quick-bar { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-4); }
.quick-hint { font-size: 12px; color: var(--gray-400); }

.gq-block {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); border: 1px solid var(--gray-100); margin-bottom: var(--space-3);
}
.gq-label { font-size: 14px; font-weight: 600; color: var(--gray-900); margin-bottom: var(--space-2); }
.gq-ref { font-size: 13px; color: var(--color-primary); margin-bottom: 4px; padding: 8px 12px; background: #e8f0fe; border-radius: var(--radius-md); }
.gq-user { font-size: 13px; color: var(--gray-700); margin-bottom: 4px; padding: 8px 12px; background: var(--gray-50); border-radius: var(--radius-md); }
.gq-explain { font-size: 12px; color: var(--gray-500); margin-bottom: 4px; }
.gq-score-row { display: flex; align-items: center; gap: var(--space-2); margin-top: var(--space-2); }
.gq-max { font-size: 13px; color: var(--gray-400); }

.grade-actions { display: flex; justify-content: flex-end; gap: var(--space-2); margin-top: var(--space-4); }

@media (max-width: 768px) {
  .pend-grid { grid-template-columns: 1fr; }
}
</style>
