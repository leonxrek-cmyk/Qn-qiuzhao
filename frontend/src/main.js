import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { useAuth } from './composables/useAuth.js'

const app = createApp(App)

// 使用路由
app.use(router)

// 初始化用户认证状态
const { initAuth } = useAuth()
initAuth()

// 挂载应用
app.mount('#app')