<template>
  <div class="page-root">
    <div class="page-header">
      <h2>重考审批</h2>
      <p class="page-desc">审核学生提交的正式考试重考申请</p>
    </div>

    <div class="content-card" v-loading="loading">
      <!-- Tabs -->
      <div class="tab-row">
        <button v-for="t in tabs" :key="t.key" class="tab-btn" :class="{active: activeTab === t.key}" @click="activeTab = t.key">
          {{ t.label }}
          <span v-if="t.count !== undefined" class="tab-count">{{ t.count }}</span>
        </button>
      </div>

      <template v-if="filteredList.length">
        <div class="app-list">
          <div v-for="app in filteredList" :key="app.id" class="app-card">
            <div class="app-main">
              <div class="app-avatar">{{ app.fullname?.charAt(0) || '?' }}</div>
              <div class="app-info">
                <div class="app-user">{{ app.fullname }} <span class="app-username">@{{ app.username }}</span></div>
                <div class="app-exam">{{ app.exam_title }}</div>
                <div class="app-meta">
                  <span>{{ app.created_at?.slice(0, 16).replace('T',' ') }}</span>
                  <span v-if="app.reason" class="app-reason">原因：{{ app.reason }}</span>
                </div>
              </div>
            </div>
            <div class="app-actions" v-if="app.status === 'pending'">
              <el-button type="success" size="small" @click="handleApprove(app)">批准</el-button>
              <el-button type="danger" size="small" plain @click="handleReject(app)">拒绝</el-button>
            </div>
            <div class="app-status" v-else>
              <el-tag :type="app.status==='approved'?'success':'danger'" size="small">{{ app.status==='approved'?'已批准':'已拒绝' }}</el-tag>
            </div>
          </div>
        </div>
      </template>
      <div v-else class="empty-state">
        <p>{{ activeTab==='pending' ? '暂无待审批的申请' : '暂无记录' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'

import { ref, computed, onMounted } from 'vue'
import api from '../api'

const loading = ref(false)
const apps = ref([])
const activeTab = ref('pending')

const tabs = computed(() => [
  { key: 'pending', label: '待审批', count: apps.value.filter(a => a.status === 'pending').length },
  { key: 'approved', label: '已批准' },
  { key: 'rejected', label: '已拒绝' },
  { key: 'all', label: '全部' },
])

const filteredList = computed(() => {
  if (activeTab.value === 'all') return apps.value
  return apps.value.filter(a => a.status === activeTab.value)
})

async function fetchApps() {
  loading.value = true
  try {
    const { data } = await api.get('/exams/retake-applications')
    apps.value = data
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function handleApprove(app) {
  try {
    await ElMessageBox.confirm(`确定批准 ${app.fullname} 的重考申请？`, '确认批准', { type: 'warning' })
    await api.post(`/exams/retake-applications/${app.id}/approve`)
    ElMessage.success('已批准重考')
    fetchApps()
  } catch {}
}

async function handleReject(app) {
  try {
    await ElMessageBox.confirm(`确定拒绝 ${app.fullname} 的重考申请？`, '确认拒绝', { type: 'warning' })
    await api.post(`/exams/retake-applications/${app.id}/reject`)
    ElMessage.success('已拒绝')
    fetchApps()
  } catch {}
}

onMounted(fetchApps)
</script>

<style scoped>
.page-root { max-width: 900px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 20px; font-weight: 700; margin: 0; color: var(--gray-900); }
.page-desc { font-size: 13px; color: var(--gray-500); margin: 4px 0 0; }

.content-card {
  background: var(--gray-25); border-radius: 12px; padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid var(--gray-100);
}

.tab-row { display: flex; gap: 4px; margin-bottom: 20px; background: var(--gray-50); padding: 4px; border-radius: 8px; }
.tab-btn {
  padding: 8px 20px; border: none; border-radius: 6px;
  background: transparent; font-size: 14px; color: var(--gray-600);
  cursor: pointer; transition: all 0.15s; font-weight: 500;
  display: flex; align-items: center; gap: 6px;
}
.tab-btn:hover { color: var(--gray-900); }
.tab-btn.active { background: var(--gray-25); color: var(--color-primary); box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.tab-count {
  background: var(--color-primary); color: #fff; font-size: 11px;
  padding: 1px 7px; border-radius: 99px; font-weight: 600;
}

.app-list { display: flex; flex-direction: column; gap: 12px; }
.app-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border: 1px solid var(--gray-100); border-radius: 10px;
  transition: all 0.15s;
}
.app-card:hover { border-color: var(--color-primary); box-shadow: 0 2px 8px rgba(79,110,247,0.08); }

.app-main { display: flex; align-items: center; gap: 14px; flex: 1; min-width: 0; }
.app-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--color-primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 16px; flex-shrink: 0;
}
.app-info { min-width: 0; }
.app-user { font-size: 15px; font-weight: 600; color: var(--gray-900); }
.app-username { font-size: 12px; color: var(--gray-400); font-weight: 400; }
.app-exam { font-size: 13px; color: var(--gray-600); margin-top: 2px; }
.app-meta { font-size: 12px; color: var(--gray-400); margin-top: 4px; display: flex; gap: 12px; }
.app-reason { color: var(--gray-500); }

.app-actions { display: flex; gap: 8px; flex-shrink: 0; }
.app-status { flex-shrink: 0; }

.empty-state { text-align: center; padding: 48px 0; color: var(--gray-400); }

@media (max-width: 768px) {
  .content-card { padding: 16px; }
  .app-card { flex-direction: column; align-items: flex-start; gap: 12px; }
  .app-actions { width: 100%; justify-content: flex-end; }
}
</style>
