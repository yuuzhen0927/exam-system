<template>
  <div class="page-container">
    <div class="page-header"><h2>练习中心</h2></div>

    <!-- Setup -->
    <div v-if="!practicing" class="practice-setup">
      <!-- Subject cards -->
      <div v-if="!isReviewMode" class="section-title">选择科目</div>
      <div v-if="!isReviewMode" class="subject-grid">
        <div class="subject-card" :class="{active: form.subject_id===null}" @click="openSetup(null)">
          <div class="subject-card-icon all"><el-icon size="22"><Collection /></el-icon></div>
          <div class="subject-card-name">全部科目</div>
          <div class="subject-card-count">{{ totalQuestions }} 题</div>
        </div>
        <div v-for="s in subjects" :key="s.id" class="subject-card" :class="{active: form.subject_id===s.id}" :style="{'--card-accent': cardColor(s.id)}" @click="openSetup(s.id)">
          <div class="subject-card-icon" :style="{background: cardColor(s.id),color:'#fff'}">{{ s.name[0] }}</div>
          <div class="subject-card-name">{{ s.name }}</div>
          <div class="subject-card-count">{{ s.question_count }} 题</div>
        </div>
      </div>
    </div>

    <!-- Practice session -->
    <div v-if="practicing" class="practice-session">
      <div class="practice-topbar">
        <button class="back-btn" @click="exitPractice"><el-icon><ArrowLeft /></el-icon></button>
        <div class="progress-wrap">
          <div class="progress-bar"><div class="progress-fill" :style="{width: ((currentIdx/practiceQuestions.length)*100)+'%'}"></div></div>
          <span class="progress-text">{{ currentIdx+1 }} / {{ practiceQuestions.length }}</span>
        </div>
        <span class="topbar-tag"><el-tag size="small">{{ typeLabel(practiceQuestions[currentIdx]?.type) }}</el-tag></span>
      </div>

      <div class="question-card" :key="currentIdx">
        <div class="q-body">
          <div class="q-stem">
            <span class="q-index">{{ currentIdx+1 }}.</span>
            <span class="q-text">{{ practiceQuestions[currentIdx]?.content }}</span>
          </div>
          <div v-if="practiceQuestions[currentIdx]?.images?.length" class="q-images">
            <img v-for="img in practiceQuestions[currentIdx].images" :key="img" :src="img" class="q-img" />
          </div>
        </div>

        <div v-if="practiceQuestions[currentIdx]?.type!=='composite'" class="q-options">
          <div v-for="o in parseOptions(practiceQuestions[currentIdx]?.options)" :key="o.label"
            class="option-card"
            :class="{
              selected: isSelected(o.label),
              correct: showResult && isCorrectOption(o.label),
              wrong: showResult && isSelected(o.label) && !isCorrectOption(o.label)
            }"
            @click="!showResult && selectOption(o.label)">
            <span class="option-letter">{{ o.label }}</span>
            <span class="option-text">{{ o.text }}</span>
            <span v-if="showResult && isCorrectOption(o.label)" class="option-badge correct">✓</span>
            <span v-if="showResult && isSelected(o.label) && !isCorrectOption(o.label)" class="option-badge wrong">✗</span>
          </div>
        </div>
        <div v-else-if="practiceQuestions[currentIdx]?.type === 'blank'" class="q-blank">
          <el-input v-model="currentAnswer" placeholder="请输入答案" size="large" :disabled="showResult" />
        </div>
        <div v-else>
          <el-input v-model="currentAnswer" type="textarea" :rows="4" placeholder="请输入答案" :disabled="showResult" />
        </div>

        <div v-if="showResult" class="q-explanation" :class="{correct:lastCorrect,wrong:!lastCorrect}">
          <div class="explain-header">
            <span v-if="lastCorrect" class="explain-icon correct">✓ 回答正确</span>
            <span v-else class="explain-icon wrong">✗ 回答错误</span>
          </div>
          <div v-if="!lastCorrect && practiceQuestions[currentIdx]?.type !== 'blank'" class="explain-answer">正确答案：<b>{{ practiceQuestions[currentIdx]?.answer }}</b></div>
          <div v-if="practiceQuestions[currentIdx]?.explanation" class="explain-text">{{ practiceQuestions[currentIdx]?.explanation }}</div>
        </div>

        <div class="q-footer">
          <div class="q-footer-actions">
            <el-button text size="small" @click="toggleFav(practiceQuestions[currentIdx]?.id)" :type="favSet.has(practiceQuestions[currentIdx]?.id)?'warning':''">
              <el-icon><Star /></el-icon>{{ favSet.has(practiceQuestions[currentIdx]?.id)?'已收藏':'收藏' }}
            </el-button>
            <el-button text size="small" @click="openNote(practiceQuestions[currentIdx])"><el-icon><Edit /></el-icon>笔记</el-button>
            <el-button text size="small" @click="openFeedback(practiceQuestions[currentIdx])"><el-icon><Warning /></el-icon>反馈</el-button>
          </div>
          <div class="q-footer-btn">
            <el-button v-if="!showResult" type="primary" size="large" @click="checkAnswer" :disabled="!hasAnswer">确认答案</el-button>
            <el-button v-else type="primary" size="large" @click="nextQuestion">
              {{ currentIdx < practiceQuestions.length-1 ? '下一题' : '查看结果' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Practice result -->
    <div v-if="practiceDone" class="practice-result">
      <div class="result-card">
        <div class="result-icon" :class="{good: resultStats.accuracy>=60}">{{ resultStats.accuracy>=60 ? '🎉' : '💪' }}</div>
        <div class="result-title">练习完成</div>
        <div class="result-stats">
          <div class="result-stat"><span class="rs-val">{{ resultStats.total }}</span><span class="rs-label">总题数</span></div>
          <div class="result-stat correct"><span class="rs-val">{{ resultStats.correct }}</span><span class="rs-label">正确</span></div>
          <div class="result-stat wrong"><span class="rs-val">{{ resultStats.wrong }}</span><span class="rs-label">错误</span></div>
          <div class="result-stat"><span class="rs-val">{{ resultStats.accuracy }}%</span><span class="rs-label">正确率</span></div>
        </div>
        <div class="result-actions">
          <el-button type="primary" @click="resetPractice">再来一组</el-button>
        </div>
      </div>
    </div>

    <!-- Setup dialog -->
    <el-dialog v-model="setupVisible" :title="setupSubjectName" width="460px" :close-on-click-modal="false">
      <div class="setup-body">
        <div class="setup-section">
          <label class="setup-label">练习模式</label>
          <div class="mode-tabs">
            <button v-for="m in modes" :key="m.key" class="mode-tab" :class="{active:form.mode===m.key}" @click="form.mode=m.key">
              <span class="mode-tab-icon">{{ m.icon }}</span>
              <span>{{ m.label }}</span>
            </button>
          </div>
        </div>
        <div class="setup-row">
          <div class="setup-col" v-if="form.mode==='chapter'">
            <label class="setup-label">章节</label>
            <el-select v-model="form.chapter_id" placeholder="选择章节" style="width:100%">
              <el-option v-for="c in chapters" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </div>
          <div class="setup-col">
            <label class="setup-label">题型</label>
            <el-select v-model="form.question_type" clearable placeholder="不限" style="width:100%">
              <el-option label="单选题" value="single" />
              <el-option label="多选题" value="multi" />
              <el-option label="判断题" value="truefalse" />
              <el-option label="填空题" value="blank" />
            </el-select>
          </div>
          <div class="setup-col">
            <label class="setup-label">题目数量</label>
            <el-input-number v-model="form.count" :min="5" :max="100" :step="5" style="width:100%" />
          </div>
        </div>
        <!-- Review mode summary -->
        <div v-if="form.mode==='review'" class="review-summary">
          <div class="review-stat">
            <span class="review-stat-icon wr">✗</span>
            <span class="review-stat-label">待复习错题</span>
            <span class="review-stat-val">{{ reviewStats.wrongCount }} 题</span>
          </div>
          <div class="review-stat">
            <span class="review-stat-icon fv">★</span>
            <span class="review-stat-label">收藏题目</span>
            <span class="review-stat-val">{{ reviewStats.favCount }} 题</span>
          </div>
          <div class="review-stat total">
            <span class="review-stat-label">合并去重后</span>
            <span class="review-stat-val">{{ reviewStats.totalUnique }} 题</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="setupVisible=false">取消</el-button>
        <el-button type="primary" @click="startPractice" :loading="loadingStart">开始练习</el-button>
      </template>
    </el-dialog>

    <!-- Note/Feedback dialogs -->
    <el-dialog v-model="noteDialog.visible" title="添加笔记" width="420">
      <el-input v-model="noteDialog.content" type="textarea" :rows="4" placeholder="笔记内容" />
      <template #footer><el-button @click="noteDialog.visible=false">取消</el-button><el-button type="primary" @click="saveNote">保存</el-button></template>
    </el-dialog>
    <el-dialog v-model="fbDialog.visible" title="题目反馈" width="420">
      <el-input v-model="fbDialog.content" type="textarea" :rows="3" placeholder="请描述问题..." />
      <template #footer><el-button @click="fbDialog.visible=false">取消</el-button><el-button type="primary" @click="submitFeedback">提交</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Star, Edit, Warning, ArrowLeft, Collection } from '@element-plus/icons-vue'

import { ref, reactive, onMounted, watch, computed } from 'vue'
import api from '../api'

const subjects = ref([])
const chapters = ref([])
const form = reactive({ mode: 'random', subject_id: null, chapter_id: null, question_type: '', count: 20 })
const practicing = ref(false)
const practiceDone = ref(false)
const practiceQuestions = ref([])
const currentIdx = ref(0)
const currentAnswer = ref('')
const multiAnswer = ref([])
const showResult = ref(false)
const lastCorrect = ref(false)
const allAnswers = reactive({})
const recordId = ref(null)
const favSet = ref(new Set())
const isReviewMode = ref(false)
const setupVisible = ref(false)
const loadingStart = ref(false)
const setupSubjectName = ref('全部科目')
const resultStats = reactive({ total:0, correct:0, wrong:0, accuracy:0 })
const reviewStats = reactive({ wrongCount: 0, favCount: 0, totalUnique: 0 })

const noteDialog = reactive({ visible: false, questionId: null, content: '' })
const fbDialog = reactive({ visible: false, questionId: null, content: '' })

const totalQuestions = computed(() => subjects.value.reduce((s,x)=>s+(x.question_count||0),0))

const modes = [
  { key:'random', icon:'🎉', label:'随机练习' },
  { key:'chapter', icon:'📼', label:'章节练习' },
  { key:'specialty', icon:'🎆', label:'专项练习' },
  { key:'review', icon:'🔄', label:'复习模式' },
  { key:'memorize', icon:'🧥', label:'背题模式' },
  { key:'flashcard', icon:'🃏', label:'闪卡模式' },
]

const cardColors = ['#4f6ef7','#22c55e','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#ec4899','#f97316']
function cardColor(id) { return cardColors[(id-1) % cardColors.length] }

onMounted(async () => {
  try { const s = await api.get('/subjects'); subjects.value = s.data } catch { subjects.value = [] }
})

function openSetup(subjectId) {
  form.subject_id = subjectId; form.chapter_id = null; form.mode = 'random'
  setupSubjectName.value = subjectId ? (subjects.value.find(s=>s.id===subjectId)?.name || '练习设置') : '全部科目'
  setupVisible.value = true
}

// When mode changes to review, fetch stats
watch(() => form.mode, async (newMode) => {
  if (newMode === 'review') {
    try {
      const [wb, fav] = await Promise.all([
        api.get('/wrongbook', { params: { is_mastered: false } }),
        api.get('/favorites'),
      ])
      const wrongIds = new Set((wb.data.items || []).map(i => i.question_id))
      const favIds = new Set((fav.data || []).map(i => i.question_id))
      const allIds = new Set([...wrongIds, ...favIds])
      reviewStats.wrongCount = wrongIds.size
      reviewStats.favCount = favIds.size
      reviewStats.totalUnique = allIds.size
    } catch { reviewStats.wrongCount = 0; reviewStats.favCount = 0; reviewStats.totalUnique = 0 }
  }
})

watch(() => form.subject_id, async (sid) => {
  if (!sid) { chapters.value = []; return }
  try { const { data } = await api.get(`/subjects/${sid}/chapters`); chapters.value = data } catch { chapters.value = [] }
})

async function startPractice() {
  loadingStart.value = true
  try {
    isReviewMode.value = false; practiceDone.value = false
    const endpoint = form.mode === 'review' ? '/practice/review' : '/practice/start'
    const { data } = await api.post(endpoint, { ...form })
    practiceQuestions.value = data.questions; recordId.value = data.record_id
    currentIdx.value = 0; showResult.value = false; practicing.value = true; setupVisible.value = false
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '加载失败')
  } finally {
    loadingStart.value = false
  }
}

function exitPractice() { practicing.value = false; practiceQuestions.value = []; showResult.value = false }

const hasAnswer = computed(() => {
  if (!practiceQuestions.value[currentIdx.value]) return false
  const t = practiceQuestions.value[currentIdx.value].type
  if (t==='multi') return multiAnswer.value.length > 0
  if (t==='composite') return currentAnswer.value.trim().length > 0
    if (t==='blank') return currentAnswer.value.trim().length > 0
  return !!currentAnswer.value
})

const correctAnswer = computed(() => {
  const q = practiceQuestions.value[currentIdx.value]
  let a = (q?.answer || '')
  try { const p = JSON.parse(a); if (Array.isArray(p)) a = p.join('') } catch {}
  return String(a).toUpperCase()
})

function isCorrectOption(label) {
  const q = practiceQuestions.value[currentIdx.value]
  if (q?.type === 'multi') return correctAnswer.value.includes(label.toUpperCase())
  return label.toUpperCase() === correctAnswer.value
}

function isSelected(label) {
  const t = practiceQuestions.value[currentIdx.value]?.type
  if (t==='multi') return multiAnswer.value.includes(label)
  return currentAnswer.value === label
}

function selectOption(label) {
  const t = practiceQuestions.value[currentIdx.value]?.type
  if (t==='multi') {
    const idx = multiAnswer.value.indexOf(label)
    if (idx>=0) multiAnswer.value.splice(idx,1); else multiAnswer.value.push(label)
  } else {
    currentAnswer.value = label
  }
}

function checkAnswer() {
  const q = practiceQuestions.value[currentIdx.value]
  let userAns
  if (q.type === 'multi') {
    userAns = [...multiAnswer.value].map(a=>a.toUpperCase().trim()).sort().join('')
  } else {
    userAns = (currentAnswer.value || '').toUpperCase().trim()
  }
  const ans = userAns
  allAnswers[q.id] = ans
  showResult.value = true
  let correctAns = (q.answer || '')
  try { const parsed = JSON.parse(correctAns); if (Array.isArray(parsed)) correctAns = parsed.map(a=>String(a).toUpperCase().trim()).sort().join('') } catch {}
  correctAns = String(correctAns).toUpperCase().trim()
  // Unified truefalse comparison: normalize A/B ↔ true/false ↔ 对/错
  const normalizeTF = (v) => {
    const s = String(v).toUpperCase().trim()
    if (s === 'TRUE' || s === '对') return 'A'
    if (s === 'FALSE' || s === '错') return 'B'
    return s
  }
  if (q.type === 'truefalse') {
    lastCorrect.value = normalizeTF(userAns) === normalizeTF(correctAns)
  } else {
    lastCorrect.value = userAns === correctAns
  }
  if (lastCorrect.value) resultStats.correct++; else resultStats.wrong++
  resultStats.total++
}

async function nextQuestion() {
  if (currentIdx.value >= practiceQuestions.value.length - 1) {
    await submitAll()
    practicing.value = false
    resultStats.accuracy = resultStats.total ? Math.round(resultStats.correct/resultStats.total*100) : 0
    practiceDone.value = true
    return
  }
  currentIdx.value++; currentAnswer.value = ''; multiAnswer.value = []; showResult.value = false
}

function resetPractice() {
  practiceDone.value = false; resultStats.total=0; resultStats.correct=0; resultStats.wrong=0; resultStats.accuracy=0
  Object.keys(allAnswers).forEach(k => delete allAnswers[k])
}

async function submitAll() { await api.post(`/practice/${recordId.value}/submit`, allAnswers) }

function parseOptions(opt) { if (!opt) return []; if (Array.isArray(opt)) return opt; try { return JSON.parse(opt) } catch { return [] } }
function typeLabel(t) { return { single:'单选题',multi:'多选题',truefalse:'判断题',composite:'综合题',blank:'填空题' }[t]||t }

async function toggleFav(qid) {
  try { const { data } = await api.post(`/favorites/toggle/${qid}`); if (data.is_favorited) favSet.value.add(qid); else favSet.value.delete(qid) } catch {}
}
function openNote(q) { noteDialog.questionId = q?.id; noteDialog.content = ''; noteDialog.visible = true }
async function saveNote() {
  if (!noteDialog.content.trim()) return
  try { await api.post('/notes', { question_id: noteDialog.questionId, content: noteDialog.content }); ElMessage.success('已保存') } catch {}
  noteDialog.visible = false
}
function openFeedback(q) { fbDialog.questionId = q?.id; fbDialog.content = ''; fbDialog.visible = true }
async function submitFeedback() {
  if (!fbDialog.content.trim()) return
  try { await api.post('/feedback', { question_id: fbDialog.questionId, content: fbDialog.content }); ElMessage.success('已提交') } catch {}
  fbDialog.visible = false
}
</script>

<style scoped>
.setup-body { padding: 0 var(--space-1); }
.setup-section { margin-bottom: var(--space-4); }
.setup-label { display: block; font-size: var(--text-sm); font-weight: var(--font-mid); color: var(--gray-700); margin-bottom: var(--space-2); }
.setup-row { display: flex; gap: var(--space-3); }
.setup-col { flex: 1; min-width: 0; }

.practice-setup { max-width: 1200px; }
.section-title { font-size: var(--text-md); font-weight: var(--font-semibold); color: var(--gray-700); margin-bottom: var(--space-3); }
.subject-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: var(--space-3); }
.subject-card { background: var(--gray-25); border: 2px solid var(--gray-100); border-left: 4px solid var(--card-accent, var(--color-primary)); border-radius: var(--radius-lg); padding: var(--space-4); cursor: pointer; transition: all var(--transition-fast); text-align: center; }
.subject-card:hover { border-color: var(--color-primary); transform: translateY(-2px); }
.subject-card.active { border-color: var(--color-primary); border-left-color: var(--card-accent, var(--color-primary)); background: var(--color-primary-light); box-shadow: 0 0 0 1px var(--color-primary), var(--shadow-sm); }
.subject-card-icon { width: 44px; height: 44px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; margin: 0 auto var(--space-2); font-size: 18px; font-weight: var(--font-bold); }
.subject-card-icon.all { background: var(--gray-200); color: var(--gray-600); }
.subject-card-name { font-size: var(--text-sm); font-weight: var(--font-mid); color: var(--gray-800); margin-bottom: 2px; }
.subject-card-count { font-size: var(--text-xs); color: var(--gray-500); }

