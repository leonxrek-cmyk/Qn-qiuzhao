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
    // 可以在这里添加token等认证信息
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

  // 角色扮演聊天接口
  characterChat(characterName, characterDescription, userQuery, model = 'deepseek-v3', stream = false) {
    return apiClient.post('/character_chat', {
      character_name: characterName,
      character_description: characterDescription,
      user_query: userQuery,
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

  // 文字转语音接口 - 支持角色特定参数
  textToSpeech(text, characterId = null, voice = 'zh-CN', speed = 1.0) {
    return apiClient.post('/text_to_speech', {
      text,
      character_id: characterId,
      voice,
      speed
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

  // 流式响应处理
  streamChat(characterName, characterDescription, userQuery, onChunk, onComplete, onError) {
    // 使用axios的POST请求替代EventSource，以匹配后端实现
    apiClient.post('/character_chat', {
      character_name: characterName,
      character_description: characterDescription,
      user_query: userQuery,
      stream: true,
      model: 'deepseek-v3'
    })
    .then(response => {
      if (response && response.success && response.content) {
        // 后端当前不支持真正的流式响应，返回完整内容
        onChunk(response.content)
        if (onComplete) {
          onComplete()
        }
      } else {
        const error = new Error('流式响应格式错误')
        console.error('流式响应格式错误:', response)
        if (onError) {
          onError(error)
        }
      }
    })
    .catch(error => {
      console.error('流式请求失败:', error)
      if (onError) {
        onError(error)
      }
    })
    
    // 返回取消函数（当前简单实现）
    return () => {
      console.log('取消流式请求')
    }
  }
}

export default apiService