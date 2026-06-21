<template>
  <div class="page-root">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:var(--color-warning-light);color:var(--color-warning)"><el-icon><Warning /></el-icon></div>
        <div>
          <h2>异常报告</h2>
          <p class="ph-sub">正式考试中的异常操作记录</p>
        </div>
      </div>
      <el-button @click="load" :loading="loading">刷新</el-button>
    </div>

    <div class="content-card">
      <div v-if="loading" style="text-align:center;padding:48px 0">
        <el-icon class="is-loading" size="24"><Loading /></el-icon>
        <p style="color:var(--gray-400);margin-top:8px">加载中...</p>
      </div>

      <template v-else-if="items.length">
        <div class="ab-grid">
          <div v-for="r in items" :key="r.id" class="ab-card" :class="{ judged: r.is_judged }">
            <div class="ab-top">
              <div class="ab-user">
                <span class="ab-avatar" :style="{background: avatarColor(r.fullname || r.username)}">{{ (r.fullname || r.username || '?')[0].toUpperCase() }}</span>
                <div>
                  <div class="ab-name">{{ r.fullname || r.username }}</div>
                  <div class="ab-username">@{{ r.username }}</div>
                </div>
              </div>
              <div class="ab-tags">
                <el-tag size="small" :type="r.is_judged ? (r.judgment === 'valid' ? 'success' : 'danger') : 'warning'" effect="plain">
                  {{ r.is_judged ? (r.judgment === 'valid' ? '已忽略' : '确认作弊') : '待判定' }}
                </el-tag>
                <el-tag size="small" :type="r.reason==='tab_switch'?'warning':'danger'">{{ reasonMap[r.reason] || r.reason }}</el-tag>
              </div>
            </div>
            <div v-if="r.detail" class="ab-detail">{{ r.detail }}</div>
            <div class="ab-meta">{{ formatTime(r.created_at) }}</div>
            <div v-if="!r.is_judged" class="ab-btns">
              <el-button size="small" type="success" @click="judge(r, 'valid')">忽略</el-button>
              <el-button size="small" type="danger" @click="judge(r, 'invalid')">确认作弊</el-button>
            </div>
            <div v-else class="ab-judged-by">判定人：{{ r.judged_by }} | {{ r.judgment==='valid'?'忽略':'作弊' }}</div>
          </div>
        </div>

        <div v-if="total > 20" class="page-pagination">
          <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="prev,next" @current-change="load" size="small" />
        </div>
      </template>

      <div v-else class="empty-state">
        <el-icon size="48" color="#d1d5db"><Warning /></el-icon>
        <p>暂无异常报告</p>
        <p class="empty-hint">正式考试中出现切屏等异常操作时会自动记录</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning, Loading } from '@element-plus/icons-vue'

import { ref, onMounted } from 'vue'
import api from '../api'

const items = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)

const reasonMap = { tab_switch: '切屏', blur: '失焦', visibility: '隐藏页面' }
const avatarColors = ['#4f6ef7','#22c55e','#f59e0b','#ef4444','#8b5cf6','#ec4899','#06b6d4']

onMounted(load)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/abnormal', { params: { page: page.value, page_size: 20 } })
    items.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    ElMessage.error('加载失败：' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

async function judge(row, judgment) {
  try {
    await ElMessageBox.confirm(
      judgment === 'valid' ? '确定忽略此异常记录？' : '确定判定为作弊？此操作将标记该考生的考试成绩为作弊。',
      '确认操作',
      { type: 'warning' }
    )
    await api.post(`/abnormal/${row.id}/judge`, null, { params: { judgment } })
    row.is_judged = true
    row.judgment = judgment
    ElMessage.success(judgment === 'valid' ? '已忽略' : '已判定为作弊')
  } catch {}
}

function avatarColor(name) {
  let h = 0
  for (let i = 0; i < (name || 'U').length; i++) h += (name || 'U').charCodeAt(i)
  return avatarColors[h % avatarColors.length]
}

function formatTime(t) {
  if (!t) return ''
  return t.substring(0, 16).replace('T', ' ')
}
</script>

<style scoped>
.page-root { max-width: 960px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.ph-left { display: flex; align-items: center; gap: 12px; }
.ph-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }

.content-card { background: var(--gray-25); border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid var(--gray-100); }

.ab-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 12px; }
.ab-card {
  background: var(--gray-25); border-radius: 10px; padding: 16px 20px;
  border: 1px solid var(--gray-100); transition: all 0.15s;
  display: flex; flex-direction: column; gap: 10px;
}
.ab-card:hover { border-color: var(--color-primary); }
.ab-card.judged { opacity: 0.5; background: var(--gray-50); }

.ab-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.ab-user { display: flex; align-items: center; gap: 10px; }
.ab-avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; font-size: 14px; flex-shrink: 0; }
.ab-name { font-size: 14px; font-weight: 600; color: var(--gray-900); }
.ab-username { font-size: 12px; color: var(--gray-400); }
.ab-tags { display: flex; gap: 6px; flex-shrink: 0; }

.ab-detail { font-size: 13px; color: var(--gray-600); background: var(--gray-50); padding: 8px 12px; border-radius: 8px; }
.ab-meta { font-size: 12px; color: var(--gray-400); }
.ab-btns { display: flex; gap: 8px; padding-top: 8px; border-top: 1px solid var(--gray-100); }
.ab-judged-by { font-size: 12px; color: var(--gray-500); padding-top: 8px; border-top: 1px solid var(--gray-100); }

.page-pagination { margin-top: 16px; display: flex; justify-content: center; }

.empty-state { text-align: center; padding: 60px 0; color: var(--gray-400); }
.empty-hint { font-size: 12px; color: var(--gray-300); margin-top: 4px; }

@media (max-width: 768px) {
  .ab-grid { grid-template-columns: 1fr; }
  .content-card { padding: 16px; }
}
</style>