.mode-tabs { display: flex; gap: 4px; background: var(--gray-50); border-radius: var(--radius-md); padding: 4px; flex-wrap: wrap; }
.mode-tab { flex: 1; border: none; background: none; padding: 8px 6px; border-radius: var(--radius-sm); cursor: pointer; font-size: var(--text-xs); color: var(--gray-600); transition: all var(--transition-fast); display: flex; flex-direction: column; align-items: center; gap: 2px; min-width: 55px; }
.mode-tab.active { background: var(--gray-25); color: var(--color-primary); box-shadow: var(--shadow-xs); font-weight: var(--font-mid); }
.mode-tab-icon { font-size: 16px; }

/* Review summary */
.review-summary { background: var(--gray-50); border-radius: var(--radius-md); padding: var(--space-3) var(--space-4); margin-top: var(--space-3); display: flex; gap: var(--space-4); }
.review-stat { display: flex; align-items: center; gap: var(--space-2); font-size: var(--text-sm); }
.review-stat.total { margin-left: auto; font-weight: var(--font-semibold); }
.review-stat-icon { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: var(--font-bold); }
.review-stat-icon.wr { background: var(--color-danger-light); color: var(--color-danger); }
.review-stat-icon.fv { background: #fef9e7; color: var(--color-warning); }
.review-stat-label { color: var(--gray-500); }
.review-stat-val { color: var(--gray-900); font-weight: var(--font-mid); }

/* Practice session */
.practice-session { max-width: 760px; margin: 0 auto; }
.practice-topbar { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-4); }
.back-btn { background: none; border: none; cursor: pointer; padding: var(--space-2); color: var(--gray-500); border-radius: var(--radius-sm); display: flex; align-items: center; min-width: 36px; min-height: 36px; justify-content: center; }
.back-btn:hover { background: var(--gray-50); color: var(--gray-700); }
.progress-wrap { flex: 1; display: flex; align-items: center; gap: var(--space-3); }
.progress-bar { flex: 1; height: 6px; background: var(--gray-100); border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--color-primary); border-radius: 99px; transition: width 0.3s; }
.progress-text { font-size: var(--text-sm); color: var(--gray-500); white-space: nowrap; }

