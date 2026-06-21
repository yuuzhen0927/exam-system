<template>
  <div class="exam-take-root" style="min-height:calc(100vh - 60px)">
  <!-- 考前准备页 -->
  <div v-if="!started" class="exam-ready">
    <div class="ready-card">
      <div class="ready-icon">📋</div>
      <h1>{{ exam.title }}</h1>
      <div class="ready-tags">
        <el-tag :type="exam.mode==='formal'?'danger':'warning'" size="large" effect="dark">{{ exam.mode==='formal'?'正式考试':'模拟考试' }}</el-tag>
      </div>
      <div class="ready-info">
        <div class="info-row"><span class="info-label">题目数量</span><span class="info-value">{{ exam.questions?.length || 0 }} 题</span></div>
        <div class="info-row"><span class="info-label">考试时长</span><span class="info-value">{{ exam.duration_minutes }} 分钟</span></div>
        <div class="info-row"><span class="info-label">总分</span><span class="info-value">{{ exam.total_score }} 分</span></div>
        <div class="info-row"><span class="info-label">及格线</span><span class="info-value">{{ exam.pass_score }} 分</span></div>
      </div>
      <div v-if="exam.mode==='formal'" class="ready-warn">
        <el-icon><WarningFilled /></el-icon>
        <span>正式考试期间请勿切屏，超过 {{ exam.max_tab_switches || 3 }} 次将强制交卷</span>
      </div>
      <el-button type="primary" size="large" @click="startExam" class="ready-btn">开始考试</el-button>
    </div>
  </div>

  <!-- 考试中 -->
  <div v-else-if="!submitted" class="exam-sim">
    <header class="sim-header">
      <div class="sim-header-left">
        <span class="sim-exam-name">{{ exam.title }}</span>
        <el-tag :type="exam.mode==='formal'?'danger':''" size="small" effect="dark">{{ exam.mode==='formal'?'正式':'模拟' }}</el-tag>
      </div>
      <div class="sim-timer" :class="{urgent: remaining < 300, critical: remaining < 60}">
        <svg class="timer-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        <span class="timer-text">{{ formatTime(remaining) }}</span>
      </div>
      <span v-if="exam.mode==='formal'" class="sim-anti-cheat" :class="{warned: tabSwitches>0}"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg> {{ tabSwitches }}/{{ exam.max_tab_switches || 3 }}</span>
      <button class="sim-submit-btn" @click="submitExam" :disabled="submitting">
        {{ submitting ? '提交中...' : '交卷' }}
      </button>
    </header>

    <div class="sim-body">
      <div class="sim-question-area">
        <div class="sim-question-card">
          <div class="sq-header">
            <span class="sq-num">第 {{ currentIdx + 1 }} 题</span>
            <el-tag size="small" effect="plain">{{ typeLabel(currentQ?.type) }}</el-tag>
            <span class="sq-score" v-if="currentQ?.difficulty">难度 {{ '★'.repeat(currentQ.difficulty) }}</span>
          </div>
          <div class="sq-content" v-latex>{{ currentQ?.content }}</div>
          <div v-if="currentQ?.images?.length" class="sq-images">
            <img v-for="img in currentQ.images" :key="img" :src="img" class="sq-img" @click="previewImg=img" />
          </div>
          <div v-if="currentQ?.type !== 'composite' && currentQ?.type !== 'blank'" class="sq-options">
            <template v-if="currentQ?.type==='single' || currentQ?.type==='truefalse'">
              <div v-for="o in parseOptions(currentQ?.options)" :key="o.label"
                class="sq-option"
                :class="{selected: answers[currentQ?.id]===o.label}"
                @click="answers[currentQ.id] = o.label">
                <span class="sq-option-label">{{ o.label }}</span>
                <span class="sq-option-text">{{ o.text }}</span>
              </div>
            </template>
            <template v-else>
              <div v-for="o in parseOptions(currentQ?.options)" :key="o.label"
                class="sq-option"
                :class="{selected: multiAnswers[currentQ?.id]?.includes(o.label)}"
                @click="toggleMulti(currentQ.id, o.label)">
                <span class="sq-option-label" :class="{checked: multiAnswers[currentQ?.id]?.includes(o.label)}">{{ o.label }}</span>
                <span class="sq-option-text">{{ o.text }}</span>
              </div>
            </template>
          </div>
          <div v-else-if="currentQ?.type === 'blank'" class="sq-blank">
            <el-input v-model="answers[currentQ?.id]" placeholder="请输入答案" size="large" />
          </div>
          <div v-else class="sq-essay">
            <el-input v-model="answers[currentQ?.id]" type="textarea" :rows="5" placeholder="请输入答案..." />
          </div>
        </div>

        <div class="sq-nav">
          <button class="sq-nav-btn" :disabled="currentIdx === 0" @click="goPrev">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
            上一题
          </button>
          <span class="sq-nav-info">{{ currentIdx + 1 }} / {{ exam.questions?.length || 0 }}</span>
          <button class="sq-nav-btn" :disabled="currentIdx >= (exam.questions?.length||0) - 1" @click="goNext">
            下一题
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>

        <div class="sq-tools">
          <button class="sq-tool" @click="toggleFav(currentQ?.id)" :class="{active: favSet.has(currentQ?.id)}">
            <svg viewBox="0 0 24 24" width="16" height="16" :fill="favSet.has(currentQ?.id)?'currentColor':'none'" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            {{ favSet.has(currentQ?.id) ? '已收藏' : '收藏' }}
          </button>
          <button class="sq-tool" @click="openNote(currentQ)">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            笔记
          </button>
          <button class="sq-tool" @click="openFeedback(currentQ)">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            反馈
          </button>
          <button class="sq-tool" @click="toggleFlag(currentQ?.id)" :class="{active: flaggedQuestions.has(currentQ?.id)}">
            <svg viewBox="0 0 24 24" width="16" height="16" :fill="flaggedQuestions.has(currentQ?.id)?'currentColor':'none'" stroke="currentColor" stroke-width="2"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>
            {{ flaggedQuestions.has(currentQ?.id) ? '已标注' : '标注' }}
          </button>
          <button class="sq-tool" @click="calcVisible=!calcVisible" :class="{active:calcVisible}">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="10" x2="16" y2="10"/><line x1="8" y1="14" x2="12" y2="14"/></svg>
            计算器
          </button>
        </div>
      </div>

      <aside class="sim-answer-sheet">
        <div class="sheet-header">
          <h3>答题卡</h3>
          <span class="sheet-count">{{ answeredCount }}/{{ exam.questions?.length || 0 }}</span>
        </div>
        <div class="sheet-legend">
          <span class="legend-dot current"></span>当前
          <span class="legend-dot done"></span>已答
          <span class="legend-dot pending"></span>未答
          <span class="legend-flag">🚩</span>标注
        </div>
        <div class="sheet-grid">
          <button v-for="(q, i) in exam.questions" :key="q.id"
            class="sheet-num"
            :class="{ current: currentIdx === i, done: isAnswered(q.id), flagged: flaggedQuestions.has(q.id) }"
            @click="currentIdx = i">{{ i + 1 }}</button>
        </div>
        <button class="sheet-submit" @click="submitExam" :disabled="submitting">
          {{ submitting ? '提交中...' : '交卷' }}
        </button>
      </aside>
    </div>
  </div>

  <!-- 考试水印（正式考试）-->
  <div v-if="exam.mode==='formal' && started && !submitted" class="exam-watermark">{{ auth.user?.fullname || auth.user?.username }} | {{ new Date().toLocaleString() }}</div>

  <!-- 提交结果 -->
  <div v-if="submitted" class="exam-result">
    <div class="result-card">
      <div class="result-icon" :class="{pass: result?.passed}">{{ result?.passed ? '✓' : '✗' }}</div>
      <h2>{{ result?.passed ? '恭喜通过' : '未通过' }}</h2>
      <div class="result-score">{{ result?.auto_score }}<span> / {{ result?.total_score }} 分</span></div>
      <div class="result-actions">
        <el-button type="primary" @click="$router.push('/results')">查看成绩</el-button>
        <el-button @click="$router.push('/dashboard')">返回首页</el-button>
      </div>
    </div>
  </div>

  <!-- 笔记弹窗 -->
  <el-dialog v-model="noteDialog.visible" title="添加笔记" width="420">
    <el-input v-model="noteDialog.content" type="textarea" :rows="4" placeholder="笔记内容" />
    <template #footer><el-button @click="noteDialog.visible=false">取消</el-button><el-button type="primary" @click="saveNote">保存</el-button></template>
  </el-dialog>

  <!-- 反馈弹窗 -->
  <el-dialog v-model="fbDialog.visible" title="题目反馈" width="420">
    <el-input v-model="fbDialog.content" type="textarea" :rows="3" placeholder="请描述问题..." />
    <template #footer><el-button @click="fbDialog.visible=false">取消</el-button><el-button type="primary" @click="submitFeedback">提交</el-button></template>
  </el-dialog>

  <!-- 科学计算器 -->
  <div v-if="calcVisible" class="calc-panel" :style="{left:calcX+'px',top:calcY+'px'}" @mousedown.stop>
    <div class="calc-header" @mousedown="startDrag" @mouseup="stopDrag" @mouseleave="stopDrag">
      <span>科学计算器</span>
      <button class="calc-close" @click="calcVisible=false">&#xd7;</button>
    </div>
    <div class="calc-display">{{ calcDisplay || '0' }}</div>
    <div class="calc-keys">
      <button v-for="k in calcKeys" :key="k" class="calc-key" :class="{fn:k.length>1&&k!=='+'&&k!=='-'}" @click="calcPress(k)">{{ k }}</button>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { WarningFilled } from '@element-plus/icons-vue'

