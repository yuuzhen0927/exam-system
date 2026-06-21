<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <h2>错题本</h2>
        <span class="count-badge" v-if="total">{{ total }} 题</span>
      </div>
      <el-button v-if="unmasteredCount > 0" type="primary" @click="startBatchPractice">
        <el-icon><VideoPlay /></el-icon> 加强掌握 ({{ unmasteredCount }})
      </el-button>
    </div>

    <div class="toolbar">
      <el-input v-model="searchText" placeholder="搜索错题..." clearable size="default">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filter.subject_id" placeholder="全部科目" clearable @change="load">
        <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-select v-model="filter.is_mastered" placeholder="全部状态" clearable @change="load">
        <el-option label="未掌握" :value="false" /><el-option label="已掌握" :value="true" />
      </el-select>
      <el-button @click="clearMastered" type="danger" plain size="default">清除已掌握</el-button>
    </div>

    <div v-if="!filteredItems.length" class="empty-state">
      <el-empty :description="searchText||filter.subject_id?'未找到匹配的错题':'暂无错题，继续加油'" />
    </div>

    <div v-else class="fav-list">
      <!-- Quick answer dialog -->
      <el-dialog v-model="answerVisible" title="题目详情" width="600px">
        <div v-if="viewingQuestion" style="line-height:1.8">
          <div style="font-size:15px;font-weight:600;margin-bottom:12px;color:var(--gray-900)">{{ viewingQuestion.content }}</div>
          <el-divider />
          <div v-if="viewingQuestion && viewingQuestion.question_type!=='composite'">
            <div v-for="o in parseOptions(viewingQuestion.options)" :key="o.label" style="padding:4px 0;font-size:14px">{{ o.label }}. {{ o.text }}</div>
          </div>
          <div style="margin-top:12px;background:var(--gray-50);padding:12px;border-radius:8px">
            <div style="font-weight:600;color:var(--color-success)">正确答案：{{ viewingQuestion.answer }}</div>
            <div v-if="viewingQuestion.explanation" style="margin-top:8px;color:var(--gray-600)">解析：{{ viewingQuestion.explanation }}</div>
          </div>
        </div>
      </el-dialog>
      <div v-for="row in filteredItems" :key="row.id" class="fav-item" @click="viewAnswer(row)" style="cursor:pointer" :class="{mastered: row.is_mastered}">
        <div class="fi-left">
          <div class="fi-type" :class="row.question_type">{{ typeIcon(row.question_type) }}</div>
        </div>
        <div class="fi-body">
          <div class="fi-content">{{ row.question_content }}</div>
          <div class="fi-meta">
            <el-tag size="small" type="info">{{ row.subject_name }}</el-tag>
            <el-tag size="small" effect="plain">{{ typeLabel(row.question_type) }}</el-tag>
            <span class="fi-wrong">错<b>{{ row.wrong_count }}</b> 次</span>
          </div>
        </div>
        <div class="fi-right">
          <el-button size="small" type="info" @click.stop="viewAnswer(row)">查看解析</el-button>
          <el-button v-if="!row.is_mastered" size="small" type="primary" @click.stop="startRedo(row)">重做</el-button>
          <span v-else class="mastered-tag">✓ 已掌握</span>
          <el-button size="small" type="danger" text @click.stop="delWrong(row.id)">移除</el-button>
        </div>
      </div>
    </div>

    <el-pagination v-if="total>50" v-model:current-page="page" :total="total" :page-size="50" layout="prev, pager, next" @current-change="load" style="justify-content:center;margin-top:24px" />

    <!-- 加强掌握 全屏练习模式 -->
    <teleport to="body">
      <div v-if="batchActive" class="batch-overlay">
        <div class="batch-container">
          <!-- Header bar -->
          <div class="batch-header">
            <div class="batch-header-left">
              <span class="batch-title">加强掌握</span>
              <el-tag size="small" type="info">{{ currentBatchIdx + 1 }} / {{ batchQuestions.length }}</el-tag>
            </div>
            <div class="batch-header-right">
              <span class="batch-correct-count">已掌握 {{ batchMastered }} 题</span>
              <el-button type="danger" text @click="exitBatchPractice">
                <el-icon><Close /></el-icon> 退出
              </el-button>
            </div>
          </div>

          <!-- Progress bar -->
          <div class="batch-progress-bar">
            <div class="batch-progress-fill" :style="{ width: ((currentBatchIdx + 1) / batchQuestions.length * 100) + '%' }"></div>
          </div>

          <!-- Question card -->
          <div class="batch-question-card" v-if="batchCurrent">
            <div class="bq-type-row">
              <el-tag :type="batchTypeTag(batchCurrent.question_type)" size="small">{{ typeLabel(batchCurrent.question_type) }}</el-tag>
              <span class="bq-wrong-count">错 {{ batchCurrent.wrong_count }} 次</span>
            </div>
            <div class="bq-stem">{{ batchCurrent.question_content }}</div>

            <!-- Options for single/multi/truefalse -->
            <div v-if="batchCurrent.question_type !== 'composite'" class="bq-options">
              <div v-for="o in parseOptions(batchCurrent.options)" :key="o.label"
                class="bq-opt"
                :class="{
                  selected: batchSelected.includes(o.label),
                  correct: batchSubmitted && batchCorrectAnswers.includes(o.label),
                  wrong: batchSubmitted && batchSelected.includes(o.label) && !batchCorrectAnswers.includes(o.label),
                }"
                @click="toggleBatchOption(o.label)">
                <span class="bq-opt-label">{{ o.label }}</span>
                <span class="bq-opt-text">{{ o.text }}</span>
              </div>
            </div>

            <!-- Composite input -->
            <div v-else class="bq-composite">
              <el-input v-model="batchCompositeAnswer" type="textarea" :rows="5" placeholder="请输入你的答案..." :disabled="batchSubmitted" />
            </div>

            <!-- Submit button -->
            <div v-if="!batchSubmitted" class="bq-submit-row">
              <el-button type="primary" size="large" @click="submitBatchAnswer" :disabled="!canBatchSubmit" class="bq-submit-btn">
                提交答案
              </el-button>
            </div>

            <!-- Result -->
            <div v-if="batchSubmitted" class="bq-result" :class="batchIsCorrect ? 'result-ok' : 'result-fail'">
              <div class="bq-result-icon">{{ batchIsCorrect ? '✓' : '✗' }}</div>
              <div class="bq-result-body">
                <div class="bq-result-title">{{ batchIsCorrect ? '回答正确！已标记为已掌握' : '回答错误，请继续加油' }}</div>
                <div class="bq-result-answer" v-if="!batchIsCorrect">正确答案：<b>{{ batchCorrectDisplay }}</b></div>
                <div class="bq-result-explain" v-if="batchCurrent.explanation">{{ batchCurrent.explanation }}</div>
              </div>
            </div>

            <!-- Next button -->
            <div v-if="batchSubmitted" class="bq-next-row">
              <el-button v-if="currentBatchIdx < batchQuestions.length - 1" type="primary" size="large" @click="nextBatchQuestion" class="bq-next-btn">
                下一题 <el-icon><ArrowRight /></el-icon>
              </el-button>
              <el-button v-else type="success" size="large" @click="finishBatchPractice" class="bq-next-btn">
                <el-icon><Trophy /></el-icon> 完成练习
              </el-button>
            </div>
          </div>

          <!-- Completion summary -->
          <div v-if="batchDone" class="batch-summary">
            <div class="bs-icon">🎉</div>
            <div class="bs-title">练习完成！</div>
            <div class="bs-stats">
              <div class="bs-stat"><span class="bs-num">{{ batchQuestions.length }}</span><span class="bs-label">总题数</span></div>
              <div class="bs-stat"><span class="bs-num bs-green">{{ batchMastered }}</span><span class="bs-label">已掌握</span></div>
              <div class="bs-stat"><span class="bs-num bs-red">{{ batchQuestions.length - batchMastered }}</span><span class="bs-label">未掌握</span></div>
            </div>
            <div class="bs-actions">
              <el-button type="primary" size="large" @click="startBatchPractice" v-if="batchQuestions.length - batchMastered > 0">再练一遍未掌握</el-button>
              <el-button size="large" @click="exitBatchPractice">返回错题本</el-button>
            </div>
          </div>
        </div>
      </div>
    </teleport>

    <!-- Redo dialog (single question) -->
    <el-dialog v-model="redoVisible" title="重做错题" width="600px" :close-on-click-modal="false" destroy-on-close>
      <div v-if="redoQuestion" class="redo-body">
        <div class="redo-content">
          <el-tag size="small" type="info" style="margin-bottom:8px">{{ typeLabel(redoQuestion.type) }}</el-tag>
          <div class="redo-stem">{{ redoQuestion.content }}</div>
        </div>
        <div v-if="redoQuestion.type !== 'composite'" class="redo-options">
          <div v-for="o in redoParsedOptions" :key="o.label"
            class="redo-opt"
            :class="{
              selected: redoSelected.includes(o.label),
              correct: redoSubmitted && redoCorrectAns.includes(o.label),
              wrong: redoSubmitted && redoSelected.includes(o.label) && !redoCorrectAns.includes(o.label),
            }"
            @click="toggleOption(o.label)">
            <span class="ro-label">{{ o.label }}</span>
            <span class="ro-text">{{ o.text }}</span>
          </div>
        </div>
        <div v-else>
          <el-input v-model="redoAnswer" type="textarea" :rows="4" placeholder="请输入你的答案..." :disabled="redoSubmitted" />
        </div>
        <div v-if="!redoSubmitted">
          <el-button type="primary" @click="submitRedo" :disabled="!canSubmit" style="margin-top:16px;width:100%">提交答案</el-button>
        </div>
        <div v-if="redoSubmitted" class="redo-result" :class="{'result-ok': redoIsCorrect, 'result-fail': !redoIsCorrect}">
          <div class="rr-icon">{{ redoIsCorrect ? '✓' : '✗' }}</div>
          <div class="rr-text">
            <div class="rr-verdict">{{ redoIsCorrect ? '回答正确！已标记为已掌握' : '回答错误，请继续加油' }}</div>
            <div class="rr-answer" v-if="!redoIsCorrect">正确答案：<b>{{ redoCorrectDisplay }}</b></div>
            <div class="rr-explanation" v-if="redoQuestion.explanation">{{ redoQuestion.explanation }}</div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="redoVisible=false">{{ redoSubmitted ? '关闭' : '取消' }}</el-button>
        <el-button v-if="!redoIsCorrect && redoSubmitted" type="primary" @click="startRedoAgain">再次重做</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Close, ArrowRight, Trophy, VideoPlay } from '@element-plus/icons-vue'

