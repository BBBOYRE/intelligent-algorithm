import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
    meta: { title: '系统概览', icon: '🏠' },
  },
  {
    path: '/upload',
    name: 'upload',
    component: () => import('../views/UploadView.vue'),
    meta: { title: '文档上传', icon: '📄' },
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('../views/ChatView.vue'),
    meta: { title: '智能问答', icon: '💬' },
  },
  {
    path: '/table-fill',
    name: 'tableFill',
    component: () => import('../views/TableFillView.vue'),
    meta: { title: '表格填写', icon: '📊' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || '文档智能系统'} - 文档智能系统`
})

export default router