import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const exam = ref({ questions: [] })
const answers = reactive({})
const multiAnswers = reactive({})
const started = ref(false)
const submitted = ref(false)
const result = ref({})
const currentIdx = ref(0)
const remaining = ref(0)
const submitting = ref(false)
const previewImg = ref(null)
const favSet = ref(new Set())
const flaggedQuestions = ref(new Set())  // 题目标注（不确定）
const tabSwitches = ref(0)
const noteDialog = reactive({ visible: false, questionId: null, content: '' })
const fbDialog = reactive({ visible: false, questionId: null, content: '' })
const calcVisible = ref(false)
const calcDisplay = ref('')
const calcX = ref(200)
const calcY = ref(100)
let calcExpr = ''
let dragging = false; let dragStartX = 0; let dragStartY = 0
const calcKeys = ['sin','cos','tan','log','ln','C','(',')','√','π','7','8','9','÷','x²','x³','4','5','6','×','xʸ','EXP','1','2','3','-','±','.','0','=','+','DEL']

function startDrag(e) { dragging = true; dragStartX = e.clientX - calcX.value; dragStartY = e.clientY - calcY.value; document.addEventListener('mousemove', onDrag); document.addEventListener('mouseup', stopDrag) }
function onDrag(e) { if (!dragging) return; calcX.value = e.clientX - dragStartX; calcY.value = e.clientY - dragStartY }
function stopDrag() { dragging = false; document.removeEventListener('mousemove', onDrag); document.removeEventListener('mouseup', stopDrag) }
function calcPress(k) {
  if (k === 'C') { calcExpr = ''; calcDisplay.value = ''; return }
  if (k === 'DEL') { calcExpr = calcExpr.slice(0,-1); calcDisplay.value = calcExpr; return }
  if (k === '=') { try { let v = evalExpr(calcExpr); calcDisplay.value = String(v); calcExpr = String(v) } catch { calcDisplay.value = 'Error' } return }
  const map = { '\u00d7':'*', '\u00f7':'/', '\u03c0':`(${Math.PI})`, '\u221a':'Math.sqrt(', 'x\u00b2':'**2', 'x\u00b3':'**3', 'x\u02b8':'**', 'EXP':'e', '\u00b1':'-' }
  calcExpr += map[k] || k
  calcDisplay.value = calcExpr
}
function evalExpr(e) {
  let s = e.replace(/sin/g,'Math.sin').replace(/cos/g,'Math.cos').replace(/tan/g,'Math.tan').replace(/log/g,'Math.log10').replace(/ln/g,'Math.log').replace(/\^/g,'**')
  return Function('\"use strict\"; return (' + s + ')')()
}