import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api'

const subjects = ref([]); const items = ref([]); const total = ref(0); const page = ref(1)
const searchText = ref(''); const filter = reactive({ subject_id: null, is_mastered: null })

// Unmastered count for button badge
const unmasteredCount = computed(() => items.value.filter(i => !i.is_mastered).length)

// === Batch practice state ===
const batchActive = ref(false)
const batchDone = ref(false)
const batchQuestions = ref([])
const currentBatchIdx = ref(0)
const batchMastered = ref(0)
const batchSelected = ref([])
const batchCompositeAnswer = ref('')
const batchSubmitted = ref(false)
const batchIsCorrect = ref(false)
const batchCorrectAnswers = ref([])

const batchCurrent = computed(() => batchQuestions.value[currentBatchIdx.value] || null)

const batchCorrectDisplay = computed(() => {
  if (!batchCurrent.value) return ''
  if (batchCurrent.value.question_type === 'composite') {
    try { return JSON.parse(batchCurrent.value.answer || '[]').join('；') }
    catch { return batchCurrent.value.answer }
  }
  return batchCorrectAnswers.value.join(', ')
})

const canBatchSubmit = computed(() => {
  if (!batchCurrent.value) return false
  if (batchCurrent.value.question_type === 'composite') return batchCompositeAnswer.value.trim().length > 0
  return batchSelected.value.length > 0
})

