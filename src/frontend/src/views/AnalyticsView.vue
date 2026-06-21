<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:#eef2ff;color:var(--color-primary)"><el-icon size="22"><TrendCharts /></el-icon></div>
        <div><h2>数据分析</h2><p class="ph-sub">平台数据概览与用户行为分析</p></div>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="stats-row">
      <div v-for="s in stats" :key="s.label" class="stat-mini" :style="{borderLeft: '3px solid ' + s.color}">
        <div class="sm-icon" :style="{background: s.color + '15', color: s.color}"><el-icon size="20"><component :is="s.icon" /></el-icon></div>
        <div class="sm-info">
          <span class="sm-val">{{ s.value }}</span>
          <span class="sm-lbl">{{ s.label }}</span>
        </div>
      </div>
    </div>

    <!-- Three Column: Subject + Weak Points + High Freq Wrong -->
    <div class="ana-three">
      <!-- Subject Distribution -->
      <div class="ana-card subject-card">
        <div class="ac-head">
          <span class="ac-dot" style="background:var(--color-primary)"></span>
          科目题量分布
        </div>
        <div v-if="!subjects.length" class="ac-empty">暂无数据</div>
        <div v-else class="subject-list">
          <div v-for="(s, i) in subjects" :key="s.id" class="subject-item">
            <div class="si-top">
              <span class="si-name">{{ s.name }}</span>
              <span class="si-count">{{ s.question_count }} 题</span>
            </div>
            <div class="si-bar-wrap">
              <div class="si-bar" :style="{width: Math.max(8, (s.question_count / maxSubjectCount) * 100) + '%', background: subjectColors[i % subjectColors.length]}"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Weak Points -->
      <div class="ana-card">
        <div class="ac-head">
          <span class="ac-dot" style="background:#ef4444"></span>
          知识薄弱点
        </div>
        <div v-if="!weakPoints.length" class="ac-empty">暂无数据</div>
        <div v-else class="ac-list">
          <div v-for="(w, i) in weakPoints.slice(0, 6)" :key="i" class="ac-item">
            <span class="ac-rank" :class="{hot: i < 3}">{{ i+1 }}</span>
            <div class="ac-info">
              <span class="ac-name">{{ w.chapter }}</span>
              <div class="ac-bar-wrap">
                <div class="ac-bar" :style="{width: Math.max(10, (w.wrong_total / maxWeakCount) * 100) + '%'}"></div>
              </div>
            </div>
            <span class="ac-num danger">{{ w.wrong_total }} 错</span>
          </div>
        </div>
      </div>

      <!-- High Freq Wrong -->
      <div class="ana-card">
        <div class="ac-head">
          <span class="ac-dot" style="background:#f59e0b"></span>
          高频错题
        </div>
        <div v-if="!questionAcc.length" class="ac-empty">暂无数据</div>
        <div v-else class="ac-list">
          <div v-for="(q, i) in questionAcc.slice(0, 6)" :key="i" class="ac-item">
            <span class="ac-rank" :class="{hot: i < 3}">{{ i+1 }}</span>
            <div class="ac-info">
              <span class="ac-name" :title="q.content">{{ q.content?.substring(0, 28) }}{{ q.content?.length > 28 ? '...' : '' }}</span>
              <div class="ac-bar-wrap">
                <div class="ac-bar amber" :style="{width: Math.max(10, (q.wrong_count / maxWrongCount) * 100) + '%'}"></div>
              </div>
            </div>
            <span class="ac-num warning">{{ q.wrong_count }} 次</span>
          </div>
        </div>
      </div>
    </div>

    <!-- User Activity -->
    <div class="ana-card" style="margin-top:16px">
      <div class="ac-head">
        <span class="ac-dot" style="background:var(--color-primary)"></span>
        用户活跃度
        <span class="ac-count">{{ userAct.length }} 人</span>
      </div>
      <div v-if="!userAct.length" class="ac-empty">暂无数据</div>
      <div v-else class="user-grid">
        <div v-for="u in userAct" :key="u.username" class="user-mini">
          <div class="um-avatar" :style="{background: avatarColor(u.username)}">{{ u.fullname?.[0] || u.username[0] }}</div>
          <div class="um-info">
            <div class="um-name">{{ u.fullname || u.username }}</div>
            <div class="um-stat">
              <span class="um-tag practice">练习 {{ u.practice_count }}</span>
              <span class="um-tag exam">考试 {{ u.exam_count }}</span>
            </div>
          </div>
          <div class="um-right">
            <div class="um-bar-wrap" v-if="u.practice_count + u.exam_count > 0">
              <div class="um-bar" :style="{width: Math.min(100, ((u.practice_count + u.exam_count) / maxUserActivity) * 100) + '%'}"></div>
            </div>
            <span class="um-time">{{ u.last_active_at?.substring(0, 10) || '未活跃' }}</span>
          </div>
        </div>
      </div>
    </div>


    <div class="ana-card" style="margin-top:16px">
      <div class="ac-head">
        <span class="ac-dot" style="background:#4f6ef7"></span>
        成绩分布
      </div>
      <div v-if="!scoreDist.length" class="ac-empty">暂无数据</div>
      <div v-else class="score-dist-chart">
        <div v-for="d in scoreDist" :key="d.range" class="sd-bar-group">
          <div class="sd-bar-wrap">
            <div class="sd-bar" :style="{height: Math.max(4, (d.count / maxScoreCount) * 100) + '%'}"></div>
          </div>
          <div class="sd-label">{{ d.range }}</div>
          <div class="sd-count">{{ d.count }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { TrendCharts, User, DataBoard, List, ChatLineSquare, Warning } from '@element-plus/icons-vue'
import api from '../api'

const stats = ref([])
const questionAcc = ref([])
const weakPoints = ref([])
const userAct = ref([])
const subjects = ref([])
const scoreDist = ref([])

const avatarColors = ['#4f6ef7','#22c55e','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#ec4899','#f97316']
const subjectColors = ['#4f6ef7','#22c55e','#f59e0b','#8b5cf6','#06b6d4','#ec4899','#f97316','#14b8a6']

function avatarColor(name) { let h = 0; for (let i = 0; i < name.length; i++) h += name.charCodeAt(i); return avatarColors[h % avatarColors.length] }

const maxSubjectCount = computed(() => Math.max(1, ...subjects.value.map(s => s.question_count)))
const maxWeakCount = computed(() => Math.max(1, ...weakPoints.value.map(w => w.wrong_total)))
const maxWrongCount = computed(() => Math.max(1, ...questionAcc.value.map(q => q.wrong_count)))
const maxScoreCount = computed(() => Math.max(1, ...scoreDist.value.map(d => d.count)))
const maxUserActivity = computed(() => Math.max(1, ...userAct.value.map(u => (u.practice_count || 0) + (u.exam_count || 0))))

onMounted(async () => {
  try {
    const [o, q, w, u, s] = await Promise.all([
      api.get('/analytics/overview'), api.get('/analytics/question-accuracy'),
      api.get('/analytics/weak-points'), api.get('/analytics/user-activity'),
      api.get('/analytics/subjects'),
      api.get('/analytics/score-distribution'),
    ])
    const d = o.data
    stats.value = [
      { label: '总用户', value: d.total_users, icon: User, color: '#4f6ef7' },
      { label: '题库总量', value: d.total_questions, icon: DataBoard, color: '#22c55e' },
      { label: '考试次数', value: d.total_exams, icon: List, color: '#f59e0b' },
      { label: '练习次数', value: d.total_practices, icon: TrendCharts, color: '#8b5cf6' },
      { label: '待处理反馈', value: d.total_feedbacks_pending, icon: ChatLineSquare, color: '#ef4444' },
      { label: '异常报告', value: d.total_abnormal, icon: Warning, color: '#ec4899' },
    ]
    questionAcc.value = q.data || []
    weakPoints.value = w.data || []
    userAct.value = u.data.items || []
    subjects.value = s.data || []
    scoreDist.value = (await api.get("/analytics/score-distribution")).data || []
  } catch {}
})
</script>

<style scoped>
.page-header { margin-bottom: var(--space-4); }
.ph-left { display: flex; align-items: center; gap: var(--space-3); }
.ph-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }

