import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/',
    component: () => import('../views/LayoutView.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'profile', name: 'Profile', component: () => import('../views/PersonalView.vue'), meta: { title: '个人中心' } },
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/DashboardView.vue'), meta: { title: '工作台' } },
      // 用户端
      { path: 'practice', name: 'Practice', component: () => import('../views/PracticeView.vue'), meta: { title: '练习中心' } },
      { path: 'exams', name: 'Exams', component: () => import('../views/ExamsView.vue'), meta: { title: '考试管理' } },
      { path: 'exam/:id/take', name: 'ExamTake', component: () => import('../views/ExamTakeView.vue'), meta: { title: '考试' } },
      { path: 'exam/:id/results', name: 'ExamResults', component: () => import('../views/ExamResultsView.vue'), meta: { title: '成绩详情' } },
      { path: 'results', name: 'MyResults', component: () => import('../views/MyResultsView.vue'), meta: { title: '我的成绩' } },
      { path: 'review/:resultId', name: 'ExamReview', component: () => import('../views/ExamReviewView.vue'), meta: { title: '考试回看' } },
      { path: 'practice-records', name: 'PracticeHistory', component: () => import('../views/PracticeHistoryView.vue'), meta: { title: '练习记录' } },
      { path: 'wrongbook', name: 'WrongBook', component: () => import('../views/WrongBookView.vue'), meta: { title: '错题本' } },
      { path: 'favorites', name: 'Favorites', component: () => import('../views/FavoritesView.vue'), meta: { title: '收藏夹' } },
      { path: 'leaderboard', name: 'Leaderboard', component: () => import('../views/LeaderboardView.vue'), meta: { title: '排行榜' } },
      { path: 'notes', name: 'Notes', component: () => import('../views/NotesView.vue'), meta: { title: '笔记管理' } },
      { path: 'resources', name: 'Resources', component: () => import('../views/ResourcesView.vue'), meta: { title: '学习资料' } },
      { path: 'videos', name: 'Videos', component: () => import('../views/VideoCoursesView.vue'), meta: { title: '视频课程' } },
      { path: 'certificates', name: 'Certificates', component: () => import('../views/CertificatesView.vue'), meta: { title: '证书中心' } },
    { path: 'user-announcements', name: 'UserAnnouncements', component: () => import('../views/UserAnnouncementsView.vue'), meta: { title: '公告通知' } },
      // 管理端
      { path: 'subjects', name: 'Subjects', component: () => import('../views/SubjectsView.vue'), meta: { title: '科目管理' } },
      { path: 'questions', name: 'Questions', component: () => import('../views/QuestionsView.vue'), meta: { title: '题库管理' } },
      { path: 'exams-manage', name: 'ExamsManage', component: () => import('../views/ExamsView.vue'), meta: { title: '试卷管理' } },
      { path: 'announcements', name: 'Announcements', component: () => import('../views/AnnouncementsView.vue'), meta: { title: '公告管理' } },
      { path: 'resources-manage', name: 'ResourcesManage', component: () => import('../views/ResourcesView.vue'), meta: { title: '资料管理' } },
      { path: 'videos-manage', name: 'VideosManage', component: () => import('../views/VideoCoursesView.vue'), meta: { title: '视频管理' } },
      { path: 'feedback-manage', name: 'FeedbackManage', component: () => import('../views/FeedbackView.vue'), meta: { title: '题目反馈' } },
      { path: 'abnormal', name: 'Abnormal', component: () => import('../views/AbnormalView.vue'), meta: { title: '异常报告' } },
      { path: 'audit', name: 'AuditLog', component: () => import('../views/AuditLogView.vue'), meta: { title: '操作日志' } },
      { path: 'analytics', name: 'Analytics', component: () => import('../views/AnalyticsView.vue'), meta: { title: '数据分析' } },
      { path: 'users', name: 'Users', component: () => import('../views/UsersView.vue'), meta: { title: '用户管理' } },
      { path: 'manual-grade', name: 'ManualGrade', component: () => import('../views/ManualGradeView.vue'), meta: { title: '人工批改' } },
      { path: 'certificates-manage', name: 'CertificatesManage', component: () => import('../views/CertificatesView.vue'), meta: { title: '证书管理' } },
      { path: 'roles', name: 'Roles', component: () => import('../views/RolesView.vue'), meta: { title: '角色管理' } },
      { path: 'retake-approvals', name: 'RetakeApprovals', component: () => import('../views/RetakeView.vue'), meta: { title: '重考审批' } },
      { path: 'notifications', name: 'Notifications', component: () => import('../views/NotificationsView.vue'), meta: { title: '通知中心' } },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'Login' && !token) next({ name: 'Login' })
  else if (to.name === 'Login' && token) next({ name: 'Dashboard' })
  // 正式考试防切出：拦截路由跳转
  else if (from.name === 'ExamTake' && to.name !== 'ExamTake') {
    // Check if there's an active formal exam session
    const examId = from.params.id
    try {
      const raw = sessionStorage.getItem(`exam_session_${examId}`)
      if (raw) {
        const state = JSON.parse(raw)
        if (state.mode === 'formal') {
          const elapsed = Date.now() - (state.savedAt || 0); const maxMs = (state.durationMinutes || 120) * 60 * 1000; if (elapsed >= maxMs) { sessionStorage.removeItem(`exam_session_${examId}`); next(); return }
          // Don't block the navigation, but it will be caught by the component's onBeforeRouteLeave
          // This is a backup guard
          if (!window.confirm('你正在参加正式考试，离开页面可能被记录为作弊。确定离开吗？')) { next(false); return }
          sessionStorage.removeItem(`exam_session_${examId}`); next(); return
        }
      }
    } catch {}
    next()
  }
  else next()
})

export default router
