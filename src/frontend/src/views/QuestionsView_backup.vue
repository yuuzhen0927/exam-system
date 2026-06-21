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
        @click="openDialog(q)"
      >
        <!-- Card Top: Type + Difficulty + ID -->
        <div class="q-top">
          <el-tag
            :type="tagType(q.type)"
            size="small"
            effect="dark"
            round
            disable-transitions
          >{{ typeLabel(q.type) }}</el-tag>
          <div class="q-stars" :title="'难度: ' + (q.difficulty || 1) + '/5'">
            <span
              v-for="s in 5"
              :key="s"
              :class="s <= (q.difficulty || 1) ? 'star-on' : 'star-off'"
            >★</span>
          </div>
          <span class="q-id">#{{ q.id }}</span>
        </div>

        <!-- Card Body: Content -->
        <div class="q-body">
          <p class="q-content">{{ q.content }}</p>
          <div v-if="qImages(q).length" class="q-img-hint">
            <el-icon size="14"><Picture /></el-icon>
            <span>{{ qImages(q).length }}张图片</span>
          </div>
        </div>

        <!-- Card Meta: Subject + Chapter -->
        <div class="q-meta">
          <el-tag v-if="q.subject_name" size="small" type="info" effect="plain" round>
            {{ q.subject_name }}
          </el-tag>
          <el-tag v-if="q.chapter_name" size="small" effect="plain" round class="ch-tag">
            {{ q.chapter_name }}
          </el-tag>
        </div>

        <!-- Card Footer: Actions -->
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

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination-wrap">
      <el-pagination
        v-model:current-page="page"
        :total="total"
        :page-size="pageSize"
        layout="total, prev, pager, next"
        @current-change="fetchQuestions"
        background
        small
      />
    </div>

    <!-- Create / Edit Dialog -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑题目' : '新建题目'"
      width="640px"
      top="3vh"
      :close-on-click-modal="false"
      destroy-on-close
      class="q-dialog"
    >
      <div class="dlg-cards">
        <div class="dlg-card">
          <div class="dlg-card-head"><span class="dlg-card-dot" style="background:#4f6ef7"></span>基本信息</div>
          <div class="dlg-card-body">
            <div class="dlg-row">
              <el-form-item label="科目" required class="dlg-col">
                <el-select v-model="dialog.form.subject_id" placeholder="选择科目" @change="onDlgSubjectChange" style="width:100%">
                  <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="章节" class="dlg-col">
                <el-select v-model="dialog.form.chapter_id" placeholder="选择章节" clearable style="width:100%">
                  <el-option v-for="c in dialogChapters" :key="c.id" :label="c.name" :value="c.id" />
                </el-select>
              </el-form-item>
            </div>
            <div class="dlg-row">
              <el-form-item label="题型" class="dlg-col dlg-type-col">
                <div class="type-segments">
                  <button v-for="t in [{l:'单选',v:'single'},{l:'多选',v:'multi'},{l:'判断',v:'truefalse'},{l:'综合',v:'composite'}]" :key="t.v" class="type-seg" :class="{active: dialog.form.type===t.v}" @click.prevent="dialog.form.type=t.v; onDlgTypeChange(t.v)">{{ t.l }}</button>
                </div>
              </el-form-item>
              <el-form-item label="难度" class="dlg-col">
                <el-rate v-model="dialog.form.difficulty" :max="5" />
              </el-form-item>
            </div>
          </div>
        </div>

        <div class="dlg-card">
          <div class="dlg-card-head"><span class="dlg-card-dot" style="background:#22c55e"></span>题目内容</div>
          <div class="dlg-card-body">
            <el-input v-model="dialog.form.content" type="textarea" :rows="3" placeholder="请输入题目内容（支持 $ 格式）" resize="vertical" />
          </div>
        </div>

        <div class="dlg-card" v-if="dialog.form.type !== 'composite'">
          <div class="dlg-card-head"><span class="dlg-card-dot" style="background:#f59e0b"></span>选项（勾选正确答案）</div>
          <div class="dlg-card-body">
            <div v-for="(opt, idx) in dlgOptions" :key="idx" class="opt-row">
              <el-checkbox :model-value="dlgAnswers.includes(opt.label)" @change="(v) => toggleAnswer(opt.label, v)" class="opt-chk" />
              <span class="opt-letter">{{ opt.label }}</span>
              <el-input v-model="opt.text" :placeholder="'选项 ' + opt.label" class="opt-input" />
              <el-button v-if="dlgOptions.length > 2 && dialog.form.type !== 'truefalse'" text type="danger" size="small" @click="removeDlgOption(idx)">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            <el-button v-if="dialog.form.type !== 'truefalse'" text type="primary" size="small" @click="addDlgOption" class="add-opt-btn">
              <el-icon><Plus /></el-icon> 添加选项
            </el-button>
          </div>
        </div>

        <div class="dlg-card" v-if="dialog.form.type === 'composite'">
          <div class="dlg-card-head"><span class="dlg-card-dot" style="background:#8b5cf6"></span>参考答案</div>
          <div class="dlg-card-body">
            <el-input v-model="dialog.form.answer" type="textarea" :rows="3" placeholder="请输入参考答案" resize="vertical" />
          </div>
        </div>

        <div class="dlg-card">
          <div class="dlg-card-head"><span class="dlg-card-dot" style="background:#06b6d4"></span>解析与图片</div>
          <div class="dlg-card-body">
            <el-input v-model="dialog.form.explanation" type="textarea" :rows="2" placeholder="可选，题目解析" resize="vertical" />
            <div class="img-list" style="margin-top:10px">
              <el-upload action="/api/questions/upload-image" :show-file-list="false" :on-success="onUploadImage" accept="image/*">
                <div class="img-add"><el-icon size="24"><Plus /></el-icon><span>上传图片</span></div>
              </el-upload>
              <div v-for="(img, idx) in dlgImages" :key="idx" class="img-thumb">
                <img :src="img" alt="" />
                <div class="img-del" @click.stop="dlgImages.splice(idx, 1)"><el-icon size="12"><Close /></el-icon></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dlg-footer">
          <span v-if="!canSave.ok" class="save-hint">{{ canSave.msg }}</span>
          <span v-else class="save-hint save-ok">可以保存</span>
          <div class="dlg-btns">
            <el-button @click="dialog.visible = false">取消</el-button>
            <el-button type="primary" :disabled="!canSave.ok" @click="saveQuestion">
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
  Warning, FolderOpened, Download, Printer, Refresh
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
  return { single: '单选', multi: '多选', truefalse: '判断', composite: '综合' }[t] || t
}
function tagType(t) {
  return { single: '', multi: 'success', truefalse: 'warning', composite: 'danger' }[t] || 'info'
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
  flex-direction: column;
}
.q-card:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.1);
  transform: translateY(-2px);
}

