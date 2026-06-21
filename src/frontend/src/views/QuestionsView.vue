<template>
  <div class="questions-page">
    <!-- Header -->
    <div class="page-header">
      <div class="ph-info">
        <div class="ph-icon"><el-icon size="22"><Document /></el-icon></div>
        <div>
          <h2>题库管理</h2>
          <p class="ph-sub">共 {{ total }} 道题目</p>
        </div>
      </div>
      <div class="ph-actions">
        <el-dropdown @command="handleImportCmd">
          <el-button>
            <el-icon><Upload /></el-icon>
            <span class="btn-text">导入</span>
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="template">下载模板</el-dropdown-item>
              <el-dropdown-item command="import">批量导入</el-dropdown-item>
              <el-dropdown-item command="export">导出Excel</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon>
          <span class="btn-text">新建题目</span>
        </el-button>
      </div>
      <input ref="importBtnRef" type="file" accept=".xlsx,.xls" style="display:none" @change="uploadExcel" />
    </div>

    <!-- Type Stats -->
    <div class="type-stats" v-if="items.length">
      <div class="ts-item" v-for="ts in typeStats" :key="ts.type">
        <span class="ts-dot" :style="{ background: ts.color }"></span>
        <span class="ts-label">{{ ts.label }}</span>
        <span class="ts-count">{{ ts.count }}</span>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <el-input
        v-model="searchText"
        placeholder="搜索题目内容..."
        clearable
        class="fb-search"
        @input="onSearch"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filter.subject_id" placeholder="科目" clearable @change="onSearch" class="fb-sel">
        <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-select v-model="filter.type" placeholder="题型" clearable @change="onSearch" class="fb-sel fb-sel-sm">
        <el-option label="单选题" value="single" />
        <el-option label="多选题" value="multi" />
        <el-option label="判断题" value="truefalse" />
        <el-option label="综合题" value="composite" />
              <el-option label="填空题" value="blank" />
      </el-select>
      <el-select v-model="filter.difficulty" placeholder="难度" clearable @change="onSearch" class="fb-sel fb-sel-sm">
        <el-option v-for="d in 5" :key="d" :label="d + '星'" :value="d" />
      </el-select>
      <el-button text @click="resetFilters" class="reset-btn">
        <el-icon><RefreshRight /></el-icon>
      </el-button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="state-box">
      <el-icon class="is-loading" size="28"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="!items.length" class="state-box">
      <el-empty description="暂无题目" :image-size="120">
        <el-button type="primary" @click="openDialog()">新建第一道题目</el-button>
      </el-empty>
    </div>

    <!-- Question Cards Grid -->
    <div v-else class="q-grid">
      <div
        v-for="q in filteredItems"
        :key="q.id"
        class="q-card"
        :class="'q-card-' + q.type"
        @click="openDialog(q)"
      >
        <!-- Type color bar -->
        <div class="q-accent" :style="{ background: typeColor(q.type) }"></div>
        <div class="q-card-inner">
          <!-- Top row: type badge + difficulty + id -->
          <div class="q-top">
            <span class="q-type-badge" :style="{ background: typeColor(q.type) }">{{ typeLabel(q.type) }}</span>
            <div class="q-stars" :title="'难度: ' + (q.difficulty || 1) + '/5'">
              <span v-for="s in 5" :key="s" :class="s <= (q.difficulty || 1) ? 'star-on' : 'star-off'">&#9733;</span>
            </div>
            <span class="q-id">#{{ q.id }}</span>
          </div>

          <!-- Content -->
          <div class="q-body">
            <p class="q-content">{{ q.content }}</p>
            <div v-if="qImages(q).length" class="q-img-hint">
              <el-icon size="14"><Picture /></el-icon>
              <span>{{ qImages(q).length }}张图片</span>
            </div>
          </div>

          <!-- Meta -->
          <div class="q-meta">
            <span v-if="q.subject_name" class="qm-tag qm-subject">
              <el-icon size="12"><FolderOpened /></el-icon>{{ q.subject_name }}
            </span>
            <span v-if="q.chapter_name" class="qm-tag qm-chapter">{{ q.chapter_name }}</span>
          </div>

          <!-- Footer actions -->
          <div class="q-foot">
            <el-button text type="primary" size="small" @click.stop="openDialog(q)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button text type="danger" size="small" @click.stop="delQuestion(q.id)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination-wrap">
      <el-pagination
        v-model:current-page="page"
        :total="total"
        :page-size="pageSize"
        layout="total, prev, pager, next"
        @current-change="fetchQuestions"
        background
        size="small"
      />
    </div>

    <!-- Create / Edit Dialog -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑题目' : '新建题目'"
      width="680px"
      top="4vh"
      :close-on-click-modal="false"
      destroy-on-close
      class="q-dialog"
    >
      <div class="dlg-body">
        <!-- Type + Difficulty bar -->
        <div class="dlg-type-bar">
          <div class="dlg-type-group">
            <button
              v-for="t in [{l:'单选',v:'single',c:'#409eff'},{l:'多选',v:'multi',c:'#67c23a'},{l:'判断',v:'truefalse',c:'#e6a23c'},{l:'综合',v:'composite',c:'#f56c6c'},{l:'填空',v:'blank',c:'#909399'}]"
              :key="t.v"
              class="type-seg"
              :class="{ active: dialog.form.type === t.v }"
              :style="dialog.form.type === t.v ? { background: t.c, borderColor: t.c } : {}"
              @click.prevent="dialog.form.type = t.v; onDlgTypeChange(t.v)"
            >{{ t.l }}</button>
          </div>
          <div class="dlg-diff">
            <span class="diff-label">难度</span>
            <el-rate v-model="dialog.form.difficulty" :max="5" />
          </div>
        </div>

        <!-- Inline meta row: Subject + Chapter -->
        <div class="dlg-meta-row">
          <el-select v-model="dialog.form.subject_id" placeholder="科目 *" @change="onDlgSubjectChange" size="default" style="flex:1">
            <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
          <el-select v-model="dialog.form.chapter_id" placeholder="章节" clearable size="default" style="flex:1">
            <el-option v-for="c in dialogChapters" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </div>

        <!-- Content -->
        <div class="dlg-field">
          <div class="field-head">
            <span class="field-title">题目内容</span>
            <span class="field-req">*必填</span>
          </div>
          <el-input v-model="dialog.form.content" type="textarea" :rows="3" placeholder="输入题目内容，支持 $ LaTeX 公式" resize="vertical" />
        </div>

        <!-- Options (non-composite, non-blank) -->
        <div class="dlg-field" v-if="dialog.form.type !== 'composite' && dialog.form.type !== 'blank'">
          <div class="field-head">
            <span class="field-title">选项</span>
            <span class="field-hint" v-if="dialog.form.type === 'single'">单选</span>
            <span class="field-hint" v-else-if="dialog.form.type === 'multi'">多选</span>
            <span class="field-hint" v-else>判断题</span>
          </div>
          <div class="opt-list">
            <label
              v-for="(opt, idx) in dlgOptions"
              :key="idx"
              class="opt-card"
              :class="{ 'opt-card-active': dlgAnswers.includes(opt.label) }"
            >
              <input type="checkbox" :checked="dlgAnswers.includes(opt.label)" @change="(e) => toggleAnswer(opt.label, e.target.checked)" class="opt-card-chk" />
              <span class="opt-card-letter" :class="{ 'letter-on': dlgAnswers.includes(opt.label) }">{{ opt.label }}</span>
              <input
                v-model="opt.text"
                :placeholder="'选项 ' + opt.label"
                class="opt-card-input"
                @click.stop
              />
              <button
                v-if="dlgOptions.length > 2 && dialog.form.type !== 'truefalse'"
                class="opt-card-del"
                @click.stop="removeDlgOption(idx)"
                title="删除选项"
              >&times;</button>
            </label>
          </div>
          <button v-if="dialog.form.type !== 'truefalse'" class="opt-add-btn" @click="addDlgOption">
            <el-icon size="14"><Plus /></el-icon> 添加选项
          </button>
        </div>

        <!-- Reference Answer (fill-blank) -->
        <div class="dlg-field" v-if="dialog.form.type === 'blank'">
          <div class="field-head">
            <span class="field-title">正确答案</span>
            <span class="field-req">*必填</span>
          </div>
          <el-input v-model="dialog.form.answer" placeholder="输入正确答案，多个答案用 | 分隔" />
          <span class="field-hint">多个可接受答案用 | 分隔，如：水泥|硅酸盐水泥</span>
        </div>
        <!-- Reference Answer (composite) -->
        <div class="dlg-field" v-if="dialog.form.type === 'composite'">
          <div class="field-head">
            <span class="field-title">参考答案</span>
            <span class="field-req">*必填</span>
          </div>
          <el-input v-model="dialog.form.answer" type="textarea" :rows="3" placeholder="输入参考答案" resize="vertical" />
        </div>

        <!-- Collapsible: Explanation + Images -->
        <details class="dlg-field dlg-expand">
          <summary class="field-head expand-summary">
            <span class="field-title">解析与图片</span>
            <span class="field-hint">选填</span>
          </summary>
          <div class="expand-body">
            <el-input v-model="dialog.form.explanation" type="textarea" :rows="2" placeholder="题目解析（可选）" resize="vertical" style="margin-top:8px" />
            <div class="img-list">
              <el-upload action="/api/questions/upload-image" :show-file-list="false" :on-success="onUploadImage" accept="image/*">
                <div class="img-add"><el-icon size="18"><Plus /></el-icon></div>
              </el-upload>
              <div v-for="(img, idx) in dlgImages" :key="idx" class="img-thumb">
                <img :src="img" alt="" />
                <div class="img-del" @click.stop="dlgImages.splice(idx, 1)"><el-icon size="10"><Close /></el-icon></div>
              </div>
            </div>
          </div>
        </details>
      </div>

      <template #footer>
        <div class="dlg-footer">
          <span v-if="!canSave.ok" class="save-hint">{{ canSave.msg }}</span>
          <span v-else class="save-hint save-ok"><CircleCheck /> 可以保存</span>
          <div class="dlg-btns">
            <el-button @click="dialog.visible = false">取消</el-button>
            <el-button type="primary" :disabled="!canSave.ok" @click="saveQuestion" size="default">
              {{ dialog.isEdit ? '保存修改' : '创建题目' }}
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {
  Search, Plus, Edit, Delete, Document, Upload, View,
  Warning, FolderOpened, Download, Printer, Refresh, CircleCheck, Close
} from '@element-plus/icons-vue'