// === Single redo state ===
const redoVisible = ref(false)
const answerVisible = ref(false); const viewingQuestion = ref(null)
const redoQuestion = ref(null)
const redoSelected = ref([])
const redoAnswer = ref('')
const redoSubmitted = ref(false)
const redoIsCorrect = ref(false)
const redoCorrectAns = ref([])
const redoCurrentRow = ref(null)

const filteredItems = computed(() => {
  let list = items.value
  if (searchText.value) {
    const q = searchText.value.toLowerCase()
    list = list.filter(r => (r.question_content||'').toLowerCase().includes(q) || (r.subject_name||'').toLowerCase().includes(q))
  }
  return list
})

const redoParsedOptions = computed(() => {
  if (!redoQuestion.value) return []
  try { return JSON.parse(redoQuestion.value.options || '[]') }
  catch { return [] }
})

const redoCorrectDisplay = computed(() => {
  if (!redoQuestion.value) return ''
  if (redoQuestion.value.type === 'composite') {
    try { return JSON.parse(redoQuestion.value.answer || '[]').join('；') }
    catch { return redoQuestion.value.answer }
  }
  return redoCorrectAns.value.join(', ')
})

const canSubmit = computed(() => {
  if (!redoQuestion.value) return false
  if (redoQuestion.value.type === 'composite') return redoAnswer.value.trim().length > 0
  return redoSelected.value.length > 0
})

