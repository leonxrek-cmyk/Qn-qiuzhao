import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ChatPage from '../views/ChatPage.vue'
import CharacterList from '../views/CharacterList.vue'
import SettingsPage from '../views/SettingsPage.vue'
import LoginPage from '../views/LoginPage.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

// 定义路由
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/chat/:characterId?',
    name: 'Chat',
    component: ChatPage,
    props: true
  },
  {
    path: '/characters',
    name: 'CharacterList',
    component: CharacterList
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsPage,
    meta: { requiresAuth: true }  // 设置页面需要登录
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }  // 管理页面需要管理员权限
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('auth_token')
  
  // 如果路由需要认证但用户未登录
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }
  
  // 如果路由需要管理员权限
  if (to.meta.requiresAdmin && token) {
    try {
      // 检查用户是否为管理员
      const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}')
      if (!userInfo.is_admin) {
        next('/')  // 非管理员重定向到首页
        return
      }
    } catch (error) {
      console.error('检查管理员权限失败:', error)
      next('/')
      return
    }
  }
  
  // 如果已登录用户访问登录页面，重定向到首页
  if (to.name === 'Login' && token) {
    next('/')
    return
  }
  
  next()
})

export default router