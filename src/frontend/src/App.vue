<template>
  <div v-if="!ready" style="display:flex;align-items:center;justify-content:center;height:100vh;background:#f0f2f5">
    <div style="text-align:center">
      <div style="width:40px;height:40px;border:3px solid #e5e7eb;border-top-color:#4f6ef7;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 16px"></div>
      <p style="color:#6b7280">加载中...</p>
    </div>
  </div>
  <ErrorBoundary v-else>
    <router-view />
  </ErrorBoundary>
</template>

<script setup>
import { ref, onMounted } from "vue"
import ErrorBoundary from "./components/ErrorBoundary.vue"

const ready = ref(false)

onMounted(() => {
  const theme = localStorage.getItem("theme") || "light"
  if (theme === "dark") {
    document.documentElement.setAttribute("data-theme", "dark")
  }
  ready.value = true
})
</script>

<style>
@keyframes spin { to { transform: rotate(360deg); } }
</style>
