<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:var(--color-warning-light);color:var(--color-warning)"><el-icon size="22"><Star /></el-icon></div>
        <div><h2>收藏夹</h2><p class="ph-sub">{{ total }} 道收藏题目</p></div>
      </div>
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
      <el-input v-model="searchText" placeholder="搜索收藏题目..." clearable class="fb-search">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <div class="fb-filters">
        <el-select v-model="filter.subject_id" placeholder="全部科目" clearable @change="load" style="width:140px">
          <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-select v-model="filter.question_type" placeholder="全部题型" clearable @change="load" style="width:120px">
          <el-option label="单选题" value="single" />
          <el-option label="多选题" value="multi" />
          <el-option label="判断题" value="truefalse" />
          <el-option label="综合题" value="composite" />
        </el-select>
      </div>
    </div>

    <!-- Empty -->
    <div v-if="!filteredItems.length" class="empty-wrap">
      <el-empty :description="searchText || filter.subject_id ? '未找到匹配收藏' : '还没有收藏题目'">
        <p class="hint" v-if="!searchText && !filter.subject_id">练习或考试时点击题目下方的星标即可收藏</p>
        <el-button v-if="!searchText && !filter.subject_id" type="primary" @click="$router.push('/practice')">去练习</el-button>
      </el-empty>
    </div>

    <!-- Card grid -->
    <div v-else class="fav-grid">
      <div v-for="row in filteredItems" :key="row.id" class="fav-card" @click="toggleExpand(row.id)">
        <div class="fc-top">
          <span class="fc-type" :class="row.question_type">{{ typeLabel(row.question_type) }}</span>
          <span class="fc-difficulty" v-if="row.difficulty">
            <span v-for="i in 5" :key="i" class="star" :class="{filled: i <= row.difficulty}">★</span>
          </span>
        </div>
        <div class="fc-content">{{ row.question_content }}</div>
        <div class="fc-meta">
          <el-tag size="small" type="info" effect="plain">{{ row.subject_name }}</el-tag>
          <span class="fc-answer">答案：<b>{{ row.question_answer }}</b></span>
        </div>
        <!-- Expanded details -->
        <div v-if="expandedIds.has(row.id)" class="fc-expanded">
          <div class="fc-exp-item">
            <span class="fc-exp-label">正确答案</span>
            <span class="fc-exp-value correct">
              <template v-for="letter in String(row.question_answer).toUpperCase()" :key="letter">
                <span class="fc-exp-option">{{ letter }}. {{ getOptionText(row, letter) }}</span>
              </template>
            </span>
          </div>
          <div v-if="row.explanation" class="fc-exp-item">
            <span class="fc-exp-label">解析</span>
            <span class="fc-exp-value">{{ row.explanation }}</span>
          </div>
          <div class="fc-exp-item">
            <span class="fc-exp-label">收藏时间</span>
            <span class="fc-exp-value">{{ row.created_at?.slice(0, 19).replace('T', ' ') }}</span>
          </div>
        </div>
        <div class="fc-actions">
          <span class="fc-date">{{ row.created_at?.slice(0, 10) }}</span>
          <span class="fc-expand-hint">{{ expandedIds.has(row.id) ? '收起 ↑' : '展开 ↓' }}</span>
          <el-button size="small" type="warning" :icon="StarFilled" circle @click.stop="unfav(row.id)" title="取消收藏" />
        </div>
      </div>
    </div>

    <el-pagination v-if="total > 50" v-model:current-page="page" :total="total" :page-size="50" layout="prev, pager, next" @current-change="load" style="justify-content:center;margin-top:24px" size="small" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const subjects = ref([]); const items = ref([]); const total = ref(0); const page = ref(1)
const searchText = ref(''); const filter = reactive({ subject_id: null, question_type: '' })
    const answerVisible = ref(false); const viewingQuestion = ref(null)
    const expandedIds = ref(new Set())
    function toggleExpand(id) { const s = new Set(expandedIds.value); s.has(id) ? s.delete(id) : s.add(id); expandedIds.value = s }