/* Card Top */
.q-top {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px 0;
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
  padding: 10px 16px;
  flex: 1;
}
.q-content {
  font-size: 14px;
  color: var(--el-text-color-primary);
  line-height: 1.65;
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
  padding: 0 16px 10px;
}
.ch-tag {
  --el-tag-bg-color: var(--el-fill-color-light);
  --el-tag-border-color: var(--el-border-color-lighter);
  --el-tag-text-color: var(--el-text-color-regular);
}

/* Card Footer */
.q-foot {
  display: flex;
  align-items: center;
  padding: 8px 10px;
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

/* ---- Type Segments ---- */
.type-segments { display: flex; gap: 0; border: 1px solid var(--el-border-color, #dcdfe6); border-radius: 8px; overflow: hidden; }
.type-seg { flex: 1; padding: 7px 0; border: none; background: var(--el-fill-color-blank, #fff); font-size: 13px; font-weight: 500; color: var(--el-text-color-regular, #606266); cursor: pointer; transition: all 0.15s; border-right: 1px solid var(--el-border-color, #dcdfe6); }
.type-seg:last-child { border-right: none; }
.type-seg.active { background: var(--el-color-primary, #409eff); color: #fff; }
.type-seg:hover:not(.active) { background: var(--el-fill-color-light, #f5f7fa); }
.dlg-type-col .el-form-item__content { flex-wrap: nowrap; }
/* ---- Dialog Cards ---- */
.dlg-cards { display: flex; flex-direction: column; gap: 12px; }
.dlg-card { background: var(--el-fill-color-blank, #fff); border: 1px solid var(--el-border-color-lighter, #e4e7ed); border-radius: 10px; overflow: hidden; }
.dlg-card-head { display: flex; align-items: center; gap: 8px; padding: 8px 14px; font-size: 13px; font-weight: 600; color: var(--el-text-color-primary, #303133); border-bottom: 1px solid var(--el-border-color-lighter, #e4e7ed); background: var(--el-fill-color-light, #f5f7fa); }
.dlg-card-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dlg-card-body { padding: 10px 14px; }

.q-dialog .el-dialog__body {
  padding: 16px 20px 0;
  max-height: 70vh;
  overflow-y: auto;
}
.q-dialog .el-form-item { margin-bottom: 8px; } /* .q-dialog .el-form-item {
  margin-bottom: 10px;
}
.q-dialog .el-form-item__label {
  font-size: 13px;
  font-weight: 500;
}
.dlg-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 20px;
}
.dlg-col {
  margin-bottom: 0;
}
/* ---- Dialog ---- */
.q-dialog .el-dialog__body {
  padding: 12px 20px 0;
  max-height: 70vh;
  overflow-y: auto;
}
.q-dialog .el-form-item { margin-bottom: 8px; } /* .q-dialog .el-form-item {
  margin-bottom: 12px;
}
.q-dialog .el-form-item__label {
  font-size: 13px;
  font-weight: 500;
}
.dlg-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 20px;
}
.dlg-col {
  margin-bottom: 0;
}

/* Options */
.opts-wrap {
  width: 100%;
}
.opt-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.opt-row .el-input {
  flex: 1;
}
.opt-chk {
  flex-shrink: 0;
}
.opt-letter {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--el-fill-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-regular);
  flex-shrink: 0;
}
.opt-input {
  flex: 1;
}
.add-opt-btn {
  margin-top: 2px;
}

/* Image upload */
.img-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: flex-start;
}
.img-add {
  width: 88px;
  height: 88px;
  border: 2px dashed var(--el-border-color);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-placeholder);
  cursor: pointer;
  transition: all 0.2s;
  gap: 4px;
  font-size: 12px;
}
.img-add:hover {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
}
.img-thumb {
  width: 88px;
  height: 88px;
  border-radius: 10px;
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
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}
.img-del:hover {
  background: var(--el-color-danger);
}

/* Dialog Footer */
.dlg-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.save-hint {
  font-size: 12px;
  color: var(--el-color-danger);
}
.save-ok {
  color: var(--el-color-success);
}
.dlg-btns {
  display: flex;
  gap: 8px;
}

/* ---- Mobile ---- */
/* Dialog scroll fix */
@media (max-height: 700px) {
  .q-dialog .el-dialog__body {
    max-height: 55vh;
  }
}

@media (max-width: 768px) {
  .q-dialog {
    --el-dialog-width: 95vw !important;
    margin: 0 auto !important;
  }
  .q-dialog .el-dialog__body {
    max-height: 65vh;
    padding: 8px 12px 0;
  }
  .page-header {
    flex-direction: column;
  }
  .ph-actions {
    width: 100%;
    justify-content: flex-end;
  }
  .filter-bar {
    flex-direction: column;
    gap: 8px;
    padding: 12px;
  }
  .fb-search,
  .fb-sel,
  .fb-sel-sm {
    max-width: 100%;
    width: 100%;
  }
  .q-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .dlg-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
  .btn-text {
    display: inline;
  }
}

@media (max-width: 480px) {
  .btn-text {
    display: none;
  }
  .ph-actions .el-button {
    padding: 8px 12px;
  }
}
</style>
