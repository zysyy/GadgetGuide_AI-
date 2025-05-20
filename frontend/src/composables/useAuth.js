// src/composables/useAuth.js
import { ref } from "vue"
import { getToken } from "@/utils/token"

// 全局唯一 isLogin
const isLogin = ref(!!getToken())

// 每次 token 变化后手动调用，刷新登录状态
export function syncLoginStatus() {
  isLogin.value = !!getToken()
}

// composable 用于在各组件内响应式获取 isLogin
export function useAuth() {
  return { isLogin, syncLoginStatus }
}