let timer = null

// ===== 考试会话持久化（防止页面刷新丢失状态）=====
const SESSION_KEY = computed(() => `exam_session_${route.params.id}`)

function saveSession() {
  if (!started.value || submitted.value) return
  const state = {
    examId: exam.value.id,
    examTitle: exam.value.title,
    mode: exam.value.mode,
    durationMinutes: exam.value.duration_minutes,
    maxTabSwitches: exam.value.max_tab_switches || 3,
    answers: Object.assign({}, answers),
    multiAnswers: {},
    currentIdx: currentIdx.value,
    remaining: remaining.value,
    tabSwitches: tabSwitches.value,
    questions: exam.value.questions,
    savedAt: Date.now()
  }
  for (const k of Object.keys(multiAnswers)) { state.multiAnswers[k] = [...(multiAnswers[k]||[])] }
  try { sessionStorage.setItem(SESSION_KEY.value, JSON.stringify(state)) } catch {}
}

function loadSession() {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY.value)
    if (!raw) return false
    const state = JSON.parse(raw)
    if (String(state.examId) !== String(exam.value.id)) return false
    if (state.questions?.length) { exam.value.questions = state.questions }
    Object.assign(answers, state.answers || {})
    for (const k of Object.keys(state.multiAnswers || {})) { multiAnswers[k] = state.multiAnswers[k] }
    currentIdx.value = state.currentIdx || 0
    tabSwitches.value = state.tabSwitches || 0
    const elapsed = Math.floor((Date.now() - state.savedAt) / 1000)
    remaining.value = Math.max(0, state.remaining - elapsed)
    return true
  } catch { return false }
}

