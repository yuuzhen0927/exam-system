<template>
  <div class="dash-root">
    <!-- Welcome banner -->
    <div class="welcome-banner">
      <div class="welcome-text">
        <div class="welcome-date">{{ todayStr }} {{ weekDay }}</div>
        <h2>{{ greeting }}，{{ auth.user?.fullname || auth.user?.username || '用户' }} 👋</h2>
        <p>{{ auth.isManager ? '今天也要高效组织培训考核哦！' : '今天也要努力学习哦！' }}</p>
      </div>
      <div class="welcome-quick">
        <el-button v-if="auth.isManager" @click="router.push('/questions')"><el-icon><Edit /></el-icon> 导入题库</el-button>
        <el-button v-if="auth.isManager" type="primary" @click="router.push('/exams-manage')"><el-icon><Plus /></el-icon> 创建考试</el-button>
        <el-button v-if="!auth.isManager" type="primary" @click="router.push('/practice')">开始练习</el-button>
        <el-button v-if="!auth.isManager" @click="router.push('/exams')">参加考试</el-button>
      </div>
    </div>

    <!-- Stats row -->
    <div class="stats-row">
      <div class="stat-card" v-for="s in statItems" :key="s.label">
        <div class="stat-icon-wrap" :style="{ background: s.bg, color: s.color }">
          <el-icon :size="20"><component :is="s.icon" /></el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-num">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-sub">{{ s.sub }}</div>
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="section-card">
      <div class="section-header">
        <span class="section-title">快捷入口</span>
      </div>
      <div class="actions-grid">
        <div class="action-card" v-for="a in actionItems" :key="a.label" @click="router.push(a.to)">
          <div class="action-icon" :style="{ background: a.bg, color: a.color }">
            <el-icon :size="22"><component :is="a.icon" /></el-icon>
          </div>
          <div class="action-label">{{ a.label }}</div>
        </div>
      </div>
    </div>

    <!-- Announcements cards -->
    <div v-if="announcements.length" class="section-card">
      <div class="section-header">
        <span class="section-title">系统公告</span>
        <el-button text size="small" @click="router.push('/announcements')">查看全部 <el-icon><ArrowRight /></el-icon></el-button>
      </div>
      <div class="ann-cards">
        <div v-for="a in announcements.slice(0,3)" :key="a.id" class="ann-card">
          <div class="ann-card-header">
            <el-tag v-if="a.is_pinned" type="danger" size="small" effect="dark">置顶</el-tag>
            <span class="ann-card-title">{{ a.title }}</span>
          </div>
          <div class="ann-card-content">{{ a.content }}</div>
          <div v-if="a.created_at" class="ann-card-time">{{ new Date(a.created_at).toLocaleDateString('zh-CN') }}</div>
        </div>
      </div>
    </div>

    <!-- Bottom grid -->
    <div class="bottom-grid">
      <!-- Recent exams (table style) -->
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">最近考试</span>
          <el-button text size="small" @click="router.push(auth.isManager ? '/results' : '/my-results')">查看全部 <el-icon><ArrowRight /></el-icon></el-button>
        </div>
        <div v-if="recentExams.length" class="exam-table">
          <div class="exam-table-header">
            <span class="etc-name">考试名称</span>
            <span class="etc-status">状态</span>
            <span class="etc-time">考试时间</span>
            <span class="etc-action">操作</span>
          </div>
          <div v-for="e in recentExams.slice(0,5)" :key="e.id" class="exam-table-row">
            <span class="etc-name">
              <el-icon class="etc-icon" :style="{color: e.passed ? '#10b981' : '#ef4444'}"><Document /></el-icon>
              {{ e.exam_title }}
            </span>
            <span class="etc-status">
              <span class="status-dot" :class="e.passed ? 'passed' : 'failed'"></span>
              {{ e.passed ? '通过' : '未通过' }}
            </span>
            <span class="etc-time">{{ e.finished_at?.substring(0,16).replace('T',' ') }}</span>
            <span class="etc-action">
              <el-button text size="small" type="primary" @click.stop="router.push('/my-results')">查看</el-button>
            </span>
          </div>
        </div>
        <div v-else class="panel-empty">
          <el-empty description="暂无考试记录" :image-size="80">
            <el-button type="primary" size="small" @click="router.push('/exams')">去参加考试</el-button>
          </el-empty>
        </div>
      </div>

      <!-- Right column: overview + todo -->
      <div class="right-col">
        <!-- System overview (admin) -->
        <div class="panel" v-if="auth.isManager && overview">
          <div class="panel-header"><span class="panel-title">数据概览</span></div>
          <div class="overview-grid">
            <div class="ov-item" v-for="o in overviewItems" :key="o.label">
              <div class="ov-num" :style="{color: o.color}">{{ o.value }}</div>
              <div class="ov-label">{{ o.label }}</div>
            </div>
          </div>
        </div>

        <!-- Todo / Trend -->
        <div class="panel">
          <div class="panel-header"><span class="panel-title">{{ auth.isManager ? '待办事项' : '学习趋势' }}</span></div>
          <div v-if="auth.isManager" class="todo-list">
            <div class="todo-item" v-if="overview?.total_feedbacks_pending > 0" @click="router.push('/feedback-manage')">
              <span class="todo-dot warning"></span>
              <span class="todo-text">{{ overview.total_feedbacks_pending }} 份待处理反馈</span>
              <el-icon class="todo-arrow"><ArrowRight /></el-icon>
            </div>
            <div class="todo-item" v-if="overview?.total_abnormal > 0" @click="router.push('/abnormal')">
              <span class="todo-dot danger"></span>
              <span class="todo-text">{{ overview.total_abnormal }} 条异常报告</span>
              <el-icon class="todo-arrow"><ArrowRight /></el-icon>
            </div>
            <div class="todo-item" @click="router.push('/exams-manage')">
              <span class="todo-dot info"></span>
              <span class="todo-text">管理试卷和题库</span>
              <el-icon class="todo-arrow"><ArrowRight /></el-icon>
            </div>
            <div class="todo-item" @click="router.push('/users')">
              <span class="todo-dot success"></span>
              <span class="todo-text">管理用户和角色</span>
              <el-icon class="todo-arrow"><ArrowRight /></el-icon>
            </div>
            <div v-if="overview?.total_feedbacks_pending === 0 && overview?.total_abnormal === 0" class="todo-empty">
              <el-icon :size="28" color="#22c55e"><CircleCheck /></el-icon>
              <span>暂无待处理事项</span>
            </div>
          </div>
          <div v-else>
            <div ref="trendChartEl" class="chart-container"></div>
            <div v-if="!hasActivity" class="panel-empty" style="padding:16px">
              <el-empty description="暂无学习记录" :image-size="60">
                <el-button type="primary" size="small" @click="router.push('/practice')">去练习</el-button>
              </el-empty>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import * as echarts from 'echarts'
