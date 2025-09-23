import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api',
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
  chat(messages, model = 'x-ai/grok-4-fast', stream = false) {
    return apiClient.post('/chat', {
      messages,
      model,
      stream
    })
  },

  // 角色扮演聊天接口
  characterChat(characterName, characterDescription, userQuery, model = 'x-ai/grok-4-fast', stream = false) {
    return apiClient.post('/character_chat', {
      character_name: characterName,
      character_description: characterDescription,
      user_query: userQuery,
      model,
      stream
    })
  },

  // 语音识别接口
  voiceRecognition(audioFile) {
    const formData = new FormData()
    formData.append('audio', audioFile)
    return apiClient.post('/voice_recognition', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 文字转语音接口
  textToSpeech(text, language = 'zh-CN') {
    return apiClient.post('/text_to_speech', {
      text,
      language
    })
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
  }
}

export default apiService