function clearSession() {
  try { sessionStorage.removeItem(SESSION_KEY.value) } catch {}
}

watch([answers, multiAnswers, currentIdx], () => { saveSession() }, { deep: true })

const currentQ = computed(() => exam.value.questions[currentIdx.value])

const answeredCount = computed(() => {
  let c = 0
  for (const q of exam.value.questions) {
    if (answers[q.id] || (multiAnswers[q.id]?.length)) c++
  }
  return c
})

// 正式考试防切出：拦截路由跳转
onBeforeRouteLeave((_to, _from, next) => {
  if (started.value && !submitted.value && exam.value?.mode === 'formal') {
    countRouteSwitch()
    ElMessage.error('正式考试期间禁止离开考试页面！请先交卷。')
    next(false)
  } else {
    next()
  }
})

onMounted(async () => {
  try {
    const { data } = await api.get(`/exams/${route.params.id}/take`)
    exam.value = data
    // 检查是否有保存的考试会话（页面刷新后恢复）
    const restored = loadSession()
    if (restored && exam.value.mode === 'formal') {
      // 恢复考试状态
      started.value = true
      timer = setInterval(() => {
        remaining.value--
        saveSession()
        if (remaining.value <= 0) { clearInterval(timer); submitExam({force:true}) }
      }, 1000)
      document.addEventListener('visibilitychange', onVis)
      // Block browser back/forward during formal exam
      if (exam.value?.mode === 'formal') {
        history.pushState(null, '', window.location.href)
        window.addEventListener('popstate', (ev) => {
          if (started.value && !submitted.value) {
            history.pushState(null, '', window.location.href)
            countSwitch()
            ElMessage.error('正式考试期间禁止离开页面！')
          }
        })
        // Block context menu
        document.addEventListener('contextmenu', (e) => e.preventDefault())
        // Block F5/Ctrl+R refresh
        const blockRefresh = (e) => {
          if ((e.key === 'F5') || (e.ctrlKey && e.key === 'r') || (e.ctrlKey && e.key === 'R')) {
            e.preventDefault()
            ElMessage.error('正式考试期间禁止刷新页面！')
          }
        }
        document.addEventListener('keydown', blockRefresh)
        // Store handler for cleanup
        window.__exam_blockRefresh = blockRefresh
      }
      window.addEventListener('blur', onBlur)
      // Block right-click context menu during formal exam
      if (exam.value?.mode === 'formal') {
        document.addEventListener('contextmenu', (e) => e.preventDefault())
      }
      window.addEventListener('beforeunload', onBeforeUnload)
      ElMessage.info('已恢复考试状态')
    } else {
      remaining.value = data.duration_minutes * 60
    }
    document.addEventListener('keydown', handleKeydown)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '加载失败')
    router.push('/exams')
  }
})

onUnmounted(() => {
  saveSession()
  clearInterval(timer)
  document.removeEventListener('visibilitychange', onVis)
    document.removeEventListener('contextmenu', () => {})
    if (window.__exam_blockRefresh) {
      document.removeEventListener('keydown', window.__exam_blockRefresh)
      delete window.__exam_blockRefresh
    }
  document.removeEventListener('blur', onBlur)
  document.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('beforeunload', onBeforeUnload)
})

function startExam() {
  started.value = true
  timer = setInterval(() => {
    remaining.value--; saveSession()
    if (remaining.value <= 0) { clearInterval(timer); submitExam({force:true}) }
  }, 1000)
  if (exam.value.mode === 'formal') {
    document.addEventListener('visibilitychange', onVis)
      // Block browser back/forward during formal exam
      if (exam.value?.mode === 'formal') {
        history.pushState(null, '', window.location.href)
        window.addEventListener('popstate', (ev) => {
          if (started.value && !submitted.value) {
            history.pushState(null, '', window.location.href)
            countSwitch()
            ElMessage.error('正式考试期间禁止离开页面！')
          }
        })
        // Block context menu
        document.addEventListener('contextmenu', (e) => e.preventDefault())
        // Block F5/Ctrl+R refresh
        const blockRefresh = (e) => {
          if ((e.key === 'F5') || (e.ctrlKey && e.key === 'r') || (e.ctrlKey && e.key === 'R')) {
            e.preventDefault()
            ElMessage.error('正式考试期间禁止刷新页面！')
          }
        }
        document.addEventListener('keydown', blockRefresh)
        // Store handler for cleanup
        window.__exam_blockRefresh = blockRefresh
      }
    document.addEventListener('blur', onBlur)
    window.addEventListener('beforeunload', onBeforeUnload)
  }
  saveSession()
}

