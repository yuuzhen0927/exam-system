<template>
  <template v-if="!error"><slot /></template>
  <div v-else class="error-boundary">
    <div class="eb-icon">!</div>
    <div class="eb-title">页面出现错误</div>
    <div class="eb-msg">{{ error.message || '未知错误' }}</div>
    <button class="eb-btn" @click="retry">重新加载</button>
  </div>
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue'

const error = ref(null)

onErrorCaptured((err) => {
  error.value = err
  return false
})

function retry() {
  error.value = null
}
</script>

<style scoped>
.error-boundary {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 300px; padding: 40px; text-align: center;
}
.eb-icon {
  width: 48px; height: 48px; border-radius: 50%; background: #fef2f2; color: #ef4444;
  display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700;
  margin-bottom: 16px;
}
.eb-title { font-size: 16px; font-weight: 600; color: var(--gray-900); margin-bottom: 8px; }
.eb-msg { font-size: 13px; color: var(--gray-500); margin-bottom: 20px; }
.eb-btn {
  background: var(--color-primary); color: #fff; border: none; padding: 8px 24px;
  border-radius: 8px; cursor: pointer; font-size: 14px;
}
.eb-btn:hover { opacity: .9; }
</style>
