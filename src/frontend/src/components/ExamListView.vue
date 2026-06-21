<template>
  <div class="exam-list">
    <!-- 模拟考试 -->
    <div class="exam-section" v-if="mockExams.length">
      <div class="section-header">
        <div class="section-icon mock">📋</div>
        <div>
          <div class="section-title">模拟考试</div>
          <div class="section-desc">不限次数，自由练习，不记录异常操作</div>
        </div>
      </div>
      <div class="exam-grid">
        <div v-for="e in mockExams" :key="e.id" class="exam-card" @click="handleClick(e)">
          <div class="exam-card-top">
            <el-tag type="info" size="small">模拟</el-tag>
            <span v-if="hasTaken(e.id)" class="exam-taken-badge">已做</span>
          </div>
          <div class="exam-card-title">{{ e.title }}</div>
          <div class="exam-card-desc" v-if="e.description">{{ e.description }}</div>
          <div class="exam-card-meta">
            <span>📝 {{ e.question_count }}题</span>
            <span>⏱ {{ e.duration_minutes }}分钟</span>
            <span>📊 {{ e.pass_score }}分及格</span>
          </div>
          <div class="exam-card-actions">
            <el-button type="primary" size="small" @click.stop="goTake(e)">{{ hasTaken(e.id) ? '重新练习' : '开始练习' }}</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 正式考试 -->
    <div class="exam-section" v-if="formalExams.length">
      <div class="section-header">
        <div class="section-icon formal">🏅</div>
        <div>
          <div class="section-title">正式考试</div>
          <div class="section-desc">仅限一次作答，开启防作弊监测，切屏将记录异常</div>
        </div>
      </div>
      <div class="exam-grid">
        <div v-for="e in formalExams" :key="e.id" class="exam-card formal" @click="handleClick(e)">
          <div class="exam-card-top">
            <el-tag type="danger" size="small">正式</el-tag>
            <span v-if="hasTaken(e.id)" class="exam-done-label">已完成</span>
          </div>
          <div class="exam-card-title">{{ e.title }}</div>
          <div class="exam-card-desc" v-if="e.description">{{ e.description }}</div>
          <div class="exam-card-meta">
            <span>📝 {{ e.question_count }}题</span>
            <span>⏱ {{ e.duration_minutes }}分钟</span>
            <span>📊 {{ e.pass_score }}分及格</span>
            <span>🛡 切屏≤{{ e.max_tab_switches }}次</span>
          </div>
          <div class="exam-card-actions">
            <template v-if="!hasTaken(e.id)">
              <el-button type="danger" size="small" @click.stop="goTake(e)">开始考试</el-button>
            </template>
            <template v-else>
              <el-tag type="info" size="small">已完成</el-tag>
              <el-button size="small" type="warning" @click.stop="applyRetake(e)">申请重考</el-button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!mockExams.length && !formalExams.length" class="empty-state"><p>暂无可参加的考试</p></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  exams: { type: Array, default: () => [] },
  myResults: { type: Array, default: () => [] },
})

const emit = defineEmits(['take', 'retry', 'reapply'])

const mockExams = computed(() => props.exams.filter(e => e.mode === 'mock'))
const formalExams = computed(() => props.exams.filter(e => e.mode === 'formal'))

function hasTaken(examId) {
  return props.myResults.some(r => r.exam_id === examId)
}

function handleClick(e) {
  // for formal exams that are already taken, do nothing on card click
  if (e.mode === 'formal' && hasTaken(e.id)) return
  goTake(e)
}

function goTake(e) { emit('take', e.id) }
function applyRetake(e) { emit('reapply', e.id) }
</script>

<style scoped>
.exam-list { max-width: 900px; }

.exam-section { margin-bottom: var(--space-8); }
.section-header { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-4); }
.section-icon { width: 44px; height: 44px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 22px; }
.section-icon.mock { background: #DBEAFE; }
.section-icon.formal { background: #FEE2E2; }
.section-title { font-size: var(--text-lg); font-weight: var(--font-bold); color: var(--gray-900); }
.section-desc { font-size: var(--text-xs); color: var(--gray-500); margin-top: 2px; }

.exam-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-4); }

.exam-card {
  background: #fff; border-radius: var(--radius-lg); padding: var(--space-5);
  box-shadow: var(--shadow-sm); border: 1px solid var(--gray-100);
  cursor: pointer; transition: all var(--transition-fast);
}
.exam-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: var(--color-primary); }
.exam-card.formal { border-left: 3px solid var(--color-danger); }
.exam-card-top { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-3); }
.exam-taken-badge { font-size: 11px; color: var(--color-success); background: var(--color-success-light); padding: 1px 8px; border-radius: 99px; }
.exam-done-label { font-size: 11px; color: var(--gray-500); background: var(--gray-100); padding: 1px 8px; border-radius: 99px; }
.exam-card-title { font-size: var(--text-md); font-weight: var(--font-semibold); color: var(--gray-900); margin-bottom: var(--space-1); }
.exam-card-desc { font-size: var(--text-xs); color: var(--gray-500); margin-bottom: var(--space-3); }
.exam-card-meta { display: flex; flex-wrap: wrap; gap: var(--space-3); font-size: var(--text-xs); color: var(--gray-600); margin-bottom: var(--space-4); }
.exam-card-actions { display: flex; align-items: center; gap: var(--space-2); padding-top: var(--space-3); border-top: 1px solid var(--gray-50); }

@media (max-width: 768px) {
  .exam-grid { grid-template-columns: 1fr; }
  .exam-card { padding: var(--space-4); }
}
</style>
