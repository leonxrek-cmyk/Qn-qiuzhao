import axios from 'axios';

// 创建axios实例（支持通过环境变量配置后端地址），并规范为以 /api 结尾
const rawApiBase = (import.meta?.env?.VITE_API_BASE || '').trim()
let apiBaseURL = '/api'
if (rawApiBase) {
  const trimmed = rawApiBase.replace(/\/$/, '')
  apiBaseURL = /\/api$/.test(trimmed) ? trimmed : `${trimmed}/api`
}
const apiClient = axios.create({
  baseURL: apiBaseURL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 自动添加认证令牌
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    if (response.data && response.data.success === false) {
      throw new Error(response.data.error || '请求失败')
    }
    return response.data
  },
  error => {
    console.error('API请求错误:', error)
    
    // 处理认证错误
    if (error.response && error.response.status === 401) {
      // 清除本地存储的认证信息
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_info')
      
      // 如果当前不在登录页面，跳转到登录页面
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

// API方法
export const apiService = {
  // 获取模型列表
  getModels() {
    return apiClient.get('/models')
  },

  // 基础聊天接口
  chat(messages, model = 'deepseek-v3', stream = false) {
    return apiClient.post('/chat', {
      messages,
      model,
      stream
    })
  },

  // 角色扮演聊天接口（支持会话上下文）
  characterChat(characterName, characterDescription, userQuery, model = 'deepseek-v3', stream = false, sessionId = null) {
    return apiClient.post('/character_chat', {
      character_name: characterName,
      character_description: characterDescription,
      user_query: userQuery,
      session_id: sessionId,
      model,
      stream
    })
  },

  // 通过角色ID进行聊天
  characterChatById(characterId, userQuery, model = 'deepseek-v3', stream = false, sessionId = null) {
    return apiClient.post('/character_chat', {
      character_id: characterId,
      user_query: userQuery,
      session_id: sessionId,
      model,
      stream
    })
  },

  // 语音识别接口
  voiceRecognition(formData) {
    return apiClient.post('/voice_recognition', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 文字转语音接口 - 使用pyttsx3/gTTS，支持角色特定参数
  textToSpeech(text, characterId = null, useOnline = false, language = 'zh') {
    return apiClient.post('/text_to_speech', {
      text,
      character_id: characterId,
      use_online: useOnline,
      language: language
    }, {
      responseType: 'blob'  // 确保返回二进制数据
    })
  },

  // 获取角色配置
  getCharacterConfigs() {
    return apiClient.get('/character_config')
      .then(data => {
        // 确保返回的数据是角色配置数组
        if (data && data.success && Array.isArray(data.configs)) {
          return data.configs
        }
        // 如果API返回的数据格式不正确，返回空数组
        console.warn('获取角色配置失败，返回的数据格式不正确:', data)
        return []
      })
      .catch(error => {
        console.error('获取角色配置失败:', error)
        // 出错时返回空数组，避免应用崩溃
        return []
      })
  },

  // 会话管理接口
  // 创建新会话
  createSession(characterId = null, userId = 'anonymous') {
    return apiClient.post('/sessions', {
      character_id: characterId,
      user_id: userId
    })
  },

  // 获取会话信息
  getSession(sessionId) {
    return apiClient.get(`/sessions/${sessionId}`)
  },

  // 获取会话消息历史
  getSessionMessages(sessionId) {
    return apiClient.get(`/sessions/${sessionId}/messages`)
  },

  // 清空会话消息
  clearSession(sessionId) {
    return apiClient.post(`/sessions/${sessionId}/clear`)
  },

  // 流式响应处理
  streamChat(characterName, characterDescription, userQuery, onChunk, onComplete, onError) {
    const eventSource = new EventSource(`/api/character_chat?character_name=${encodeURIComponent(characterName)}&character_description=${encodeURIComponent(characterDescription)}&user_query=${encodeURIComponent(userQuery)}&stream=true`)
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.content) {
          onChunk(data.content)
        }
      } catch (error) {
        console.error('解析流式响应失败:', error)
      }
    }
    
    eventSource.onopen = () => {
      console.log('流式连接已建立')
    }
    
    eventSource.onerror = (error) => {
      console.error('流式连接错误:', error)
      eventSource.close()
      if (onError) {
        onError(error)
      }
    }
    
    eventSource.onclose = () => {
      console.log('流式连接已关闭')
      if (onComplete) {
        onComplete()
      }
    }
    
    return () => {
      eventSource.close()
    }
  },

  // 用户认证接口
  // 用户注册
  register(username, password, email = '') {
    return apiClient.post('/auth/register', {
      username,
      password,
      email
    })
  },

  // 用户登录
  login(username, password) {
    return apiClient.post('/auth/login', {
      username,
      password
    })
  },

  // 用户登出
  logout() {
    const token = localStorage.getItem('auth_token')
    return apiClient.post('/auth/logout', {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 获取当前用户信息
  getCurrentUser() {
    const token = localStorage.getItem('auth_token')
    return apiClient.get('/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 获取用户设置
  getUserSettings() {
    const token = localStorage.getItem('auth_token')
    return apiClient.get('/auth/settings', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 更新用户设置
  updateUserSettings(settings) {
    const token = localStorage.getItem('auth_token')
    return apiClient.put('/auth/settings', {
      settings
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 更新用户头像
  updateUserAvatar(avatarUrl) {
    const token = localStorage.getItem('auth_token')
    return apiClient.put('/auth/avatar', {
      avatar: avatarUrl
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 更新用户昵称
  updateNickname(nickname) {
    const token = localStorage.getItem('auth_token')
    return apiClient.post('/auth/update-nickname', {
      nickname: nickname
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 更新用户邮箱
  updateEmail(email) {
    const token = localStorage.getItem('auth_token')
    return apiClient.post('/auth/update-email', {
      email: email
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 管理员API
  // 获取所有用户
  getAllUsers() {
    const token = localStorage.getItem('auth_token')
    return apiClient.get('/admin/users', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 创建用户
  createUser(userData) {
    const token = localStorage.getItem('auth_token')
    return apiClient.post('/admin/users', userData, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 更新用户
  updateUser(userId, userData) {
    const token = localStorage.getItem('auth_token')
    return apiClient.put(`/admin/users/${userId}`, userData, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 删除用户
  deleteUser(userId) {
    const token = localStorage.getItem('auth_token')
    return apiClient.delete(`/admin/users/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 创建角色
  createCharacter(characterData) {
    const token = localStorage.getItem('auth_token')
    return apiClient.post('/admin/characters', characterData, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 更新角色
  updateCharacter(characterId, characterData) {
    const token = localStorage.getItem('auth_token')
    return apiClient.put(`/admin/characters/${characterId}`, characterData, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 删除角色
  deleteCharacter(characterId) {
    const token = localStorage.getItem('auth_token')
    return apiClient.delete(`/admin/characters/${characterId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 获取统计数据
  getStatistics(params = {}) {
    const token = localStorage.getItem('auth_token')
    return apiClient.get('/admin/statistics', {
      params,
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 获取用户会话历史
  getUserSessions(characterId = null) {
    const token = localStorage.getItem('auth_token')
    const params = characterId ? { character_id: characterId } : {}
    return apiClient.get('/user_sessions', {
      params,
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 获取用户与特定角色的最新会话
  getLatestSession(characterId) {
    const token = localStorage.getItem('auth_token')
    return apiClient.get(`/latest_session/${characterId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 删除会话
  deleteSession(characterId, sessionId) {
    const token = localStorage.getItem('auth_token')
    return apiClient.delete(`/delete_session/${characterId}/${sessionId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  },

  // 清空所有历史记录
  clearAllHistory() {
    const token = localStorage.getItem('auth_token')
    return apiClient.delete('/clear_all_history', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
  }
}

export default apiService