/* Stats */
.stats-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: var(--space-3); margin-bottom: var(--space-5); }
.stat-mini {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); display: flex; align-items: center; gap: var(--space-3);
  border: 1px solid var(--gray-100); border-left-width: 3px;
  transition: transform 0.15s, box-shadow 0.15s;
}
.stat-mini:hover { transform: translateY(-1px); box-shadow: var(--shadow-sm); }
.sm-icon { width: 42px; height: 42px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.sm-info { display: flex; flex-direction: column; min-width: 0; }
.sm-val { font-size: 22px; font-weight: 700; color: var(--gray-900); line-height: 1.1; }
.sm-lbl { font-size: 11px; color: var(--gray-500); margin-top: 2px; white-space: nowrap; }

/* Three-column grid */
.ana-three { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--space-3); }

/* Card */
.ana-card {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-4);
  box-shadow: var(--shadow-xs); border: 1px solid var(--gray-100);
}
.ac-head {
  font-size: 14px; font-weight: 600; color: var(--gray-800); margin-bottom: var(--space-3);
  display: flex; align-items: center; gap: 8px;
}
.ac-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.ac-count { margin-left: auto; font-size: 12px; font-weight: 400; color: var(--gray-400); }
.ac-empty { text-align: center; padding: 24px; color: var(--gray-400); font-size: 13px; }