onMounted(async () => { const { data } = await api.get('/subjects'); subjects.value = data; load() })

async function load() {
  const params = { page: page.value, page_size: 50 }
  if (filter.subject_id) params.subject_id = filter.subject_id
  if (filter.is_mastered !== null && filter.is_mastered !== '') params.is_mastered = filter.is_mastered
  const { data } = await api.get('/wrongbook', { params })
  items.value = data.items || []; total.value = data.total || 0
}

// ===== BATCH PRACTICE (加强掌握) =====
async function startBatchPractice() {
  // Load all unmastered wrong questions with full question data
  const unmastered = items.value.filter(i => !i.is_mastered)
  if (!unmastered.length) { ElMessage.info('没有未掌握的错题'); return }

  // Fetch full question details for each
  const fullQuestions = []
  for (const row of unmastered) {
    try {
      const { data } = await api.get(`/questions/${row.question_id}`)
      fullQuestions.push({ ...data, _wrongbook_row_id: row.id, wrong_count: row.wrong_count })
    } catch { /* skip missing questions */ }
  }
  if (!fullQuestions.length) { ElMessage.error('无法加载错题数据'); return }

  batchQuestions.value = fullQuestions
  currentBatchIdx.value = 0
  batchMastered.value = 0
  batchDone.value = false
  batchSelected.value = []
  batchCompositeAnswer.value = ''
  batchSubmitted.value = false
  batchIsCorrect.value = false
  batchCorrectAnswers.value = []
  batchActive.value = true
}

function toggleBatchOption(label) {
  if (batchSubmitted.value) return
  const q = batchCurrent.value
  if (!q) return
  if (q.question_type === 'single' || q.question_type === 'truefalse') {
    batchSelected.value = [label]
  } else {
    const idx = batchSelected.value.indexOf(label)
    if (idx >= 0) batchSelected.value.splice(idx, 1)
    else batchSelected.value.push(label)
  }
}