function onBeforeUnload(e) {
  if (exam.value.mode !== 'formal' || !started.value || submitted.value) return

  saveSession()
  const token = localStorage.getItem("token") || ""
  const maxSw = exam.value.max_tab_switches || 3
  // 使用绝对 URL，确保 sendBeacon 在跨域导航时也能送达
  const base = window.location.origin
  const url = `${base}/api/exams/${route.params.id}/report-tab-switch?count=${maxSw}&token=${encodeURIComponent(token)}`

  // sendBeacon 在 unload 期间可靠送达；备选同步 XHR
  if (navigator.sendBeacon) {
    navigator.sendBeacon(url)
  } else {
    try { const xhr = new XMLHttpRequest(); xhr.open('POST', url, false); xhr.send() } catch {}
  }

  e.preventDefault()
  e.returnValue = '你正在进行正式考试，离开将记录为切屏行为'
  return e.returnValue
}

function countRouteSwitch() {
  countSwitch()
  ElMessage.error('正式考试期间禁止离开考试页面！已记录切屏')
}

function onVis() {
  if (!document.hidden && document.visibilityState !== 'hidden') return
  countSwitch()
}

function onBlur() { countSwitch() }

function countSwitch() {
  tabSwitches.value++
  try { api.post(`/exams/${route.params.id}/report-tab-switch?count=1`) } catch {}
  const max = exam.value.max_tab_switches || 3
  if (tabSwitches.value >= max) {
    ElMessage.error(`切屏次数达上限(${max}次)，强制交卷`)
    submitExam({force:true})
  } else {
    ElMessage.warning(`警告：已切屏 ${tabSwitches.value}/${max} 次`)
  }
}

function isAnswered(qid) { return !!(answers[qid] || (multiAnswers[qid]?.length)) }
function goPrev() { if (currentIdx.value > 0) currentIdx.value-- }
function goNext() { if (currentIdx.value < (exam.value.questions?.length || 0) - 1) currentIdx.value++ }
function toggleFlag(qid) { if (flaggedQuestions.value.has(qid)) { flaggedQuestions.value.delete(qid) } else { flaggedQuestions.value.add(qid) } }

function handleKeydown(e) {
  // Ignore if typing in input/textarea
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) return
  
  const q = exam.value.questions?.[currentIdx.value]
  if (!q || submitted.value) return
  
  // A/B/C/D for single/multi choice
  if (q.type === 'single' || q.type === 'multi') {
    const key = e.key.toUpperCase()
    if (key >= 'A' && key <= 'D') {
      e.preventDefault()
      const idx = key.charCodeAt(0) - 65
      const options = typeof q.options === 'string' ? JSON.parse(q.options || '[]') : (q.options || [])
      if (idx < options.length) {
        if (q.type === 'single') {
          answers[currentIdx.value] = key
        } else {
          // Toggle multi-select
          const cur = (multiAnswers[currentIdx.value] || '').split('')
          const pos = cur.indexOf(key)
          if (pos >= 0) cur.splice(pos, 1)
          else cur.push(key)
          multiAnswers[currentIdx.value] = cur.sort().join('')
        }
      }
      return
    }
  }
  
  // Arrow keys for navigation
  if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
    e.preventDefault()
    if (e.key === 'ArrowLeft' && currentIdx.value > 0) {
      currentIdx.value--
    } else if (e.key === 'ArrowRight' && currentIdx.value < exam.value.questions.length - 1) {
      currentIdx.value++
    }
    return
  }
  
  // Space to flag/unflag
  if (e.key === ' ') {
    e.preventDefault()
    toggleFlag(currentIdx.value)
    return
  }
  
  // Enter to submit (with confirmation)
  if (e.key === 'Enter' && !e.shiftKey && q.type === 'composite') {
    e.preventDefault()
    // For composite questions, Enter doesn't auto-submit
    return
  }
}

function toggleMulti(qid, label) {
  if (!multiAnswers[qid]) multiAnswers[qid] = []
  const idx = multiAnswers[qid].indexOf(label)
  if (idx >= 0) multiAnswers[qid].splice(idx, 1)
  else multiAnswers[qid].push(label)
}

