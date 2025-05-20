// src/utils/axios.js

import axios from "axios"
import { getToken } from "./token"

const instance = axios.create({
  baseURL: "http://localhost:8000", // 后端 API 根路径
  timeout: 5000
})

// 请求拦截器：自动附加 token
instance.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

export default instance
