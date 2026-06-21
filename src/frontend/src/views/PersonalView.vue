<template>
  <div class="page-container">
    <div class="page-header">
      <h2>个人中心</h2>
    </div>

    <!-- 用户信息卡片 -->
    <div class="profile-card">
      <div class="pc-avatar">
        <el-avatar :size="72" :style="{background: avatarColor, color:'#fff', fontSize:'28px', fontWeight:700}">{{ avatarChar }}</el-avatar>
      </div>
      <div class="pc-info">
        <div class="pc-name">{{ auth.user?.fullname || auth.user?.username }}</div>
        <div class="pc-role">{{ auth.roleLabel }}</div>
        <div class="pc-meta">注册时间：{{ auth.user?.created_at?.slice(0, 10) || '—' }}</div>
      </div>
    </div>

    <!-- 学习统计 -->
    <div class="section-title">学习统计</div>
    <div class="stat-grid">
      <div class="stat-item">
        <div class="stat-num">{{ stats.total_practice || 0 }}</div>
        <div class="stat-lbl">做题总数</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">{{ stats.correct_rate || 0 }}%</div>
        <div class="stat-lbl">正确率</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">{{ stats.study_days || 0 }}</div>
        <div class="stat-lbl">学习天数</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">{{ stats.certs || 0 }}</div>
        <div class="stat-lbl">获得证书</div>
      </div>
    </div>

    <!-- 修改密码 -->
    <div class="section-title">修改密码</div>
    <el-form :model="pwForm" :rules="pwRules" ref="pwFormRef" label-width="80px" class="pw-form">
      <el-form-item label="旧密码" prop="old_password">
        <el-input v-model="pwForm.old_password" type="password" show-password placeholder="请输入当前密码" />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input v-model="pwForm.new_password" type="password" show-password placeholder="请输入新密码" />
      </el-form-item>
      <!-- Password strength -->
      <div v-if="pwForm.new_password" class="pw-strength">
        <div class="pw-bar"><div class="pw-fill" :class="pwLevel.class" :style="{width: pwLevel.width}"></div></div>
        <span class="pw-label" :class="pwLevel.class">{{ pwLevel.text }}</span>
      </div>
      <div v-if="pwForm.new_password" class="pw-rules">
        <span :class="{ok: pwForm.new_password.length >= 6}">至少6位</span>
        <span :class="{ok: /[A-Za-z]/.test(pwForm.new_password)}">含字母</span>
        <span :class="{ok: /[0-9]/.test(pwForm.new_password)}">含数字</span>
      </div>
      <el-form-item label="确认密码" prop="confirm">
        <el-input v-model="pwForm.confirm" type="password" show-password placeholder="再次输入新密码" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="changePassword" :loading="pwLoading">保存修改</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const auth = useAuthStore()
const pwFormRef = ref(null)
const pwLoading = ref(false)
const stats = reactive({ total_practice: 0, correct_rate: 0, study_days: 0, certs: 0 })

const pwForm = reactive({ old_password: '', new_password: '', confirm: '' })

const pwLevel = computed(() => {
  const p = pwForm.new_password
  if (!p) return { text: '', class: '', width: '0%' }
  let score = 0
  if (p.length >= 6) score++
  if (p.length >= 8) score++
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  if (score <= 1) return { text: '弱', class: 'weak', width: '20%' }
  if (score <= 2) return { text: '一般', class: 'fair', width: '50%' }
  if (score <= 3) return { text: '良好', class: 'good', width: '75%' }
  return { text: '强', class: 'strong', width: '100%' }
})

