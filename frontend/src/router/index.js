import { createRouter, createWebHistory } from 'vue-router';
import ChatInterface from '../components/ChatInterface.vue'; // 您的聊天组件
import DocumentUploader from '../components/DocumentUploader.vue'; // 您的文档上传组件

const routes = [
  {
    path: '/', // 根路径
    redirect: '/chat' // 当用户访问根路径时，自动重定向到聊天界面
  },
  {
    path: '/chat',
    name: 'Chat',
    component: ChatInterface,
    meta: { title: 'GadgetGuide AI - 聊天' } // 可选：页面标题
  },
  {
    path: '/upload',
    name: 'UploadDocuments',
    component: DocumentUploader,
    meta: { title: 'GadgetGuide AI - 上传文档' } // 可选：页面标题
  },
  // --- 未来可以添加更多路由 ---
  // {
  //   path: '/login',
  //   name: 'Login',
  //   component: () => import('../views/LoginPage.vue') // 示例：异步加载组件
  // },
  // {
  //   path: '/history',
  //   name: 'ChatHistory',
  //   component: () => import('../views/ChatHistoryPage.vue'),
  //   meta: { requiresAuth: true } // 示例：路由元信息，用于导航守卫
  // }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL || '/'), // 使用 HTML5 History 模式
  routes
});

// 可选：全局前置导航守卫，例如用于设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'GadgetGuide AI';
  next();
});

export default router;