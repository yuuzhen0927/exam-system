<template>
  <div class="page-container">
    <div class="page-header"><h2>角色管理</h2><el-button type="primary" @click="openDialog()">+ 新建角色</el-button></div>

    <div v-if="!items.length" class="empty-state"><el-empty description="暂无角色" /></div>

    <div v-else class="role-grid">
      <div v-for="r in items" :key="r.id" class="role-card" :class="{system: r.is_system}">
        <div class="role-card-top">
          <div class="role-icon" :style="{background: roleColor(r.name)}">{{ r.name[0]?.toUpperCase() }}</div>
          <div class="role-info">
            <div class="role-name">
              {{ r.name }}
              <el-tag v-if="r.is_system" size="small" type="info" effect="plain">系统</el-tag>
              <el-tag v-if="r.is_manager" size="small" type="warning" effect="plain">管理</el-tag>
            </div>
            <div class="role-desc">{{ r.description || '无描述' }}</div>
          </div>
        </div>
        <div class="role-card-bottom">
          <span class="role-meta">排序: {{ r.sort_order }}</span>
          <span class="role-meta">{{ r.created_at?.substring(0, 10) }}</span>
          <div class="role-actions">
            <el-button size="small" text type="primary" @click="openDialog(r)" :disabled="r.is_system">编辑</el-button>
            <el-popconfirm title="确定删除此角色？关联用户将变为学生角色" @confirm="del(r.id)" v-if="!r.is_system">
              <template #reference>
                <el-button size="small" text type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialog.visible" :title="dialog.isEdit ? '编辑角色' : '新建角色'" width="480">
      <el-form :model="dialog.form" label-width="80px">
        <el-form-item label="角色名称" required>
          <el-input v-model="dialog.form.name" placeholder="例如：实验员、教务" maxlength="20" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="dialog.form.description" placeholder="角色说明" maxlength="100" />
        </el-form-item>
        <el-form-item label="管理权限">
          <el-switch v-model="dialog.form.is_manager" active-text="可访问后台" />
          <span style="margin-left:8px;color:var(--gray-500);font-size:13px">开启后可访问管理功能</span>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="dialog.form.sort_order" :min="0" :max="99" size="small" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api'

const items = ref([])
const dialog = reactive({ visible: false, isEdit: false, editId: null, form: { name: '', description: '', is_manager: false, sort_order: 0 } })

const roleColors = ['#4f6ef7', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316']
function roleColor(name) {
  let h = 0
  for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h)
  return roleColors[Math.abs(h) % roleColors.length]
}

onMounted(load)
async function load() {
  try {
    const { data } = await api.get('/roles')
    items.value = data
  } catch { items.value = [] }
}

function openDialog(row) {
  if (row) {
    dialog.isEdit = true; dialog.editId = row.id
    dialog.form = { name: row.name, description: row.description, is_manager: row.is_manager, sort_order: row.sort_order }
  } else {
    dialog.isEdit = false; dialog.editId = null
    dialog.form = { name: '', description: '', is_manager: false, sort_order: 0 }
  }
  dialog.visible = true
}

async function save() {
  if (!dialog.form.name.trim()) { ElMessage.warning('请输入角色名称'); return }
  try {
    if (dialog.isEdit) await api.put(`/roles/${dialog.editId}`, dialog.form)
    else await api.post('/roles', dialog.form)
    dialog.visible = false; ElMessage.success('保存成功'); load()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '操作失败') }
}

async function del(id) {
  try { await api.delete(`/roles/${id}`); ElMessage.success('已删除'); load() }
  catch (e) { ElMessage.error(e.response?.data?.detail || '删除失败') }
}
</script>

<style scoped>
.role-grid { display: flex; flex-direction: column; gap: var(--space-2); }
.role-card {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--space-3);
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4);
  box-shadow: var(--shadow-xs); transition: all var(--transition-fast);
}
.role-card.system { border-left: 3px solid var(--gray-200); }
.role-card-top { display: flex; align-items: center; gap: var(--space-3); }
.role-icon {
  width: 40px; height: 40px; border-radius: var(--radius-md); color: #fff;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; flex-shrink: 0;
}
.role-info { display: flex; flex-direction: column; gap: 2px; }
.role-name { font-size: var(--text-base); font-weight: var(--font-semibold); display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.role-desc { font-size: var(--text-sm); color: var(--gray-500); }
.role-card-bottom { display: flex; align-items: center; gap: var(--space-3); }
.role-meta { font-size: var(--text-xs); color: var(--gray-400); }
.role-actions { display: flex; gap: 4px; }

@media (max-width: 768px) {
  .role-card { flex-direction: column; align-items: flex-start; }
  .role-card-bottom { width: 100%; justify-content: space-between; }
}
</style>