import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

// --------------- State ---------------
const subjects = ref([])
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)
const searchText = ref('')
const filter = reactive({ subject_id: null, type: null, difficulty: null })
const importBtnRef = ref(null)

// Dialog state
const dialogChapters = ref([])
const dlgOptions = ref([])
const dlgAnswers = ref([])
const dlgImages = ref([])
const dialog = reactive({
  visible: false,
  isEdit: false,
  editId: null,
  form: {
    subject_id: null,
    chapter_id: null,
    specialty: '',
    type: 'single',
    difficulty: 1,
    content: '',
    answer: '',
    explanation: '',
    reference: ''
  }
})

// --------------- Computed ---------------
const filteredItems = computed(() => {
  if (!searchText.value) return items.value
  const q = searchText.value.toLowerCase()
  return items.value.filter(i =>
    (i.content || '').toLowerCase().includes(q) ||
    (i.subject_name || '').toLowerCase().includes(q) ||
    (i.chapter_name || '').toLowerCase().includes(q)
  )
})

const typeStats = computed(() => {
  const counts = { single: 0, multi: 0, truefalse: 0, composite: 0, blank: 0 }
  items.value.forEach(q => { if (counts[q.type] !== undefined) counts[q.type]++ })
  return [
    { type: 'single', label: '单选题', count: counts.single, color: '#409eff' },
    { type: 'multi', label: '多选题', count: counts.multi, color: '#67c23a' },
    { type: 'truefalse', label: '判断题', count: counts.truefalse, color: '#e6a23c' },
    { type: 'composite', label: '综合题', count: counts.composite, color: '#f56c6c' }
  ]
})

