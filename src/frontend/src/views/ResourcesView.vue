<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:#e0f2fe;color:#06b6d4"><el-icon size="22"><FolderOpened /></el-icon></div>
        <div><h2>{{ isManage ? '资料管理' : '学习资料' }}</h2><p class="ph-sub">文档资料按科目分类管理</p></div>
      </div>
      <el-button v-if="isManage" type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> 上传资料</el-button>
    </div>

    <div class="filter-bar">
      <el-input v-model="searchText" placeholder="搜索资料..." clearable class="fb-search">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filter.subject_id" placeholder="科目" clearable @change="load" style="width:130px">
        <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-select v-model="filter.file_type" placeholder="文件类型" clearable @change="load" style="width:110px">
        <el-option label="PDF" value="pdf" />
        <el-option label="Word" value="docx" />
        <el-option label="Excel" value="xlsx" />
        <el-option label="PPT" value="pptx" />
        <el-option label="图片" value="image" />
        <el-option label="压缩包" value="zip" />
      </el-select>
    </div>

    <div v-if="!filteredItems.length" class="empty-wrap"><el-empty description="暂无资料" /></div>

    <div v-else class="res-grid">
      <div v-for="r in filteredItems" :key="r.id" class="res-card" @click="openView(r)">
        <div class="rc-thumb" v-if="isImage(r.file_type)">
          <img :src="r.file_url" :alt="r.title" @error="$event.target.style.display='none'" />
        </div>
        <div class="rc-icon" v-else :style="{background: fileColor(r.file_type)}">{{ fileIcon(r.file_type) }}</div>
        <div class="rc-body">
          <div class="rc-title">{{ r.title }}</div>
          <div v-if="r.description" class="rc-desc">{{ r.description?.slice(0, 60) }}{{ r.description?.length > 60 ? '...' : '' }}</div>
          <div class="rc-meta">
            <span>{{ r.file_type?.toUpperCase() }}</span>
            <span>{{ formatSize(r.file_size) }}</span>
            <span>↓{{ r.download_count || 0 }}</span>
          </div>
        </div>
        <div v-if="isManage" class="rc-actions" @click.stop>
          <el-button size="small" text type="primary" @click="openDialog(r)"><el-icon><Edit /></el-icon></el-button>
          <el-button size="small" text type="danger" @click="del(r.id)"><el-icon><Delete /></el-icon></el-button>
        </div>
      </div>
    </div>

    <div v-if="total > 20" style="text-align:center;margin-top:20px">
      <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="total,prev,next" @current-change="load" size="small" />
    </div>

    <!-- PDF viewer -->
    <el-dialog v-model="viewVisible" title="" width="900px" top="3vh" :close-on-click-modal="true" destroy-on-close>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">{{ viewTitle }}</span>
          <el-button size="small" type="primary" @click="download(viewItem)">下载</el-button>
        </div>
      </template>
      <iframe v-if="viewVisible" :src="viewUrl" style="width:100%;height:70vh;border:none;border-radius:8px" />
    </el-dialog>

    <!-- PDF Preview Dialog -->
    <el-dialog v-model="pdfPreviewVisible" title="PDF预览" width="90%" top="3vh" :close-on-click-modal="false">
      <iframe v-if="pdfUrl" :src="pdfUrl" style="width:100%;height:75vh;border:none;border-radius:8px"></iframe>
    </el-dialog>

    <el-dialog v-model="dialog.visible" :title="dialog.isEdit ? '编辑资料' : '上传资料'" width="450px" top="5vh">
      <el-form :model="dialog.form" label-width="60px">
        <el-form-item v-if="!dialog.isEdit" label="选择文件" required>
          <div class="upload-drop-zone" :class="{active: selectedFile}" @click="$refs.fileInput.click()" @dragover.prevent @drop.prevent="onDropFile">
            <input ref="fileInput" type="file" @change="onFileChange" style="display:none" accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.webp,.zip,.rar,.txt" />
            <template v-if="!selectedFile">
              <el-icon size="32" color="#9ca3af"><Upload /></el-icon>
              <span class="drop-text">点击选择或拖拽文件到此处</span>
              <span class="drop-hint">支持 PDF、Word、Excel、PPT、图片、压缩包等</span>
            </template>
            <template v-else>
              <el-icon size="28" color="#4f6ef7"><Document /></el-icon>
              <span class="drop-text">{{ dialog.form.title }}</span>
              <span class="drop-hint">{{ formatSize(selectedFile.size) }} · 点击重新选择</span>
            </template>
          </div>
          <div v-if="uploadStatus && uploadStatus !== 'ok'" class="upload-error">{{ uploadStatus }}</div>
        </el-form-item>
        <el-form-item label="标题"><el-input v-model="dialog.form.title" placeholder="自动取文件名" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="dialog.form.description" type="textarea" :rows="2" placeholder="可选" /></el-form-item>
        <el-form-item label="科目">
          <el-select v-model="dialog.form.subject_id" clearable style="width:100%" placeholder="可选">
            <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible=false">取消</el-button>
        <el-button type="primary" @click="save" :loading="saving" :disabled="!dialog.isEdit && !selectedFile">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Edit, Delete, FolderOpened, Upload, Document } from '@element-plus/icons-vue'

