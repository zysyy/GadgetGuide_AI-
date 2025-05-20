// src/api/auth.js

import axios from "@/utils/axios"

// 登录接口（JSON参数）
export function login(username, password) {
  return axios.post("/auth/login", { username, password })
}

// 注册接口（JSON参数）
export function register(username, password) {
  return axios.post("/auth/register", { username, password })
}
