<template>
  <div class="login-page">
    <!-- Left panel: brand showcase -->
    <div class="login-hero">
      <div class="hero-content">
        <div class="hero-brand">
          <div class="hero-logo">
            <svg viewBox="0 0 44 44" fill="none"><rect width="44" height="44" rx="12" fill="rgba(255,255,255,0.2)"/><path d="M12 22l5 5 11-11" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <div>
            <div class="hero-title">智考通</div>
            <div class="hero-subtitle">Enterprise Exam Platform</div>
          </div>
        </div>

        <h1 class="hero-headline">让培训考核<br/>更高效、更智能</h1>
        <p class="hero-desc">一站式企业内部培训考核平台，覆盖学、练、考、评全流程</p>

        <div class="hero-features">
          <div class="hf-item" v-for="f in features" :key="f.title">
            <div class="hf-icon">{{ f.icon }}</div>
            <div class="hf-text">
              <div class="hf-title">{{ f.title }}</div>
              <div class="hf-desc">{{ f.desc }}</div>
            </div>
          </div>
        </div>

        <div class="hero-footer">© 2026 智考通 · 在线考试学习系统</div>
      </div>
      <!-- Decorative circles -->
      <div class="deco deco-1"></div>
      <div class="deco deco-2"></div>
      <div class="deco deco-3"></div>
    </div>

    <!-- Right panel: login form -->
    <div class="login-form-panel">
      <div class="login-card">
        <div class="login-brand">
          <div class="brand-icon">
            <svg viewBox="0 0 44 44" fill="none"><rect width="44" height="44" rx="12" fill="var(--color-primary)"/><path d="M12 22l5 5 11-11" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <h2>欢迎回来</h2>
          <p>企业内部培训考核平台</p>
        </div>

        <div class="card-tabs">
          <button :class="{active:!isRegister}" @click="isRegister=false">登录</button>
          <button :class="{active:isRegister}" @click="isRegister=true">注册</button>
        </div>

        <el-form :model="form" :rules="currentRules" ref="formRef" @keyup.enter="submit" class="login-form">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" size="large" :prefix-icon="UserIcon" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password :prefix-icon="LockIcon" />
          </el-form-item>
          <template v-if="isRegister">
            <div v-if="form.password" class="pw-strength">
              <div class="pw-bar"><div class="pw-fill" :class="pwLevel.class" :style="{width: pwLevel.width}"></div></div>
              <span class="pw-label" :class="pwLevel.class">{{ pwLevel.text }}</span>
            </div>
            <div class="pw-rules">
              <span :class="{ok: form.password.length >= 6}">至少6位</span>
              <span :class="{ok: /[A-Za-z]/.test(form.password)}">含字母</span>
              <span :class="{ok: /[0-9]/.test(form.password)}">含数字</span>
            </div>
            <el-form-item prop="fullname">
              <el-input v-model="form.fullname" placeholder="姓名（选填）" size="large" />
            </el-form-item>
          </template>
          <el-form-item>
            <el-button type="primary" size="large" :loading="loading" @click="submit" class="submit-btn">
              {{ isRegister ? '创建账号' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">首次使用请联系管理员获取账号</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref(null)
const loading = ref(false)
const isRegister = ref(false)

// Simple SVG icon components
const UserIcon = { render() { return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', width: '16', height: '16' }, [h('path', { d: 'M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2' }), h('circle', { cx: '12', cy: '7', r: '4' })]) } }
const LockIcon = { render() { return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', width: '16', height: '16' }, [h('rect', { x: '3', y: '11', width: '18', height: '11', rx: '2', ry: '2' }), h('path', { d: 'M7 11V7a5 5 0 0110 0v4' })]) } }

const features = [
  { icon: '📝', title: '题库管理', desc: '五种题型，智能组卷' },
  { icon: '✅', title: '考试管理', desc: '防作弊，自动阅卷' },
  { icon: '📚', title: '学习管理', desc: '进度跟踪，在线学习' },
  { icon: '📊', title: '数据分析', desc: '多维统计，可视化报表' },
]

const form = reactive({ username: '', password: '', fullname: '' })

const pwLevel = computed(() => {
  const p = form.password
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

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, message: '用户名至少2个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
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
}

const currentRules = computed(() => isRegister.value ? registerRules : loginRules)

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    if (isRegister.value) await auth.register(form.username, form.password, form.fullname)
    else await auth.login(form.username, form.password)
    try {
      const { data } = await import('../api').then(m => m.default.get('/announcements?published_only=true'))
      const pinned = (data.items || data || []).filter(a => a.is_pinned)
      if (pinned.length && !isRegister.value) {
        localStorage.setItem('pinned_ann_alert', JSON.stringify(pinned.map(a => ({title:a.title,content:a.content,is_pinned:a.is_pinned}))))
      }
    } catch {}
    router.push('/')
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
}

/* ===== Left Hero Panel ===== */
.login-hero {
  flex: 0 0 50%;
  background: linear-gradient(135deg, #4F6EF7 0%, #3B5BDE 50%, #2D4AC0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 48px;
}
.hero-content {
  position: relative;
  z-index: 2;
  max-width: 480px;
  width: 100%;
}
.hero-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 48px;
}
.hero-logo svg { width: 44px; height: 44px; }
.hero-title {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
}
.hero-subtitle {
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  letter-spacing: 0.5px;
}
.hero-headline {
  font-size: 40px;
  font-weight: 800;
  color: #fff;
  line-height: 1.3;
  margin: 0 0 16px;
}
.hero-desc {
  font-size: 16px;
  color: rgba(255,255,255,0.85);
  line-height: 1.6;
  margin: 0 0 40px;
}
.hero-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.hf-item {
  display: flex;
  align-items: center;
  gap: 14px;
}
.hf-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(255,255,255,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.hf-title {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
}
.hf-desc {
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  margin-top: 1px;
}
.hero-footer {
  margin-top: 48px;
  font-size: 12px;
  color: rgba(255,255,255,0.5);
}
/* Decorative circles */
.deco {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
}
.deco-1 { width: 300px; height: 300px; top: -60px; right: -80px; }
.deco-2 { width: 200px; height: 200px; bottom: 100px; right: 40px; }
.deco-3 { width: 160px; height: 160px; bottom: -40px; left: 60px; }

/* ===== Right Form Panel ===== */
.login-form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  padding: 48px;
}
.login-card {
  width: 100%;
  max-width: 400px;
}
.login-brand {
  text-align: center;
  margin-bottom: 32px;
}
.brand-icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 16px;
}
.brand-icon svg { width: 100%; height: 100%; }
.login-brand h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 6px;
}
.login-brand p {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.card-tabs {
  display: flex;
  margin-bottom: 24px;
  border-bottom: 2px solid #e2e8f0;
}
.card-tabs button {
  flex: 1;
  border: none;
  background: none;
  padding: 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: #94a3b8;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}
.card-tabs button.active {
  color: #4F6EF7;
  border-bottom-color: #4F6EF7;
}
.card-tabs button:hover { color: #4F6EF7; }

.login-form { margin-bottom: 8px; }

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}

.login-footer {
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 20px;
}

/* Password strength */
.pw-strength { display: flex; align-items: center; gap: 8px; margin: -8px 0 12px; }
.pw-bar { flex: 1; height: 4px; background: #e2e8f0; border-radius: 2px; overflow: hidden; }
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

.pw-rules { display: flex; gap: 8px; margin: -6px 0 12px; flex-wrap: wrap; }
.pw-rules span { font-size: 11px; color: #94a3b8; padding: 2px 8px; border-radius: 4px; background: #f1f5f9; transition: all 0.2s; }
.pw-rules span.ok { color: #22c55e; background: #f0fdf4; }

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .login-page { flex-direction: column; }
  .login-hero {
    display: none !important;
  }
  .hero-brand { margin-bottom: 16px; }
  .hero-headline { font-size: 22px; margin-bottom: 8px; }
  .hero-desc { font-size: 13px; margin-bottom: 16px; }
  .hero-features { flex-direction: row; flex-wrap: wrap; gap: 10px; }
  .hf-item { flex: 0 0 calc(50% - 5px); padding: 8px; }
  .hf-icon { width: 32px; height: 32px; font-size: 14px; }
  .hf-title { font-size: 12px; }
  .hf-desc { font-size: 10px; }
  .hero-footer { margin-top: 16px; font-size: 11px; }
  .deco { display: none; }
  .login-form-panel { padding: 20px; }
  .login-brand { margin-bottom: 20px; }
  .login-brand h2 { font-size: 20px; }
}

@media (max-width: 480px) {
  .login-hero { padding: 20px 16px 16px; }
  .hero-headline { font-size: 20px; }
  .hf-item { flex: 0 0 100%; }
  .hero-footer { margin-top: 12px; }
  .login-form-panel { padding: 16px; }
  .login-card { max-width: 100%; }
}

@media (max-width: 420px) {
  .login-hero { display: none !important; }
  .login-form-panel { flex: 1; }
}
</style>
