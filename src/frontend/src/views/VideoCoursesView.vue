<template>
  <div class="page-container">
    <div class="page-header vp-header">
      <div class="vp-left">
        <div class="ph-icon" style="background:#ede9fe;color:#7c3aed"><el-icon size="22"><VideoCamera /></el-icon></div>
        <div><h2>{{ isManage ? '视频管理' : '视频课程' }}</h2><p class="ph-sub">{{ isManage ? '管理平台所有视频资源' : '按科目分类播放视频课程' }}</p></div>
      </div>
      <el-button v-if="isManage" type="primary" @click="openDialog()" class="vp-btn"><el-icon><Plus /></el-icon> 上传视频</el-button>
    </div>

    <div class="toolbar">
      <el-input v-model="searchText" placeholder="搜索课程..." clearable class="vp-search">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <div v-if="!filteredItems.length" class="empty-state"><el-empty description="暂无课程" /></div>

    <!-- PC端卡片布局 -->
    <div v-else class="video-grid">
      <div v-for="v in filteredItems" :key="v.id" class="video-card">
        <div class="vc-cover" @click="viewVideo(v)">
          <div class="vc-play">▶</div>
          <span class="vc-duration">{{ formatDuration(v.duration_seconds) }}</span>
        </div>
        <div class="vc-body">
          <div class="vc-title">{{ v.title }}</div>
          <div class="vc-desc" v-if="v.description">{{ v.description?.slice(0,80) }}</div>
          <div class="vc-actions">
            <el-button size="small" type="primary" @click="viewVideo(v)">播放</el-button>
            <template v-if="isManage">
              <el-button size="small" @click="openDialog(v)">编辑</el-button>
              <el-button size="small" type="danger" @click="del(v.id)">删除</el-button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- 移动端列表布局 -->
    <div v-if="filteredItems.length" class="video-mobile-list">
      <div v-for="v in filteredItems" :key="'m-'+v.id" class="video-m-card" @click="viewVideo(v)">
        <div class="vm-cover"><div class="vm-play">▶</div><span class="vm-dur">{{ formatDuration(v.duration_seconds) }}</span></div>
        <div class="vm-info"><div class="vm-title">{{ v.title }}</div><div class="vm-meta" v-if="v.description">{{ v.description?.slice(0,50) }}</div></div>
        <div class="vm-actions" v-if="isManage"><el-icon @click.stop="openDialog(v)" class="vm-icon"><EditPen /></el-icon><el-icon @click.stop="del(v.id)" class="vm-icon vm-del"><Delete /></el-icon></div>
      </div>
    </div>

    <!-- Video Player Dialog -->
    <el-dialog v-model="videoPlayerVisible" :title="currentVideo?.title || '视频播放'" width="80%" top="3vh" :close-on-click-modal="false" destroy-on-close>
      <video v-if="currentVideo" :src="currentVideo.video_url" controls autoplay
        style="width:100%;max-height:70vh;border-radius:8px;background:#000"
        @timeupdate="onVideoTimeUpdate" @loadedmetadata="onVideoLoaded"></video>
    </el-dialog>

    <el-dialog v-model="dialog.visible" :title="dialog.isEdit ? '编辑视频' : '上传视频'" width="450">
      <el-form :model="dialog.form" label-width="60px">
        <el-form-item v-if="!dialog.isEdit" label="选择文件" required>
          <div class="upload-drop-zone" :class="{active: selectedFile}" @click="$refs.fileInput.click()" @dragover.prevent @drop.prevent="onDropFile">
            <input ref="fileInput" type="file" @change="onFileChange" style="display:none" accept="video/*" />
            <template v-if="!selectedFile">
              <el-icon size="32" color="#9ca3af"><Upload /></el-icon>
              <span class="drop-text">点击选择或拖拽视频文件</span>
              <span class="drop-hint">支持 MP4、AVI、MOV 等常见格式</span>
            </template>
            <template v-else>
              <el-icon size="28" color="#4f6ef7"><VideoCamera /></el-icon>
              <span class="drop-text">{{ dialog.form.title }}</span>
              <span class="drop-hint">点击重新选择</span>
            </template>
          </div>
          <div v-if="uploadStatus && uploadStatus !== 'ok'" class="upload-error">{{ uploadStatus }}</div>
        </el-form-item>
        <el-form-item label="或URL"><el-input v-model="dialog.form.video_url" placeholder="直接粘贴视频链接" /></el-form-item>
        <el-form-item label="标题"><el-input v-model="dialog.form.title" placeholder="自动取文件名" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="dialog.form.description" type="textarea" :rows="2" placeholder="可选" /></el-form-item>
        <el-form-item label="科目"><el-select v-model="dialog.form.subject_id" clearable style="width:100%" placeholder="可选"><el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog.visible=false">取消</el-button><el-button type="primary" @click="save" :loading="saving" :disabled="!dialog.isEdit && !selectedFile && !dialog.form.video_url">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, VideoCamera, Upload, EditPen, Delete } from '@element-plus/icons-vue'

