<template>
  <div class="page-container">
    <div class="page-header">
      <div class="ph-left">
        <div class="ph-icon" style="background:#fef3c7;color:#d97706"><el-icon size="22"><Trophy /></el-icon></div>
        <div><h2>排行榜</h2><p class="ph-sub">考试成绩排名</p></div>
      </div>
    </div>
    <div v-if="!board.length" class="empty-wrap"><el-empty description="暂无考试记录" /></div>
    <div v-else class="lb-grid">
      <div v-for="item in board" :key="item.rank" class="lb-card" :class="{gold: item.rank===1, silver: item.rank===2, bronze: item.rank===3}">
        <div class="lb-rank">
          <span v-if="item.rank <= 3" class="lb-medal">{{ ['🥇','🥈','🥉'][item.rank-1] }}</span>
          <span v-else class="lb-num">{{ item.rank }}</span>
        </div>
        <div class="lb-avatar" :style="{background: avatarColor(item.username)}">{{ (item.fullname||item.username||'?')[0] }}</div>
        <div class="lb-info">
          <div class="lb-name">{{ item.fullname || item.username }}</div>
          <div class="lb-stats">
            <span class="lb-tag">最高 {{ item.best_score }}</span>
            <span class="lb-tag">平均 {{ item.avg_score }}</span>
            <span class="lb-tag">{{ item.exam_count }} 次考试</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { Trophy } from '@element-plus/icons-vue'
import api from '../api'
const board = ref([])
const colors = ['#4f6ef7','#22c55e','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#ec4899','#f97316']
function avatarColor(name) { let h=0; for(let i=0;i<(name||'').length;i++) h+=name.charCodeAt(i); return colors[h%colors.length] }
onMounted(async () => { try { const {data} = await api.get('/analytics/leaderboard'); board.value = data || [] } catch {} })
</script>
<style scoped>
.ph-left{display:flex;align-items:center;gap:12px}
.ph-icon{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center}
.page-header h2{margin:0;font-size:20px;font-weight:700}
.ph-sub{margin:2px 0 0;font-size:13px;color:var(--gray-500)}
.lb-grid{display:flex;flex-direction:column;gap:8px}
.lb-card{display:flex;align-items:center;gap:12px;background:var(--gray-25);border-radius:10px;padding:14px 18px;border:1px solid var(--gray-100);transition:all 0.2s}
.lb-card:hover{box-shadow:0 2px 8px rgba(0,0,0,0.06)}
.lb-card.gold{border-color:#fbbf24;background:#fffbeb}
.lb-card.silver{border-color:#94a3b8;background:#f8fafc}
.lb-card.bronze{border-color:#f97316;background:#fff7ed}
.lb-rank{width:36px;text-align:center;flex-shrink:0}
.lb-medal{font-size:28px}
.lb-num{font-size:18px;font-weight:700;color:var(--gray-400)}
.lb-avatar{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:16px;flex-shrink:0}
.lb-info{flex:1;min-width:0}
.lb-name{font-weight:600;font-size:15px;color:var(--gray-900);margin-bottom:4px}
.lb-stats{display:flex;gap:8px;flex-wrap:wrap}
.lb-tag{font-size:12px;color:var(--gray-500);background:var(--gray-50);padding:2px 8px;border-radius:4px}
@media(max-width:768px){.lb-card{padding:10px 12px}.lb-medal{font-size:22px}}
</style>
<style>
[data-theme="dark"] .lb-card { background: #212226; border-color: #2a2b30; }
[data-theme="dark"] .lb-card.gold { background: #2a2518; border-color: #92700a; }
[data-theme="dark"] .lb-card.silver { background: #232528; border-color: #64748b; }
[data-theme="dark"] .lb-card.bronze { background: #2a2118; border-color: #9a6a3a; }
[data-theme="dark"] .lb-name { color: #f0f1f4; }
[data-theme="dark"] .lb-num { color: #a8a9b0; }
[data-theme="dark"] .lb-tag { background: #2a2b30; color: #a8a9b0; }
[data-theme="dark"] .lb-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
</style>