async function submitBatchAnswer() {
  const q = batchCurrent.value
  if (!q) return

  // Parse correct answer
  let correctAns = []
  if (q.question_type !== 'composite') {
    try { correctAns = JSON.parse(q.answer || '[]') }
    catch { correctAns = [q.answer] }
  }
  batchCorrectAnswers.value = correctAns

  let userAnswer
  if (q.question_type === 'composite') {
    userAnswer = batchCompositeAnswer.value.trim()
  } else {
    batchSelected.value.sort()
    userAnswer = JSON.stringify(batchSelected.value)
  }

  batchSubmitted.value = true
  const correctAnswer = (q.answer || '').trim()

  if (q.question_type === 'composite') {
    batchIsCorrect.value = userAnswer === correctAnswer
  } else {
    batchIsCorrect.value = userAnswer === correctAnswer
  }

  if (batchIsCorrect.value) {
    batchMastered.value++
    // Mark as mastered on backend
    try {
      await api.post(`/wrongbook/mark-mastered/${q._wrongbook_row_id}`, null, { params: { mastered: true } })
      // Update local item
      const localItem = items.value.find(i => i.id === q._wrongbook_row_id)
      if (localItem) localItem.is_mastered = true
    } catch {}
  }
}

function nextBatchQuestion() {
  currentBatchIdx.value++
  batchSelected.value = []
  batchCompositeAnswer.value = ''
  batchSubmitted.value = false
  batchIsCorrect.value = false
  batchCorrectAnswers.value = []
}

function finishBatchPractice() {
  batchDone.value = true
  // Refresh the list to reflect mastered status
  load()
}

function exitBatchPractice() {
  batchActive.value = false
  batchDone.value = false
  batchQuestions.value = []
  load()
}

// ===== SINGLE REDO =====
async function startRedo(row) {
  redoCurrentRow.value = row
  redoSubmitted.value = false
  redoSelected.value = []
  redoAnswer.value = ''
  redoIsCorrect.value = false
  redoCorrectAns.value = []
  try {
    const { data } = await api.get(`/questions/${row.question_id}`)
    redoQuestion.value = data
    if (data.type !== 'composite') {
      try { redoCorrectAns.value = JSON.parse(data.answer || '[]') }
      catch { redoCorrectAns.value = [data.answer] }
    }
    redoVisible.value = true
  } catch { ElMessage.error('加载题目失败') }
}

function startRedoAgain() {
  redoSubmitted.value = false
  redoSelected.value = []
  redoAnswer.value = ''
  redoIsCorrect.value = false
}

function toggleOption(label) {
  if (redoSubmitted.value) return
  if (redoQuestion.value.type === 'single' || redoQuestion.value.type === 'truefalse') {
    redoSelected.value = [label]
  } else {
    const idx = redoSelected.value.indexOf(label)
    if (idx >= 0) redoSelected.value.splice(idx, 1)
    else redoSelected.value.push(label)
  }
}

async function submitRedo() {
  let userAnswer
  if (redoQuestion.value.type === 'composite') {
    userAnswer = redoAnswer.value.trim()
  } else {
    redoSelected.value.sort()
    userAnswer = JSON.stringify(redoSelected.value)
  }
  redoSubmitted.value = true
  const correctAnswer = (redoQuestion.value.answer || '').trim()
  if (redoQuestion.value.type === 'composite') {
    redoIsCorrect.value = userAnswer === correctAnswer
  } else {
    redoIsCorrect.value = userAnswer === correctAnswer
  }
  if (redoIsCorrect.value) {
    await api.post(`/wrongbook/mark-mastered/${redoCurrentRow.value.id}`, null, { params: { mastered: true } })
    redoCurrentRow.value.is_mastered = true
    ElMessage.success('恭喜，已掌握！')
  } else {
    ElMessage.warning('答案不正确')
  }
}

