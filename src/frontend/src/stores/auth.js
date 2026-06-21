import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('token') || '')
  const roles = ref([])

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const roleLabel = computed(() => {
    const map = { admin: '管理员', teacher: '负责人', student: '学生' }
    const r = roles.value.find(r => r.name === user.value?.role)
    return r?.description || map[user.value?.role] || (user.value?.role ?? '学生')
  })

  const isManager = computed(() => {
    if (user.value?.role === 'admin' || user.value?.role === 'teacher') return true
    const r = roles.value.find(r => r.name === user.value?.role)
    return r?.is_manager || false
  })

const theme = ref(localStorage.getItem('theme') || 'system')
// Initialize theme attribute on page load
if (theme.value === 'dark' || (theme.value === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
  document.documentElement.setAttribute('data-theme', 'dark')
} else {
  document.documentElement.setAttribute('data-theme', '')
}
function toggleTheme() {
theme.value = theme.value === 'dark' ? 'light' : 'dark'
localStorage.setItem('theme', theme.value)
document.documentElement.setAttribute('data-theme', theme.value === 'dark' ? 'dark' : '')
}

  async function loadRoles() {
    try { const { data } = await api.get('/roles'); roles.value = data }
    catch { roles.value = [] }
  }

  async function login(username, password) {
    const form = new URLSearchParams()
    form.append('username', username)
    form.append('password', password)
    const res = await api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))
    await loadRoles()
    return res.data
  }

  async function register(username, password, fullname) {
    const res = await api.post('/auth/register', { username, password, fullname })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))
    await loadRoles()
    return res.data
  }

  function logout() {
    token.value = ''
    user.value = null
    roles.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { user, token, roles, isLoggedIn, isAdmin, isManager, roleLabel, theme, toggleTheme, login, register, logout, loadRoles }
})