import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const auth = useAuthStore(); const route = useRoute(); const isManage = computed(() => route.path === '/videos-manage')
const items = ref([]); const subjects = ref([]); const searchText = ref('')
const videoPlayerVisible = ref(false); const currentVideo = ref(null)
const dialog = reactive({ visible: false, isEdit: false, editId: null, form: { title:'', description:'', video_url:'', cover_url:'', duration_seconds:0, subject_id:null } }); const fileInput = ref(null); const selectedFile = ref(null); const uploadStatus = ref(''); const saving = ref(false)

const filteredItems = computed(() => {
  if (!searchText.value) return items.value
  const q = searchText.value.toLowerCase()
  return items.value.filter(v => (v.title||'').toLowerCase().includes(q))
})

onMounted(async () => {
  const [v, s] = await Promise.all([api.get('/videos'), api.get('/subjects')])
  items.value = v.data.items || []; subjects.value = s.data
})

function viewVideo(v) { currentVideo.value = v; videoPlayerVisible.value = true }
function onVideoTimeUpdate(e) { if (currentVideo.value) localStorage.setItem('video_' + currentVideo.value.id, Math.floor(e.target.currentTime)) }
function onVideoLoaded(e) { const saved = localStorage.getItem('video_' + (currentVideo.value?.id || 0)); if (saved) e.target.currentTime = parseInt(saved) }

function openDialog(row) {
  if (row) { dialog.isEdit=true; dialog.editId=row.id; dialog.form={ ...row } }
  else { dialog.isEdit=false; dialog.editId=null; dialog.form={ title:'', description:'', video_url:'', cover_url:'', duration_seconds:0, subject_id:null } }
  dialog.visible = true
}
function formatSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0; let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return size.toFixed(i > 0 ? 1 : 0) + ' ' + units[i]
}
function onDropFile(e) {
  const f = e.dataTransfer.files[0]
  if (!f) return
  selectedFile.value = f
  if (!dialog.form.title) dialog.form.title = f.name.replace(/\.[^.]+$/, '')
  dialog.form.duration_seconds = 0
  uploadStatus.value = 'ok'
}
function onFileChange(e) {
  const f = e.target.files[0]
  if (!f) { selectedFile.value = null; uploadStatus.value = ''; return }
  selectedFile.value = f
  const dot = f.name.lastIndexOf('.'); const name = dot > 0 ? f.name.substring(0, dot) : f.name
  if (!dialog.form.title) dialog.form.title = name
  uploadStatus.value = 'ok'
}
async function save() {
  saving.value = true
  try {
    if (dialog.isEdit) {
      await api.put(`/videos/${dialog.editId}`, dialog.form)
    } else if (selectedFile.value) {
      const fd = new FormData(); fd.append('file', selectedFile.value)
      fd.append('title', dialog.form.title || '')
      if (dialog.form.subject_id) fd.append('subject_id', String(dialog.form.subject_id))
      await api.post('/videos/upload', fd)
    } else {
      await api.post('/videos', dialog.form)
    }
    dialog.visible = false; ElMessage.success('保存成功')
    const { data } = await api.get('/videos'); items.value = data.items || []
  } catch (e) {
    uploadStatus.value = e.response?.data?.detail || '上传失败'
  } finally { saving.value = false }
}
async function del(id) { await ElMessageBox.confirm('确定删除？','警告',{type:'warning'}); await api.delete(`/videos/${id}`); items.value = items.value.filter(i => i.id !== id) }
function formatDuration(s) { if(!s)return''; const m=Math.floor(s/60); const sec=s%60; return m>0?`${m}:${String(sec).padStart(2,'0')}`:`0:${String(sec).padStart(2,'0')}` }
</script>