/* List items */
.ac-list { display: flex; flex-direction: column; gap: 2px; }
.ac-item {
  display: flex; align-items: center; gap: var(--space-3);
  padding: 8px 6px; border-radius: var(--radius-sm); transition: background 0.15s;
}
.ac-item:hover { background: var(--gray-50); }
.ac-rank {
  width: 22px; height: 22px; border-radius: 6px;
  background: var(--gray-100); display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 11px; color: var(--gray-500); flex-shrink: 0;
}
.ac-rank.hot { background: #fef2f2; color: #ef4444; }
.ac-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.ac-name { font-size: 13px; color: var(--gray-800); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ac-bar-wrap { height: 3px; background: var(--gray-100); border-radius: 2px; overflow: hidden; }
.ac-bar { height: 100%; background: #ef4444; border-radius: 2px; transition: width 0.6s ease; }
.ac-bar.amber { background: #f59e0b; }
.ac-num { font-size: 12px; color: var(--gray-500); white-space: nowrap; flex-shrink: 0; font-weight: 500; }
.ac-num.danger { color: #ef4444; }
.ac-num.warning { color: #f59e0b; }

/* Subject distribution */
.subject-list { display: flex; flex-direction: column; gap: var(--space-3); }
.subject-item { display: flex; flex-direction: column; gap: 4px; }
.si-top { display: flex; justify-content: space-between; align-items: center; }
.si-name { font-size: 13px; color: var(--gray-800); font-weight: 500; }
.si-count { font-size: 12px; color: var(--gray-500); }
.si-bar-wrap { height: 6px; background: var(--gray-100); border-radius: 3px; overflow: hidden; }
.si-bar { height: 100%; border-radius: 3px; transition: width 0.6s ease; }

/* User activity */
.user-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--space-2); }
.user-mini {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-3); background: var(--gray-50); border-radius: var(--radius-md);
  transition: background 0.15s;
}
.user-mini:hover { background: var(--gray-100); }
.um-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 700; font-size: 14px; flex-shrink: 0;
}
.um-info { flex: 1; min-width: 0; }
.um-name { font-weight: 600; font-size: 13px; color: var(--gray-800); }
.um-stat { display: flex; gap: 6px; margin-top: 4px; }
.um-tag {
  font-size: 11px; padding: 1px 8px; border-radius: 99px; font-weight: 500;
}
.um-tag.practice { background: #eef2ff; color: #4f6ef7; }
.um-tag.exam { background: #fef3c7; color: #d97706; }
.um-right { text-align: right; flex-shrink: 0; display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.um-bar-wrap { width: 60px; height: 3px; background: var(--gray-200); border-radius: 2px; overflow: hidden; }
.um-bar { height: 100%; background: var(--color-primary); border-radius: 2px; }
.um-time { font-size: 11px; color: var(--gray-400); white-space: nowrap; }

.score-dist-chart { display: flex; gap: 6px; align-items: flex-end; height: 160px; padding-top: 10px; }
.sd-bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.sd-bar-wrap { height: 120px; width: 100%; display: flex; align-items: flex-end; justify-content: center; }
.sd-bar { width: 80%; max-width: 40px; background: linear-gradient(180deg, #4f6ef7, #818cf8); border-radius: 4px 4px 0 0; transition: height 0.5s ease; min-height: 4px; }
.sd-label { font-size: 10px; color: var(--gray-500); text-align: center; }
.sd-count { font-size: 11px; font-weight: 600; color: var(--gray-700); }

/* Responsive */
@media (max-width: 1200px) { .ana-three { grid-template-columns: 1fr 1fr; } .ana-three .subject-card { grid-column: 1 / -1; } }
@media (max-width: 768px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); gap: var(--space-2); }
  .stat-mini { padding: var(--space-3); }
  .sm-val { font-size: 18px; }
  .ana-three { grid-template-columns: 1fr; }
  .user-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) { .stats-row { grid-template-columns: 1fr 1fr; } }
</style>

<style>
/* Dark mode for analytics */
[data-theme="dark"] .stat-mini { background: #212226; border-color: #2a2b30; }
[data-theme="dark"] .stat-mini:hover { background: #2a2b30; }
[data-theme="dark"] .sm-val { color: #e0e2e5; }
[data-theme="dark"] .sm-lbl { color: #8a8c92; }
[data-theme="dark"] .ana-card { background: #212226; border-color: #2a2b30; }
[data-theme="dark"] .ac-head { color: #e0e2e5; }
[data-theme="dark"] .ac-count { color: #6b6d73; }
[data-theme="dark"] .ac-name { color: #c3c5c9; }
[data-theme="dark"] .ac-rank { background: #2a2b30; color: #8a8c92; }
[data-theme="dark"] .ac-rank.hot { background: rgba(239,68,68,0.15); color: #f87171; }
[data-theme="dark"] .ac-item:hover { background: #2a2b30; }
[data-theme="dark"] .ac-bar-wrap { background: #2a2b30; }
[data-theme="dark"] .ac-num { color: #8a8c92; }
[data-theme="dark"] .ac-num.danger { color: #f87171; }
[data-theme="dark"] .ac-num.warning { color: #fbbf24; }
[data-theme="dark"] .si-name { color: #c3c5c9; }
[data-theme="dark"] .si-count { color: #8a8c92; }
[data-theme="dark"] .si-bar-wrap { background: #2a2b30; }
[data-theme="dark"] .user-mini { background: #1a1b1e; }
[data-theme="dark"] .user-mini:hover { background: #2a2b30; }
[data-theme="dark"] .um-name { color: #e0e2e5; }
[data-theme="dark"] .um-tag.practice { background: rgba(79,110,247,0.15); color: #818cf8; }
[data-theme="dark"] .um-tag.exam { background: rgba(245,158,11,0.15); color: #fbbf24; }
[data-theme="dark"] .um-bar-wrap { background: #2a2b30; }
[data-theme="dark"] .um-time { color: #6b6d73; }
[data-theme="dark"] .ac-empty { color: #6b6d73; }
[data-theme="dark"] .page-header h2 { color: #e0e2e5; }
[data-theme="dark"] .page-header .ph-sub { color: #6b6d73; }
</style>