function parseOptions(opt) { let r = []; if (!opt) r = []; else if (Array.isArray(opt)) r = opt; else { try { r = JSON.parse(opt) } catch { r = [] } } return r.sort((a,b)=>(a.label||"").localeCompare(b.label||"")) }
function typeLabel(t) { return { single:'单选', multi:'多选', truefalse:'判断', composite:'综合', blank:'填空' }[t] || t }
function formatTime(s) {
  if (s < 0) s = 0
  const m = Math.floor(s / 60)
  return `${String(m).padStart(2,'0')}:${String(s % 60).padStart(2,'0')}`
}

async function toggleFav(qid) {
  if (!qid) return
  try {
    const { data } = await api.post(`/favorites/toggle/${qid}`)
    if (data.is_favorited) favSet.value.add(qid)
    else favSet.value.delete(qid)
  } catch {}
}
function openNote(q) { noteDialog.questionId = q?.id; noteDialog.content = ''; noteDialog.visible = true }
async function saveNote() {
  if (!noteDialog.content.trim()) return
  try { await api.post('/notes', { question_id: noteDialog.questionId, content: noteDialog.content }) } catch {}
  noteDialog.visible = false; ElMessage.success('笔记已保存')
}
function openFeedback(q) { fbDialog.questionId = q?.id; fbDialog.content = ''; fbDialog.visible = true }
async function submitFeedback() {
  if (!fbDialog.content.trim()) return
  try { await api.post('/feedback', { question_id: fbDialog.questionId, content: fbDialog.content, type: 'doubt' }) } catch {}
  fbDialog.visible = false; ElMessage.success('反馈已提交')
}

async function submitExam(opts = {}) {
  if (!opts.force) {
    try { await ElMessageBox.confirm('确定提交试卷？', '确认交卷', { confirmButtonText: '确定交卷', cancelButtonText: '继续答题', type: 'warning' }) } catch { return }
  }
  submitting.value = true; clearInterval(timer)
  const finalAnswers = { ...answers }
  for (const [qid, arr] of Object.entries(multiAnswers)) { finalAnswers[qid] = [...arr].sort().join('') }
  try {
    const { data } = await api.post(`/exams/${route.params.id}/submit`, { answers: finalAnswers })
    clearSession()
    result.value = data; submitted.value = true
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
    submitting.value = false
    timer = setInterval(() => { remaining.value--; if (remaining.value <= 0) { clearInterval(timer); submitExam({force:true}) } }, 1000)
  }
}
</script>

<style scoped>
/* ========== 考前准备 ========== */
.exam-ready {
  display: flex; align-items: center; justify-content: center;
  min-height: calc(100vh - 60px); background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: var(--space-6);
}
.ready-card {
  background: var(--gray-25); border-radius: 20px; padding: 48px 40px;
  max-width: 480px; width: 100%; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
.ready-icon { font-size: 64px; margin-bottom: 16px; }
.ready-card h1 { font-size: 24px; font-weight: 700; margin: 0 0 12px; color: var(--gray-900); }
.ready-tags { margin-bottom: 24px; }
.ready-info { text-align: left; margin-bottom: 20px; }
.info-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--gray-100); }
.info-row:last-child { border: none; }
.info-label { color: var(--gray-500); font-size: 14px; }
.info-value { font-weight: 600; color: var(--gray-800); }
.ready-warn {
  display: flex; align-items: center; gap: 8px;
  background: var(--gray-25)3cd; color: #856404; padding: 12px 16px;
  border-radius: 10px; font-size: 13px; margin-bottom: 24px; text-align: left;
}
.ready-btn { width: 100%; height: 48px; font-size: 16px; border-radius: 12px; }

/* ========== 考试仿真界面 ========== */
.exam-sim {
  height: calc(100vh - 60px); display: flex; flex-direction: column;
  background: #f0f2f5;
}

