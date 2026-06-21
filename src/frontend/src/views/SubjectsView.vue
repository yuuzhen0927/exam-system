<template>
  <div class="page-container">
    <div class="page-header"><h2>科目章节</h2><el-button type="primary" @click="openSubjectDialog()">+ 新建科目</el-button></div>

    <div class="subject-grid">
      <div v-for="s in subjects" :key="s.id" class="subject-card">
        <div class="sc-header">
          <div class="sc-icon" :style="{background: cardColor(s.id)}">{{ s.name[0] }}</div>
          <div class="sc-info">
            <div class="sc-name">{{ s.name }}</div>
            <div class="sc-desc" v-if="s.description">{{ s.description }}</div>
          </div>
        </div>
        <div class="sc-meta">
          <span class="sc-count">{{ s.question_count || 0 }} 题</span>
        </div>
        <div class="sc-actions">
          <el-button size="small" @click="openChapterDialog(s)">章节</el-button>
          <el-button size="small" type="primary" @click="openSubjectDialog(s)">编辑</el-button>
          <el-button size="small" type="danger" @click="delSubject(s.id)">删除</el-button>
        </div>
      </div>
      <div v-if="!subjects.length" class="empty-state"><el-empty description="暂无科目，点击上方按钮创建" /></div>
    </div>

    <!-- Subject dialog -->
    <el-dialog v-model="subDialog.visible" :title="subDialog.isEdit?'编辑科目':'新建科目'" width="500">
      <el-form :model="subDialog.form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="subDialog.form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="subDialog.form.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="subDialog.visible=false">取消</el-button><el-button type="primary" @click="saveSubject">保存</el-button></template>
    </el-dialog>

    <!-- Chapter dialog -->
    <el-dialog v-model="chDialog.visible" :title="chDialog.subjectName + ' - 章节管理'" width="550">
      <div style="display:flex;gap:8px;margin-bottom:16px">
        <el-input v-model="chDialog.newName" placeholder="新章节名" style="flex:1" />
        <el-button type="primary" @click="addChapter">添加</el-button>
      </div>
      <div v-if="!chDialog.items.length" style="text-align:center;padding:20px;color:var(--gray-500)">暂无章节</div>
      <div v-else class="ch-list">
        <div v-for="ch in chDialog.items" :key="ch.id" class="ch-item">
          <span class="ch-name">{{ ch.name }}</span>
          <span class="ch-count">{{ ch.question_count || 0 }} 题</span>
          <el-button size="small" type="danger" text @click="delChapter(ch.id)">删除</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'

import { ref, reactive, onMounted } from 'vue'
import api from '../api'

const subjects = ref([])
const subDialog = reactive({ visible: false, isEdit: false, form: { name: '', description: '' }, editId: null })
const chDialog = reactive({ visible: false, subjectId: null, subjectName: '', items: [], newName: '' })

const cardColors = ['#4f6ef7','#22c55e','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#ec4899','#f97316']
function cardColor(id) { return cardColors[(id-1) % cardColors.length] }

onMounted(loadSubjects)

async function loadSubjects() { const { data } = await api.get('/subjects'); subjects.value = data }

function openSubjectDialog(row) {
  if (row) { subDialog.isEdit = true; subDialog.editId = row.id; subDialog.form = { name: row.name, description: row.description } }
  else { subDialog.isEdit = false; subDialog.editId = null; subDialog.form = { name: '', description: '' } }
  subDialog.visible = true
}
async function saveSubject() {
  if (subDialog.isEdit) await api.put(`/subjects/${subDialog.editId}`, subDialog.form)
  else await api.post('/subjects', subDialog.form)
  subDialog.visible = false; ElMessage.success('保存成功'); loadSubjects()
}
async function delSubject(id) {
  await ElMessageBox.confirm('确定删除？', '警告', { type: 'warning' })
  await api.delete(`/subjects/${id}`); ElMessage.success('已删除'); loadSubjects()
}
async function openChapterDialog(subject) {
  chDialog.subjectId = subject.id; chDialog.subjectName = subject.name; chDialog.newName = ''
  const { data } = await api.get(`/subjects/${subject.id}/chapters`); chDialog.items = data; chDialog.visible = true
}
async function addChapter() {
  if (!chDialog.newName.trim()) return
  await api.post(`/subjects/${chDialog.subjectId}/chapters`, { subject_id: chDialog.subjectId, name: chDialog.newName })
  chDialog.newName = ''
  const { data } = await api.get(`/subjects/${chDialog.subjectId}/chapters`); chDialog.items = data
}
async function delChapter(id) {
  await api.delete(`/subjects/chapters/${id}`)
  const { data } = await api.get(`/subjects/${chDialog.subjectId}/chapters`); chDialog.items = data
}
</script>

<style scoped>
.subject-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--space-3); }
.subject-card { background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4); box-shadow: var(--shadow-xs); transition: all var(--transition-fast); }
.subject-card:hover { box-shadow: var(--shadow-sm); }
.sc-header { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-3); }
.sc-icon { width: 44px; height: 44px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: var(--font-bold); }
.sc-name { font-weight: var(--font-semibold); font-size: var(--text-base); color: var(--gray-900); }
.sc-desc { font-size: var(--text-xs); color: var(--gray-500); margin-top: 2px; }
.sc-meta { margin-bottom: var(--space-3); }
.sc-count { font-size: var(--text-sm); color: var(--gray-500); background: var(--gray-50); padding: 2px 10px; border-radius: 99px; }
.sc-actions { display: flex; gap: 6px; }

.ch-list { display: flex; flex-direction: column; gap: 4px; }
.ch-item { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-2) var(--space-3); background: var(--gray-50); border-radius: var(--radius-sm); }
.ch-name { flex: 1; font-size: var(--text-sm); }
.ch-count { font-size: var(--text-xs); color: var(--gray-500); }

@media (max-width: 768px) {
  .subject-grid { grid-template-columns: 1fr; }
}
</style>
