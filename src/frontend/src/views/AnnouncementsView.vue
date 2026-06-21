<template>
  <div class="page-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>公告管理</h2>
        <span class="header-count">共 {{ items.length }} 条</span>
      </div>
      <el-button type="primary" @click="openDialog()" :icon="Plus">新建公告</el-button>
    </div>

    <!-- Stats -->
    <div class="ann-stats" v-if="items.length">
      <div class="stat-card">
        <div class="stat-icon published">📢</div>
        <div class="stat-info"><span class="stat-num">{{ publishedCount }}</span><span class="stat-label">已发布</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon draft">📝</div>
        <div class="stat-info"><span class="stat-num">{{ draftCount }}</span><span class="stat-label">草稿</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon pinned">📌</div>
        <div class="stat-info"><span class="stat-num">{{ pinnedCount }}</span><span class="stat-label">置顶</span></div>
      </div>
    </div>

    <!-- Empty -->
    <div v-if="!items.length" class="empty-state">
      <div class="empty-icon">📢</div>
      <p>暂无公告</p>
      <el-button type="primary" @click="openDialog()">发布第一条公告</el-button>
    </div>

    <!-- Announcement List -->
    <div v-else class="ann-list">
      <div v-for="a in sortedItems" :key="a.id" class="ann-card" :class="{ pinned: a.is_pinned, draft: !a.is_published }">
        <div class="card-header">
          <div class="card-tags">
            <el-tag v-if="a.is_pinned" type="danger" size="small" effect="dark" class="pin-tag">📌 置顶</el-tag>
            <el-tag :type="a.is_published ? 'success' : 'info'" size="small" effect="plain">
              {{ a.is_published ? '已发布' : '草稿' }}
            </el-tag>
          </div>
          <div class="card-actions">
            <el-button text size="small" @click="openDialog(a)">编辑</el-button>
            <el-button text size="small" :type="a.is_published ? 'warning' : 'success'" @click="togglePublish(a)">
              {{ a.is_published ? '撤回' : '发布' }}
            </el-button>
            <el-button text size="small" type="danger" @click="del(a.id)">删除</el-button>
          </div>
        </div>
        <div class="card-title">{{ a.title }}</div>
        <div class="card-content">{{ a.content }}</div>
        <div class="card-footer">
          <span class="footer-item">👤 {{ a.created_by }}</span>
          <span class="footer-item">📅 {{ formatDate(a.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- Dialog -->
    <el-dialog v-model="dialog.visible" :title="dialog.isEdit ? '编辑公告' : '新建公告'" width="600px" :close-on-click-modal="false">
      <el-form :model="dialog.form" label-width="70px" label-position="top">
        <el-form-item label="公告标题">
          <el-input v-model="dialog.form.title" placeholder="请输入公告标题" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="公告内容">
          <el-input v-model="dialog.form.content" type="textarea" :rows="8" placeholder="请输入公告内容，支持多行文本" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="dialog.form.is_pinned">置顶公告</el-checkbox>
          <el-checkbox v-model="dialog.form.is_published">立即发布</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="save">{{ dialog.isEdit ? '保存修改' : '创建公告' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api'

const items = ref([])
const dialog = reactive({
  visible: false, isEdit: false, editId: null,
  form: { title: '', content: '', is_pinned: false, is_published: false }
})

const sortedItems = computed(() => {
  return [...items.value].sort((a, b) => {
    if (a.is_pinned !== b.is_pinned) return b.is_pinned ? 1 : -1
    return (b.id || 0) - (a.id || 0)
  })
})
const publishedCount = computed(() => items.value.filter(i => i.is_published).length)
const draftCount = computed(() => items.value.filter(i => !i.is_published).length)
const pinnedCount = computed(() => items.value.filter(i => i.is_pinned).length)

function formatDate(d) {
  if (!d) return ''
  return d.substring(0, 10)
}

onMounted(load)
async function load() {
  const { data } = await api.get('/announcements')
  items.value = data.items || []
}

function openDialog(row) {
  if (row) {
    dialog.isEdit = true; dialog.editId = row.id
    dialog.form = { title: row.title, content: row.content, is_pinned: row.is_pinned, is_published: row.is_published }
  } else {
    dialog.isEdit = false; dialog.editId = null
    dialog.form = { title: '', content: '', is_pinned: false, is_published: false }
  }
  dialog.visible = true
}

async function save() {
  if (!dialog.form.title.trim()) { ElMessage.warning('请输入公告标题'); return }
  if (dialog.isEdit) await api.put(`/announcements/${dialog.editId}`, dialog.form)
  else await api.post('/announcements', dialog.form)
  dialog.visible = false; ElMessage.success(dialog.isEdit ? '修改成功' : '创建成功'); load()
}

async function togglePublish(row) {
  await api.put(`/announcements/${row.id}`, {
    title: row.title, content: row.content,
    is_pinned: row.is_pinned, is_published: !row.is_published
  })
  row.is_published = !row.is_published
  ElMessage.success(row.is_published ? '已发布' : '已撤回')
}

async function del(id) {
  await ElMessageBox.confirm('确定删除此公告？', '提示', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
  await api.delete(`/announcements/${id}`)
  items.value = items.value.filter(i => i.id !== id)
  ElMessage.success('已删除')
}
</script>

<style scoped>
.page-container { max-width: 960px; margin: 0 auto; padding: var(--space-4); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); }
.header-left { display: flex; align-items: baseline; gap: var(--space-2); }
.header-left h2 { font-size: 20px; font-weight: 700; color: var(--gray-900); margin: 0; }
.header-count { font-size: 13px; color: var(--gray-400); }

.ann-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); margin-bottom: var(--space-4); }
.stat-card {
  display: flex; align-items: center; gap: var(--space-3);
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4);
  box-shadow: var(--shadow-xs);
}
.stat-icon { width: 40px; height: 40px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 18px; }
.stat-icon.published { background: #e8f5e9; }
.stat-icon.draft { background: #f3f4f6; }
.stat-icon.pinned { background: #fff3e0; }
.stat-info { display: flex; flex-direction: column; }
.stat-num { font-size: 20px; font-weight: 700; color: var(--gray-900); line-height: 1.2; }
.stat-label { font-size: 12px; color: var(--gray-400); }

.empty-state { text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state p { color: var(--gray-400); margin-bottom: 16px; }

.ann-list { display: flex; flex-direction: column; gap: var(--space-3); }
.ann-card {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); transition: all 0.2s; border-left: 3px solid transparent;
}
.ann-card:hover { box-shadow: var(--shadow-sm); transform: translateY(-1px); }
.ann-card.pinned { border-left-color: var(--color-danger); background: #fef9f9; }
.ann-card.draft { opacity: 0.65; }

.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.card-tags { display: flex; gap: 6px; align-items: center; }
.card-actions { display: flex; gap: 2px; }

.card-title { font-size: 16px; font-weight: 600; color: var(--gray-900); margin-bottom: 8px; line-height: 1.4; }
.card-content { font-size: 14px; color: var(--gray-600); line-height: 1.7; margin-bottom: 12px; white-space: pre-wrap; word-break: break-word; }
.card-footer { display: flex; gap: var(--space-4); font-size: 12px; color: var(--gray-400); }
.footer-item { display: flex; align-items: center; gap: 4px; }

@media (max-width: 768px) {
  .ann-stats { grid-template-columns: repeat(3, 1fr); gap: 8px; }
  .stat-card { padding: 10px 12px; }
  .stat-icon { width: 32px; height: 32px; font-size: 14px; }
  .stat-num { font-size: 16px; }
  .card-actions { flex-wrap: wrap; }
  .card-header { flex-direction: column; align-items: flex-start; gap: 8px; }
}
</style>
<style>
[data-theme="dark"] .stat-card { background: #212226; }
[data-theme="dark"] .stat-icon.published { background: rgba(34,197,94,0.15); }
[data-theme="dark"] .stat-icon.draft { background: #2a2b30; }
[data-theme="dark"] .stat-icon.pinned { background: rgba(245,158,11,0.15); }
[data-theme="dark"] .stat-num { color: #f0f1f4; }
[data-theme="dark"] .stat-label { color: #8b8c93; }
[data-theme="dark"] .ann-card { background: #212226; border-color: #2a2b30; }
[data-theme="dark"] .ann-card.pinned { background: #2a2228; border-left-color: var(--color-danger); }
[data-theme="dark"] .card-title { color: #f0f1f4; }
[data-theme="dark"] .card-content { color: #a8a9b0; }
[data-theme="dark"] .card-footer { color: #6b6c72; }
[data-theme="dark"] .header-left h2 { color: #f0f1f4; }
</style>
