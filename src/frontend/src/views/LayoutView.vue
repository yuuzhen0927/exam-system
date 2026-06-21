<template>
  <div class="app-layout">
    <div class="sidebar-overlay" v-if="mobileOpen" @click="mobileOpen=false"></div>
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed && !isMobile, open: mobileOpen }">
      <div class="sidebar-header">
        <div class="sidebar-logo" v-show="!sidebarCollapsed || isMobile">
          <span class="logo-icon">K</span>
          <span class="logo-text">考试系统</span>
        </div>
        <button class="collapse-btn" v-if="!isMobile" @click="sidebarCollapsed=!sidebarCollapsed">
          <el-icon><Fold v-if="!sidebarCollapsed"/><Expand v-else/></el-icon>
        </button>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-item" :class="{active:route.path==='/dashboard'}" @click="closeMobile">
          <el-icon><DataBoard /></el-icon><span v-show="!sidebarCollapsed || isMobile">工作台</span>
        </router-link>

        <div class="nav-divider" v-show="!sidebarCollapsed || isMobile"></div>
        <template v-if="!auth.isManager">
        <div class="nav-section" v-show="!sidebarCollapsed || isMobile">学习中心</div>
        <router-link to="/practice" class="nav-item" @click="closeMobile">
          <el-icon><EditPen /></el-icon><span v-show="!sidebarCollapsed || isMobile">练习中心</span>
        </router-link>
        <router-link to="/exams" class="nav-item" @click="closeMobile">
          <el-icon><Notebook /></el-icon><span v-show="!sidebarCollapsed || isMobile">考试管理</span>
        </router-link>
        <router-link to="/results" class="nav-item" @click="closeMobile">
          <el-icon><Trophy /></el-icon><span v-show="!sidebarCollapsed || isMobile">我的成绩</span>
        </router-link>
        <router-link to="/practice-records" class="nav-item" @click="closeMobile">
          <el-icon><Timer /></el-icon><span v-show="!sidebarCollapsed || isMobile">练习记录</span>
        </router-link>
        <router-link to="/wrongbook" class="nav-item" @click="closeMobile">
          <el-icon><WarningFilled /></el-icon><span v-show="!sidebarCollapsed || isMobile">错题本</span>
        </router-link>
        <router-link to="/favorites" class="nav-item" @click="closeMobile">
          <el-icon><Star /></el-icon><span v-show="!sidebarCollapsed || isMobile">收藏夹</span>
        </router-link>
        <router-link to="/leaderboard" class="nav-item" @click="closeMobile">
          <el-icon><Trophy /></el-icon><span v-show="!sidebarCollapsed || isMobile">排行榜</span>
        </router-link>
        <router-link to="/notes" class="nav-item" @click="closeMobile">
          <el-icon><Edit /></el-icon><span v-show="!sidebarCollapsed || isMobile">笔记管理</span>
        </router-link>
        <router-link to="/user-announcements" class="nav-item" @click="closeMobile">
              <el-icon><Bell /></el-icon><span v-show="!sidebarCollapsed || isMobile">公告通知</span>
            </router-link>
            <router-link v-if="!auth.isManager" to="/resources" class="nav-item" @click="closeMobile">
          <el-icon><FolderOpened /></el-icon><span v-show="!sidebarCollapsed || isMobile">学习资料</span>
        </router-link>
        <router-link v-if="!auth.isManager" to="/videos" class="nav-item" @click="closeMobile">
          <el-icon><VideoCamera /></el-icon><span v-show="!sidebarCollapsed || isMobile">视频课程</span>
        </router-link>
        <router-link v-if="!auth.isManager" to="/certificates" class="nav-item" @click="closeMobile">
          <el-icon><Medal /></el-icon><span v-show="!sidebarCollapsed || isMobile">证书中心</span>
        </router-link>

        </template>
        <template v-if="auth.isManager">
          <!-- 教学内容 -->
          <div class="nav-divider" v-show="!sidebarCollapsed || isMobile"></div>
          <div class="nav-section nav-section--collapsible" v-show="!sidebarCollapsed || isMobile" @click="toggleGroup('teaching')">
            <span>教学内容</span>
            <el-icon class="nav-section-arrow"><ArrowDown v-if="openGroups.teaching" /><ArrowRight v-else /></el-icon>
          </div>
          <div v-show="openGroups.teaching || (sidebarCollapsed && !isMobile)">
            <router-link to="/subjects" class="nav-item" @click="closeMobile">
              <el-icon><Collection /></el-icon><span v-show="!sidebarCollapsed || isMobile">科目章节</span>
            </router-link>
            <router-link to="/questions" class="nav-item" @click="closeMobile">
              <el-icon><Document /></el-icon><span v-show="!sidebarCollapsed || isMobile">题库管理</span>
            </router-link>
            <router-link to="/exams-manage" class="nav-item" @click="closeMobile">
              <el-icon><List /></el-icon><span v-show="!sidebarCollapsed || isMobile">试卷管理</span>
            </router-link>
            <router-link to="/resources-manage" class="nav-item" @click="closeMobile">
              <el-icon><Upload /></el-icon><span v-show="!sidebarCollapsed || isMobile">资料管理</span>
            </router-link>
            <router-link to="/announcements" class="nav-item" @click="closeMobile">
              <el-icon><Bell /></el-icon><span v-show="!sidebarCollapsed || isMobile">公告管理</span>
            </router-link>
          </div>

          <!-- 课程资源 -->
          <div class="nav-divider" v-show="!sidebarCollapsed || isMobile"></div>
          <div class="nav-section nav-section--collapsible" v-show="!sidebarCollapsed || isMobile" @click="toggleGroup('resources')">
            <span>课程资源</span>
            <el-icon class="nav-section-arrow"><ArrowDown v-if="openGroups.resources" /><ArrowRight v-else /></el-icon>
          </div>
          <div v-show="openGroups.resources || (sidebarCollapsed && !isMobile)">
            <router-link to="/videos-manage" class="nav-item" @click="closeMobile">
              <el-icon><VideoCamera /></el-icon><span v-show="!sidebarCollapsed || isMobile">视频课程</span>
            </router-link>
            <router-link v-if="auth.isAdmin" to="/certificates-manage" class="nav-item" @click="closeMobile">
              <el-icon><Medal /></el-icon><span v-show="!sidebarCollapsed || isMobile">证书管理</span>
            </router-link>
          </div>

          <!-- 考试运营 -->
          <div class="nav-divider" v-show="!sidebarCollapsed || isMobile"></div>
          <div class="nav-section nav-section--collapsible" v-show="!sidebarCollapsed || isMobile" @click="toggleGroup('exam')">
            <span>考试运营</span>
            <el-icon class="nav-section-arrow"><ArrowDown v-if="openGroups.exam" /><ArrowRight v-else /></el-icon>
          </div>
          <div v-show="openGroups.exam || (sidebarCollapsed && !isMobile)">
            <router-link v-if="auth.isAdmin" to="/manual-grade" class="nav-item" @click="closeMobile">
              <el-icon><Checked /></el-icon><span v-show="!sidebarCollapsed || isMobile">人工批改</span>
            </router-link>
            <router-link v-if="auth.isAdmin" to="/retake-approvals" class="nav-item" @click="closeMobile">
              <el-icon><Refresh /></el-icon><span v-show="!sidebarCollapsed || isMobile">重考审批</span>
            </router-link>
            <router-link to="/abnormal" class="nav-item" @click="closeMobile">
              <el-icon><Warning /></el-icon><span v-show="!sidebarCollapsed || isMobile">异常报告</span>
            </router-link>
            <router-link to="/feedback-manage" class="nav-item" @click="closeMobile">
              <el-icon><ChatLineSquare /></el-icon><span v-show="!sidebarCollapsed || isMobile">题目反馈</span>
            </router-link>
          </div>

          <!-- 人员管理 -->
          <div class="nav-divider" v-show="!sidebarCollapsed || isMobile"></div>
          <div class="nav-section nav-section--collapsible" v-show="!sidebarCollapsed || isMobile" @click="toggleGroup('users')">
            <span>人员管理</span>
            <el-icon class="nav-section-arrow"><ArrowDown v-if="openGroups.users" /><ArrowRight v-else /></el-icon>
          </div>
          <div v-show="openGroups.users || (sidebarCollapsed && !isMobile)">
            <router-link v-if="auth.isAdmin" to="/users" class="nav-item" @click="closeMobile">
              <el-icon><UserFilled /></el-icon><span v-show="!sidebarCollapsed || isMobile">用户管理</span>
            </router-link>
            <router-link v-if="auth.isAdmin" to="/roles" class="nav-item" @click="closeMobile">
              <el-icon><Setting /></el-icon><span v-show="!sidebarCollapsed || isMobile">角色管理</span>
            </router-link>
          </div>

          <!-- 数据报表 -->
          <div class="nav-divider" v-show="!sidebarCollapsed || isMobile"></div>
          <div class="nav-section nav-section--collapsible" v-show="!sidebarCollapsed || isMobile" @click="toggleGroup('reports')">
            <span>数据报表</span>
            <el-icon class="nav-section-arrow"><ArrowDown v-if="openGroups.reports" /><ArrowRight v-else /></el-icon>
          </div>
          <div v-show="openGroups.reports || (sidebarCollapsed && !isMobile)">
            <router-link to="/analytics" class="nav-item" @click="closeMobile">
              <el-icon><TrendCharts /></el-icon><span v-show="!sidebarCollapsed || isMobile">数据分析</span>
            </router-link>
            <router-link v-if="auth.isAdmin" to="/audit" class="nav-item" @click="closeMobile">
              <el-icon><Clock /></el-icon><span v-show="!sidebarCollapsed || isMobile">操作日志</span>
            </router-link>
          </div>
        

        </template>

      </nav>

      <div class="sidebar-footer" v-show="!sidebarCollapsed || isMobile">
        <div class="footer-user">
          <el-avatar :size="32" :style="{background: avatarColor, color: '#fff', fontWeight: 700}">{{ avatarChar }}</el-avatar>
          <div class="footer-user-info">
            <div class="footer-user-name">{{ auth.user?.fullname || auth.user?.username }}</div>
            <div class="footer-user-role">{{ roleLabel }}</div>
          </div>
        </div>
      </div>
    </aside>

    <div class="main-area" :class="{expanded: sidebarCollapsed && !isMobile}">
      <header class="topbar">
        <div class="topbar-left">
          <button class="hamburger" v-if="isMobile" @click="mobileOpen=!mobileOpen">
            <el-icon size="20"><Menu /></el-icon>
          </button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{path:'/'}">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta.title">{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="topbar-right">
          <button class="search-btn" @click="searchOpen = true" title="搜索 (Ctrl+K)"><el-icon size="18"><Search /></el-icon></button>
          <button class="theme-btn" @click="auth.toggleTheme()" :title="auth.theme==='dark'?'切换亮色':'切换暗色'">
            <el-icon><Sunny v-if="auth.theme==='dark'"/><Moon v-else/></el-icon>
          </button>
          <!-- 通知铃铛 -->
          <el-dropdown trigger="click">
            <button class="notification-btn">
              <el-icon :size="18"><Bell /></el-icon>
              <span class="notification-badge" v-if="unreadCount > 0">{{ unreadCount }}</span>
            </button>
            <template #dropdown>
              <el-dropdown-menu class="notification-dropdown">
                <div class="notification-header">
                  <span class="notification-title">通知</span>
                  <span class="notification-read-all" @click="markAllRead">全部已读</span>
                </div>
                <div class="notification-list">
                  <div v-for="n in notifications.slice(0, 5)" :key="n.id" class="notification-item" :class="{'unread': !n.read}">
                    <div class="notification-dot" v-if="!n.read"></div>
                    <div class="notification-content">
                      <div class="notification-item-title">{{ n.title }}</div>
                      <div class="notification-item-desc">{{ n.desc }}</div>
                      <div class="notification-item-time">{{ n.time }}</div>
                    </div>
                  </div>
                </div>
                <router-link to="/notifications" class="notification-view-all">
                  查看全部
                </router-link>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <el-dropdown trigger="click">
            <span class="user-btn">
              <el-avatar :size="28" :style="{background: avatarColor, color: '#fff', fontWeight: 700, fontSize: '13px'}">{{ avatarChar }}</el-avatar>
              <span class="user-name" v-if="!isMobile">{{ auth.user?.fullname || auth.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>{{ auth.user?.username }}</el-dropdown-item>
                <el-dropdown-item divided @click="router.push('/profile')">个人中心</el-dropdown-item>
                <el-dropdown-item @click="doLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <main class="main-content">
        <router-view v-slot="{ Component, route: rvRoute }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="rvRoute.fullPath" />
          </transition>
        </router-view>
      </main>

      <!-- 移动端底部导航 -->
      <nav class="mobile-nav" v-if="isMobile">
        <template v-if="!auth.isManager">
          <router-link to="/dashboard" class="mobile-nav-item nav-item-anim" :class="{active:route.path==='/dashboard'}"><el-icon><DataBoard /></el-icon><span>首页</span></router-link>
          <router-link to="/practice" class="mobile-nav-item nav-item-anim" :class="{active:route.path==='/practice'}"><el-icon><EditPen /></el-icon><span>练习</span></router-link>
          <router-link to="/exams" class="mobile-nav-item nav-item-anim" :class="{active:route.path==='/exams'}"><el-icon><Notebook /></el-icon><span>考试</span></router-link>
          <router-link to="/wrongbook" class="mobile-nav-item nav-item-anim" :class="{active:route.path==='/wrongbook'}"><el-icon><WarningFilled /></el-icon><span>错题</span></router-link>
        </template>
        <template v-else>
          <router-link to="/dashboard" class="mobile-nav-item nav-item-anim" :class="{active:route.path==='/dashboard'}"><el-icon><DataBoard /></el-icon><span>工作台</span></router-link>
          <router-link to="/questions" class="mobile-nav-item nav-item-anim" :class="{active:route.path==='/questions'}"><el-icon><Document /></el-icon><span>题库</span></router-link>
          <router-link to="/exams-manage" class="mobile-nav-item nav-item-anim" :class="{active:route.path==='/exams-manage'}"><el-icon><List /></el-icon><span>试卷</span></router-link>
          <router-link to="/manual-grade" class="mobile-nav-item nav-item-anim" :class="{active:route.path==='/manual-grade'}"><el-icon><Checked /></el-icon><span>批改</span></router-link>
          <router-link v-if="auth.isAdmin" to="/users" class="mobile-nav-item nav-item-anim" :class="{active:route.path==='/users'}"><el-icon><UserFilled /></el-icon><span>用户</span></router-link>
        </template>
        <a class="mobile-nav-item nav-item-anim" :class="{active: moreOpen}" @click="moreOpen=!moreOpen">
          <el-icon><MoreFilled /></el-icon>
          <span>更多</span>
        </a>
      </nav>
      <!-- 更多全屏网格页面 -->
      <transition name="slide-up">
        <div class="more-panel" v-if="moreOpen && isMobile">
          <div class="more-panel-inner">
            <div class="more-panel-header">
              <span>更多功能</span>
              <button class="more-panel-close" @click="moreOpen=false">
                <el-icon><Close /></el-icon>
              </button>
            </div>
            <div class="more-section" v-if="!auth.isManager">
              <div class="more-section-title">学习中心</div>
              <div class="more-panel-grid">
                <router-link to="/results" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Trophy /></el-icon></div>
                  <span>我的成绩</span>
                </router-link>
                <router-link to="/favorites" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Star /></el-icon></div>
                  <span>收藏夹</span>
                </router-link>
                <router-link to="/notes" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Edit /></el-icon></div>
                  <span>笔记</span>
                </router-link>
                <router-link to="/practice-records" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Timer /></el-icon></div>
                  <span>练习记录</span>
                </router-link>
                <router-link to="/profile" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Setting /></el-icon></div>
                  <span>个人中心</span>
                </router-link>
              </div>
            </div>
            <div class="more-section" v-if="auth.isManager">
              <div class="more-section-title">教学内容</div>
              <div class="more-panel-grid">
                <router-link to="/subjects" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Collection /></el-icon></div>
                  <span>科目章节</span>
                </router-link>
                <router-link to="/questions" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Document /></el-icon></div>
                  <span>题库管理</span>
                </router-link>
                <router-link to="/exams-manage" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><List /></el-icon></div>
                  <span>试卷管理</span>
                </router-link>
                <router-link to="/announcements" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Bell /></el-icon></div>
                  <span>公告管理</span>
                </router-link>
                <router-link to="/resources-manage" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Upload /></el-icon></div>
                  <span>资料管理</span>
                </router-link>
                <router-link to="/videos-manage" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><VideoCamera /></el-icon></div>
                  <span>视频管理</span>
                </router-link>
              </div>
            </div>
            <div class="more-section" v-if="auth.isManager">
              <div class="more-section-title">考试运营</div>
              <div class="more-panel-grid">
                <router-link to="/manual-grade" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Checked /></el-icon></div>
                  <span>人工批改</span>
                </router-link>
                <router-link to="/retake-approvals" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Refresh /></el-icon></div>
                  <span>重考审批</span>
                </router-link>
                <router-link to="/abnormal" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Warning /></el-icon></div>
                  <span>异常报告</span>
                </router-link>
                <router-link to="/feedback-manage" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><ChatLineSquare /></el-icon></div>
                  <span>题目反馈</span>
                </router-link>
              </div>
            </div>
            <div class="more-section" v-if="auth.isAdmin">
              <div class="more-section-title">人员与数据</div>
              <div class="more-panel-grid">
                <router-link to="/users" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><UserFilled /></el-icon></div>
                  <span>用户管理</span>
                </router-link>
                <router-link to="/roles" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Setting /></el-icon></div>
                  <span>角色管理</span>
                </router-link>
                <router-link to="/analytics" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><TrendCharts /></el-icon></div>
                  <span>数据分析</span>
                </router-link>
                <router-link to="/audit" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Clock /></el-icon></div>
                  <span>操作日志</span>
                </router-link>
                <router-link v-if="auth.isAdmin" to="/certificates-manage" class="more-panel-item" @click="moreOpen=false">
                  <div class="more-panel-icon"><el-icon><Medal /></el-icon></div>
                  <span>证书管理</span>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>

    <!-- 登录后置顶公告弹窗 -->
    <el-dialog v-model="annDialogVisible" title="" width="480px" :close-on-click-modal="false" :close-on-press-escape="false" :show-close="true" center class="ann-dialog">
      <div class="ann-popup">
        <div class="ann-popup-icon">📢</div>
        <h3 class="ann-popup-title">系统公告</h3>
        <div v-for="a in annDialogItems" :key="a.title" class="ann-popup-item">
          <div class="ann-popup-item-title">
            <el-tag v-if="a.is_pinned" type="danger" size="small" effect="dark">置顶</el-tag>
            {{ a.title }}
          </div>
          <div class="ann-popup-item-content">{{ a.content }}</div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="annDialogVisible = false" size="large" style="width:100%">我知道了</el-button>
      </template>
    </el-dialog>
    <!-- 全局搜索弹窗 -->
    <el-dialog v-model="searchOpen" title="全局搜索" width="600px" :close-on-click-modal="true">
      <el-input v-model="searchQuery" placeholder="搜索题目、资料、公告..." size="large" @input="doSearch" clearable>
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <div v-if="searchResults.questions.length" style="margin-top:16px">
        <div class="search-section-title">题目</div>
        <div v-for="q in searchResults.questions" :key="'q'+q.id" class="search-item" @click="searchOpen=false; router.push('/practice')">
          <span class="si-type" :class="q.type">{{ typeLabel(q.type) }}</span>
          <span class="si-text">{{ q.content }}</span>
        </div>
      </div>
      <div v-if="searchResults.resources.length" style="margin-top:16px">
        <div class="search-section-title">资料</div>
        <div v-for="r in searchResults.resources" :key="'r'+r.id" class="search-item" @click="searchOpen=false; router.push('/resources')">
          <span class="si-type" style="background:#06b6d4">{{ r.file_type?.toUpperCase() }}</span>
          <span class="si-text">{{ r.title }}</span>
        </div>
      </div>
      <div v-if="searchResults.announcements.length" style="margin-top:16px">
        <div class="search-section-title">公告</div>
        <div v-for="a in searchResults.announcements" :key="'a'+a.id" class="search-item" @click="searchOpen=false; router.push('/dashboard')">
          <span class="si-type" style="background:#f59e0b">公告</span>
          <span class="si-text">{{ a.title }}</span>
        </div>
      </div>
      <div v-if="!searchQuery.trim()" class="search-hint">输入关键词开始搜索，或使用 Ctrl+K 快速打开</div>
      <div v-else-if="!searchResults.questions.length && !searchResults.resources.length && !searchResults.announcements.length" class="search-hint">未找到结果</div>
    </el-dialog>

</template>
<script setup>
import {
  Fold, Expand, DataBoard, EditPen, Notebook, Trophy, Timer,
  WarningFilled, Star, Edit, Bell, FolderOpened, VideoCamera,
  Medal, ChatLineSquare, User, Setting, Document, Search,
  List, TrendCharts, CircleCheck, ChatDotSquare, Reading, Key, Lock
} from '@element-plus/icons-vue'

import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const sidebarCollapsed = ref(false)
const mobileOpen = ref(false)
const moreOpen = ref(false)
const openGroups = reactive({ teaching: true, resources: true, exam: true, reports: true, users: true })
const searchOpen = ref(false)
const searchQuery = ref('')
const searchResults = reactive({ questions: [], resources: [], announcements: [] })
const searchTimeout = ref(null)
const notifications = ref([])
const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)
const annDialogVisible = ref(false)
const annDialogItems = ref([])

const isMobile = ref(window.innerWidth <= 768)
function onResize() { isMobile.value = window.innerWidth <= 768 }

const avatarChar = computed(() => {
  const name = auth.user?.fullname || auth.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})
const avatarColor = computed(() => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#00b894', '#6c5ce7']
  const name = auth.user?.username || 'u'
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
})
const roleLabel = computed(() => {
  if (auth.isAdmin) return '管理员'
  if (auth.isManager) return '负责人'
  return '学员'
})

function closeMobile() { mobileOpen.value = false }

function toggleGroup(name) { openGroups[name] = !openGroups[name] }

async function doSearch() {
  clearTimeout(searchTimeout.value)
  if (!searchQuery.value.trim()) {
    searchResults.questions = []; searchResults.resources = []; searchResults.announcements = []; return
  }
  searchTimeout.value = setTimeout(async () => {
    try {
      const { data } = await api.get('/search', { params: { q: searchQuery.value.trim() } })
      searchResults.questions = data.questions || []
      searchResults.resources = data.resources || []
      searchResults.announcements = data.announcements || []
    } catch {}
  }, 300)
}

function typeLabel(t) {
  const map = { single: '单选', multi: '多选', judge: '判断', fill: '填空', essay: '简答', composite: '综合' }
  return map[t] || t
}

async function doLogout() {
  auth.logout()
  router.push('/login')
}

async function markAllRead() {
  try {
    await api.post('/notifications/mark-all-read')
    notifications.value.forEach(n => n.is_read = true)
  } catch {}
}

async function loadNotifications() {
  try {
    const { data } = await api.get('/notifications')
    notifications.value = data?.items || data || []
  } catch {}
}

async function loadAnnouncements() {
  try {
    if (sessionStorage.getItem('ann_shown')) return
    const { data } = await api.get('/announcements')
    const items = data?.items || data || []
    const pinned = items.filter(a => a.is_pinned && a.is_published)
    if (pinned.length > 0) {
      annDialogItems.value = pinned
      annDialogVisible.value = true
      sessionStorage.setItem('ann_shown', '1')
    }
  } catch {}
}

// Keyboard shortcut for search
function onKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    searchOpen.value = true
  }
}

