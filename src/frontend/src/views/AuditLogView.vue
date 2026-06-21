<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:#faf5ff;color:#8b5cf6"><el-icon><Clock /></el-icon></div>
        <div><h2>操作日志</h2><p class="ph-sub">后台操作留痕记录</p></div>
      </div>
    </div>

    <div class="filter-bar">
      <el-select v-model="filter.action" placeholder="操作类型" clearable @change="load" style="min-width:110px">
        <el-option label="创建" value="create" /><el-option label="更新" value="update" />
        <el-option label="删除" value="delete" /><el-option label="发布" value="publish" />
        <el-option label="导入" value="import" />
      </el-select>
      <el-select v-model="filter.target_type" placeholder="操作对象" clearable @change="load" style="min-width:110px">
        <el-option label="科目" value="subject" /><el-option label="题目" value="question" />
        <el-option label="考试" value="exam" /><el-option label="用户" value="user" />
        <el-option label="证书" value="certificate" /><el-option label="公告" value="announcement" />
      </el-select>
    </div>

    <div v-if="!items.length" class="empty-wrap"><el-empty description="暂无操作日志" /></div>

    <div v-else class="log-grid">
      <div v-for="item in items" :key="item.id" class="log-card">
        <div class="lc-icon" :style="{background: actionBg(item.action)}">{{ actionIcon(item.action) }}</div>
        <div class="lc-body">
          <div class="lc-top">
            <span class="lc-user">{{ item.username }}</span>
            <el-tag size="small" effect="plain">{{ targetLabel(item.target_type) }}</el-tag>
            <span class="lc-act">{{ actionLabel(item.action) }}</span>
          </div>
          <div v-if="item.detail" class="lc-detail">{{ item.detail }}</div>
          <div class="lc-meta">
            <span>ID: {{ item.target_id }}</span>
            <span>{{ item.created_at?.slice(0, 19) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="page-pagination">
      <el-pagination v-model:current-page="page" :total="total" :page-size="50" layout="total,prev,next" @current-change="load" size="small" />
    </div>
  </div>
</template>

<script setup>
import { Clock } from '@element-plus/icons-vue'

import { ref, reactive, onMounted } from 'vue'
import api from '../api'

const items = ref([])
const total = ref(0)
const page = ref(1)
const filter = reactive({ action: null, target_type: null })

onMounted(load)

async function load() {
  const params = { page: page.value, page_size: 50 }
  if (filter.action) params.action = filter.action
  if (filter.target_type) params.target_type = filter.target_type
  const { data } = await api.get('/audit', { params })
  items.value = data.items; total.value = data.total
}

function actionLabel(a) { return { create:'创建', update:'更新', delete:'删除', publish:'发布', revoke:'撤销', grade:'批改', import:'导入' }[a] || a }
function actionIcon(a) { return { create:'+', update:'↗', delete:'−', publish:'→', revoke:'←', grade:'✓', import:'⇩' }[a] || '·' }
function actionBg(a) { return { create:'#e8f5e9', update:'#e3f2fd', delete:'#fce4ec', publish:'#e8f5e9', revoke:'#fff3e0', grade:'#e8eaf6', import:'#e0f2f1' }[a] || '#f5f5f5' }
function targetLabel(t) { return { subject:'科目', chapter:'章节', question:'题目', exam:'考试', user:'用户', certificate:'证书', announcement:'公告', resource:'资料', video:'视频', feedback:'反馈' }[t] || t }
</script>

<style scoped>
.page-header { margin-bottom: var(--space-4); }
.ph-left { display: flex; align-items: center; gap: var(--space-3); }
.ph-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }

.filter-bar { display: flex; gap: var(--space-2); margin-bottom: var(--space-4); flex-wrap: wrap; }
.empty-wrap { padding: 60px 0; }

.log-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: var(--space-3); }
.log-card {
  display: flex; align-items: flex-start; gap: var(--space-3);
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4);
  box-shadow: var(--shadow-xs); border: 1px solid var(--gray-100); transition: all 0.2s;
}
.log-card:hover { box-shadow: var(--shadow-sm); }
.lc-icon {
  width: 36px; height: 36px; border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 700; flex-shrink: 0; color: var(--gray-700);
}
.lc-body { flex: 1; min-width: 0; }
.lc-top { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px; }
.lc-user { font-weight: 600; font-size: 13px; color: var(--gray-900); }
.lc-act { font-size: 13px; color: var(--gray-500); }
.lc-detail { font-size: 13px; color: var(--gray-700); margin: 4px 0; line-height: 1.5; }
.lc-meta { display: flex; gap: var(--space-4); font-size: 12px; color: var(--gray-400); }

.page-pagination { margin-top: var(--space-4); display: flex; justify-content: center; }

@media (max-width: 768px) { .log-grid { grid-template-columns: 1fr; } }
</style>