import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const auth = useAuthStore(); const route = useRoute(); const isManage = computed(() => route.path === '/resources-manage')
const subjects = ref([])
const items = ref([])
const total = ref(0)
const page = ref(1)
const searchText = ref('')
const filter = reactive({ subject_id: null, file_type: '' })
const dialog = reactive({ visible: false, isEdit: false, editId: null, form: { title:'', description:'', subject_id:null, file_url:'', file_type:'', file_size:0 } }); const fileInput = ref(null); const selectedFile = ref(null); const uploadStatus = ref(''); const saving = ref(false)
const viewVisible = ref(false); const viewItem = ref(null); const viewTitle = ref(""); const viewUrl = ref("")
const pdfPreviewVisible = ref(false); const pdfUrl = ref("")

function openView(item) {
  if (item.file_type === 'pdf') {
    viewItem.value = item; viewTitle.value = item.title; viewUrl.value = item.file_url; viewVisible.value = true
  } else {
    download(item)
  }
}

const filteredItems = computed(() => {
  if (!searchText.value) return items.value
  const q = searchText.value.toLowerCase()
  return items.value.filter(r => (r.title||'').toLowerCase().includes(q) || (r.description||'').toLowerCase().includes(q))
})

onMounted(async () => {
  const { data } = await api.get('/subjects'); subjects.value = data; load()
})

async function load() {
  const params = { page: page.value, page_size: 20 }
  if (filter.subject_id) params.subject_id = filter.subject_id
  if (filter.file_type) params.file_type = filter.file_type
  const url = isManage.value ? '/resources/manage' : '/resources'
  const { data } = await api.get(url, { params })
  items.value = data.items || []; total.value = data.total || 0
}

async function download(row) {
  const { data } = await api.post(`/resources/${row.id}/download`)
  window.open(data.file_url); load()
}

