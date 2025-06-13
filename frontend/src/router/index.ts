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
    meta: { title: '登录' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册' },
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/ChatPage.vue'),
    meta: { title: '聊天' },
  },
  {
    path: '/admin',
    component: () => import('@/views/AdminDashboard.vue'),
    children: [
      {
        path: '',
        name: 'AdminHome',
        component: () => import('@/views/admin/AdminHome.vue'),
        meta: { title: '后台管理' },
      },
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('@/views/admin/UserManage.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'kb',
        name: 'KnowledgeManage',
        component: () => import('@/views/admin/KnowledgeManage.vue'),
        meta: { title: '知识库管理' },
      },
      {
        path: 'stats',
        name: 'HotStats',
        component: () => import('@/views/admin/HotStats.vue'),
        meta: { title: '热词统计' },
      },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
