<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" :style="{background: isManage ? '#fef3c7' : '#e8f0fe', color: isManage ? '#d97706' : '#4f6ef7'}">
          <el-icon size="22"><Medal /></el-icon>
        </div>
        <div>
          <h2>{{ isManage ? '证书管理' : '证书中心' }}</h2>
          <p class="ph-sub">{{ isManage ? '管理证书模板与颁发' : '查看已获得的证书' }}</p>
        </div>
      </div>
      <el-button v-if="isManage" type="primary" @click="openCertDialog()"><el-icon><Plus /></el-icon> 新建模板</el-button>
    </div>

    <!-- ========== Admin view ========== -->
    <template v-if="isManage">
      <el-tabs v-model="adminTab" type="card" style="margin-bottom:16px">
        <el-tab-pane label="考试证书模板" name="exam" />
        <el-tab-pane label="练习证书模板" name="practice" />
        <el-tab-pane label="已颁发证书" name="issued" />
      </el-tabs>

      <!-- Certificate Templates -->
      <template v-if="adminTab !== 'issued'">
        <div v-if="!filteredTemplates.length" class="empty-wrap"><el-empty description="暂无模板" /></div>
        <div v-else class="cert-admin-grid">
          <div v-for="c in filteredTemplates" :key="c.id" class="cert-admin-card">
            <div class="cac-cover" :class="c.cert_type === 'practice' ? 'practice' : 'exam'">
              <span class="cac-icon">{{ c.cert_type === 'practice' ? '📝' : '🎖️' }}</span>
              <span class="cac-type-label">{{ c.cert_type === 'practice' ? '练习证书' : '考试证书' }}</span>
            </div>
            <div class="cac-body">
              <div class="cac-name">{{ c.name }}</div>
              <div class="cac-desc" v-if="c.description">{{ c.description }}</div>
              <div class="cac-chapter" v-if="c.chapter_id">{{ chapterName(c.chapter_id) }}</div>
            </div>
            <div class="cac-actions">
              <el-button size="small" @click="openCertDialog(c)">编辑</el-button>
              <el-button size="small" type="primary" @click="issueCert(c)">颁发</el-button>
              <el-button size="small" type="danger" @click="delCert(c.id)">删除</el-button>
            </div>
          </div>
        </div>
      </template>

      <!-- Issued certificates -->
      <template v-else>
        <div v-if="!issued.length" class="empty-wrap"><el-empty description="暂无已颁发证书" /></div>
        <div v-else class="issued-list">
          <div v-for="row in issued" :key="row.id" class="issued-card" :class="{'is-revoked': row.is_revoked}">
            <div class="ic-left">
              <div class="ic-icon" :class="row.is_revoked ? 'revoked' : ''">🎖️</div>
            </div>
            <div class="ic-body">
              <div class="ic-title">{{ row.certificate_name || '未命名证书' }}</div>
              <div class="ic-meta">
                <span class="ic-user">👤 {{ row.fullname || row.username }}</span>
                <span class="ic-no">📋 {{ row.certificate_no }}</span>
                <span class="ic-date">📅 {{ row.issued_at?.slice(0,10) }}</span>
              </div>
            </div>
            <div class="ic-right">
              <el-tag :type="row.is_revoked ? 'danger' : 'success'" size="small" effect="plain">{{ row.is_revoked ? '已撤销' : '有效' }}</el-tag>
              <el-button size="small" @click="viewCert(row)"><el-icon><View /></el-icon></el-button>
              <el-button v-if="!row.is_revoked" size="small" type="danger" text @click="revokeCert(row.id)">撤销</el-button>
            </div>
          </div>
        </div>
      </template>
    </template>

    <!-- ========== Student view ========== -->
    <template v-else>
      <!-- Exam certificates -->
      <div class="section-title">
        <div class="st-icon" style="background:var(--color-warning-light);color:#d97706">🎖️</div>
        <div>
          <h3>考试证书</h3>
          <p class="st-desc">通过正式考试后获得的证书</p>
        </div>
      </div>

      <div v-if="!examMyCerts.length && !practiceMyCerts.length && !practiceEligible.length && !examEligible.filter(e=>e.can_apply).length" class="empty-wrap">
        <el-empty description="暂无证书，参加考试或完成练习即可获得" />
      </div>

      <div v-if="examMyCerts.length" class="cert-grid">
        <div v-for="cert in examMyCerts" :key="cert.id" class="cert-card" @click="viewCert(cert)">
          <div class="cc-cover exam" :class="{revoked: cert.is_revoked}">
            <div class="cc-badge">🎖️</div>
            <span class="cc-type">考试证书</span>
          </div>
          <div class="cc-body">
            <div class="cc-title">{{ cert.certificate_name }}</div>
            <div class="cc-no">{{ cert.certificate_no }}</div>
            <div class="cc-footer">
              <el-tag :type="cert.is_revoked ? 'danger' : 'success'" size="small" effect="plain">{{ cert.is_revoked ? '已撤销' : '有效' }}</el-tag>
              <span class="cc-date">{{ cert.issued_at?.slice(0,10) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Exam certificate eligibility -->
      <div v-if="examEligible.filter(e => e.can_apply).length" class="practice-list" style="margin-top:12px">
        <div v-for="item in examEligible.filter(e => e.can_apply)" :key="item.certificate_id" class="practice-item">
          <div class="pi-left">
            <div class="pi-ring pass">
              <span class="pi-ring-val">{{ item.best_score }}%</span>
            </div>
            <div class="pi-info">
              <div class="pi-name">{{ item.certificate_name }}</div>
              <div class="pi-sub">最佳成绩：{{ item.best_exam }}</div>
            </div>
          </div>
          <div class="pi-right">
            <el-button type="primary" size="small" @click="applyExam(item)">申请证书</el-button>
          </div>
        </div>
      </div>

      <!-- Already issued exam certs shown with status for those who have them -->
      <div v-for="item in examEligible.filter(e => e.already_issued)" :key="'exam-done-'+item.certificate_id" style="display:none"></div>

      <!-- Practice certificates -->
      <div class="section-title" style="margin-top:28px">
        <div class="st-icon" style="background:#e8f0fe;color:var(--color-primary)">📝</div>
        <div>
          <h3>练习证书</h3>
          <p class="st-desc">章节正确率达60%即可申请</p>
        </div>
      </div>

      <!-- Eligibility list -->
      <div v-if="practiceEligible.length" class="practice-list">
        <div v-for="item in practiceEligible" :key="item.certificate_id" class="practice-item">
          <div class="pi-left">
            <div class="pi-ring" :class="item.pass_rate >= 60 ? 'pass' : 'fail'">
              <span class="pi-ring-val">{{ item.pass_rate }}%</span>
            </div>
            <div class="pi-info">
              <div class="pi-name">{{ item.certificate_name }}</div>
              <div class="pi-sub">{{ item.subject_name }} · {{ item.chapter_name }}</div>
              <div class="pi-stats">
                {{ item.correct_questions }}/{{ item.total_questions }} 正确
              </div>
            </div>
          </div>
          <div class="pi-right">
            <template v-if="item.already_issued">
              <el-tag type="success" size="small">已获得</el-tag>
              <span style="font-size:11px;color:var(--gray-500);margin-top:2px">{{ item.certificate_no }}</span>
            </template>
            <el-button v-else-if="item.pass_rate >= 60" type="primary" size="small" @click="applyPractice(item)">申请证书</el-button>
            <el-tag v-else type="info" size="small">不足60%</el-tag>
          </div>
        </div>
      </div>

      <!-- Already issued practice certs -->
      <div v-if="practiceMyCerts.length" class="cert-grid" style="margin-top:12px">
        <div v-for="cert in practiceMyCerts" :key="cert.id" class="cert-card" @click="viewCert(cert)">
          <div class="cc-cover practice" :class="{revoked: cert.is_revoked}">
            <div class="cc-badge">📝</div>
            <span class="cc-type">练习证书</span>
          </div>
          <div class="cc-body">
            <div class="cc-title">{{ cert.certificate_name }}</div>
            <div class="cc-no">{{ cert.certificate_no }}</div>
            <div class="cc-footer">
              <el-tag :type="cert.is_revoked ? 'danger' : 'success'" size="small" effect="plain">{{ cert.is_revoked ? '已撤销' : '有效' }}</el-tag>
              <span class="cc-date">{{ cert.issued_at?.slice(0,10) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ===== Dialogs ===== -->
    <el-dialog v-model="certDialog.visible" :title="certDialog.isEdit ? '编辑模板' : '新建证书模板'" width="500">
      <el-form :model="certDialog.form" label-width="80px">
        <el-form-item label="类型">
          <el-radio-group v-model="certDialog.form.cert_type">
            <el-radio value="exam">考试证书</el-radio>
            <el-radio value="practice">练习证书</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="名称"><el-input v-model="certDialog.form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="certDialog.form.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item v-if="certDialog.form.cert_type === 'practice'" label="关联章节">
          <el-select v-model="certDialog.form.chapter_id" placeholder="选择章节" clearable style="width:100%">
            <el-option v-for="ch in allChapters" :key="ch.id" :label="ch.subject_name + ' - ' + ch.name" :value="ch.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="模板图片"><el-input v-model="certDialog.form.template_image" placeholder="可选图片URL" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="certDialog.visible=false">取消</el-button><el-button type="primary" @click="saveCert">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="issueDialog.visible" title="颁发证书" width="420">
      <el-form :model="issueDialog" label-width="80px">
        <el-form-item label="选择用户">
          <el-select v-model="issueDialog.user_id" placeholder="搜索用户名或姓名" filterable style="width:100%">
            <el-option v-for="u in allUsers" :key="u.id" :label="(u.fullname || u.username) + ' (ID:' + u.id + ')'" :value="u.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="issueDialog.visible=false">取消</el-button><el-button type="primary" @click="doIssue">颁发</el-button></template>
    </el-dialog>

    <!-- Certificate preview with Canvas rendering -->
    <el-dialog v-model="certViewVisible" title="" width="750px" :close-on-click-modal="true" class="cert-view-dialog">
      <div class="certificate-document" v-if="viewingCert">
        <canvas ref="certCanvas" :width="700" :height="500" style="width:100%;height:auto;border-radius:8px"></canvas>
        <div v-if="viewingCert.is_revoked" class="cert-revoke-overlay">已撤销</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Medal, Plus, View } from '@element-plus/icons-vue'

import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const auth = useAuthStore(); const route = useRoute(); const isManage = computed(() => route.path === '/certificates-manage')
const certs = ref([]); const issued = ref([]); const myCerts = ref([])
const certViewVisible = ref(false); const viewingCert = ref(null); const certCanvas = ref(null)
const adminTab = ref('exam')
const practiceEligible = ref([])
const examEligible = ref([])
const allChapters = ref([]); const allUsers = ref([])
const certDialog = reactive({ visible: false, isEdit: false, editId: null, form: { name:'', description:'', template_image:'', cert_type:'exam', chapter_id:null } })
const issueDialog = reactive({ visible: false, certId: null, user_id: '' })

const examCerts = computed(() => certs.value.filter(c => c.cert_type === 'exam' || !c.cert_type))
const practiceCerts = computed(() => certs.value.filter(c => c.cert_type === 'practice'))
const examMyCerts = computed(() => myCerts.value.filter(c => !c.cert_type || c.cert_type === 'exam'))
const practiceMyCerts = computed(() => myCerts.value.filter(c => c.cert_type === 'practice'))
const filteredTemplates = computed(() => adminTab.value === 'exam' ? examCerts.value : practiceCerts.value)

function chapterName(cid) {
  if (!cid) return '-'
  const ch = allChapters.value.find(c => c.id === cid)
  return ch ? (ch.subject_name + ' - ' + ch.name) : '-'
}

onMounted(async () => {
  if (isManage.value) {
    const [c, i] = await Promise.all([api.get('/certificates'), api.get('/certificates/all-issued')])
    certs.value = c.data; issued.value = i.data.items || []
    try { const { data } = await api.get('/subjects/chapters/all'); allChapters.value = data } catch {}; try { const { data } = await api.get('/users'); allUsers.value = (data.items || data || []).filter(u => u.role !== 'admin') } catch {}
  } else {
    try {
      const [my, eligibility, examElig, chapters] = await Promise.all([
        api.get('/certificates/my'),
        api.get('/certificates/practice-eligibility'),
        api.get('/certificates/exam-eligibility'),
        api.get('/subjects/chapters/all').catch(() => ({ data: [] })),
      ])
      myCerts.value = my.data || []
      practiceEligible.value = eligibility.data || []
      examEligible.value = examElig.data || []
      allChapters.value = chapters.data || []
    } catch {}
  }
})

function viewCert(cert) { viewingCert.value = cert; certViewVisible.value = true; nextTick(() => renderCertCanvas()) }

function renderCertCanvas() {
  const canvas = certCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const w = canvas.width; const h = canvas.height
  const c = viewingCert.value
  if (!c) return
  
  // Background gradient
  const bg = ctx.createLinearGradient(0, 0, w, h)
  bg.addColorStop(0, '#fdf6e3'); bg.addColorStop(0.3, '#fffef9'); bg.addColorStop(0.7, '#fffef9'); bg.addColorStop(1, '#fdf6e3')
  ctx.fillStyle = bg; ctx.fillRect(0, 0, w, h)
  
  // Outer border
  ctx.strokeStyle = '#c9a84c'; ctx.lineWidth = 6
  ctx.strokeRect(20, 20, w - 40, h - 40)
  
  // Inner border
  ctx.strokeStyle = '#d4b85c'; ctx.lineWidth = 2
  ctx.strokeRect(32, 32, w - 64, h - 64)
  
  // Corner decorations
  const corners = [[50,50],[w-50,50],[50,h-50],[w-50,h-50]]
  ctx.fillStyle = '#c9a84c'
  corners.forEach(([cx, cy]) => {
    ctx.beginPath(); ctx.arc(cx, cy, 12, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(cx, cy, 6, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = '#c9a84c'
  })
  
  // Title
  ctx.fillStyle = '#8b6914'; ctx.font = 'bold 36px "KaiTi", "STKaiti", "SimSun", serif'
  ctx.textAlign = 'center'; ctx.fillText('证书', w / 2, 110)
  
  ctx.fillStyle = '#b8860b'; ctx.font = '16px Georgia, serif'
  ctx.fillText('CERTIFICATE', w / 2, 140)
  
  // Divider
  ctx.strokeStyle = '#d4b85c'; ctx.lineWidth = 1
  ctx.beginPath(); ctx.moveTo(120, 160); ctx.lineTo(w - 120, 160); ctx.stroke()
  
  // Recipient name
  ctx.fillStyle = '#333'; ctx.font = 'bold 24px "KaiTi", "STKaiti", "Microsoft YaHei", sans-serif'
  ctx.fillText(c.fullname || c.username || '', w / 2, 210)
  
  // Description
  ctx.fillStyle = '#555'; ctx.font = '16px "KaiTi", "STKaiti", "Microsoft YaHei", sans-serif'
  const desc = '在《' + (c.certificate_name || '') + '》中表现优异'
  ctx.fillText(desc, w / 2, 255)
  ctx.fillText('经考核合格，特发此证，以资鼓励。', w / 2, 280)
  
  // Details
  ctx.textAlign = 'left'
  ctx.fillStyle = '#555'; ctx.font = '15px "Microsoft YaHei", sans-serif'
  ctx.fillText('证书编号：' + (c.certificate_no || ''), 120, 340)
  ctx.fillText('颁发日期：' + (c.issued_at?.slice(0, 10) || ''), 120, 370)
  
  // Seal
  const sx = w - 130; const sy = h - 140
  ctx.save()
  ctx.translate(sx, sy); ctx.rotate(-0.3)
  ctx.strokeStyle = '#c41e3a'; ctx.lineWidth = 5
  ctx.beginPath(); ctx.arc(0, 0, 45, 0, Math.PI * 2); ctx.stroke()
  ctx.fillStyle = '#c41e3a'; ctx.font = 'bold 14px "KaiTi", "SimSun", serif'
  ctx.textAlign = 'center'; ctx.fillText('证书', 0, -4); ctx.fillText('专用章', 0, 18)
  ctx.restore()
  
  // Bottom text
  ctx.textAlign = 'center'; ctx.fillStyle = '#999'; ctx.font = '12px sans-serif'
  ctx.fillText('本证书由在线题库学习系统颁发', w / 2, h - 30)
}
function openCertDialog(row) {
  if (row) {
    certDialog.isEdit = true; certDialog.editId = row.id
    certDialog.form = { name: row.name, description: row.description || '', template_image: row.template_image || '', cert_type: row.cert_type || 'exam', chapter_id: row.chapter_id || null }
  } else {
    certDialog.isEdit = false; certDialog.editId = null
    certDialog.form = { name: '', description: '', template_image: '', cert_type: 'exam', chapter_id: null }
  }
  certDialog.visible = true
}
async function saveCert() {
  const payload = { ...certDialog.form }
  if (payload.cert_type === 'exam') payload.chapter_id = null
  if (certDialog.isEdit) await api.put(`/certificates/${certDialog.editId}`, payload)
  else await api.post('/certificates', payload)
  certDialog.visible = false; ElMessage.success('保存成功')
  const { data } = await api.get('/certificates'); certs.value = data
}
async function delCert(id) {
  try { await ElMessageBox.confirm('确定删除？', '警告', { type: 'warning' }) } catch { return }
  await api.delete(`/certificates/${id}`); certs.value = certs.value.filter(c => c.id !== id)
}
function issueCert(cert) { issueDialog.certId = cert.id; issueDialog.user_id = ''; issueDialog.visible = true }
async function doIssue() {
  await api.post('/certificates/issue', null, { params: { certificate_id: issueDialog.certId, user_id: issueDialog.user_id } })
  issueDialog.visible = false; ElMessage.success('已颁发')
  const { data } = await api.get('/certificates/all-issued'); issued.value = data.items || []
}
async function revokeCert(id) {
  await api.post(`/certificates/${id}/revoke`)
  const item = issued.value.find(i => i.id === id); if (item) item.is_revoked = true
  ElMessage.success('已撤销')
}
async function applyExam(item) {
  try {
    await ElMessageBox.confirm('确认申请「' + item.certificate_name + '」？', '申请考试证书')
  } catch { return }
  try {
    await api.post('/certificates/apply', null, { params: { certificate_id: item.certificate_id } })
    ElMessage.success('证书申请成功！')
    const [my, examElig] = await Promise.all([
      api.get('/certificates/my'),
      api.get('/certificates/exam-eligibility'),
    ])
    myCerts.value = my.data || []; examEligible.value = examElig.data || []
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '申请失败，请稍后重试')
  }
}
async function applyPractice(item) {
  try {
    await ElMessageBox.confirm('确认申请「' + item.certificate_name + '」？', '申请练习证书')
  } catch { return }
  try {
    await api.post('/certificates/apply', null, { params: { certificate_id: item.certificate_id } })
    ElMessage.success('证书申请成功！')
    const [my, eligibility] = await Promise.all([
      api.get('/certificates/my'),
      api.get('/certificates/practice-eligibility'),
    ])
    myCerts.value = my.data || []; practiceEligible.value = eligibility.data || []
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '申请失败，请稍后重试')
  }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-4); gap: var(--space-3); flex-wrap: wrap; }
.ph-left { display: flex; align-items: center; gap: var(--space-3); }
.ph-icon { width: 44px; height: 44px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 20px; font-weight: 700; color: var(--gray-900); }
.ph-sub { margin: 2px 0 0; font-size: 13px; color: var(--gray-500); }

.empty-wrap { padding: 60px 0; }

/* ===== Section titles ===== */
.section-title { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-4); }
.st-icon { width: 40px; height: 40px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.section-title h3 { margin: 0; font-size: 16px; font-weight: 600; color: var(--gray-900); }
.st-desc { margin: 2px 0 0; font-size: 12px; color: var(--gray-500); }

/* ===== Student cert grid (VideoCourses style) ===== */
.cert-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: var(--space-3); }
.cert-card {
  background: var(--gray-25); border-radius: var(--radius-lg); overflow: hidden;
  box-shadow: var(--shadow-sm); cursor: pointer; transition: all 0.2s;
}
.cert-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.cc-cover { height: 110px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; }
.cc-cover.exam { background: linear-gradient(135deg, #d4a853, #c9973a); }
.cc-cover.practice { background: linear-gradient(135deg, #4f6ef7, #3b5de7); }
.cc-cover.revoked { background: linear-gradient(135deg, #9ca3af, #6b7280) !important; }
.cc-badge { font-size: 32px; }
.cc-type { color: rgba(255,255,255,0.9); font-size: 12px; font-weight: 600; letter-spacing: 3px; }
.cc-body { padding: var(--space-3); }
.cc-title { font-size: 14px; font-weight: 600; color: var(--gray-900); margin-bottom: 4px; }
.cc-no { font-size: 11px; color: var(--gray-500); margin-bottom: var(--space-2); }
.cc-footer { display: flex; justify-content: space-between; align-items: center; }
.cc-date { font-size: 11px; color: var(--gray-400); }

/* ===== Practice eligibility ===== */
.practice-list { display: flex; flex-direction: column; gap: var(--space-2); margin-bottom: var(--space-3); }
.practice-item {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4);
  box-shadow: var(--shadow-xs); gap: var(--space-3);
}
.pi-left { display: flex; align-items: center; gap: var(--space-3); }
.pi-ring {
  width: 48px; height: 48px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  border: 3px solid #e5e7eb; flex-shrink: 0;
}
.pi-ring.pass { border-color: var(--color-success); background: var(--color-success-light); }
.pi-ring.fail { border-color: var(--color-danger); background: var(--color-danger-light); }
.pi-ring-val { font-size: 13px; font-weight: 700; }
.pi-ring.pass .pi-ring-val { color: #16a34a; }
.pi-ring.fail .pi-ring-val { color: #dc2626; }
.pi-name { font-weight: 600; font-size: 14px; color: var(--gray-900); }
.pi-sub { font-size: 12px; color: var(--gray-500); margin: 2px 0; }
.pi-stats { font-size: 12px; color: var(--gray-600); }
.pi-right { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; flex-shrink: 0; }

/* ===== Admin cert cards ===== */
.cert-admin-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--space-3); }
.cert-admin-card {
  background: var(--gray-25); border-radius: var(--radius-lg); box-shadow: var(--shadow-xs);
  border: 1px solid var(--gray-100); overflow: hidden; transition: all 0.2s;
}
.cert-admin-card:hover { box-shadow: var(--shadow-sm); }
.cac-cover {
  height: 80px; display: flex; align-items: center; justify-content: center; gap: var(--space-2);
}
.cac-cover.exam { background: linear-gradient(135deg, #fef3c7, #fde68a); }
.cac-cover.practice { background: linear-gradient(135deg, #e0e7ff, #c7d2fe); }
.cac-icon { font-size: 24px; }
.cac-type-label { font-size: 13px; font-weight: 600; color: var(--gray-700); }
.cac-body { padding: var(--space-3); }
.cac-name { font-size: 15px; font-weight: 600; color: var(--gray-900); }
.cac-desc { font-size: 12px; color: var(--gray-500); margin-top: 2px; }
.cac-chapter { font-size: 11px; color: var(--color-primary); margin-top: 4px; }
.cac-actions { padding: var(--space-2) var(--space-3); border-top: 1px solid var(--gray-50); display: flex; gap: 6px; }

/* ===== Issued list ===== */
.issued-list { display: flex; flex-direction: column; gap: var(--space-2); }
.issued-card {
  display: flex; align-items: center; gap: var(--space-3);
  background: var(--gray-25); border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4);
  box-shadow: var(--shadow-xs);
}
.ic-left { flex-shrink: 0; }
.ic-icon { width: 40px; height: 40px; border-radius: var(--radius-md); background: var(--color-warning-light); display: flex; align-items: center; justify-content: center; font-size: 18px; }
.ic-icon.revoked { background: var(--gray-100); opacity: 0.6; }
.ic-body { flex: 1; min-width: 0; }
.ic-title { font-weight: 700; font-size: 15px; color: var(--gray-900); margin-bottom: 4px; line-height: 1.4; }
.ic-meta { display: flex; gap: var(--space-3); font-size: 12px; color: var(--gray-500); flex-wrap: wrap; }
.ic-user, .ic-no, .ic-date { display: inline-flex; align-items: center; gap: 3px; }
.is-revoked { opacity: 0.6; }
.ic-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }

/* ===== Certificate preview ===== */
.cert-view-dialog :deep(.el-dialog__header) { display: none; }
.cert-view-dialog :deep(.el-dialog__body) { padding: 0 !important; }
.certificate-document { padding: 0; background: #f5f0e8; }
.cert-border-outer { padding: 30px 24px; background: linear-gradient(135deg, #faf6ed 0%, #f0e8d5 100%); position: relative; min-height: 420px; }
.cert-border-inner { border: 3px double #8b7355; padding: 30px 24px; text-align: center; position: relative; }
.cert-seal-top { width: 60px; height: 4px; background: linear-gradient(90deg, #c4a97d, #8b7355, #c4a97d); margin: 0 auto 20px; }
.cert-document-title { font-size: 32px; font-weight: 700; letter-spacing: 12px; color: #5c3d2e; margin-bottom: 4px; }
/* Override for the certificate preview title to not conflict */
.cert-border-inner .cert-title { font-size: 32px; font-weight: 700; letter-spacing: 12px; color: #5c3d2e; margin-bottom: 4px; }
.cert-border-inner .cert-subtitle { font-size: 13px; letter-spacing: 6px; color: #8b7355; margin-bottom: 16px; }
.cert-document-divider { width: 80px; height: 1px; background: #c4a97d; margin: 0 auto 20px; }
/* override divider */
.cert-border-inner .cert-divider { width: 80px; height: 1px; background: #c4a97d; margin: 0 auto 20px; }
.cert-border-inner .cert-body { padding: 0 20px; }
.cert-border-inner .cert-recipient { font-size: 22px; font-weight: 600; color: #3d2010; margin-bottom: 16px; letter-spacing: 2px; }
.cert-border-inner .cert-description { font-size: 14px; color: #6b5b4f; line-height: 1.8; margin-bottom: 20px; }
.cert-highlight { color: #8b4513; font-weight: 600; }
.cert-border-inner .cert-details { display: inline-block; text-align: left; background: rgba(255,255,255,0.5); border-radius: 8px; padding: 12px 24px; }
.cert-detail-row { display: flex; gap: 12px; margin-bottom: 4px; font-size: 13px; }
.cert-detail-row:last-child { margin-bottom: 0; }
.cert-label { color: #8b7355; min-width: 60px; }
.cert-value { color: #3d2010; font-weight: 500; }
.cert-border-inner .cert-footer { margin-top: 24px; display: flex; justify-content: flex-end; }
.cert-seal-circle { width: 80px; height: 80px; border: 3px solid #c41e3a; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #c41e3a; font-size: 13px; font-weight: 700; transform: rotate(-15deg); opacity: 0.85; line-height: 1.3; text-align: center; }
.cert-revoke-stamp { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%) rotate(-25deg); font-size: 48px; font-weight: 900; color: rgba(220,38,38,0.35); border: 4px solid rgba(220,38,38,0.35); border-radius: 12px; padding: 8px 24px; pointer-events: none; letter-spacing: 8px; }

@media (max-width: 768px) {
  .cert-grid { grid-template-columns: 1fr; }
  .cert-admin-grid { grid-template-columns: 1fr; }
  .practice-item { flex-direction: column; align-items: flex-start; }
  .pi-right { flex-direction: row; align-items: center; gap: var(--space-2); }
  .issued-card { flex-direction: column; align-items: flex-start; }
  .ic-right { width: 100%; justify-content: flex-end; }
  .cert-border-outer { padding: 16px 10px; }
  .cert-border-inner { padding: 16px 10px; }
  .cert-border-inner .cert-title { font-size: 24px; letter-spacing: 8px; }
  .cert-border-inner .cert-recipient { font-size: 18px; }
  .cert-seal-circle { width: 60px; height: 60px; font-size: 11px; }
  .cert-revoke-stamp { font-size: 32px; letter-spacing: 4px; padding: 4px 12px; }
}
</style>