function isImage(type) { return ['image', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(type?.toLowerCase()) }

function openDialog(row) {
  selectedFile.value = null; uploadStatus.value = ''
  if (row) {
    dialog.isEdit = true; dialog.editId = row.id; dialog.form = { ...row }
  } else {
    dialog.isEdit = false; dialog.editId = null
    dialog.form = { title:'', description:'', subject_id:null, file_url:'', file_type:'', file_size:0 }
  }
  dialog.visible = true
}

function onDropFile(e) {
  const f = e.dataTransfer.files[0]
  if (!f) return
  selectedFile.value = f
  if (!dialog.form.title) dialog.form.title = f.name.replace(/\.[^.]+$/, '')
  dialog.form.file_type = f.name.split('.').pop() || ''
  dialog.form.file_size = f.size
  uploadStatus.value = 'ok'
}
function onFileChange(e) {
  const f = e.target.files[0]
  if (!f) { selectedFile.value = null; uploadStatus.value = ''; return }
  selectedFile.value = f
  const dot = f.name.lastIndexOf('.')
  const name = dot > 0 ? f.name.substring(0, dot) : f.name
  if (!dialog.form.title) dialog.form.title = name
  uploadStatus.value = 'ok'
}

async function save() {
  saving.value = true
  try {
    if (dialog.isEdit) {
      await api.put(`/resources/${dialog.editId}`, dialog.form)
    } else {
      const fd = new FormData()
      if (selectedFile.value) fd.append('file', selectedFile.value)
      fd.append('title', dialog.form.title || '')
      if (dialog.form.description) fd.append('description', dialog.form.description)
      if (dialog.form.subject_id) fd.append('subject_id', String(dialog.form.subject_id))
      await api.post('/resources/upload', fd)
    }
    dialog.visible = false; ElMessage.success('保存成功'); load()
  } catch (e) {
    uploadStatus.value = e.response?.data?.detail || '上传失败'
  } finally {
    saving.value = false
  }
}

async function del(id) {
  await ElMessageBox.confirm('确定删除？', '警告', { type: 'warning' })
  await api.delete(`/resources/${id}`); load()
}

function formatSize(b) { if(!b) return '-'; if(b<1024) return b+'B'; if(b<1048576) return (b/1024).toFixed(1)+'KB'; return (b/1048576).toFixed(1)+'MB' }
function fileColor(t) { const m={pdf:'#ef4444',docx:'#3b82f6',xlsx:'#22c55e',pptx:'#f59e0b',image:'#8b5cf6',zip:'#6b7280'}; return m[t?.toLowerCase()]||'#6b7280' }
function fileIcon(t) { return t?.toUpperCase()?.slice(0,4) || 'FILE' }
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-4); gap: var(--space-3); flex-wrap: wrap; }
.ph-left { display: flex; align-items: center; gap: var(--space-3); }
.ph-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }

.filter-bar { display: flex; gap: var(--space-2); margin-bottom: var(--space-4); align-items: center; flex-wrap: wrap; }
.fb-search { max-width: 280px; flex: 1; min-width: 150px; }

.empty-wrap { padding: 60px 0; }

.res-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--space-3); }
.res-card {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-3);
  box-shadow: var(--shadow-xs); border: 1px solid var(--gray-100);
  transition: all 0.2s; display: flex; gap: var(--space-3); align-items: center; cursor: pointer;
}
.res-card:hover { box-shadow: var(--shadow-sm); transform: translateY(-1px); }
.rc-thumb { width: 56px; height: 56px; border-radius: var(--radius-md); overflow: hidden; flex-shrink: 0; background: var(--gray-50); }
.rc-thumb img { width: 100%; height: 100%; object-fit: cover; }
.rc-icon {
  width: 48px; height: 48px; border-radius: var(--radius-md); display: flex;
  align-items: center; justify-content: center; color: #fff; font-weight: 700; font-size: 11px; flex-shrink: 0;
}
.rc-body { flex: 1; min-width: 0; }
.rc-title { font-size: 14px; font-weight: 600; color: var(--gray-900); }
.rc-desc { font-size: 12px; color: var(--gray-500); margin: 2px 0; }
.rc-meta { display: flex; gap: var(--space-3); font-size: 11px; color: var(--gray-400); }
.rc-actions { display: flex; gap: 2px; flex-shrink: 0; }

@media (max-width: 768px) {
  .filter-bar { flex-direction: column; }
  .fb-search { max-width: 100%; }
  .res-grid { grid-template-columns: 1fr; }
}

/* Upload drop zone */
.upload-drop-zone {
  width: 100%; min-height: 100px; border: 2px dashed var(--el-border-color);
  border-radius: 12px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 6px;
  cursor: pointer; transition: all 0.2s; background: var(--el-fill-color-blank);
}
.upload-drop-zone:hover, .upload-drop-zone.active {
  border-color: var(--el-color-primary); background: rgba(79,110,247,0.04);
}
.upload-drop-zone .drop-text { font-size: 14px; color: var(--el-text-color-regular); font-weight: 500; }
.upload-drop-zone .drop-hint { font-size: 12px; color: var(--el-text-color-placeholder); }
.upload-error { font-size: 12px; color: var(--el-color-danger); margin-top: 4px; }
</style>