async function delWrong(id) { await api.delete(`/wrongbook/${id}`); items.value = items.value.filter(i => i.id !== id) }
async function viewAnswer(row) {
  try {
    const { data } = await api.get('/questions/' + row.question_id + '')
    viewingQuestion.value = { ...data, wrong_count: row.wrong_count }
    answerVisible.value = true
  } catch { ElMessage.error('加载题目详情失败') }
}
function parseOptions(opts) { try { return typeof opts === 'string' ? JSON.parse(opts) : (opts || []) } catch { return [] } }
async function clearMastered() { await api.post('/wrongbook/clear-mastered'); ElMessage.success('已清除'); load() }
function typeLabel(t) { return { single:'单选', multi:'多选', truefalse:'判断', composite:'综合' }[t]||t }
function typeIcon(t) { return { single:'单', multi:'多', truefalse:'判', composite:'综' }[t]||'?' }
function batchTypeTag(t) { return { single:'primary', multi:'warning', truefalse:'success', composite:'' }[t]||'info' }
</script>

<style scoped>
.count-badge { font-size: var(--text-sm); color: var(--gray-400); background: var(--gray-50); padding: 2px 10px; border-radius: 99px; }
.ph-left { display: flex; align-items: center; gap: 12px; }
.fav-list { display: flex; flex-direction: column; gap: var(--space-2); }
.fav-item {
  display: flex; align-items: center; gap: var(--space-4);
  background: var(--gray-25); border-radius: var(--radius-md); padding: var(--space-3) var(--space-4);
  box-shadow: var(--shadow-xs); transition: all var(--transition-fast);
}
.fav-item:hover { box-shadow: var(--shadow-sm); }
.fav-item.mastered { opacity: 0.55; }
.fi-left { flex-shrink: 0; }
.fi-type {
  width: 36px; height: 36px; border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
  font-size: var(--text-xs); font-weight: var(--font-bold); color: #fff;
}
.fi-type.single { background: var(--color-primary); }
.fi-type.multi { background: #f59e0b; }
.fi-type.truefalse { background: #22c55e; }
.fi-type.composite { background: #8b5cf6; }
.fi-body { flex: 1; min-width: 0; }
.fi-content { font-size: var(--text-base); line-height: 1.6; color: var(--gray-800); margin-bottom: var(--space-2); }
.fi-meta { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; }
.fi-wrong { font-size: var(--text-xs); color: var(--color-danger); }
.fi-right { flex-shrink: 0; display: flex; align-items: center; gap: var(--space-2); }
.mastered-tag { font-size: var(--text-xs); color: var(--color-success); font-weight: var(--font-mid); white-space: nowrap; }

/* ===== 加强掌握 全屏覆盖 ===== */
.batch-overlay {
  position: fixed; inset: 0; z-index: 3000;
  background: var(--el-bg-color, #f8fafc);
  display: flex; flex-direction: column;
  overflow-y: auto;
}
.batch-container {
  width: 100%; max-width: 720px; margin: 0 auto;
  padding: 0 20px 40px;
}
.batch-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 0; border-bottom: 1px solid var(--el-border-color-lighter, #e4e7ed);
  position: sticky; top: 0; background: var(--el-bg-color, #f8fafc); z-index: 10;
}
.batch-header-left { display: flex; align-items: center; gap: 10px; }
.batch-title { font-size: 18px; font-weight: 700; color: var(--el-text-color-primary, #303133); }
.batch-header-right { display: flex; align-items: center; gap: 16px; }
.batch-correct-count { font-size: 13px; color: #22c55e; font-weight: 600; }

.batch-progress-bar {
  height: 4px; background: var(--el-fill-color-light, #f5f7fa);
  border-radius: 2px; margin: 12px 0 24px; overflow: hidden;
}
.batch-progress-fill {
  height: 100%; background: linear-gradient(90deg, #4f6ef7, #06b6d4);
  border-radius: 2px; transition: width 0.3s ease;
}

.batch-question-card {
  background: var(--el-bg-color, #fff);
  border-radius: 14px; padding: 28px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border: 1px solid var(--el-border-color-lighter, #e4e7ed);
}
.bq-type-row { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.bq-wrong-count { font-size: 12px; color: var(--el-color-danger, #f56c6c); font-weight: 500; }
.bq-stem { font-size: 17px; line-height: 1.8; color: var(--el-text-color-primary, #303133); margin-bottom: 24px; font-weight: 500; }

.bq-options { display: flex; flex-direction: column; gap: 10px; }
.bq-opt {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 18px; border: 2px solid var(--el-border-color, #dcdfe6);
  border-radius: 10px; cursor: pointer; transition: all 0.15s;
}
.bq-opt:hover { border-color: var(--el-color-primary, #409eff); background: rgba(79,110,247,0.03); }
.bq-opt.selected { border-color: var(--el-color-primary, #409eff); background: rgba(79,110,247,0.08); }
.bq-opt.correct { border-color: #22c55e; background: rgba(34,197,94,0.08); }
.bq-opt.wrong { border-color: #ef4444; background: rgba(239,68,68,0.08); }
.bq-opt-label {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 14px;
  border: 2px solid var(--el-border-color, #dcdfe6);
  flex-shrink: 0; transition: all 0.15s;
}
.bq-opt.selected .bq-opt-label { background: var(--el-color-primary, #409eff); border-color: var(--el-color-primary); color: #fff; }
.bq-opt.correct .bq-opt-label { background: #22c55e; border-color: #22c55e; color: #fff; }
.bq-opt.wrong .bq-opt-label { background: #ef4444; border-color: #ef4444; color: #fff; }
.bq-opt-text { font-size: 15px; color: var(--el-text-color-regular, #606266); }

.bq-composite { margin-bottom: 4px; }

.bq-submit-row { margin-top: 20px; }
.bq-submit-btn { width: 100%; height: 48px; font-size: 16px; border-radius: 10px; }

.bq-result {
  display: flex; gap: 14px; margin-top: 20px; padding: 18px;
  border-radius: 12px; animation: fadeSlideIn 0.25s ease;
}
@keyframes fadeSlideIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.bq-result.result-ok { background: #f0fdf4; border: 1px solid #bbf7d0; }
.bq-result.result-fail { background: #fef2f2; border: 1px solid #fecaca; }
.bq-result-icon { font-size: 28px; font-weight: 800; flex-shrink: 0; }
.result-ok .bq-result-icon { color: #22c55e; }
.result-fail .bq-result-icon { color: #ef4444; }
.bq-result-title { font-weight: 600; margin-bottom: 4px; }
.result-ok .bq-result-title { color: #16a34a; }
.result-fail .bq-result-title { color: #dc2626; }
.bq-result-answer { font-size: 14px; color: var(--el-text-color-secondary, #909399); margin-top: 4px; }
.bq-result-explain { font-size: 14px; color: var(--el-text-color-secondary, #909399); margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.06); line-height: 1.7; }

.bq-next-row { margin-top: 20px; text-align: center; }
.bq-next-btn { height: 48px; font-size: 16px; border-radius: 10px; min-width: 180px; }

/* ===== Completion summary ===== */
.batch-summary { text-align: center; padding: 60px 20px; animation: fadeSlideIn 0.3s ease; }
.bs-icon { font-size: 56px; margin-bottom: 16px; }
.bs-title { font-size: 24px; font-weight: 700; color: var(--el-text-color-primary, #303133); margin-bottom: 32px; }
.bs-stats { display: flex; justify-content: center; gap: 40px; margin-bottom: 40px; }
.bs-stat { text-align: center; }
.bs-num { display: block; font-size: 36px; font-weight: 800; color: var(--el-text-color-primary, #303133); }
.bs-green { color: #22c55e; }
.bs-red { color: #ef4444; }
.bs-label { font-size: 13px; color: var(--el-text-color-secondary, #909399); margin-top: 4px; display: block; }
.bs-actions { display: flex; gap: 12px; justify-content: center; }

/* ===== Mobile ===== */
@media (max-width: 768px) {
  .batch-container { padding: 0 14px 24px; }
  .batch-question-card { padding: 18px; }
  .bq-stem { font-size: 15px; }
  .bq-opt { padding: 12px 14px; }
  .bs-stats { gap: 20px; }
  .bs-num { font-size: 28px; }
  .fav-item { padding: var(--space-2) var(--space-3); gap: var(--space-3); }
  .fi-content { font-size: var(--text-sm); }
  .fi-right { flex-wrap: wrap; gap: var(--space-1); }
}

/* Redo dialog (single question) */
.redo-body { padding: var(--space-1); }
.redo-content { margin-bottom: var(--space-4); }
.redo-stem { font-size: var(--text-lg); color: var(--gray-900); line-height: 1.8; }
.redo-options { display: flex; flex-direction: column; gap: var(--space-2); }
.redo-opt {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-3) var(--space-4); border: 2px solid var(--gray-200);
  border-radius: var(--radius-md); cursor: pointer; transition: all var(--transition-fast);
}
.redo-opt:hover { border-color: var(--color-primary); background: var(--gray-50); }
.redo-opt.selected { border-color: var(--color-primary); background: var(--color-primary-light); }
.redo-opt.correct { border-color: var(--color-success); background: var(--color-success-light); }
.redo-opt.wrong { border-color: var(--color-danger); background: var(--color-danger-light); }
.ro-label {
  width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: var(--font-bold); font-size: var(--text-sm); border: 2px solid var(--gray-300); flex-shrink: 0;
}
.redo-opt.selected .ro-label { background: var(--color-primary); border-color: var(--color-primary); color: #fff; }
.redo-opt.correct .ro-label { background: #22c55e; border-color: var(--color-success); color: #fff; }
.redo-opt.wrong .ro-label { background: #ef4444; border-color: var(--color-danger); color: #fff; }
.ro-text { font-size: var(--text-base); }

.redo-result { display: flex; gap: var(--space-3); margin-top: var(--space-4); padding: var(--space-4); border-radius: var(--radius-md); }
.redo-result.result-ok { background: var(--color-success-light); border: 1px solid #bbf7d0; }
.redo-result.result-fail { background: var(--color-danger-light); border: 1px solid #fecaca; }
.rr-icon { font-size: 24px; font-weight: var(--font-bold); }
.result-ok .rr-icon { color: var(--color-success); }
.result-fail .rr-icon { color: var(--color-danger); }
.rr-verdict { font-weight: var(--font-semibold); margin-bottom: 4px; }
.result-ok .rr-verdict { color: #16a34a; }
.result-fail .rr-verdict { color: #dc2626; }
.rr-answer { font-size: var(--text-sm); color: var(--gray-700); margin-top: 4px; }
.rr-explanation { font-size: var(--text-sm); color: var(--gray-600); margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(0,0,0,0.06); }

</style>

<style>
/* Dark mode */
[data-theme="dark"] .fav-item { background: #2a2b2e; }
[data-theme="dark"] .fav-item:hover { background: #323337; }
[data-theme="dark"] .fi-content { color: #d0d2d6; }
[data-theme="dark"] .count-badge { background: #2a2b2e; color: #a0a2a8; }
[data-theme="dark"] .batch-overlay { background: var(--gray-900); }
[data-theme="dark"] .batch-question-card { background: #2a2b2e; color: #d0d2d6; }
[data-theme="dark"] .bq-opt { border-color: #36373b; color: #d0d2d6; }
[data-theme="dark"] .bq-opt:hover { border-color: var(--color-primary); background: rgba(79,110,247,0.1); }
[data-theme="dark"] .bq-opt.selected { background: rgba(79,110,247,0.15); }
[data-theme="dark"] .bq-opt.correct { background: rgba(34,197,94,0.12); }
[data-theme="dark"] .bq-opt.wrong { background: rgba(239,68,68,0.12); }
[data-theme="dark"] .redo-opt { border-color: #36373b; color: #d0d2d6; }
[data-theme="dark"] .redo-opt.selected { background: rgba(79,110,247,0.15); }
</style>