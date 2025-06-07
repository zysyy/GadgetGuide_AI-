import { createRouter, createWebHistory } from "vue-router"

const routes = [
  {
    path: "/",
    redirect: "/login"  // 主页自动跳转到登录页，防止空白
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/Login.vue"),
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/Register.vue"),  // 注册页
  },
  {
    path: "/chat",
    name: "Chat",
    component: () => import("@/views/ChatPage.vue"),
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