const validateConfirm = (rule, value, callback) => {
  if (value !== pwForm.new_password) callback(new Error('两次密码不一致'))
  else callback()
}
const pwRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
    {
      validator: (rule, value, cb) => {
        if (!value) return cb()
        if (!/[A-Za-z]/.test(value)) return cb(new Error('密码必须包含字母'))
        if (!/[0-9]/.test(value)) return cb(new Error('密码必须包含数字'))
        if (/^(.)\1+$/.test(value)) return cb(new Error('密码不能全是相同字符'))
        if (['123456','password','qwerty','abc123','111111','aaaaaa'].includes(value.toLowerCase()))
          return cb(new Error('密码过于简单'))
        cb()
      },
      trigger: 'blur',
    },
  ],
  confirm: [{ required: true, validator: validateConfirm, trigger: 'blur' }],
}

const avatarColors = ['#4f6ef7','#22c55e','#f59e0b','#ef4444','#8b5cf6','#ec4899','#06b6d4','#f97316','#84cc16','#6366f1']
const avatarColor = computed(() => {
  const name = auth.user?.fullname || auth.user?.username || 'U'
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return avatarColors[Math.abs(hash) % avatarColors.length]
})
const avatarChar = computed(() => (auth.user?.fullname || auth.user?.username || 'U')[0].toUpperCase())

onMounted(async () => {
  try { const { data } = await api.get('/profile/stats'); Object.assign(stats, data) } catch {}
})

async function changePassword() {
  const valid = await pwFormRef.value.validate().catch(() => false)
  if (!valid) return
  pwLoading.value = true
  try {
    await api.put('/profile/password', { old_password: pwForm.old_password, new_password: pwForm.new_password })
    ElMessage.success('密码修改成功')
    pwForm.old_password = ''; pwForm.new_password = ''; pwForm.confirm = ''
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '修改失败')
  } finally { pwLoading.value = false }
}
</script>

<style scoped>
.profile-card {
  display: flex; align-items: center; gap: var(--space-5);
  background: var(--gray-25); border-radius: var(--radius-lg);
  padding: var(--space-6); margin-bottom: var(--space-5);
}
.pc-name { font-size: var(--text-xl); font-weight: var(--font-bold); color: var(--gray-900); }
.pc-role { font-size: var(--text-sm); color: var(--gray-500); margin-top: 4px; }
.pc-meta { font-size: var(--text-xs); color: var(--gray-400); margin-top: 2px; }

.section-title { font-size: var(--text-md); font-weight: var(--font-bold); color: var(--gray-800); margin: var(--space-4) 0 var(--space-3); }

.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); margin-bottom: var(--space-5); }
.stat-item {
  background: var(--gray-25); border-radius: var(--radius-lg);
  padding: var(--space-4); text-align: center;
}
.stat-num { font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--color-primary); }
.stat-lbl { font-size: var(--text-xs); color: var(--gray-500); margin-top: 4px; }

.pw-form { max-width: 420px; }

/* Password strength */
.pw-strength { display: flex; align-items: center; gap: 8px; margin: -8px 0 12px 80px; }
.pw-bar { flex: 1; height: 4px; background: var(--gray-100); border-radius: 2px; overflow: hidden; }
.pw-fill { height: 100%; border-radius: 2px; transition: width 0.3s ease, background 0.3s ease; }
.pw-fill.weak { background: #ef4444; }
.pw-fill.fair { background: #f59e0b; }
.pw-fill.good { background: #3b82f6; }
.pw-fill.strong { background: #22c55e; }
.pw-label { font-size: 11px; font-weight: 600; white-space: nowrap; }
.pw-label.weak { color: #ef4444; }
.pw-label.fair { color: #f59e0b; }
.pw-label.good { color: #3b82f6; }
.pw-label.strong { color: #22c55e; }

/* Password rules */
.pw-rules { display: flex; gap: 8px; margin: -6px 0 12px 80px; flex-wrap: wrap; }
.pw-rules span { font-size: 11px; color: var(--gray-400); padding: 2px 8px; border-radius: 4px; background: var(--gray-50); transition: all 0.2s; }
.pw-rules span.ok { color: #22c55e; background: #f0fdf4; }

@media (max-width: 768px) {
  .profile-card { flex-direction: column; text-align: center; }
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .pw-strength, .pw-rules { margin-left: 0; }
}
</style>
