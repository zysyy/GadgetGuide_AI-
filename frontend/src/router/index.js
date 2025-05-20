// src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import ChatInterface from '../components/ChatInterface.vue'
import DocumentUploader from '../components/DocumentUploader.vue'
import UserLogin from '../components/UserLogin.vue'
import UserRegister from '../components/UserRegister.vue' // ✅ 新增注册页
import { getToken } from '@/utils/token'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'UserLogin',
    component: UserLogin,
    meta: { title: 'GadgetGuide AI - 登录', public: true }
  },
  {
    path: '/register',
    name: 'UserRegister',
    component: UserRegister,
    meta: { title: 'GadgetGuide AI - 注册', public: true }
  },
  {
    path: '/chat',
    name: 'ChatInterface',
    component: ChatInterface,
    meta: { title: 'GadgetGuide AI - 聊天', requiresAuth: true }
  },
  {
    path: '/upload',
    name: 'UploadDocuments',
    component: DocumentUploader,
    meta: { title: 'GadgetGuide AI - 上传文档', requiresAuth: true }
  },
  // ...其他页面
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL || '/'),
  routes
})

// 全局前置导航守卫
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'GadgetGuide AI'

  const token = getToken()
  // 访问需要登录的页面且没登录
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }
  // 已登录时禁止访问登录/注册页，自动跳到 /chat
  if ((to.path === '/login' || to.path === '/register') && token) {
    return next('/chat')
  }
  next()
})

export default router