const canSave = computed(() => {
  const f = dialog.form
  if (!f.subject_id) return { ok: false, msg: '请选择科目' }
  if (!f.content?.trim()) return { ok: false, msg: '请填写题目内容' }
  if (f.type !== 'composite') {
    const filled = dlgOptions.value.filter(o => o.text?.trim())
    if (filled.length < 2) return { ok: false, msg: '至少填写2个选项' }
    if (dlgAnswers.value.length === 0) return { ok: false, msg: '请选择正确答案' }
  } else {
    if (!f.answer?.trim()) return { ok: false, msg: '请填写参考答案' }
  }
  return { ok: true, msg: '' }
})

// --------------- Helpers ---------------
function typeLabel(t) {
  return { single: '单选', multi: '多选', truefalse: '判断', composite: '综合', blank: '填空' }[t] || t
}
function typeColor(t) {
  return { single: '#409eff', multi: '#67c23a', truefalse: '#e6a23c', composite: '#f56c6c', blank: '#909399' }[t] || '#909399'
}
function tagType(t) {
  return { single: '', multi: 'success', truefalse: 'warning', composite: 'danger', blank: 'info' }[t] || 'info'
}
function qImages(q) {
  try {
    const arr = typeof q.images === 'string' ? JSON.parse(q.images) : (q.images || [])
    return Array.isArray(arr) ? arr : []
  } catch { return [] }
}

