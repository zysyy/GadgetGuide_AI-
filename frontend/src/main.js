import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // <--- 1. 导入您创建的路由实例
import './assets/css/theme.css' // 您的全局样式文件

const app = createApp(App)

app.use(router) // <--- 2. 让 Vue 应用使用路由

app.mount('#app')