.question-card { background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-6); box-shadow: var(--shadow-sm); }
.q-body { margin-bottom: var(--space-5); }
.q-stem { display: flex; gap: var(--space-2); font-size: var(--text-md); line-height: 1.8; color: var(--gray-900); }
.q-index { font-weight: var(--font-bold); color: var(--color-primary); flex-shrink: 0; }
.q-images { display: flex; gap: var(--space-2); margin-top: var(--space-3); }
.q-img { max-width: 200px; max-height: 150px; border-radius: var(--radius-sm); border: 1px solid var(--gray-100); cursor: pointer; }

.q-options { display: flex; flex-direction: column; gap: var(--space-2); margin-bottom: var(--space-4); }
.option-card { display: flex; align-items: center; gap: var(--space-3); padding: 14px 16px; border: 2px solid var(--gray-100); border-radius: var(--radius-md); cursor: pointer; transition: all var(--transition-fast); position: relative; }
.option-card:hover:not(.correct):not(.wrong) { border-color: var(--color-primary); background: var(--color-primary-light); }
.option-card.selected { border-color: var(--color-primary); background: var(--color-primary-light); }
.option-card.correct { border-color: var(--color-success); background: var(--color-success-light); }
.option-card.wrong { border-color: var(--color-danger); background: var(--color-danger-light); }
.option-letter { width: 28px; height: 28px; border-radius: 50%; background: var(--gray-100); display: flex; align-items: center; justify-content: center; font-size: var(--text-sm); font-weight: var(--font-bold); color: var(--gray-600); flex-shrink: 0; }
.option-card.selected .option-letter { background: var(--color-primary); color: #fff; }
.option-card.correct .option-letter { background: var(--color-success); color: #fff; }
.option-card.wrong .option-letter { background: var(--color-danger); color: #fff; }
.option-text { flex: 1; font-size: var(--text-base); line-height: 1.5; }
.option-badge { position: absolute; right: 12px; font-size: 18px; font-weight: var(--font-bold); }
.option-badge.correct { color: var(--color-success); }
.option-badge.wrong { color: var(--color-danger); }

.q-explanation { margin-top: var(--space-4); padding: var(--space-4); border-radius: var(--radius-md); font-size: var(--text-sm); }
.q-explanation.correct { background: var(--color-success-light); }
.q-explanation.wrong { background: var(--color-danger-light); }
.explain-header { font-weight: var(--font-semibold); margin-bottom: var(--space-2); }
.explain-icon.correct { color: var(--color-success); }
.explain-icon.wrong { color: var(--color-danger); }
.explain-answer { margin-bottom: var(--space-1); }
.explain-text { color: var(--gray-600); line-height: 1.6; margin-top: var(--space-2); }

.q-footer { display: flex; align-items: center; justify-content: space-between; margin-top: var(--space-5); padding-top: var(--space-4); border-top: 1px solid var(--gray-100); flex-wrap: wrap; gap: var(--space-3); }
.q-footer-actions { display: flex; gap: var(--space-1); }

.practice-result { max-width: 500px; margin: 40px auto; }
.result-card { background: var(--gray-25); border-radius: var(--radius-xl); padding: var(--space-10) var(--space-6); text-align: center; box-shadow: var(--shadow-md); }
.result-icon { font-size: 48px; margin-bottom: var(--space-4); }
.result-title { font-size: var(--text-xl); font-weight: var(--font-bold); color: var(--gray-900); margin-bottom: var(--space-6); }
.result-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); margin-bottom: var(--space-6); }
.result-stat { padding: var(--space-3); border-radius: var(--radius-md); background: var(--gray-50); }
.result-stat.correct { background: var(--color-success-light); }
.result-stat.wrong { background: var(--color-danger-light); }
.rs-val { display: block; font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--gray-900); line-height: 1.2; }
.rs-label { font-size: var(--text-xs); color: var(--gray-500); }
.result-actions { display: flex; gap: var(--space-3); justify-content: center; }

@media (max-width: 768px) {
  .subject-grid { grid-template-columns: repeat(2, 1fr); gap: var(--space-4); }
  .question-card { padding: var(--space-4); }
  .q-stem { font-size: var(--text-base); }
  .option-card { padding: 12px 14px; }
  .option-letter { width: 24px; height: 24px; font-size: 12px; }
  .result-stats { grid-template-columns: repeat(2, 1fr); }
  .review-summary { flex-direction: column; gap: var(--space-2); }
  .review-stat.total { margin-left: 0; }
  .mode-tab { font-size: 11px; padding: 6px 4px; }
}
</style>
  const q = practiceQuestions.value[currentIdx.value]
}