let wsConn = null
function connectWS() {
  try {
    const userId = auth.user?.id
    if (!userId) return
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    wsConn = new WebSocket(protocol + '//' + location.host + '/ws/' + userId)
    wsConn.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data)
        if (msg.type === 'notification') {
          ElMessage.info(msg.message)
          loadNotifications()
        }
      } catch {}
    }
    wsConn.onclose = () => { setTimeout(connectWS, 5000) }
  } catch {}
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  document.addEventListener('keydown', onKeydown)
  loadNotifications()
  loadAnnouncements()
  connectWS()
})
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  document.removeEventListener('keydown', onKeydown)
  if (wsConn) { wsConn.close(); wsConn = null }
})
</script>
<style scoped>
/* Layout */
.app-layout { display: flex; min-height: 100vh; background: var(--gray-50); }
.sidebar-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.3); z-index: 90; }
.sidebar { width: 240px; background: var(--gray-900); display: flex; flex-direction: column; transition: width var(--transition-base); position: fixed; top: 0; left: 0; bottom: 0; z-index: 100; overflow-y: auto; overflow-x: hidden; box-shadow: var(--shadow-lg); scrollbar-width: none; -ms-overflow-style: none; }
.sidebar::-webkit-scrollbar { display: none; }
.sidebar.collapsed { width: 64px; }
.sidebar-header { height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 var(--space-4); border-bottom: 1px solid rgba(255,255,255,0.04); flex-shrink: 0; }
.sidebar-logo { display: flex; align-items: center; gap: 10px; }
.logo-icon { width: 32px; height: 32px; border-radius: var(--radius-md); background: var(--color-primary); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; flex-shrink: 0; }
.logo-text { color: #fff; font-size: var(--text-md); font-weight: 700; white-space: nowrap; }
.collapse-btn { background: none; border: none; color: var(--gray-400); cursor: pointer; padding: 4px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; transition: color var(--transition-fast); flex-shrink: 0; min-width: 32px; min-height: 32px; }
.collapse-btn:hover { color: #fff; }
.sidebar-nav { flex: 1; padding: var(--space-2); overflow-y: auto; scrollbar-width: none; -ms-overflow-style: none; }
.sidebar-nav::-webkit-scrollbar { display: none; }
.nav-divider { height: 1px; margin: var(--space-3); background: rgba(255,255,255,0.06); }
.nav-section { display: flex; align-items: center; justify-content: space-between; padding: var(--space-2) var(--space-3); font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.3); letter-spacing: 0.06em; user-select: none; }
.nav-section--collapsible { cursor: pointer; border-radius: var(--radius-sm); transition: color var(--transition-fast); }
.nav-section--collapsible:hover { color: rgba(255,255,255,0.5); }
.nav-section-arrow { font-size: 12px; color: rgba(255,255,255,0.25); }
.nav-item { display: flex; align-items: center; gap: 10px; padding: 9px var(--space-3); border-radius: var(--radius-md); color: var(--gray-400); text-decoration: none; font-size: 14px; transition: all var(--transition-fast); margin-bottom: 1px; white-space: nowrap; min-height: 38px; }
.nav-item:hover { background: rgba(255,255,255,0.05); color: #fff; }
.nav-item.active { background: var(--color-primary); color: #fff; }
.nav-item .el-icon { font-size: 17px; flex-shrink: 0; }
.sidebar.collapsed .nav-item { justify-content: center; padding: 10px; }
.sidebar-footer { padding: var(--space-4); border-top: 1px solid rgba(255,255,255,0.04); flex-shrink: 0; }
.footer-user { display: flex; align-items: center; gap: var(--space-3); }
.footer-user-info { overflow: hidden; }
.footer-user-name { font-size: var(--text-sm); color: #fff; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.footer-user-role { font-size: var(--text-xs); color: var(--gray-400); }

/* Main area */
.main-area { flex: 1; margin-left: 240px; display: flex; flex-direction: column; min-height: 100vh; transition: margin-left var(--transition-base); min-width: 0; }
.main-area.expanded { margin-left: 64px; }
.topbar { height: 60px; background: rgba(255,255,255,0.8); backdrop-filter: blur(8px); border-bottom: 1px solid var(--gray-100); display: flex; align-items: center; justify-content: space-between; padding: 0 var(--space-6); position: sticky; top: 0; z-index: 80; flex-shrink: 0; }
.hamburger { display: none; background: none; border: none; cursor: pointer; padding: var(--space-2); margin-right: var(--space-3); color: var(--gray-600); border-radius: var(--radius-sm); min-width: 40px; min-height: 40px; align-items: center; justify-content: center; }
.hamburger:hover { background: var(--gray-50); }
.topbar-left { display: flex; align-items: center; }
.topbar-right { display: flex; align-items: center; gap: var(--space-4); }
.user-btn { display: flex; align-items: center; gap: var(--space-2); cursor: pointer; padding: var(--space-1) var(--space-2); border-radius: var(--radius-md); transition: background var(--transition-fast); min-height: 36px; }
.user-btn:hover { background: var(--gray-50); }
.user-name { font-size: var(--text-base); color: var(--gray-800); font-weight: 500; }
.main-content { flex: 1; min-height: 0; }
.theme-btn { background: none; border: none; cursor: pointer; padding: var(--space-2); color: var(--gray-500); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; transition: color var(--transition-fast); min-width: 36px; min-height: 36px; }
.theme-btn:hover { color: var(--color-warning); background: var(--gray-50); }
.search-btn { background: none; border: none; cursor: pointer; padding: var(--space-2); color: var(--gray-500); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; transition: color var(--transition-fast); min-width: 36px; min-height: 36px; }
.search-btn:hover { color: var(--color-primary); background: var(--gray-50); }

/* Notifications */
.notification-btn { position: relative; background: none; border: none; cursor: pointer; padding: var(--space-2); color: var(--gray-500); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; transition: color var(--transition-fast); min-width: 36px; min-height: 36px; }
.notification-btn:hover { color: var(--color-primary); background: var(--gray-50); }
.notification-badge { position: absolute; top: 2px; right: 2px; min-width: 16px; height: 16px; background: var(--color-danger, #f56c6c); color: #fff; font-size: 10px; font-weight: 600; border-radius: 8px; display: flex; align-items: center; justify-content: center; padding: 0 4px; line-height: 16px; }
.notification-dropdown { width: 320px; padding: 0; }
.notification-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--gray-100); }
.notification-title { font-weight: 700; font-size: var(--text-base); color: var(--gray-800); }
.notification-read-all { font-size: var(--text-xs); color: var(--color-primary); cursor: pointer; border: none; background: none; }
.notification-read-all:hover { opacity: 0.8; }
.notification-list { max-height: 320px; overflow-y: auto; }
.notification-item { display: flex; align-items: flex-start; gap: var(--space-3); padding: 12px 16px; cursor: pointer; transition: background var(--transition-fast); border-bottom: 1px solid var(--gray-50); }
.notification-item:hover { background: var(--gray-50); }
.notification-item.unread { background: color-mix(in srgb, var(--color-primary) 8%, transparent); }
.notification-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-primary); flex-shrink: 0; margin-top: 6px; }
.notification-content { flex: 1; min-width: 0; }
.notification-item-title { font-size: var(--text-sm); font-weight: 500; color: var(--gray-800); margin-bottom: 2px; }
.notification-item-desc { font-size: var(--text-xs); color: var(--gray-500); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.notification-item-time { font-size: 11px; color: var(--gray-400); margin-top: 2px; }
.notification-view-all { display: block; text-align: center; padding: 12px; font-size: var(--text-sm); color: var(--color-primary); text-decoration: none; border-top: 1px solid var(--gray-100); transition: background var(--transition-fast); }
.notification-view-all:hover { background: var(--gray-50); }

/* Search */
.search-section-title { font-size: 12px; font-weight: 600; color: var(--gray-400); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; }
.search-item { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: var(--radius-md); cursor: pointer; transition: background 0.15s; margin-bottom: 4px; }
.search-item:hover { background: var(--gray-50); }
.si-type { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; color: #fff; background: var(--color-primary); white-space: nowrap; flex-shrink: 0; }
.si-text { font-size: 14px; color: var(--gray-800); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.search-hint { text-align: center; padding: 32px 0; color: var(--gray-400); font-size: 14px; }

/* Mobile bottom nav */
.mobile-nav { display: none; position: fixed; bottom: 0; left: 0; right: 0; height: 56px; background: var(--gray-25); border-top: 1px solid var(--gray-100); z-index: 1000; justify-content: space-around; align-items: center; padding-bottom: env(safe-area-inset-bottom); }
.mobile-nav-item { display: flex; flex-direction: column; align-items: center; gap: 2px; color: var(--gray-500); text-decoration: none; font-size: 10px; padding: 4px 8px; border-radius: 8px; transition: color 0.15s; }
.mobile-nav-item .el-icon { font-size: 20px; }
.mobile-nav-item.active, .mobile-nav-item.router-link-active { color: var(--color-primary); }
.nav-item-anim .el-icon { transition: transform 0.2s cubic-bezier(0.4,0,0.2,1), color 0.2s ease; }
.nav-item-anim.active .el-icon { transform: scale(1.2); color: var(--color-primary); }

/* More panel */
.more-panel { position: fixed; inset: 0; z-index: 2000; background: rgba(0,0,0,0.4); display: flex; align-items: flex-end; }
.more-panel-inner { background: var(--gray-25); width: 100%; border-radius: 20px 20px 0 0; padding: var(--space-4) var(--space-5) calc(var(--space-6) + env(safe-area-inset-bottom)); max-height: 70vh; overflow-y: auto; }
.more-panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); padding-bottom: var(--space-3); border-bottom: 1px solid var(--gray-100); }
.more-panel-header span { font-size: var(--text-lg); font-weight: 700; }
.more-panel-close { background: var(--gray-100); border: none; width: 32px; height: 32px; border-radius: 50%; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: var(--gray-600); }
.more-panel-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); }
.more-panel-item { display: flex; flex-direction: column; align-items: center; gap: var(--space-2); text-decoration: none; color: var(--gray-700); padding: var(--space-3) var(--space-1); border-radius: var(--radius-md); transition: background var(--transition-fast); min-height: 72px; justify-content: center; }
.more-panel-item:active { background: var(--gray-50); }
.more-panel-icon { width: 44px; height: 44px; border-radius: var(--radius-md); background: var(--gray-50); display: flex; align-items: center; justify-content: center; font-size: 20px; color: var(--color-primary); }
.more-panel-item span { font-size: 11px; white-space: nowrap; }
.more-section { margin-bottom: var(--space-4); }
.more-section-title { font-size: var(--text-sm); color: var(--gray-500); font-weight: 500; padding: 0 var(--space-2) var(--space-2); }

/* Transitions */
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s cubic-bezier(0.4,0,0.2,1); }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; }
.slide-up-enter-from .more-panel-inner, .slide-up-leave-to .more-panel-inner { transform: translateY(100%); }

