<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:var(--color-warning-light);color:var(--color-warning)"><el-icon><UserFilled /></el-icon></div>
        <div><h2>用户管理</h2><p class="ph-sub">共 {{ users.length }} 位用户</p></div>
      </div>
    </div>

    <div class="filter-bar">
      <el-input v-model="searchText" placeholder="搜索用户名或姓名..." clearable class="fb-search">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="roleFilter" placeholder="角色" clearable @change="load" style="min-width:110px">
        <el-option v-for="r in roleOptions" :key="r.value" :label="r.label" :value="r.value" />
      </el-select>
    </div>

    <div v-if="!filteredUsers.length" class="empty-wrap">
      <el-empty description="暂无用户" />
    </div>

    <div v-else class="user-grid">
      <div v-for="u in filteredUsers" :key="u.id" class="user-card" :class="{ inactive: !u.is_active }">
        <div class="uc-top">
          <div class="uc-avatar" :style="{background: avatarColor(u.username)}">{{ u.fullname[0] || u.username[0] }}</div>
          <div class="uc-body">
            <div class="uc-name">{{ u.fullname || u.username }}</div>
            <div class="uc-uname">@{{ u.username }}</div>
          </div>
          <div class="uc-status">
            <span class="status-dot" :class="{on: u.is_active}"></span>
            {{ u.is_active ? '正常' : '禁用' }}
          </div>
        </div>
        <div class="uc-mid">
          <el-tag :type="u.role==='admin'?'danger':u.role==='teacher'?'warning':'info'" size="small">{{ roleLabel(u.role) }}</el-tag>
        </div>
        <div class="uc-bottom">
          <el-button size="small" text type="primary" @click="openEdit(u)"><el-icon><Edit /></el-icon> 编辑</el-button>
          <el-button v-if="u.username !== 'admin'" size="small" text :type="u.is_active?'warning':'success'" @click="toggleActive(u)">
            {{ u.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-tooltip v-else content="admin 用户不可禁用"><span class="admin-locked"><el-icon><Lock /></el-icon> 受保护</span></el-tooltip>
        </div>
      </div>
    </div>

    <el-dialog v-model="editVisible" title="编辑用户" width="440px" top="10vh">
      <el-form :model="editForm" label-width="60px">
        <el-form-item label="姓名"><el-input v-model="editForm.fullname" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editForm.role" style="width:100%">
            <el-option v-for="r in roleOptions" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码"><el-input v-model="editForm.password" placeholder="留空不修改" type="password" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible=false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Edit, UserFilled, Lock } from '@element-plus/icons-vue'

import { ref, computed, onMounted } from 'vue'
import api from '../api'

const users = ref([])
const roleFilter = ref('')
const searchText = ref('')
const editVisible = ref(false)
const editForm = ref({ id: null, fullname: '', role: 'student', password: '' })
const roleOptions = ref([])

const filteredUsers = computed(() => {
  if (!searchText.value) return users.value
  const q = searchText.value.toLowerCase()
  return users.value.filter(u =>
    (u.fullname || '').toLowerCase().includes(q) || (u.username || '').toLowerCase().includes(q)
  )
})

const avatarColors = ['#4f6ef7','#22c55e','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#ec4899','#f97316','#84cc16','#6366f1']
function avatarColor(name) {
  let h = 0; for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h)
  return avatarColors[Math.abs(h) % avatarColors.length]
}

function roleLabel(r) {
  const found = roleOptions.value.find(ro => ro.value === r)
  return found?.label || r
}

onMounted(async () => {
  try {
    const { data: roles } = await api.get('/roles')
    roleOptions.value = (roles || []).map(r => ({ label: r.description || r.name, value: r.name }))
    if (!roleOptions.value.length) {
      roleOptions.value = [
        { label: '管理员', value: 'admin' },
        { label: '负责人', value: 'teacher' },
        { label: '学生', value: 'student' },
      ]
    }
  } catch {
    roleOptions.value = [
      { label: '管理员', value: 'admin' },
      { label: '负责人', value: 'teacher' },
      { label: '学生', value: 'student' },
    ]
  }
  load()
})

async function load() {
  const params = {}
  if (roleFilter.value) params.role = roleFilter.value
  const { data } = await api.get('/users', { params })
  users.value = data
}

function openEdit(row) {
  editForm.value = { id: row.id, fullname: row.fullname, role: row.role, password: '' }
  editVisible.value = true
}

async function saveUser() {
  const body = { fullname: editForm.value.fullname, role: editForm.value.role }
  if (editForm.value.password) body.password = editForm.value.password
  await api.put(`/users/${editForm.value.id}`, body)
  editVisible.value = false
  ElMessage.success('保存成功')
  load()
}

async function toggleActive(row) {
  await api.put(`/users/${row.id}`, { is_active: !row.is_active })
  row.is_active = !row.is_active
  ElMessage.success(row.is_active ? '已启用' : '已禁用')
}
</script>

<style scoped>
.page-header { margin-bottom: var(--space-4); }
.ph-left { display: flex; align-items: center; gap: var(--space-3); }
.ph-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }

.filter-bar { display: flex; gap: var(--space-2); margin-bottom: var(--space-4); align-items: center; }
.fb-search { max-width: 280px; flex: 1; min-width: 150px; }

.empty-wrap { padding: 60px 0; }

.user-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--space-3); }
.user-card {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); border: 1px solid var(--gray-100);
  transition: all 0.2s; display: flex; flex-direction: column; gap: var(--space-3);
}
.user-card:hover { box-shadow: var(--shadow-sm); border-color: var(--gray-200); }
.user-card.inactive { opacity: 0.55; }

.uc-top { display: flex; align-items: center; gap: var(--space-3); }
.uc-avatar { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; font-size: 18px; flex-shrink: 0; }
.uc-body { flex: 1; min-width: 0; }
.uc-name { font-weight: 600; font-size: 15px; color: var(--gray-900); }
.uc-uname { font-size: 12px; color: var(--gray-500); }
.uc-status { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--gray-500); flex-shrink: 0; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--gray-300); }
.status-dot.on { background: #22c55e; }

.uc-mid { display: flex; gap: 6px; }
.uc-bottom { display: flex; gap: 4px; padding-top: var(--space-2); border-top: 1px solid var(--gray-100); }

@media (max-width: 768px) {
  .filter-bar { flex-direction: column; }
  .fb-search { max-width: 100%; }
  .user-grid { grid-template-columns: 1fr; }
}
</style>
