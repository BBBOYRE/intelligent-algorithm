import { createRouter, createWebHashHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import AuthLayout from '../layouts/AuthLayout.vue'

const routes = [
  {
    path: '/login',
    component: AuthLayout,
    children: [
      {
        path: '',
        name: 'login',
        component: () => import('../views/LoginView.vue'),
        meta: { title: '登录', public: true },
      },
    ],
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('../views/DashboardView.vue'),
        meta: { title: '主页' },
      },
      {
        path: 'project/:id',
        name: 'projectDetail',
        component: () => import('../views/ProjectDetailView.vue'),
        meta: { title: '项目详情' },
      },
      {
        path: 'upload',
        name: 'upload',
        component: () => import('../views/UploadView.vue'),
        meta: { title: '文档上传', icon: '↑', group: 'doc' },
      },
      {
        path: 'doc-ops',
        name: 'docOps',
        component: () => import('../views/DocOpsView.vue'),
        meta: { title: '文档操作', icon: '⎘', group: 'doc' },
      },
      {
        path: 'table-fill',
        name: 'tableFill',
        component: () => import('../views/TableFillView.vue'),
        meta: { title: '表格填写', icon: '▦', group: 'doc' },
      },
      {
        path: 'chat',
        name: 'chat',
        component: () => import('../views/ChatView.vue'),
        meta: { title: '智能问答', icon: '◎', group: 'ai' },
      },
      {
        path: 'knowledge-base',
        name: 'knowledgeBase',
        component: () => import('../views/KnowledgeBaseView.vue'),
        meta: { title: '知识库管理', icon: '▤', group: 'ai' },
      },
      {
        path: 'knowledge-graph',
        name: 'knowledgeGraph2',
        component: () => import('../views/KnowledgeGraphView.vue'),
        meta: { title: '知识图谱', icon: '◇', group: 'ai' },
      },
      {
        path: 'team',
        name: 'team',
        component: () => import('../views/TeamView.vue'),
        meta: { title: '团队空间', icon: '⊞', group: 'collab' },
      },
      {
        path: 'inbox',
        name: 'inbox',
        component: () => import('../views/InboxView.vue'),
        meta: { title: '收件箱', icon: '▪', group: 'collab' },
      },
      {
        path: 'memos',
        name: 'memos',
        component: () => import('../views/MemosView.vue'),
        meta: { title: '备忘录', icon: '☐', group: 'personal' },
      },
      {
        path: 'analytics',
        name: 'analytics',
        component: () => import('../views/AnalyticsView.vue'),
        meta: { title: '数据分析', icon: '⊿', group: 'personal' },
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('../views/SettingsView.vue'),
        meta: { title: '系统设置', icon: '⚙', group: 'personal' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '文档智能系统'} - 文档智能系统`
  if (to.meta.public) {
    next()
    return
  }
  const token = localStorage.getItem('token')
  if (!token) {
    next('/login')
  } else {
    next()
  }
})

export default router
