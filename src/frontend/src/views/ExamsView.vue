<template>
  <div class="page-container">
    <div class="page-header"><h2>{{ isManageMode ? '试卷管理' : '考试管理' }}</h2>
      <el-button v-if="isManageMode" type="primary" @click="showCreateDialog">+ 创建试卷</el-button>
    </div>

    <!-- Admin: exam list -->
    <template v-if="isManageMode">
      <el-tabs v-model="tab">
        <el-tab-pane label="试卷列表" name="list">
          <div v-if="!items.length" class="empty-state"><el-empty description="暂无试卷" /></div>
          <div v-else class="exam-card-list">
            <div v-for="e in items" :key="e.id" class="exam-card" :class="{published: e.is_published}">
              <div class="ec-left">
                <div class="ec-icon" :class="e.mode">{{ e.mode==='formal'?'🔒':'📝' }}</div>
              </div>
              <div class="ec-body">
                <div class="ec-title">{{ e.title }}</div>
                <div class="ec-meta">
                  <el-tag :type="e.mode==='formal'?'danger':''" size="small">{{ e.mode==='formal'?'正式':'模拟' }}</el-tag>
                  <span>{{ e.question_count || '?' }}题</span>
                  <span>{{ e.duration_minutes }}分钟</span>
                  <span>{{ e.total_score }}分/{{ e.pass_score }}及格</span>
                  <el-tag :type="e.is_published?'success':'info'" size="small">{{ e.is_published?'已发布':'未发布' }}</el-tag>
                </div>
              </div>
              <div class="ec-actions">
                <el-button size="small" @click="togglePublish(e)">{{ e.is_published?'下架':'发布' }}</el-button>
                <el-button size="small" type="primary" @click="viewResults(e)">成绩</el-button>
                <el-button size="small" type="danger" @click="delExam(e.id)">删除</el-button>
              </div>
            </div>
          </div>
          <el-pagination v-if="total>pageSize" v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev,pager,next" @current-change="load" style="justify-content:flex-end;margin-top:12px" size="small" />
        </el-tab-pane>
        <el-tab-pane label="参加考试" name="take">
          <div class="invite-section">
            <div class="invite-row">
              <el-input v-model="inviteCode" placeholder="输入6位邀请码参加私密考试" maxlength="6" class="invite-input" clearable @keyup.enter="verifyInvite" />
              <el-button type="primary" @click="verifyInvite" :loading="inviting">验证加入</el-button>
            </div>
          </div>
          <ExamListView :exams="publishedExams" :my-results="myResults" @take="goTake" @retry="retryExam" @reapply="applyRetake" />
        </el-tab-pane>
      </el-tabs>
    </template>

    <!-- Student: take exam only -->
    <template v-else>
      <div class="invite-section">
        <div class="invite-row">
          <el-input v-model="inviteCode" placeholder="输入6位邀请码参加私密考试" maxlength="6" class="invite-input" clearable @keyup.enter="verifyInvite" />
          <el-button type="primary" @click="verifyInvite" :loading="inviting">验证加入</el-button>
        </div>
      </div>
      <ExamListView :exams="publishedExams" :my-results="myResults" @take="goTake" @retry="retryExam" @reapply="applyRetake" />
    </template>

    <!-- Create exam dialog (unchanged) -->
    <el-dialog v-model="createDialog.visible" title="创建试卷" width="680px" :close-on-click-modal="false">
      <div v-if="!createDialog.step2" style="margin-bottom:16px">
        <div style="font-size:15px;font-weight:600;margin-bottom:16px">选择组卷方式</div>
        <div class="mode-grid">
          <div v-for="m in modes" :key="m.key" class="mode-card" @click="selectMode(m)">
            <div class="mode-icon" :style="{background:m.bg,color:m.color}">{{ m.icon }}</div>
            <div class="mode-name">{{ m.name }}</div>
            <div class="mode-desc">{{ m.desc }}</div>
          </div>
        </div>
      </div>
      <div v-else>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
          <el-button text @click="createDialog.step2=false"><el-icon><ArrowLeft /></el-icon></el-button>
          <span style="font-size:15px;font-weight:600">{{ createDialog.mode?.name }}</span>
        </div>
        <el-form label-width="80px" size="default">
          <el-form-item label="试卷标题"><el-input v-model="gen.title" placeholder="请输入试卷标题" /></el-form-item>
          <el-form-item label="试卷描述"><el-input v-model="gen.description" type="textarea" :rows="2" placeholder="可选" /></el-form-item>
          <el-form-item label="试卷类型"><el-radio-group v-model="gen.mode"><el-radio value="mock">模拟考试</el-radio><el-radio value="formal">正式考试</el-radio></el-radio-group></el-form-item>
          <el-form-item label="考试时长"><el-input-number v-model="gen.duration_minutes" :min="10" :max="300" /> 分钟</el-form-item>
          <el-form-item label="总分/及格"><el-input-number v-model="gen.total_score" :min="10" :max="200" /> / <el-input-number v-model="gen.pass_score" :min="10" :max="200" /> 分</el-form-item>
          <el-form-item label="科目范围"><el-select v-model="gen.subject_ids" multiple placeholder="不限"><el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" /></el-select></el-form-item>
          <el-form-item label="题目数量"><el-input-number v-model="gen.count" :min="5" :max="200" /> 题</el-form-item>
          <el-form-item label="切屏限制"><el-input-number v-model="gen.max_tab_switches" :min="1" :max="10" /> 次（超过强制交卷）</el-form-item>
          <el-form-item label="考试有效期"><el-date-picker v-model="gen.time_range" type="datetimerange" range-separator="至" start-placeholder="开始时间" end-placeholder="结束时间" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%" /></el-form-item>
          <el-form-item label="邀请码"><el-input v-model="gen.invite_code" placeholder="可选，6位邀请码，留空则公开" maxlength="6" style="width:160px" @input="gen.invite_code=gen.invite_code.toUpperCase()" /></el-form-item>
        </el-form>
      </div>
      <template #footer v-if="createDialog.step2">
        <el-button @click="createDialog.step2=false">取消</el-button>
        <el-button type="primary" @click="doGenerate" :loading="generating">生成试卷</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import ExamListView from '../components/ExamListView.vue'

