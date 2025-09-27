/**
 * 用户认证状态管理
 */
import { ref, reactive, computed } from 'vue'
import apiService from '../apiService.js'

// 全局状态
const isAuthenticated = ref(false)
const currentUser = reactive({
  id: null,
  username: null,
  email: null,
  avatar: null,
  settings: {}
})
const isLoading = ref(false)

export function useAuth() {
  // 初始化用户状态
  const initAuth = async () => {
    const token = localStorage.getItem('auth_token')
    const userInfo = localStorage.getItem('user_info')
    
    if (token && userInfo) {
      try {
        const user = JSON.parse(userInfo)
        Object.assign(currentUser, user)
        isAuthenticated.value = true
        
        // 验证token是否仍然有效
        await refreshUserInfo()
      } catch (error) {
        console.error('初始化用户状态失败:', error)
        logout()
      }
    }
  }

  // 刷新用户信息
  const refreshUserInfo = async () => {
    try {
      const response = await apiService.getCurrentUser()
      if (response.success) {
        Object.assign(currentUser, response.user)
        localStorage.setItem('user_info', JSON.stringify(response.user))
      }
    } catch (error) {
      console.error('刷新用户信息失败:', error)
      if (error.response && error.response.status === 401) {
        logout()
      }
    }
  }

  // 登录
  const login = async (username, password) => {
    isLoading.value = true
    try {
      const response = await apiService.login(username, password)
      if (response.success) {
        localStorage.setItem('auth_token', response.token)
        localStorage.setItem('user_info', JSON.stringify(response.user))
        Object.assign(currentUser, response.user)
        isAuthenticated.value = true
        return { success: true }
      } else {
        return { success: false, error: response.error }
      }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, error: '登录失败，请检查网络连接' }
    } finally {
      isLoading.value = false
    }
  }

  // 注册
  const register = async (username, password, email = '') => {
    isLoading.value = true
    try {
      const response = await apiService.register(username, password, email)
      return response
    } catch (error) {
      console.error('注册失败:', error)
      return { success: false, error: '注册失败，请检查网络连接' }
    } finally {
      isLoading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      await apiService.logout()
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      // 清除本地状态
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_info')
      Object.assign(currentUser, {
        id: null,
        username: null,
        email: null,
        avatar: null,
        settings: {}
      })
      isAuthenticated.value = false
    }
  }

  // 更新用户设置
  const updateSettings = async (settings) => {
    try {
      const response = await apiService.updateUserSettings(settings)
      if (response.success) {
        Object.assign(currentUser.settings, response.settings)
        localStorage.setItem('user_info', JSON.stringify(currentUser))
        return { success: true }
      }
      return response
    } catch (error) {
      console.error('更新设置失败:', error)
      return { success: false, error: '更新设置失败' }
    }
  }

  // 更新用户头像
  const updateAvatar = async (avatarUrl) => {
    try {
      const response = await apiService.updateUserAvatar(avatarUrl)
      if (response.success) {
        currentUser.avatar = response.avatar
        localStorage.setItem('user_info', JSON.stringify(currentUser))
        return { success: true }
      }
      return response
    } catch (error) {
      console.error('更新头像失败:', error)
      return { success: false, error: '更新头像失败' }
    }
  }

  // 计算属性
  const userDisplayName = computed(() => {
    return currentUser.nickname || currentUser.username || '游客'
  })

  const userAvatar = computed(() => {
    return currentUser.avatar || '/user-avatar.svg'
  })

  const isAdmin = computed(() => {
    return currentUser.is_admin || false
  })

  return {
    // 状态
    isAuthenticated,
    currentUser,
    isLoading,
    userDisplayName,
    userAvatar,
    isAdmin,
    
    // 方法
    initAuth,
    refreshUserInfo,
    login,
    register,
    logout,
    updateSettings,
    updateAvatar
  }
}