/* Mobile */
@media (max-width: 768px) {
  .mobile-nav { display: flex !important; }
  .main-area { padding-bottom: 64px; margin-left: 0 !important; }
  .sidebar { transform: translate(-100%); transition: transform 0.3s cubic-bezier(0.4,0,0.2,1); width: 260px; }
  .sidebar.open { transform: translate(0); }
  .sidebar.collapsed { width: 260px; }
  .sidebar-overlay { display: block; }
  .hamburger { display: flex; }
  .topbar { padding: 0 var(--space-4); }
}

/* Dark mode */
[data-theme="dark"] .search-item:hover { background: var(--gray-100); }
[data-theme="dark"] .si-text { color: var(--gray-300); }
[data-theme="dark"] .more-panel-inner { background: var(--gray-25); }
[data-theme="dark"] .more-panel-close { background: var(--gray-200); color: var(--gray-700); }
[data-theme="dark"] .more-panel-icon { background: var(--gray-100); }
[data-theme="dark"] .notification-btn:hover { color: var(--color-primary); background: var(--gray-100); }
[data-theme="dark"] .notification-item:hover { background: var(--gray-50); }
</style>
<style>
/* Announcement dialog */
.ann-popup { text-align: center; padding: 8px 0; }
.ann-popup-icon { font-size: 48px; margin-bottom: 12px; }
.ann-popup-title { font-size: 20px; font-weight: 700; color: var(--gray-900); margin-bottom: 20px; }
.ann-popup-item { text-align: left; background: var(--gray-50); border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; border-left: 3px solid var(--color-warning); }
.ann-popup-item:last-child { margin-bottom: 0; }
.ann-popup-item-title { font-size: 15px; font-weight: 600; color: var(--gray-800); margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }
.ann-popup-item-content { font-size: 13px; color: var(--gray-600); line-height: 1.7; white-space: pre-wrap; word-break: break-word; max-height: 40vh; overflow-y: auto; }
@media (max-width: 480px) {
  .ann-dialog .el-dialog { width: 92vw !important; margin: 0 auto; }
  .ann-dialog .el-dialog__body { padding: 16px !important; }
  .ann-popup-icon { font-size: 36px; }
  .ann-popup-title { font-size: 17px; margin-bottom: 14px; }
  .ann-popup-item { padding: 10px 12px; }
  .ann-popup-item-title { font-size: 14px; }
  .ann-popup-item-content { font-size: 12px; max-height: 35vh; }
}
</style>