const route = useRoute(); const router = useRouter(); const auth = useAuthStore()
const isManageMode = route.path === '/exams-manage'
const tab = ref(isManageMode ? 'list' : 'take')
const items = ref([]); const publishedExams = ref([]); const myResults = ref([])
const inviteCode = ref(''); const inviting = ref(false)
const total = ref(0); const page = ref(1); const pageSize = 20
const subjects = ref([]); const generating = ref(false)

const createDialog = reactive({ visible: false, step2: false, mode: null })
const gen = reactive({ title: '', description: '', mode: 'mock', duration_minutes: 60, total_score: 100, pass_score: 60, subject_ids: [], count: 30, max_tab_switches: 3, time_range: null, invite_code: '' })

const modes = [
  { key: 'fast', icon: '⚡', name: '快速组卷', desc: '选科目+题数，一键生成', bg: '#FEF3C7', color: '#D97706' },
  { key: 'mock', icon: '📵', name: '模拟考试', desc: '预设 50题/120分钟', bg: '#DBEAFE', color: '#2563EB' },
  { key: 'chapter', icon: '📼', name: '章节专项', desc: '按章节分配题目数量', bg: '#D1FAE5', color: '#059669' },
  { key: 'wrong', icon: '🔄', name: '错题强化', desc: '从用户高频错题中抽取', bg: '#FEE2E2', color: '#DC2626' },
  { key: 'manual', icon: '🎆', name: '手动选题', desc: '从题库逐题挑选', bg: '#F3E8FF', color: '#7C3AED' },
]