const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

function toggleAnswer(label, checked) {
  if (dialog.form.type === 'single') {
    dlgAnswers.value = checked ? [label] : []
  } else {
    if (checked) {
      if (!dlgAnswers.value.includes(label)) dlgAnswers.value.push(label)
    } else {
      dlgAnswers.value = dlgAnswers.value.filter(a => a !== label)
    }
  }
}

function addDlgOption() {
  const idx = dlgOptions.value.length
  if (idx >= LETTERS.length) return
  dlgOptions.value.push({ label: LETTERS[idx], text: '' })
}

function removeDlgOption(idx) {
  const removed = dlgOptions.value[idx].label
  dlgOptions.value.splice(idx, 1)
  dlgOptions.value.forEach((o, i) => { o.label = LETTERS[i] })
  dlgAnswers.value = dlgAnswers.value.filter(a => a !== removed)
}

function initDlgFromForm() {
  dlgImages.value = []
  dlgAnswers.value = []
  dlgOptions.value = []
  dialogChapters.value = []

  if (dialog.form.type === 'truefalse') {
    dlgOptions.value = [
      { label: 'A', text: '正确' },
      { label: 'B', text: '错误' }
    ]
  } else if (dialog.form.type !== 'composite') {
    if (dialog.isEdit && dialog.form._rawOptions?.length) {
      dlgOptions.value = JSON.parse(JSON.stringify(dialog.form._rawOptions))
    } else {
      dlgOptions.value = [
        { label: 'A', text: '' },
        { label: 'B', text: '' },
        { label: 'C', text: '' },
        { label: 'D', text: '' }
      ]
    }
  }

  if (dialog.isEdit && dialog.form._rawImages?.length) {
    dlgImages.value = [...dialog.form._rawImages]
  }

  if (dialog.form.answer && dialog.form.type !== 'composite') {
    try {
      const parsed = typeof dialog.form.answer === 'string'
        ? JSON.parse(dialog.form.answer)
        : dialog.form.answer
      dlgAnswers.value = Array.isArray(parsed) ? parsed : [String(parsed)]
    } catch {
      dlgAnswers.value = dialog.form.answer ? [dialog.form.answer] : []
    }
  }

  if (dialog.form.subject_id) {
    api.get(`/subjects/${dialog.form.subject_id}/chapters`).then(({ data }) => {
      dialogChapters.value = data
    })
  }
}

// --------------- API ---------------
async function fetchSubjects() {
  try { const { data } = await api.get('/subjects'); subjects.value = data } catch {}
}

async function fetchQuestions() {
  loading.value = true
  const params = { page: page.value, page_size: pageSize }
  if (filter.subject_id) params.subject_id = filter.subject_id
  if (filter.type) params.type = filter.type
  if (filter.difficulty) params.difficulty = filter.difficulty
  try {
    const { data } = await api.get('/questions', { params })
    items.value = data.items || []
    total.value = data.total || 0
  } catch { items.value = []; total.value = 0 }
  loading.value = false
}

function onSearch() { page.value = 1; fetchQuestions() }
function resetFilters() {
  searchText.value = ''
  filter.subject_id = null
  filter.type = null
  filter.difficulty = null
  onSearch()
}

