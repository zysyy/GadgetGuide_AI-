// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/ChatPage.vue'),
  },
  // 管理后台嵌套路由
  {
    path: '/admin',
    component: () => import('@/views/AdminDashboard.vue'),
    children: [
      {
        path: '',
        name: 'AdminHome',
        component: () => import('@/views/admin/AdminHome.vue'),
      },
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('@/views/admin/UserManage.vue'),
      },
      {
        path: 'kb',
        name: 'KnowledgeManage',
        component: () => import('@/views/admin/KnowledgeManage.vue'),
      },
      {
        path: 'stats',
        name: 'HotStats',
        component: () => import('@/views/admin/HotStats.vue'),
      },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
