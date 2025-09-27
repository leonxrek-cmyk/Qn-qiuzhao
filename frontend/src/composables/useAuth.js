/**
 * 用户认证状态管理
 */
import { ref, reactive, computed } from 'vue'
import apiService from '../apiService.js'

// 全局状态
const isAuthenticated = ref(false)
const isGuestMode = ref(false)
const currentUser = reactive({
  id: null,
  username: null,
  email: null,
  avatar: null,
  settings: {}
})
const isLoading = ref(false)

export function useAuth() {
  // 生成随机游客信息
  const generateGuestInfo = () => {
    const adjectives = ['快乐的', '聪明的', '勇敢的', '友善的', '活泼的', '温暖的', '幽默的', '优雅的', '神秘的', '可爱的']
    const nouns = ['小猫', '小狗', '小鸟', '小熊', '小兔', '小鹿', '小狐', '小鱼', '小龙', '小象']
    const colors = ['红色', '蓝色', '绿色', '紫色', '橙色', '粉色', '黄色', '青色', '银色', '金色']
    
    const randomAdjective = adjectives[Math.floor(Math.random() * adjectives.length)]
    const randomNoun = nouns[Math.floor(Math.random() * nouns.length)]
    const randomColor = colors[Math.floor(Math.random() * colors.length)]
    const randomNum = Math.floor(Math.random() * 9999) + 1
    
    return {
      username: `guest_${randomNum}`,
      nickname: `${randomAdjective}${randomColor}${randomNoun}`,
      id: `guest_${Date.now()}_${randomNum}`,
      avatar: '/user-avatar.svg',
      email: '',
      is_guest: true,
      settings: {}
    }
  }

  // 初始化用户状态
  const initAuth = async () => {
    const token = localStorage.getItem('auth_token')
    const userInfo = localStorage.getItem('user_info')
    const guestInfo = sessionStorage.getItem('guest_info')
    
    if (token && userInfo) {
      try {
        const user = JSON.parse(userInfo)
        Object.assign(currentUser, user)
        isAuthenticated.value = true
        isGuestMode.value = false
        
        // 验证token是否仍然有效
        await refreshUserInfo()
      } catch (error) {
        console.error('初始化用户状态失败:', error)
        logout()
      }
    } else if (guestInfo) {
      try {
        const guest = JSON.parse(guestInfo)
        Object.assign(currentUser, guest)
        isAuthenticated.value = true
        isGuestMode.value = true
      } catch (error) {
        console.error('初始化游客状态失败:', error)
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
      const data = response.data
      
      if (data.success) {
        localStorage.setItem('auth_token', data.token)
        localStorage.setItem('user_info', JSON.stringify(data.user))
        Object.assign(currentUser, data.user)
        isAuthenticated.value = true
        return { success: true }
      } else {
        // 后端返回的具体错误信息
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('登录失败:', error)
      // 检查是否是网络错误
      if (error.response && error.response.data) {
        // 服务器返回了错误响应，提取具体错误信息
        const errorData = error.response.data
        return { success: false, error: errorData.error || '登录失败' }
      } else if (error.request) {
        // 请求发出但没有收到响应
        return { success: false, error: '无法连接到服务器，请检查网络连接' }
      } else {
        // 其他错误
        return { success: false, error: '登录失败，请稍后重试' }
      }
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

  // 游客登录
  const loginAsGuest = async () => {
    const guestInfo = generateGuestInfo()
    
    try {
      // 为游客生成头像
      const avatarResponse = await apiService.generateGuestAvatar(guestInfo.nickname, guestInfo.id)
      if (avatarResponse && avatarResponse.avatar) {
        guestInfo.avatar = avatarResponse.avatar
      }
    } catch (error) {
      console.error('生成游客头像失败:', error)
      // 头像生成失败不影响登录，使用默认头像
    }
    
    Object.assign(currentUser, guestInfo)
    isAuthenticated.value = true
    isGuestMode.value = true
    
    // 将游客信息存储到sessionStorage（页面关闭后自动清除）
    sessionStorage.setItem('guest_info', JSON.stringify(guestInfo))
    
    return { success: true, user: guestInfo }
  }

  // 登出
  const logout = async (router = null) => {
    try {
      if (!isGuestMode.value) {
        await apiService.logout()
      }
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      // 清除本地状态
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_info')
      sessionStorage.removeItem('guest_info')
      
      // 如果是游客模式，清除所有会话数据
      if (isGuestMode.value) {
        // 清除当前页面的会话数据
        const currentSessionId = sessionStorage.getItem('current_session_id')
        if (currentSessionId) {
          sessionStorage.removeItem('current_session_id')
          sessionStorage.removeItem(`session_${currentSessionId}`)
        }
        // 清除所有游客会话相关的sessionStorage数据
        Object.keys(sessionStorage).forEach(key => {
          if (key.startsWith('guest_') || key.startsWith('session_')) {
            sessionStorage.removeItem(key)
          }
        })
      }
      
      Object.assign(currentUser, {
        id: null,
        username: null,
        email: null,
        avatar: null,
        is_admin: false,
        is_guest: false,
        settings: {}
      })
      isAuthenticated.value = false
      isGuestMode.value = false
      
      // 如果提供了router且当前在管理页面，跳转到首页
      if (router) {
        const currentRoute = router.currentRoute.value
        if (currentRoute.name === 'Admin' || currentRoute.name === 'Chat') {
          router.push('/')
        }
      }
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
    isGuestMode,
    currentUser,
    isLoading,
    userDisplayName,
    userAvatar,
    isAdmin,
    
    // 方法
    initAuth,
    refreshUserInfo,
    login,
    loginAsGuest,
    register,
    logout,
    updateSettings,
    updateAvatar
  }
}