function onDlgSubjectChange(sid) {
  dialog.form.chapter_id = null
  dialogChapters.value = []
  if (sid) {
    api.get(`/subjects/${sid}/chapters`).then(({ data }) => { dialogChapters.value = data })
  }
}

function onDlgTypeChange() {
  dlgAnswers.value = []
  if (dialog.form.type === 'truefalse') {
    dlgOptions.value = [
      { label: 'A', text: '正确' },
      { label: 'B', text: '错误' }
    ]
  } else if (dialog.form.type !== 'composite' && dlgOptions.value.length < 2) {
    dlgOptions.value = [
      { label: 'A', text: '' },
      { label: 'B', text: '' },
      { label: 'C', text: '' },
      { label: 'D', text: '' }
    ]
  }
}

async function onUploadImage({ file }) {
  const fd = new FormData()
  fd.append('file', file)
  try {
    const { data } = await api.post('/questions/upload-image', fd)
    dlgImages.value.push(data.url)
    ElMessage.success('图片上传成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  }
}

function openDialog(row) {
  if (row) {
    dialog.isEdit = true
    dialog.editId = row.id
    let rawOpts = [], rawImgs = []
    try { rawOpts = typeof row.options === 'string' ? JSON.parse(row.options) : row.options || [] } catch {}
    try { rawImgs = typeof row.images === 'string' ? JSON.parse(row.images) : row.images || [] } catch {}
    dialog.form = {
      subject_id: row.subject_id,
      chapter_id: row.chapter_id,
      specialty: row.specialty || '',
      type: row.type,
      difficulty: row.difficulty || 1,
      content: row.content || '',
      answer: row.answer || '',
      explanation: row.explanation || '',
      reference: row.reference || '',
      _rawOptions: rawOpts,
      _rawImages: rawImgs
    }
  } else {
    dialog.isEdit = false
    dialog.editId = null
    dialog.form = {
      subject_id: null, chapter_id: null, specialty: '',
      type: 'single', difficulty: 1, content: '',
      answer: '', explanation: '', reference: ''
    }
  }
  initDlgFromForm()
  dialog.visible = true
}

async function saveQuestion() {
  let optionsJson = '[]'
  if (dialog.form.type !== 'composite') {
    optionsJson = JSON.stringify(dlgOptions.value)
  }
  let answerVal = ''
  if (dialog.form.type === 'composite') {
    answerVal = dialog.form.answer
  } else {
    answerVal = JSON.stringify([...dlgAnswers.value].sort())
  }
  const payload = {
    subject_id: dialog.form.subject_id,
    chapter_id: dialog.form.chapter_id || null,
    specialty: dialog.form.specialty || '',
    type: dialog.form.type,
    difficulty: dialog.form.difficulty,
    content: dialog.form.content,
    options: optionsJson,
    answer: answerVal,
    explanation: dialog.form.explanation || '',
    reference: dialog.form.reference || '',
    images: JSON.stringify(dlgImages.value)
  }
  try {
    if (dialog.isEdit) await api.put(`/questions/${dialog.editId}`, payload)
    else await api.post('/questions', payload)
    dialog.visible = false
    ElMessage.success(dialog.isEdit ? '修改成功' : '创建成功')
    fetchQuestions()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  }
}

async function delQuestion(id) {
  try {
    await ElMessageBox.confirm('确定删除该题目？删除后无法恢复。', '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
  } catch { return }
  try {
    await api.delete(`/questions/${id}`)
    ElMessage.success('已删除')
    fetchQuestions()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

async function exportExcel() {
  try {
    const res = await api.get('/questions/export-excel', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'questions_export.xlsx'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch { ElMessage.error('导出失败') }
}

async function downloadTemplate() {
  try {
    const res = await api.get('/questions/export-template', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'question_import_template.xlsx'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch { ElMessage.error('模板下载失败') }
}

function handleImportCmd(cmd) {
  if (cmd === 'template') downloadTemplate()
  else if (cmd === 'export') exportExcel()
  else if (cmd === 'import') importBtnRef.value?.click()
}

async function uploadExcel(e) {
  const file = e.target?.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const { data } = await api.post('/questions/batch-import-excel', fd)
    ElMessage.success(`导入成功: ${data.count || 0} 条`)
    fetchQuestions()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '导入失败')
  }
  e.target.value = ''
}

// --------------- Init ---------------
onMounted(() => {
  fetchSubjects()
  fetchQuestions()
})
</script>

<style scoped>
.questions-page {
  padding: 0;
}

/* ---- Page Header ---- */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 16px;
  flex-wrap: wrap;
}
.ph-info {
  display: flex;
  align-items: center;
  gap: 14px;
}
.ph-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #818cf8);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}
.ph-sub {
  margin: 3px 0 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.ph-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* ---- Type Stats ---- */
.type-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.ts-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--el-fill-color-blank);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  font-size: 13px;
}
.ts-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.ts-label {
  color: var(--el-text-color-secondary);
}
.ts-count {
  font-weight: 700;
  color: var(--el-text-color-primary);
  font-size: 15px;
}

/* ---- Filter Bar ---- */
.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
  padding: 14px 16px;
  background: var(--el-fill-color-blank);
  border-radius: 10px;
  border: 1px solid var(--el-border-color-lighter);
}
.fb-search {
  flex: 1;
  min-width: 200px;
  max-width: 320px;
}
.fb-sel {
  width: 140px;
}
.fb-sel-sm {
  width: 110px;
}
.reset-btn {
  color: var(--el-text-color-secondary);
}
.reset-btn:hover {
  color: var(--el-color-primary);
}

/* ---- State Box ---- */
.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 20px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

/* ---- Card Grid ---- */
.q-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.q-card {
  background: var(--el-bg-color);
  border-radius: 12px;
  border: 1px solid var(--el-border-color-lighter);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  position: relative;
}
.q-card:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}
[data-theme="dark"] .q-card:hover,
html.dark .q-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

/* Type accent bar */
.q-accent {
  width: 4px;
  flex-shrink: 0;
  border-radius: 4px 0 0 4px;
}
.q-card-inner {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* Card Top */
.q-top {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px 0;
}
.q-type-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}
.q-stars {
  font-size: 12px;
  letter-spacing: 1px;
  line-height: 1;
}
.star-on {
  color: #f59e0b;
}
.star-off {
  color: var(--el-border-color);
}
.q-id {
  margin-left: auto;
  font-size: 11px;
  color: var(--el-text-color-placeholder);
  font-family: 'SF Mono', Consolas, monospace;
}

/* Card Body */
.q-body {
  padding: 8px 14px;
  flex: 1;
}
.q-content {
  font-size: 13px;
  color: var(--el-text-color-primary);
  line-height: 1.7;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.q-img-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

/* Card Meta */
.q-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  padding: 0 14px 8px;
}
.qm-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--el-fill-color-light);
  color: var(--el-text-color-secondary);
}
.qm-subject {
  font-weight: 600;
}
.qm-chapter {
  background: var(--el-fill-color);
}

/* Card Footer */
.q-foot {
  display: flex;
  align-items: center;
  padding: 6px 10px;
  border-top: 1px solid var(--el-border-color-extra-light);
  background: var(--el-fill-color-extra-light);
  gap: 4px;
}

/* ---- Pagination ---- */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-bottom: 8px;
}

