<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:#e8f0fe;color:var(--color-primary)"><el-icon size="22"><Edit /></el-icon></div>
        <div><h2>笔记管理</h2><p class="ph-sub">{{ total }} 条笔记</p></div>
      </div>
      <el-button type="primary" @click="openCreateDialog"><el-icon><Plus /></el-icon>新建笔记</el-button>
    </div>

    <div class="filter-bar">
      <el-input v-model="keyword" placeholder="搜索笔记内容..." clearable @input="debounceSearch" class="fb-search">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <div v-if="!notes.length" class="empty-wrap">
      <el-empty description="暂无笔记">
        <p class="hint">练习时点击题目下方的"笔记"按钮即可添加</p>
        <el-button type="primary" @click="$router.push('/practice')">去练习</el-button>
      </el-empty>
    </div>

    <div v-else class="note-grid">
      <div v-for="n in notes" :key="n.id" class="note-card">
        <div class="nc-top">
          <div class="nc-badge" v-if="n.subject_name">
            <el-icon size="14"><Collection /></el-icon>
            <span>{{ n.subject_name }}</span>
          </div>
          <span v-if="n.question_id" class="nc-qid">题目 #{{ n.question_id }}</span>
          <span v-if="n.title" class="nc-title">{{ n.title }}</span>
          <span v-else-if="!n.question_id" class="nc-qid">独立笔记</span>
          <span class="nc-time">{{ n.updated_at?.slice(0, 16) }}</span>
        </div>
        <div class="nc-content">{{ n.content }}</div>
        <div class="nc-footer">
          <div></div>
          <div class="nc-actions">
            <el-button size="small" text type="primary" @click="editNote(n)"><el-icon><Edit /></el-icon>编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="deleteNote(n.id)">
              <template #reference>
                <el-button size="small" text type="danger"><el-icon><Delete /></el-icon>删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>

    <el-pagination v-if="total > pageSize" v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="loadNotes" style="justify-content:center;margin-top:20px" size="small" />

    <el-dialog v-model="editDialog.visible" :title="editDialog.isCreate ? '新建笔记' : '编辑笔记'" width="500">
      <el-form label-width="60px">
        <el-form-item v-if="!editDialog.question_id" label="标题">
          <el-input v-model="editDialog.title" placeholder="笔记标题（可选）" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="editDialog.content" type="textarea" :rows="8" placeholder="输入笔记内容..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialog.visible=false">取消</el-button>
        <el-button type="primary" @click="saveNote" :loading="saving">{{ editDialog.isCreate ? '创建' : '保存' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete, Search, Collection, Plus } from '@element-plus/icons-vue'

import { ref, onMounted } from 'vue'
import api from '../api'

const notes = ref([]); const page = ref(1); const pageSize = 50; const total = ref(0)
const keyword = ref(''); const saving = ref(false)
const editDialog = ref({ visible: false, id: null, title: '', content: '', question_id: null, isCreate: false })
let searchTimer = null
function renderMD(text) {
  if (!text) return ''
  var html = text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/### (.+)/g, '<h3>$1</h3>')
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/# (.+)/g, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
    .replace(/\*(.+?)\*/g, '<i>$1</i>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
  return html
}

onMounted(() => loadNotes())

async function loadNotes() {
  const params = { page: page.value, page_size: pageSize }
  if (keyword.value) params.keyword = keyword.value
  try { const { data } = await api.get('/notes', { params }); notes.value = data.items || []; total.value = data.total || 0 } catch {}
}
function debounceSearch() { clearTimeout(searchTimer); searchTimer = setTimeout(() => { page.value = 1; loadNotes() }, 300) }
function editNote(n) { editDialog.value = { visible: true, id: n.id, title: n.title || '', content: n.content, question_id: n.question_id, isCreate: false } }
function openCreateDialog() {
  editDialog.value = { visible: true, id: null, title: '', content: '', question_id: null, isCreate: true }
}
async function saveNote() {
  if (!editDialog.value.content.trim()) return
  saving.value = true
  try {
    if (editDialog.value.isCreate) {
      await api.post('/notes', { title: editDialog.value.title, content: editDialog.value.content })
      ElMessage.success('创建成功')
    } else {
      await api.put(`/notes/${editDialog.value.id}`, { content: editDialog.value.content, title: editDialog.value.title })
      ElMessage.success('已保存')
    }
    editDialog.value.visible = false; loadNotes()
  } catch { ElMessage.error('操作失败') }
  saving.value = false
}
async function deleteNote(id) {
  try { await api.delete(`/notes/${id}`); ElMessage.success('已删除'); loadNotes() } catch {}
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-4); gap: var(--space-3); flex-wrap: wrap; }
.ph-left { display: flex; align-items: center; gap: var(--space-3); }
.ph-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }

.filter-bar { margin-bottom: var(--space-4); }
.fb-search { max-width: 360px; }

.empty-wrap { padding: 60px 0; }
.hint { font-size: var(--text-sm); color: var(--gray-400); margin: 4px 0 16px; }

.note-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: var(--space-3); }
.note-card {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); border: 1px solid var(--gray-100);
  transition: all 0.2s; display: flex; flex-direction: column; gap: var(--space-3);
  border-left: 3px solid #4f6ef7;
}
.note-card:hover { box-shadow: var(--shadow-sm); }

.nc-top { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; }
.nc-badge { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--color-primary); background: var(--color-primary-light); padding: 2px 10px; border-radius: 99px; }
.nc-qid { font-size: 12px; color: var(--gray-400); }
.nc-title { font-size: 14px; font-weight: 600; color: var(--gray-800); }
.nc-time { font-size: 11px; color: var(--gray-400); margin-left: auto; }

.nc-content { font-size: 14px; line-height: 1.8; color: var(--gray-800); white-space: pre-wrap; flex: 1; }

.nc-footer { display: flex; justify-content: space-between; align-items: center; padding-top: var(--space-2); border-top: 1px solid var(--gray-50); }
.nc-actions { display: flex; gap: 4px; }

@media (max-width: 768px) {
  .fb-search { max-width: 100%; }
  .note-grid { grid-template-columns: 1fr; }
}
</style>