/* 顶部栏 */
.sim-header {
  height: 56px; background: #1a1a2e; display: flex; align-items: center;
  padding: 0 24px; gap: 16px; flex-shrink: 0;
}
.sim-header-left { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
.sim-exam-name { color: #fff; font-size: 15px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.sim-timer {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 16px; border-radius: 20px;
  background: rgba(255,255,255,0.1); color: #fff;
  font-size: 18px; font-weight: 700; font-variant-numeric: tabular-nums;
  transition: all 0.3s;
}
.sim-timer.urgent { background: #e6a817; color: #1a1a2e; animation: timerPulse 1s infinite; }
.sim-timer.critical { background: #dc3545; color: #fff; animation: timerPulse 0.5s infinite; }
@keyframes timerPulse { 0%,100%{opacity:1} 50%{opacity:0.7} }
.timer-text { min-width: 55px; text-align: center; }

.sim-anti-cheat {
  display: flex; align-items: center; gap: 5px;
  padding: 4px 10px; border-radius: 14px;
  background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.5);
  font-size: 12px; font-weight: 600; transition: all 0.3s;
}
.sim-anti-cheat.warned {
  background: rgba(220,53,69,0.3); color: #ff6b6b;
  animation: timerPulse 1s infinite;
}

.sim-submit-btn {
  padding: 8px 24px; border: 2px solid rgba(255,255,255,0.3); border-radius: 8px;
  background: transparent; color: #fff; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
}
.sim-submit-btn:hover { background: #dc3545; border-color: #dc3545; }
.sim-submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* 主体 */
.sim-body { flex: 1; display: flex; overflow: hidden; }

/* 题目区 */
.sim-question-area {
  flex: 1; display: flex; flex-direction: column;
  padding: 24px; overflow-y: auto; gap: 16px;
}

.sim-question-card {
  background: var(--gray-25); border-radius: 16px; padding: 32px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04); flex: 1;
}

.sq-header { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
.sq-num { font-size: 15px; font-weight: 700; color: var(--color-primary); }
.sq-score { margin-left: auto; font-size: 12px; color: var(--gray-400); }

.sq-content { font-size: 16px; line-height: 1.8; color: var(--gray-900); margin-bottom: 24px; }

.sq-images { display: flex; gap: 8px; margin-bottom: 16px; }
.sq-img { max-width: 240px; max-height: 180px; border-radius: 8px; cursor: zoom-in; border: 1px solid var(--gray-100); }

/* 选项 */
.sq-options { display: flex; flex-direction: column; gap: 10px; }
.sq-blank { padding: 12px 0; }
.sq-option {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 14px 18px; border-radius: 12px;
  border: 2px solid var(--gray-100);
  cursor: pointer; transition: all 0.15s;
}
.sq-option:hover { border-color: var(--color-primary); background: var(--color-primary-light); }
.sq-option.selected { border-color: var(--color-primary); background: var(--color-primary-light); }

.sq-option-label {
  width: 32px; height: 32px; border-radius: 50%;
  border: 2px solid var(--gray-200);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 14px; flex-shrink: 0;
  transition: all 0.15s; color: var(--gray-600);
}
.sq-option.selected .sq-option-label,
.sq-option-label.checked {
  background: var(--color-primary); border-color: var(--color-primary); color: #fff;
}
.sq-option-text { font-size: 15px; line-height: 1.6; padding-top: 4px; }

.sq-essay { margin-top: 8px; }

/* 导航 */
.sq-nav {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--gray-25); border-radius: 12px; padding: 12px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.sq-nav-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 20px; border: 2px solid var(--gray-100); border-radius: 8px;
  background: var(--gray-25); color: var(--gray-700); font-size: 14px; font-weight: 500;
  cursor: pointer; transition: all 0.15s;
}
.sq-nav-btn:hover:not(:disabled) { border-color: var(--color-primary); color: var(--color-primary); }
.sq-nav-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.sq-nav-info { font-size: 14px; color: var(--gray-500); font-weight: 500; }

/* 底部工具 */
.sq-tools {
  display: flex; gap: 8px; justify-content: center;
  background: var(--gray-25); border-radius: 12px; padding: 8px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.sq-tool {
  display: flex; align-items: center; gap: 4px;
  padding: 6px 12px; border: none; border-radius: 8px;
  background: transparent; color: var(--gray-500); font-size: 13px;
  cursor: pointer; transition: all 0.15s;
}
.sq-tool:hover { background: var(--gray-50); color: var(--gray-700); }
.sq-tool.active { color: var(--color-warning); }

/* ========== 答题卡 ========== */
.sim-answer-sheet {
  width: 260px; background: var(--gray-25); border-left: 1px solid var(--gray-100);
  display: flex; flex-direction: column; padding: 20px; flex-shrink: 0;
}
.sheet-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px;
}
.sheet-header h3 { font-size: 16px; font-weight: 700; margin: 0; color: var(--gray-900); }
.sheet-count { font-size: 13px; color: var(--gray-500); font-weight: 500; }

.sheet-legend {
  display: flex; gap: 16px; align-items: center;
  font-size: 11px; color: var(--gray-500); margin-bottom: 16px;
}
.legend-dot { width: 10px; height: 10px; border-radius: 3px; display: inline-block; }
.legend-dot.current { background: var(--gray-25); border: 2px solid var(--color-primary); }
.legend-dot.done { background: var(--color-primary); }
.legend-dot.pending { background: var(--gray-200); }

.sheet-grid {
  flex: 1; display: grid; grid-template-columns: repeat(5, 1fr);
  gap: 8px; align-content: start; overflow-y: auto;
}
.sheet-num {
  aspect-ratio: 1; border-radius: 8px;
  border: 2px solid var(--gray-100); background: var(--gray-25);
  font-size: 13px; font-weight: 600; color: var(--gray-600);
  cursor: pointer; transition: all 0.15s;
  display: flex; align-items: center; justify-content: center;
  min-width: 0;
}
.sheet-num:hover { border-color: var(--color-primary); }
.sheet-num.current { border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-light); color: var(--color-primary); }
.sheet-num.done { background: var(--color-primary); border-color: var(--color-primary); color: #fff; }
.sheet-num.flagged::after { content: '🚩'; position: absolute; top: -6px; right: -4px; font-size: 10px; }
.exam-watermark { position: fixed; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; z-index: 9999; display: flex; align-items: center; justify-content: center; font-size: 48px; color: rgba(128,128,128,0.08); transform: rotate(-30deg); user-select: none; white-space: nowrap; }
.legend-flag { font-size: 12px; }

.sheet-submit {
  margin-top: 16px; width: 100%; padding: 12px; border: none; border-radius: 10px;
  background: var(--color-danger); color: #fff; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: all 0.15s; flex-shrink: 0;
}
.sheet-submit:hover { background: #dc2626; }
.sheet-submit:disabled { opacity: 0.5; cursor: not-allowed; }

/* ========== 结果页 ========== */
.exam-result {
  display: flex; align-items: center; justify-content: center;
  min-height: calc(100vh - 60px); background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.result-card {
  background: var(--gray-25); border-radius: 20px; padding: 48px;
  text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
.result-icon {
  width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: 36px; font-weight: 700;
  background: var(--color-danger-light); color: #dc2626;
}
.result-icon.pass { background: var(--color-success-light); color: #16a34a; }
.result-card h2 { font-size: 22px; margin: 0 0 16px; color: var(--gray-900); }
.result-score { font-size: 48px; font-weight: 800; color: var(--color-primary); margin-bottom: 24px; }
.result-score span { font-size: 20px; font-weight: 500; color: var(--gray-500); }
.result-actions { display: flex; gap: 12px; justify-content: center; }

/* ========== 科学计算器 ========== */
.calc-panel {
  position: fixed; z-index: 9999;
  width: 280px; background: #1e293b; border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.35); overflow: hidden;
  user-select: none;
}
.calc-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 14px; background: #0f172a; cursor: move;
  color: #e2e8f0; font-size: 13px; font-weight: 600;
}
.calc-close {
  background: none; border: none; color: #94a3b8; font-size: 18px;
  cursor: pointer; padding: 0 4px; line-height: 1;
}
.calc-close:hover { color: #fff; }
.calc-display {
  padding: 12px 16px; background: #0f172a; color: #38bdf8;
  font-size: 22px; font-weight: 700; font-family: 'Consolas','Courier New',monospace;
  text-align: right; min-height: 48px; word-break: break-all; line-height: 1.3;
}
.calc-keys {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 1px; background: #334155;
  padding: 1px;
}
.calc-key {
  padding: 10px 4px; border: none; background: #1e293b; color: #e2e8f0;
  font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.1s;
  font-family: 'Consolas',monospace;
}
.calc-key:hover { background: #334155; }
.calc-key:active { background: #475569; }
.calc-key.fn { background: #0f172a; color: #38bdf8; font-size: 11px; }
.calc-key.fn:hover { background: #1e293b; }

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .sim-answer-sheet { display: none; }
  .calc-panel { width: 92vw; left: 4vw !important; top: 50% !important; transform: translateY(-50%); max-height: 80vh; }
  .calc-keys { grid-template-columns: repeat(5, 1fr); }
  .calc-key { padding: 14px 4px; font-size: 15px; }
  .calc-key.fn { font-size: 13px; }
  .sim-question-area { padding: 12px; }
  .sim-question-card { padding: 20px; }
  .sim-header { padding: 0 12px; }
  .sim-exam-name { font-size: 13px; }
  .sim-timer { font-size: 15px; padding: 4px 10px; }
  .sq-content { font-size: 15px; }
  .sq-option { padding: 12px 14px; }
  .sq-option-text { font-size: 14px; }
  .ready-card { padding: 32px 24px; }
  .result-card { padding: 32px 24px; }
}
</style>
