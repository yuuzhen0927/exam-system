<template>
  <div class="page-container" style="max-width:900px;margin:0 auto">
    <div class="page-header"><h2>考试回看 - {{ exam.exam_title }}</h2></div>
    <el-alert v-if="exam.manual_score === null" title="待人工评分：综合题需要人工批改，请等待管理员评分后查看最终成绩" type="warning" :closable="false" style="margin-bottom:16px" />
<el-alert v-else :title="`得分: ${exam.auto_score}${exam.manual_score != null ? ' + ' + exam.manual_score+' (人工)' : ''} / ${exam.total_score} | ${exam.passed ? '通过' : '未通过'}`" :type="exam.passed ? 'success' : 'error'" :closable="false" style="margin-bottom:16px" />

    <div v-for="(q, i) in exam.questions" :key="q.question_id" style="margin-bottom:20px;background:var(--gray-25);padding:20px;border-radius:8px;border:1px solid #e5e6eb" :style="{borderLeftColor: q.is_correct === true ? '#67c23a' : q.is_correct === false ? '#f56c6c' : '#e5e6eb', borderLeftWidth:'4px'}">
      <div style="margin-bottom:8px">
        <span style="font-weight:700">{{ i+1 }}.</span>
        <el-tag size="small" style="margin:0 6px">{{ typeLabel(q.type) }}</el-tag>
        <el-tag v-if="q.is_correct === true" type="success" size="small">正确</el-tag>
        <el-tag v-else-if="q.is_correct === false" type="danger" size="small">错误</el-tag>
        <span>{{ q.content }}</span>
      </div>
      <div v-if="q.options?.length" style="margin-bottom:8px">
        <div v-for="o in q.options" :key="o.label" style="padding:2px 0">
          <span :style="{color: o.label === q.correct_answer ? '#67c23a' : o.label === q.user_answer && q.user_answer !== q.correct_answer ? '#f56c6c' : ''}">{{ o.label }}. {{ o.text }}</span>
          <el-tag v-if="o.label === q.correct_answer" type="success" size="small" style="margin-left:4px">答案</el-tag>
          <el-tag v-if="o.label === q.user_answer && o.label !== q.correct_answer" type="danger" size="small" style="margin-left:4px">你的选择</el-tag>
        </div>
      </div>
      <div v-if="q.type==='composite'" style="margin-bottom:8px">
        <p><b>你的答案：</b>{{ q.user_answer }}</p>
        <p><b>参考答案：</b>{{ q.correct_answer }}</p>
      </div>
      <div v-if="q.explanation" style="padding:8px;background:#f0f9eb;border-radius:4px;font-size:13px"><b>解析：</b>{{ q.explanation }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const exam = ref({ questions: [] })

onMounted(async () => {
  const { data } = await api.get(`/exams/results/${route.params.resultId}/review`)
  exam.value = data
})

function typeLabel(t) { return { single:'单选',multi:'多选',truefalse:'判断',composite:'综合' }[t]||t }
</script>