import {
  Edit, Plus, ArrowRight, Document, CircleCheck,
  User, Files, Timer, Warning, Collection, VideoCamera,
  Reading, Star, DataLine, Setting, Trophy, Notebook
} from '@element-plus/icons-vue'

const auth = useAuthStore()
const router = useRouter()
const announcements = ref([])
const userStats = ref({})
const overview = ref(null)
const recentExams = ref([])
const activityData = ref([])
const hasActivity = ref(false)
const trendChartEl = ref(null)
let trendChart = null

// Greeting
const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})
const todayStr = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${String(d.getMonth()+1).padStart(2,'0')}月${String(d.getDate()).padStart(2,'0')}日`
})
const weekDay = computed(() => {
  const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
  return days[new Date().getDay()]
})

// Stats
const statItems = computed(() => {
  if (auth.isManager && overview.value) {
    return [
      { icon: User, label: '总用户', value: overview.value.total_users || 0, sub: '已注册人员', color: '#4f6ef7', bg: '#eef2ff' },
      { icon: Files, label: '题库总量', value: overview.value.total_questions || 0, sub: '累计题目数', color: '#10b981', bg: '#ecfdf5' },
      { icon: Timer, label: '本月考试', value: overview.value.total_exams_this_month || 0, sub: '本月进行中', color: '#f59e0b', bg: '#fffbeb' },
      { icon: Warning, label: '待处理', value: (overview.value.total_feedbacks_pending || 0) + (overview.value.total_abnormal || 0), sub: '需及时处理', color: '#ef4444', bg: '#fef2f2' },
    ]
  }
  return [
    { icon: Files, label: '总做题量', value: userStats.value.total_questions || 0, sub: '累计完成题目', color: '#4f6ef7', bg: '#eef2ff' },
    { icon: DataLine, label: '正确率', value: (userStats.value.accuracy || 0) + '%', sub: '平均正确率', color: '#10b981', bg: '#ecfdf5' },
    { icon: Warning, label: '错题数', value: userStats.value.total_wrong || 0, sub: '待复习题目', color: '#ef4444', bg: '#fef2f2' },
    { icon: Trophy, label: '考试次数', value: recentExams.value.length, sub: '已完成考试', color: '#f59e0b', bg: '#fffbeb' },
  ]
})

// Overview items (admin)
const overviewItems = computed(() => {
  if (!overview.value) return []
  return [
    { label: '用户数', value: overview.value.total_users || 0, color: '#4f6ef7' },
    { label: '题目总量', value: overview.value.total_questions || 0, color: '#10b981' },
    { label: '待处理反馈', value: overview.value.total_feedbacks_pending || 0, color: '#f59e0b' },
    { label: '异常报告', value: overview.value.total_abnormal || 0, color: '#ef4444' },
  ]
})

// Quick actions
const actionItems = computed(() => {
  const base = [
    { icon: Collection, label: '练习中心', to: '/practice', bg: '#eef2ff', color: '#4f6ef7' },
    { icon: Files, label: '参加考试', to: '/exams', bg: '#ecfdf5', color: '#10b981' },
    { icon: Warning, label: '错题本', to: '/wrongbook', bg: '#fef2f2', color: '#ef4444' },
    { icon: Trophy, label: '我的证书', to: '/certificates', bg: '#fffbeb', color: '#f59e0b' },
  ]
  if (auth.isManager) {
    base.push(
      { icon: Files, label: '题库管理', to: '/questions', bg: '#f5f3ff', color: '#8b5cf6' },
      { icon: Notebook, label: '试卷管理', to: '/exams-manage', bg: '#fefce8', color: '#ca8a04' },
      { icon: User, label: '人员管理', to: '/users', bg: '#f0fdfa', color: '#14b8a6' },
      { icon: DataLine, label: '考试报表', to: '/analytics', bg: '#fdf4ff', color: '#ec4899' },
    )
  } else {
    base.push(
      { icon: VideoCamera, label: '视频课程', to: '/videos', bg: '#fdf4ff', color: '#ec4899' },
      { icon: Reading, label: '学习资料', to: '/resources', bg: '#f0fdfa', color: '#14b8a6' },
      { icon: Star, label: '收藏夹', to: '/favorites', bg: '#fefce8', color: '#ca8a04' },
      { icon: Notebook, label: '笔记', to: '/notes', bg: '#f5f3ff', color: '#8b5cf6' },
    )
  }
  return base
})

// Chart
function buildTrendChart() {
  if (!trendChartEl.value) return
  if (!activityData.value.length) { hasActivity.value = false; return }
  hasActivity.value = true
  if (!trendChart) trendChart = echarts.init(trendChartEl.value)
  const dates = activityData.value.map(d => d.date.substring(5))
  const counts = activityData.value.map(d => d.count)
  trendChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}<br/>做题量: {c} 题' },
    grid: { left: 36, right: 12, top: 8, bottom: 24 },
    xAxis: { type: 'category', data: dates, axisLabel: { fontSize: 10, color: '#90939a' }, axisLine: { lineStyle: { color: '#eee' } } },
    yAxis: { type: 'value', minInterval: 1, axisLabel: { fontSize: 10, color: '#90939a' }, splitLine: { lineStyle: { color: '#f5f5f5' } } },
    series: [{
      type: 'bar', data: counts,
      itemStyle: { borderRadius: [3,3,0,0], color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#818cf8'},{offset:1,color:'#4f6ef7'}]) },
      barMaxWidth: 14,
    }],
  })
}

watch(() => auth.theme, () => {
  nextTick(() => { trendChart?.dispose(); trendChart = null; buildTrendChart() })
})

onMounted(async () => {
  try {
    const [anns, s, e] = await Promise.all([
      api.get('/announcements?published_only=true&page_size=5').catch(() => ({ data: { items: [] } })),
      api.get('/practice/stats').catch(() => ({ data: {} })),
      api.get('/exams/my-results').catch(() => ({ data: [] })),
    ])
    announcements.value = anns.data.items || []
    userStats.value = s.data
    recentExams.value = Array.isArray(e.data) ? e.data.slice(0, 5) : []
    activityData.value = s.data.daily_activity || []
    nextTick(() => buildTrendChart())
  } catch {}
  if (auth.isManager) {
    try { const o = await api.get('/analytics/overview'); overview.value = o.data } catch {}
  }
})
</script>

<style scoped>
.dash-root { max-width: 1100px; margin: 0 auto; padding: var(--space-4); }

/* Welcome banner */
.welcome-banner {
  display: flex; justify-content: space-between; align-items: center;
  background: linear-gradient(135deg, #4f6ef7 0%, #818cf8 100%);
  border-radius: var(--radius-lg); padding: 28px 32px; margin-bottom: var(--space-4); color: #fff;
}
.welcome-date { font-size: 13px; opacity: 0.8; margin-bottom: 6px; }
.welcome-text h2 { font-size: 22px; font-weight: 700; margin: 0 0 4px; }
.welcome-text p { font-size: 14px; opacity: 0.85; margin: 0; }
.welcome-quick { display: flex; gap: 10px; }
.welcome-quick .el-button { background: rgba(255,255,255,0.15); color: #fff; border: 1px solid rgba(255,255,255,0.25); border-radius: 8px; }
.welcome-quick .el-button:hover { background: rgba(255,255,255,0.25); }
.welcome-quick .el-button--primary { background: #fff; color: #4f6ef7; border-color: #fff; }
.welcome-quick .el-button--primary:hover { background: #f0f0ff; }

/* Stats */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); margin-bottom: var(--space-4); }
.stat-card {
  display: flex; align-items: center; gap: 14px;
  background: var(--gray-25); border-radius: var(--radius-lg); padding: 18px 16px;
  transition: all 0.2s; border: 1px solid var(--gray-100);
}
.stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.stat-icon-wrap {
  width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-body { display: flex; flex-direction: column; }
.stat-num { font-size: 24px; font-weight: 700; color: var(--gray-900); line-height: 1.2; }
.stat-label { font-size: 13px; color: var(--gray-600); margin-top: 2px; }
.stat-sub { font-size: 11px; color: var(--gray-400); margin-top: 1px; }

/* Section card */
.section-card {
  background: var(--gray-25); border-radius: var(--radius-lg); padding: 20px 24px;
  margin-bottom: var(--space-4); border: 1px solid var(--gray-100);
}
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.section-title { font-size: 16px; font-weight: 600; color: var(--gray-800); }

/* Actions */
.actions-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.action-card {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  background: var(--gray-50); border-radius: var(--radius-lg); padding: 18px 12px;
  cursor: pointer; transition: all 0.2s; text-align: center;
}
.action-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); background: #fff; }
.action-icon {
  width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
}
.action-label { font-size: 13px; font-weight: 600; color: var(--gray-700); }

/* Announcements */
.ann-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.ann-card {
  background: var(--gray-50); border-radius: var(--radius-md); padding: 14px;
  border: 1px solid var(--gray-100); transition: all 0.2s; cursor: default;
}
.ann-card:hover { border-color: #f59e0b; box-shadow: 0 2px 8px rgba(245,158,11,0.08); }
.ann-card-header { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; }
.ann-card-title { font-weight: 600; color: var(--gray-800); font-size: 13px; }
.ann-card-content { color: var(--gray-500); font-size: 12px; line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.ann-card-time { margin-top: 8px; font-size: 11px; color: var(--gray-400); }

/* Bottom grid */
.bottom-grid { display: grid; grid-template-columns: 1.2fr 1fr; gap: var(--space-4); }
.right-col { display: flex; flex-direction: column; gap: var(--space-4); }
.panel { background: var(--gray-25); border-radius: var(--radius-lg); padding: 20px 24px; border: 1px solid var(--gray-100); }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.panel-title { font-size: 15px; font-weight: 600; color: var(--gray-800); }

/* Exam table */
.exam-table { width: 100%; }
.exam-table-header, .exam-table-row { display: flex; align-items: center; padding: 10px 0; }
.exam-table-header { border-bottom: 2px solid var(--gray-100); font-size: 12px; font-weight: 600; color: var(--gray-500); }
.exam-table-row { border-bottom: 1px solid var(--gray-100); font-size: 13px; transition: background 0.15s; }
.exam-table-row:last-child { border-bottom: none; }
.exam-table-row:hover { background: var(--gray-50); border-radius: 6px; }
.etc-name { flex: 1; display: flex; align-items: center; gap: 8px; color: var(--gray-700); font-weight: 500; }
.etc-icon { flex-shrink: 0; }
.etc-status { width: 80px; display: flex; align-items: center; gap: 6px; color: var(--gray-600); }
.etc-time { width: 160px; color: var(--gray-400); font-size: 12px; }
.etc-action { width: 60px; text-align: right; }
.status-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.status-dot.passed { background: #10b981; }
.status-dot.failed { background: #ef4444; }

/* Overview */
.overview-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.ov-item { text-align: center; padding: 12px; background: var(--gray-50); border-radius: 8px; }
.ov-num { font-size: 22px; font-weight: 700; }
.ov-label { font-size: 12px; color: var(--gray-500); margin-top: 2px; }

/* Todo list */
.todo-list { display: flex; flex-direction: column; gap: 2px; }
.todo-item {
  display: flex; align-items: center; gap: 10px; padding: 10px 12px;
  border-radius: 8px; cursor: pointer; transition: background 0.15s;
}
.todo-item:hover { background: var(--gray-50); }
.todo-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.todo-dot.warning { background: #f59e0b; }
.todo-dot.danger { background: #ef4444; }
.todo-dot.info { background: #4f6ef7; }
.todo-dot.success { background: #10b981; }
.todo-text { flex: 1; font-size: 13px; color: var(--gray-700); }
.todo-arrow { color: var(--gray-400); font-size: 14px; }
.todo-empty { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 20px; color: var(--gray-400); font-size: 13px; }

.chart-container { height: 180px; }
.panel-empty { text-align: center; padding: 20px 16px; }

/* Responsive */
@media (max-width: 768px) {
  .welcome-banner { flex-direction: column; gap: 12px; text-align: center; padding: 16px; }
  .welcome-text h2 { font-size: 18px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); gap: 8px; }
  .stat-card { padding: 12px; gap: 10px; }
  .stat-icon-wrap { width: 38px; height: 38px; border-radius: 10px; }
  .stat-num { font-size: 20px; }
  .stat-label { font-size: 12px; }
  .stat-sub { display: none; }
  .actions-grid { grid-template-columns: repeat(4, 1fr); gap: 8px; }
  .action-card { padding: 12px 8px; }
  .action-label { font-size: 11px; }
  .ann-cards { grid-template-columns: 1fr; }
  .bottom-grid { grid-template-columns: 1fr; }
  .etc-time { display: none; }
  .section-card { padding: 14px 16px; }
}
@media (max-width: 480px) {
  .actions-grid { grid-template-columns: repeat(2, 1fr); }
  .welcome-quick { width: 100%; }
  .welcome-quick .el-button { flex: 1; }
}
</style>