onMounted(async () => {
  try { const s = await api.get('/subjects'); subjects.value = s.data } catch { subjects.value = [] }
  try { await load() } catch { items.value = []; publishedExams.value = [] }
  await loadMyResults()
})
async function loadMyResults() {
  try { const { data } = await api.get('/exams/my-results'); myResults.value = data || [] } catch { myResults.value = [] }
}
function showCreateDialog() {
  createDialog.visible = true; createDialog.step2 = false; createDialog.mode = null
  gen.title = ''; gen.description = ''; gen.subject_ids = []; gen.count = 30
  gen.time_range = null; gen.invite_code = ''
}
function selectMode(m) {
  createDialog.mode = m; createDialog.step2 = true
  if (m.key === 'mock') { gen.title = '模拟考试'; gen.duration_minutes = 120; gen.count = 50 }
  else if (m.key === 'fast') { gen.title = ''; gen.count = 30; gen.duration_minutes = 60 }
  else { gen.title = m.name + '试卷' }
}
async function doGenerate() {
  if (!gen.title) { ElMessage.warning('请输入试卷标题'); return }; generating.value = true
  try {
    await api.post('/exams/generate', {
      title: gen.title, description: gen.description, mode: gen.mode,
      duration_minutes: gen.duration_minutes, total_score: gen.total_score, pass_score: gen.pass_score,
      subject_ids: gen.subject_ids, chapter_ids: [],
      type_config: { single: Math.round(gen.count*0.6), multi: Math.round(gen.count*0.15), truefalse: Math.round(gen.count*0.2), composite: Math.round(gen.count*0.05) },
      difficulty_min: 1, difficulty_max: 5, max_tab_switches: gen.max_tab_switches,
      start_time: gen.time_range?.[0] || null, end_time: gen.time_range?.[1] || null,
      invite_code: gen.invite_code || null,
    })
    ElMessage.success('试卷创建成功'); createDialog.visible = false; load()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '创建失败') }
  generating.value = false
}
async function load() {
  try {
    const { data } = await api.get('/exams', { params: { page: page.value, page_size: pageSize } })
    items.value = data.items || []; total.value = data.total || 0
    const mock = await api.get('/exams', { params: { page: 1, page_size: 100, mode: 'mock' } })
    const formal = await api.get('/exams', { params: { page: 1, page_size: 100, mode: 'formal' } })
    publishedExams.value = [...(mock.data.items||[]),...(formal.data.items||[])].filter(e=>e.is_published)
  } catch { items.value = []; publishedExams.value = [] }
}
async function togglePublish(row) {
  await api.put(`/exams/${row.id}/publish?is_published=${!row.is_published}`)
  row.is_published = !row.is_published; ElMessage.success(row.is_published ? '已发布' : '已下架')
}
async function delExam(id) {
  try { await ElMessageBox.confirm('确定删除此试卷？','确认',{type:'warning'}) } catch { return }
  await api.delete(`/exams/${id}`); load(); ElMessage.success('已删除')
}
function viewResults(row) { router.push(`/exam/${row.id}/results`) }
function goTake(examId) { router.push(`/exam/${examId}/take`) }
async function verifyInvite() {
  const code = inviteCode.value.trim().toUpperCase()
  if (!code || code.length < 6) { ElMessage.warning('请输入6位邀请码'); return }
  inviting.value = true
  try {
    const { data } = await api.post(`/exams/verify-invite-code?code=${code}`)
    if (data.code === 404) { ElMessage.error(data.message || '邀请码无效或未发布'); return }
    if (data.code === 403) { ElMessage.warning(data.message || '考试未开放或已结束'); return }
    if (data.code === 400) { ElMessage.warning(data.message || '已参加过此考试,请申请重考'); return }
    ElMessage.success('验证成功，跳转到考试')
    const examId = data.data?.id || data.exam_id
    if (!examId) { ElMessage.error('考试信息异常'); return }
    router.push(`/exam/${examId}/take`)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '验证失败')
  } finally { inviting.value = false }
}
function retryExam(examId) {
  ElMessageBox.confirm('确定重做此模拟考试？之前的成绩将被覆盖。','确认重做',{type:'info'})
    .then(() => router.push(`/exam/${examId}/take?retry=1`)).catch(() => {})
}
async function applyRetake(examId) {
  try {
    await ElMessageBox.confirm('申请重考将提交给管理员审核，确定申请？','申请重考',{type:'warning'})
    await api.post(`/exams/${examId}/apply-retake`); ElMessage.success('重考申请已提交，请等待管理员审核')
  } catch {}
}
</script>

<style scoped>
.exam-card-list { display: flex; flex-direction: column; gap: var(--space-2); }
.exam-card {
  display: flex; align-items: center; gap: var(--space-4);
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4);
  box-shadow: var(--shadow-xs); transition: all var(--transition-fast);
}
.exam-card:hover { box-shadow: var(--shadow-sm); }
.exam-card.published { border-left: 3px solid #22c55e; }
.ec-left { flex-shrink: 0; }
.ec-icon { width: 40px; height: 40px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 18px; background: var(--gray-50); }
.ec-icon.formal { background: var(--color-danger-light); }
.ec-body { flex: 1; min-width: 0; }
.ec-title { font-weight: var(--font-semibold); font-size: var(--text-base); color: var(--gray-900); margin-bottom: 4px; }
.ec-meta { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; font-size: var(--text-sm); color: var(--gray-500); }
.ec-actions { display: flex; gap: 4px; flex-shrink: 0; }

.mode-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.mode-card { border: 2px solid var(--gray-100); border-radius: var(--radius-lg); padding: 20px 16px; text-align: center; cursor: pointer; transition: all var(--transition-fast); }
.mode-card:hover { border-color: var(--color-primary); transform: translateY(-2px); box-shadow: 0 4px 12px rgba(79,110,247,0.12); }
.mode-icon { font-size: 28px; width: 52px; height: 52px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; }
.mode-name { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.mode-desc { font-size: 12px; color: var(--gray-500); }

@media (max-width: 768px) {
  .exam-card { flex-direction: column; align-items: flex-start; }
  .ec-actions { width: 100%; justify-content: flex-end; }
  .mode-grid { grid-template-columns: 1fr; }
}

.invite-section { margin-bottom: var(--space-6); }
.invite-row { display: flex; gap: var(--space-3); max-width: 480px; }
.invite-input { flex: 1; }

/* Dark mode */
</style>

<style>
[data-theme="dark"] .exam-card { background: var(--gray-100) !important; color: var(--gray-300) !important; }
[data-theme="dark"] .exam-card:hover { background: var(--gray-200) !important; }
[data-theme="dark"] .ec-icon { background: var(--gray-200) !important; }
[data-theme="dark"] .ec-title { color: var(--gray-300) !important; }
[data-theme="dark"] .ec-desc { color: var(--gray-400) !important; }
[data-theme="dark"] .mode-card { border-color: var(--gray-200) !important; color: var(--gray-300) !important; background: var(--gray-100) !important; }
[data-theme="dark"] .mode-card:hover { border-color: var(--color-primary) !important; background: rgba(79,110,247,0.08) !important; }
[data-theme="dark"] .mode-icon { opacity: 0.9; }
</style>