/* ---- Dialog ---- */
.q-dialog .el-dialog__body {
  padding: 0;
}
.q-dialog .el-dialog__header {
  padding: 16px 20px 12px;
  margin: 0;
  border-bottom: 1px solid var(--el-border-color-extra-light);
}
.q-dialog .el-dialog__title {
  font-size: 16px;
  font-weight: 700;
}
.dlg-body {
  padding: 14px 20px 4px;
  max-height: 72vh;
  overflow-y: auto;
}

/* Type bar */
.dlg-type-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
.dlg-type-group {
  display: flex;
  gap: 6px;
}
.type-seg {
  padding: 5px 14px;
  border: 2px solid var(--el-border-color);
  border-radius: 20px;
  background: var(--el-fill-color-blank);
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  cursor: pointer;
  transition: all 0.15s;
}
.type-seg:hover:not(.active) {
  border-color: var(--el-color-primary-light-3);
  color: var(--el-color-primary);
}
.type-seg.active {
  color: #fff;
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
.dlg-diff {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
.diff-label {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}
.dlg-diff .el-rate {
  --el-rate-icon-size: 16px;
}

/* Meta row */
.dlg-meta-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

/* Field blocks */
.dlg-field {
  margin-bottom: 14px;
}
.field-head {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}
.field-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.field-req {
  font-size: 11px;
  color: var(--el-color-danger);
}
.field-hint {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
  background: var(--el-fill-color-light);
  padding: 1px 6px;
  border-radius: 4px;
}

/* Option cards */
.opt-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.opt-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1.5px solid var(--el-border-color-lighter);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  background: var(--el-fill-color-blank);
}
.opt-card:hover {
  border-color: var(--el-color-primary-light-5);
  background: var(--el-fill-color-extra-light);
}
.opt-card-active {
  border-color: var(--el-color-success) !important;
  background: var(--el-color-success-light-9) !important;
  box-shadow: 0 0 0 1px var(--el-color-success-light-5);
}
.opt-card-chk {
  display: none;
}
.opt-card-letter {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--el-fill-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: var(--el-text-color-secondary);
  flex-shrink: 0;
  transition: all 0.15s;
}
.letter-on {
  background: var(--el-color-primary);
  color: #fff;
}
.opt-card-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--el-text-color-primary);
  outline: none;
  padding: 0;
}
.opt-card-input::placeholder {
  color: var(--el-text-color-placeholder);
}
.opt-card-del {
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--el-text-color-placeholder);
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
  line-height: 1;
}
.opt-card-del:hover {
  background: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
}
.opt-add-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  padding: 4px 10px;
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  background: transparent;
  color: var(--el-color-primary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.opt-add-btn:hover {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

/* Expandable section */
.dlg-expand {
  border: none;
  padding: 0;
  margin-bottom: 10px;
}
.expand-summary {
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  background: var(--el-fill-color-light);
  transition: background 0.15s;
  list-style: none;
}
.expand-summary::-webkit-details-marker { display: none; }
.expand-summary::marker { content: ''; }
.expand-summary:hover {
  background: var(--el-fill-color);
}
.expand-body {
  padding: 8px 0 0;
}

/* Image upload */
.img-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: flex-start;
  margin-top: 8px;
}
.img-add {
  width: 60px;
  height: 60px;
  border: 2px dashed var(--el-border-color);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-placeholder);
  cursor: pointer;
  transition: all 0.2s;
}
.img-add:hover {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
}
.img-thumb {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}
.img-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.img-del {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.img-del:hover {
  background: var(--el-color-danger);
}

/* Footer */
.dlg-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  border-top: 1px solid var(--el-border-color-extra-light);
}
.save-hint {
  font-size: 12px;
  color: var(--el-color-danger);
  display: flex;
  align-items: center;
  gap: 4px;
}
.save-ok {
  color: var(--el-color-success);
}
.dlg-btns {
  display: flex;
  gap: 8px;
}