<style scoped>
.toolbar { margin-bottom: var(--space-4); }
.vp-search { max-width: 300px; }
.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--space-4); }
.video-card { background: var(--gray-25); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); overflow: hidden; transition: all var(--transition-fast); }
.video-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.vc-cover { height: 150px; background: linear-gradient(135deg, #1a1a2e, #16213e); display: flex; align-items: center; justify-content: center; cursor: pointer; position: relative; }
.vc-play { width: 48px; height: 48px; background: rgba(255,255,255,0.9); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; color: #1a1a2e; transition: transform var(--transition-fast); }
.vc-cover:hover .vc-play { transform: scale(1.1); }
.vc-duration { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.7); color: #fff; font-size: 11px; padding: 2px 6px; border-radius: 4px; }
.vc-body { padding: var(--space-3); }
.vc-title { font-size: var(--text-base); font-weight: var(--font-semibold); color: var(--gray-900); margin-bottom: 4px; }
.vc-desc { font-size: var(--text-xs); color: var(--gray-500); margin-bottom: var(--space-3); }
.vc-actions { display: flex; gap: 4px; }

/* Mobile */
.video-mobile-list { display: none; }
@media (max-width: 768px) {
  .video-grid { display: none !important; }
  .video-mobile-list { display: flex !important; flex-direction: column; gap: 10px; }
  .vp-header { flex-direction: column !important; align-items: stretch !important; gap: 12px; }
  .vp-left { flex-direction: row; align-items: center; gap: 10px; }
  .vp-btn { width: 100%; justify-content: center; flex-shrink: 0; }
  .vp-search { max-width: 100% !important; width: 100%; }
}
.video-m-card { display: flex; align-items: center; gap: 10px; background: var(--el-bg-color, #fff); border-radius: 10px; padding: 10px; border: 1px solid var(--el-border-color-lighter, #e4e7ed); cursor: pointer; transition: background 0.15s; }
.video-m-card:active { background: var(--el-fill-color-light, #f5f7fa); }
.vm-cover { width: 90px; height: 60px; border-radius: 8px; background: linear-gradient(135deg, #1a1a2e, #16213e); display: flex; align-items: center; justify-content: center; flex-shrink: 0; position: relative; overflow: hidden; }
.vm-play { width: 30px; height: 30px; background: rgba(255,255,255,0.9); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #1a1a2e; }
.vm-dur { position: absolute; bottom: 2px; right: 4px; background: rgba(0,0,0,0.7); color: #fff; font-size: 9px; padding: 1px 4px; border-radius: 3px; }
.vm-info { flex: 1; min-width: 0; }
.vm-title { font-size: 14px; font-weight: 600; color: var(--el-text-color-primary, #303133); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.vm-meta { font-size: 12px; color: var(--el-text-color-secondary, #909399); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.vm-actions { display: flex; gap: 8px; flex-shrink: 0; }
.vm-icon { font-size: 18px; cursor: pointer; color: var(--el-text-color-secondary, #909399); transition: color 0.15s; }
.vm-icon:hover { color: var(--el-color-primary, #4f6ef7); }
.vm-del:hover { color: var(--el-color-danger, #f56c6c); }

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