const filteredItems = computed(() => {
  let list = items.value
  if (searchText.value) {
    const q = searchText.value.toLowerCase()
    list = list.filter(r => (r.question_content || '').toLowerCase().includes(q) || (r.subject_name || '').toLowerCase().includes(q))
  }
  return list
})

onMounted(async () => { const { data } = await api.get('/subjects'); subjects.value = data; load() })
    async function viewAnswer(row) {
  try {
    const { data } = await api.get('/questions/' + row.question_id)
    viewingQuestion.value = data
    answerVisible.value = true
  } catch { ElMessage.error('加载题目详情失败') }
}
    function parseOptions(opts) { try { return typeof opts === 'string' ? JSON.parse(opts) : (opts || []) } catch { return [] } }
async function load() {
  const params = { page: page.value, page_size: 50 }
  if (filter.subject_id) params.subject_id = filter.subject_id
  if (filter.question_type) params.question_type = filter.question_type
  const { data } = await api.get('/favorites', { params })
  items.value = data.items || []; total.value = data.total || 0
}
async function unfav(id) { await api.delete(`/favorites/${id}`); items.value = items.value.filter(i => i.id !== id); total.value-- }
function getOptionText(row, letter) {
  try {
    const opts = typeof row.question_options === "string" ? JSON.parse(row.question_options) : (row.question_options || [])
    const found = opts.find(o => (o.label || "").toUpperCase() === letter.toUpperCase())
    return found ? found.text : ""
  } catch { return "" }
}
function typeLabel(t) { return { single:'单选', multi:'多选', truefalse:'判断', composite:'综合' }[t] || t }
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-4); gap: var(--space-3); flex-wrap: wrap; }
.ph-left { display: flex; align-items: center; gap: var(--space-3); }
.ph-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }

.filter-bar { display: flex; gap: var(--space-2); margin-bottom: var(--space-4); align-items: center; flex-wrap: wrap; }
.fb-search { max-width: 300px; flex: 1; min-width: 150px; }

.empty-wrap { padding: 60px 0; }
.hint { font-size: var(--text-sm); color: var(--gray-400); margin: 4px 0 16px; }

.fav-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--space-3); }
.fav-card {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); border: 1px solid var(--gray-100);
  transition: all 0.2s; display: flex; flex-direction: column; gap: var(--space-2);
}
.fav-card:hover { box-shadow: var(--shadow-sm); transform: translateY(-1px); border-color: #fcd34d; }

.fc-top { display: flex; justify-content: space-between; align-items: center; }
.fc-type {
  font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 99px; color: #fff;
}
.fc-type.single { background: var(--color-primary); }
.fc-type.multi { background: #f59e0b; }
.fc-type.truefalse { background: #22c55e; }
.fc-type.composite { background: #8b5cf6; }

.star { color: #e5e7eb; font-size: 12px; letter-spacing: 1px; }
.star.filled { color: var(--color-warning); }

.fc-content { font-size: 14px; line-height: 1.7; color: var(--gray-800); flex: 1; }
.fc-meta { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; }
.fc-answer { font-size: 12px; color: var(--gray-500); }
.fc-answer b { color: var(--color-success); }

.fc-actions { display: flex; justify-content: space-between; align-items: center; padding-top: var(--space-2); border-top: 1px solid var(--gray-50); }
.fc-date { font-size: 11px; color: var(--gray-400); }
.fc-expand-hint { font-size: 11px; color: var(--color-primary); cursor: pointer; user-select: none; }

/* Expanded details */
.fc-expanded {
  background: var(--gray-50);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  animation: fadeIn 0.2s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
.fc-exp-item { display: flex; flex-direction: column; gap: 2px; }
.fc-exp-label { font-size: 11px; color: var(--gray-400); font-weight: 500; }
.fc-exp-value { font-size: 13px; color: var(--gray-700); line-height: 1.6; }
.fc-exp-value.correct { color: var(--color-success); font-weight: 600; display: flex; flex-direction: column; gap: 4px; }
.fc-exp-option { display: block; }

@media (max-width: 768px) {
  .filter-bar { flex-direction: column; align-items: stretch; }
  .fb-search { max-width: 100%; }
  .fav-grid { grid-template-columns: 1fr; }
}
</style>