/* ---- Mobile ---- */
@media (max-width: 768px) {
  .q-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .type-stats {
    gap: 8px;
  }
  .ts-item {
    padding: 4px 10px;
    font-size: 12px;
  }
  .ts-count {
    font-size: 13px;
  }
  .filter-bar {
    padding: 10px 12px;
    gap: 8px;
  }
  .fb-search {
    min-width: 100%;
    max-width: 100%;
  }
  .fb-sel, .fb-sel-sm {
    flex: 1;
    min-width: 0;
  }
  .q-dialog {
    --el-dialog-width: 95vw !important;
    margin: 0 auto !important;
  }
  .dlg-body {
    padding: 10px 14px 2px;
    max-height: 68vh;
  }
  .dlg-type-bar {
    flex-wrap: wrap;
  }
  .dlg-type-group {
    width: 100%;
    justify-content: center;
  }
  .type-seg {
    flex: 1;
    text-align: center;
    padding: 6px 0;
    font-size: 14px;
  }
  .dlg-meta-row {
    flex-direction: column;
    gap: 6px;
  }
  .opt-card {
    padding: 6px 10px;
  }
  .opt-card-letter {
    width: 24px;
    height: 24px;
    font-size: 12px;
  }
  .dlg-footer {
    flex-direction: column-reverse;
    gap: 8px;
    padding: 8px 14px;
  }
  .dlg-btns {
    width: 100%;
  }
  .dlg-btns .el-button {
    flex: 1;
  }
  .save-hint {
    text-align: center;
    justify-content: center;
  }
}
</style>
