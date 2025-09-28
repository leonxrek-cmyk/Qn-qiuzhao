<template>
  <div class="chat-page">
    <!-- 顶部角色信息栏 -->
    <div class="chat-header">
      <div class="character-info">
        <button class="back-button" @click="backToCharacters" title="返回角色列表">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <div class="character-avatar">
          <img :src="currentCharacter?.avatar || '/default-avatar.png'" :alt="currentCharacter?.name" />
        </div>
        <div class="character-details">
          <h2>{{ currentCharacter?.name || '选择一个角色开始对话' }}</h2>
          <p>{{ currentCharacter?.description || '请从左侧选择一个角色或搜索角色' }}</p>
        </div>
      </div>
      
      <!-- 亲密度进度条 - 放在中间空白区域 -->
      <div class="intimacy-section" v-if="currentCharacter && !isGuestMode && intimacyData">
        <IntimacyBar 
          :intimacy="parseInt(intimacyData.intimacy) || 0"
          :level-progress="intimacyData.level_progress || {}"
          ref="intimacyBar"
        />
      </div>
      
      <div class="chat-actions">
        <button class="action-button" @click="clearChat">🗑️ 清空对话</button>
        <button class="action-button" @click="backToCharacters">👥 切换角色</button>
      </div>
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0 && currentCharacter" class="welcome-message">
        <p>👋 你好！我是 {{ currentCharacter.name }}。</p>
        <p>{{ getWelcomeMessage() }}</p>
        <p>你可以问我任何问题，我会尽力以我的身份和知识背景回答你。</p>
      </div>

      <!-- 消息列表 -->
      <MessageBubble
        v-for="message in messages"
        :key="message.id"
        :message="message.content"
        :is-user="message.isUser"
        :character="currentCharacter"
        :timestamp="message.timestamp"
        :character-id="message.characterId || (currentCharacter ? currentCharacter.id : null)"
      />

      <!-- 正在输入提示 -->
      <div v-if="isTyping" class="typing-indicator">
        <div class="character-avatar small">
          <img :src="currentCharacter?.avatar || '/default-avatar.png'" :alt="currentCharacter?.name" />
        </div>
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-area">
      <div class="input-container">
        <!-- 语音输入模式 -->
        <div v-if="isVoiceRecording" class="voice-input-container">
          <div class="voice-wave-container">
            <div class="voice-wave">
              <div class="wave-bar" v-for="i in 20" :key="i" :style="{ animationDelay: i * 0.1 + 's' }"></div>
            </div>
            <span class="voice-status">正在录音...</span>
          </div>
          <button class="voice-stop-button" @click="stopVoiceRecording">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="6" width="12" height="12" rx="2"/>
            </svg>
          </button>
        </div>
        
        <!-- 文本输入模式 -->
        <template v-else>
          <button 
            class="voice-button" 
            @click="startVoiceRecording"
            :disabled="!currentCharacter"
            title="语音输入"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C13.1 2 14 2.9 14 4V12C14 13.1 13.1 14 12 14C10.9 14 10 13.1 10 12V4C10 2.9 10.9 2 12 2ZM19 10V12C19 15.3 16.3 18 13 18V20H11V18C7.7 18 5 15.3 5 12V10H7V12C7 14.2 8.8 16 11 16H13C15.2 16 17 14.2 17 12V10H19Z"/>
            </svg>
          </button>
          <input
            type="text"
            v-model="userInput"
            placeholder="输入消息..."
            class="text-input"
            @keyup.enter="sendMessage"
            :disabled="!currentCharacter"
          />
          <button 
            class="send-button" 
            @click="sendMessage"
            :disabled="!currentCharacter || !userInput.trim()"
          >
            发送
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import MessageBubble from '../components/MessageBubble.vue'
import IntimacyBar from '../components/IntimacyBar.vue'
import apiService from '../apiService.js'
import { useAuth } from '../composables/useAuth.js'

export default {
  name: 'ChatPage',
  components: {
    MessageBubble,
    IntimacyBar
  },
  setup() {
    const { isAuthenticated, isGuestMode } = useAuth()
    return { isAuthenticated, isGuestMode }
  },
  data() {
    return {
      currentCharacter: null,
      messages: [],
      userInput: '',
      isTyping: false,
      currentSessionId: null, // 当前会话ID
      isLoadingSession: false, // 会话加载状态
      hasLoadedCharacter: false,
      currentRequestId: null, // 当前请求ID，用于取消过期请求
      abortController: null, // 用于取消HTTP请求
      characterStates: {}, // 存储每个角色的状态（消息、会话ID、等待状态等）
      intimacyData: null, // 亲密度数据
      intimacyCache: {}, // 亲密度数据缓存，按角色ID存储
      // 语音输入相关状态
      isVoiceRecording: false, // 是否正在录音
      mediaRecorder: null, // 媒体录制器
      audioChunks: [], // 音频数据块
    }
  },
  async mounted() {
    await this.handleRouteChange()
    
    // 监听会话删除事件
    window.addEventListener('sessionDeleted', this.handleSessionDeleted)
  },
  
  watch: {
    // 监听路由变化
    '$route': {
      handler: 'handleRouteChange',
      immediate: false
    }
  },
  
  beforeUnmount() {
    // 组件销毁前取消所有请求
    this.cancelCurrentRequest()
    
    // 移除事件监听器
    window.removeEventListener('sessionDeleted', this.handleSessionDeleted)
  },
  methods: {
    async handleRouteChange() {
      // 保存当前角色的状态（如果有的话）
      this.saveCurrentCharacterState()
      
      // 从路由参数获取角色ID
      const characterId = this.$route.params.characterId
      if (characterId) {
        await this.loadCharacter(characterId)
        
        // 检查是否有指定的会话ID
        const sessionId = this.$route.query.session
        if (sessionId && this.isAuthenticated) {
          await this.loadSpecificSession(sessionId)
        }
      }
    },

    // 保存当前角色的状态
    saveCurrentCharacterState() {
      if (this.currentCharacter) {
        // 游客模式下使用sessionStorage，正常用户使用内存状态
        const stateData = {
          messages: [...this.messages],
          sessionId: this.currentSessionId,
          isTyping: this.isTyping,
          requestId: this.currentRequestId,
          abortController: this.abortController
        }
        
        if (this.isGuestMode) {
          // 游客模式：存储到sessionStorage
          sessionStorage.setItem(`guest_character_${this.currentCharacter.id}`, JSON.stringify({
            messages: stateData.messages,
            sessionId: stateData.sessionId
          }))
        } else {
          // 正常用户：存储到内存
          this.characterStates[this.currentCharacter.id] = stateData
        }
        
        console.log('保存角色状态:', this.currentCharacter.id, {
          messageCount: this.messages.length,
          isTyping: this.isTyping,
          hasRequest: !!this.currentRequestId,
          mode: this.isGuestMode ? 'guest' : 'user'
        })
      }
    },

    // 恢复角色状态
    restoreCharacterState(characterId) {
      let state = null
      
      if (this.isGuestMode) {
        // 游客模式：从sessionStorage恢复
        const guestData = sessionStorage.getItem(`guest_character_${characterId}`)
        if (guestData) {
          try {
            const parsed = JSON.parse(guestData)
            state = {
              messages: parsed.messages || [],
              sessionId: parsed.sessionId || null,
              isTyping: false,
              requestId: null,
              abortController: null
            }
          } catch (error) {
            console.error('解析游客状态失败:', error)
          }
        }
      } else {
        // 正常用户：从内存恢复
        state = this.characterStates[characterId]
      }
      
      if (state) {
        this.messages = [...state.messages]
        this.currentSessionId = state.sessionId
        this.isTyping = state.isTyping || false
        this.currentRequestId = state.requestId || null
        this.abortController = state.abortController || null
        console.log('恢复角色状态:', characterId, {
          messageCount: this.messages.length,
          isTyping: this.isTyping,
          hasRequest: !!this.currentRequestId,
          mode: this.isGuestMode ? 'guest' : 'user'
        })
      } else {
        // 没有保存的状态，初始化为空
        this.messages = []
        this.currentSessionId = null
        this.isTyping = false
        this.currentRequestId = null
        this.abortController = null
        console.log('初始化角色状态:', characterId, {
          mode: this.isGuestMode ? 'guest' : 'user'
        })
      }
    },

    // 取消当前正在进行的请求（但不影响已保存的其他角色状态）
    cancelCurrentRequest() {
      if (this.abortController) {
        console.log('取消正在进行的AI请求')
        this.abortController.abort()
        this.abortController = null
      }
      
      // 重置当前状态
      this.isTyping = false
      this.currentRequestId = null
      
      // 如果有当前角色，更新其保存的状态
      if (this.currentCharacter) {
        const state = this.characterStates[this.currentCharacter.id]
        if (state) {
          state.isTyping = false
          state.requestId = null
          state.abortController = null
        }
      }
    },

    // 包装API调用以支持取消
    async makeApiCall(apiFunction) {
      // 由于当前的apiService不支持AbortController，
      // 我们使用Promise.race来实现超时和取消检查
      return new Promise((resolve, reject) => {
        const apiPromise = apiFunction()
        
        // 检查取消状态的间隔
        const checkCancelInterval = setInterval(() => {
          if (this.abortController && this.abortController.signal.aborted) {
            clearInterval(checkCancelInterval)
            const error = new Error('Request was aborted')
            error.name = 'AbortError'
            reject(error)
          }
        }, 100)

        apiPromise
          .then(result => {
            clearInterval(checkCancelInterval)
            resolve(result)
          })
          .catch(error => {
            clearInterval(checkCancelInterval)
            reject(error)
          })
      })
    },

    async loadCharacter(characterId) {
      try {
        console.log('开始加载角色:', characterId)
        
        // 如果是相同角色，恢复状态而不是清空
        if (this.currentCharacter && this.currentCharacter.id === characterId) {
          console.log('相同角色，恢复状态')
          this.restoreCharacterState(characterId)
          return
        }
        
        // 获取角色配置
        const configs = await apiService.getCharacterConfigs()
        this.currentCharacter = configs.find(char => char.id === characterId)
        
        if (!this.currentCharacter) {
          console.error('未找到角色:', characterId)
          this.$router.push('/')
          return
        }

        console.log('角色加载成功:', this.currentCharacter)
        
        // 恢复或初始化角色状态
        this.restoreCharacterState(characterId)
        
        // 如果没有历史消息且不是游客模式，尝试加载最新会话
        if (this.messages.length === 0 && this.isAuthenticated && !this.isGuestMode) {
          await this.loadLatestSession(characterId)
        }
        
        // 加载亲密度数据（仅对已登录用户）
        if (this.isAuthenticated && !this.isGuestMode) {
          await this.loadIntimacyData(characterId)
          
          // 检查是否需要发送主动问候（相见恨晚10级和伯乐100级）
          if (this.messages.length === 0 && this.intimacyData) {
            await this.checkAndSendActiveGreeting()
          }
        }
        
        this.hasLoadedCharacter = true
        
      } catch (error) {
        console.error('加载角色失败:', error)
        this.$router.push('/')
      }
    },

    getWelcomeMessage() {
      if (!this.currentCharacter) return ''
      
      const welcomeMessages = {
        'harry-potter': '我刚从霍格沃茨回来，有什么魔法问题想问我吗？',
        'sherlock-holmes': '有什么谜题需要我来推理吗？',
        'einstein': '让我们一起探讨科学的奥秘吧！',
        'shakespeare': '愿我的文字为你带来灵感！',
        'confucius': '让我们谈论人生的智慧。',
        'socrates': '让我们通过对话来寻找真理。'
      }
      
      return welcomeMessages[this.currentCharacter.id] || '很高兴与你对话！'
    },

    async sendMessage() {
      if (!this.userInput.trim() || !this.currentCharacter) return

      // 取消之前的请求
      this.cancelCurrentRequest()

      // 生成唯一的请求ID
      const requestId = Date.now() + Math.random()
      this.currentRequestId = requestId

      // 创建AbortController
      this.abortController = new AbortController()

      const userMessage = {
        id: Date.now(),
        content: this.userInput,
        isUser: true,
        timestamp: new Date().toLocaleTimeString(),
        characterId: this.currentCharacter.id
      }

      this.messages.push(userMessage)
      const userQuery = this.userInput
      const currentCharacterId = this.currentCharacter.id // 保存当前角色ID
      this.userInput = ''
      this.isTyping = true

      // 立即保存状态，确保等待状态被保存
      this.saveCurrentCharacterState()

      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom()
      })

      try {
        // 如果没有会话ID且用户已登录且不是游客模式，创建新会话
        if (!this.currentSessionId && this.isAuthenticated && !this.isGuestMode) {
          try {
            const sessionResponse = await apiService.createSession(this.currentCharacter.id)
            this.currentSessionId = sessionResponse.session_id
            console.log('创建新会话:', this.currentSessionId)
          } catch (sessionError) {
            console.error('创建会话失败:', sessionError)
          }
        }

        // 检查请求是否已被取消
        if (this.currentRequestId !== requestId) {
          console.log('请求已被取消:', requestId)
          return
        }

        console.log('发送消息到AI:', {
          characterId: this.currentCharacter.id,
          userQuery: userQuery,
          sessionId: this.currentSessionId,
          requestId: requestId
        })

        let response
        if (this.currentSessionId && !this.isGuestMode) {
          // 使用会话上下文（仅限非游客模式）
          response = await this.makeApiCall(() => 
            apiService.characterChatById(
              this.currentCharacter.id,
              userQuery,
              'deepseek-v3',
              false,
              this.currentSessionId
            )
          )
          
          // 更新会话ID（如果后端返回了新的会话ID）
          if (response.session_id && response.session_id !== this.currentSessionId) {
            this.currentSessionId = response.session_id
            console.log('会话ID已更新:', this.currentSessionId)
          }
        } else {
          // 不使用会话上下文（游客模式或无会话ID）
          response = await this.makeApiCall(() =>
            apiService.characterChatById(
              this.currentCharacter.id,
              userQuery,
              'deepseek-v3',
              false
            )
          )
        }

        // 再次检查请求是否已被取消
        if (this.currentRequestId !== requestId) {
          console.log('响应被丢弃，请求已被取消:', requestId)
          return
        }

        // 检查角色是否已切换
        if (this.currentCharacter.id !== currentCharacterId) {
          console.log('响应被丢弃，角色已切换:', currentCharacterId, '->', this.currentCharacter.id)
          return
        }

        console.log('AI响应:', response)

        const aiMessage = {
          id: Date.now() + 1,
          content: response.content,
          isUser: false,
          timestamp: new Date().toLocaleTimeString(),
          characterId: currentCharacterId // 使用请求时的角色ID
        }

        this.messages.push(aiMessage)

        // 处理亲密度更新（如果响应中包含亲密度信息）
        if (response.intimacy && this.isAuthenticated && !this.isGuestMode) {
          this.handleIntimacyUpdate(response.intimacy)
        }

        // 保存更新后的状态
        this.saveCurrentCharacterState()

        // 滚动到底部
        this.$nextTick(() => {
          this.scrollToBottom()
        })

      } catch (error) {
        // 检查是否是请求被取消
        if (error.name === 'AbortError') {
          console.log('请求被用户取消:', requestId)
          return
        }

        // 检查请求是否仍然有效
        if (this.currentRequestId !== requestId) {
          console.log('错误被忽略，请求已被取消:', requestId)
          return
        }

        // 检查角色是否已切换
        if (this.currentCharacter.id !== currentCharacterId) {
          console.log('错误被忽略，角色已切换:', currentCharacterId, '->', this.currentCharacter.id)
          return
        }

        console.error('发送消息失败:', error)
        
        const errorMessage = {
          id: Date.now() + 1,
          content: '抱歉，我现在无法回应。请稍后再试。',
          isUser: false,
          timestamp: new Date().toLocaleTimeString(),
          characterId: currentCharacterId // 使用请求时的角色ID
        }

        this.messages.push(errorMessage)

        // 保存更新后的状态
        this.saveCurrentCharacterState()
        
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      } finally {
        // 只有当前请求才清除状态
        if (this.currentRequestId === requestId) {
          this.isTyping = false
          this.currentRequestId = null
          this.abortController = null
          // 保存状态变化
          this.saveCurrentCharacterState()
        }
      }
    },

    async clearChat() {
      if (this.currentSessionId) {
        try {
          await apiService.clearSession(this.currentSessionId)
          console.log('会话已清空:', this.currentSessionId)
        } catch (error) {
          console.error('清空会话失败:', error)
        }
      }
      
      this.messages = []
      console.log('对话已清空')
    },

    backToCharacters() {
      this.$router.push('/characters')
    },

    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },


    async createNewSession() {
      if (!this.currentCharacter) return
      
      // 游客模式下不创建会话，只清空消息
      if (this.isGuestMode) {
        this.messages = []
        this.currentSessionId = null
        console.log('游客模式：清空对话历史')
        return
      }
      
      try {
        const response = await apiService.createSession(this.currentCharacter.id)
        this.currentSessionId = response.session_id
        this.messages = []
      } catch (error) {
        console.error('创建新会话失败:', error)
      }
    },

    // 加载指定会话
    async loadSpecificSession(sessionId) {
      // 游客模式下不加载会话
      if (this.isGuestMode) {
        console.log('游客模式：跳过会话加载')
        return
      }
      
      try {
        const response = await apiService.getSessionMessages(sessionId)
        if (response.success) {
          // 转换消息格式
          this.messages = response.messages.map((msg, index) => ({
            id: index + 1,
            content: msg.content,
            isUser: msg.role === 'user',
            timestamp: new Date(msg.timestamp).toLocaleTimeString(),
            characterId: this.currentCharacter.id
          }))
          
          // 更新当前会话ID
          this.currentSessionId = sessionId

          // 保存加载的状态
          this.saveCurrentCharacterState()
          
          // 滚动到底部
          this.$nextTick(() => {
            this.scrollToBottom()
          })
        }
      } catch (error) {
        console.error('加载指定会话失败:', error)
        // 如果加载失败，创建新会话
        await this.createNewSession()
      }
    },

    // 加载角色的最新会话
    async loadLatestSession(characterId) {
      // 游客模式下不加载会话
      if (this.isGuestMode) {
        console.log('游客模式：跳过最新会话加载')
        return
      }
      
      try {
        // 获取该角色的所有会话
        const response = await apiService.getUserSessions(characterId)
        if (response.success && response.sessions.length > 0) {
          // 按最后活动时间排序，获取最新的会话
          const latestSession = response.sessions.sort((a, b) => 
            new Date(b.last_activity || b.created_at) - new Date(a.last_activity || a.created_at)
          )[0]
          
          console.log('找到最新会话:', latestSession.session_id)
          
          // 加载最新会话的消息
          await this.loadSpecificSession(latestSession.session_id)
        } else {
          console.log('没有找到历史会话，保持空状态')
        }
      } catch (error) {
        console.error('加载最新会话失败:', error)
        // 失败时不做任何操作，保持空状态
      }
    },

    formatDate(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const diffTime = now - date
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        return '今天 ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })
      } else if (diffDays === 1) {
        return '昨天 ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })
      } else if (diffDays < 7) {
        return diffDays + '天前'
      } else {
        return date.toLocaleDateString('zh-CN')
      }
    },

    // 处理会话删除事件
    handleSessionDeleted(event) {
      const { characterId, sessionId } = event.detail
      
      // 清理内存中的角色状态缓存
      if (this.characterStates[characterId]) {
        const state = this.characterStates[characterId]
        if (state.sessionId === sessionId) {
          // 如果删除的是当前缓存的会话，清空该角色的状态
          delete this.characterStates[characterId]
          console.log('清理内存中的角色状态缓存:', characterId)
          
          // 如果当前正在查看被删除的会话，清空消息
          if (this.currentCharacter && this.currentCharacter.id === characterId && this.currentSessionId === sessionId) {
            this.messages = []
            this.currentSessionId = null
            console.log('清空当前显示的消息')
          }
        }
      }
    },

    // 检查并发送主动问候
    async checkAndSendActiveGreeting() {
      if (!this.intimacyData || !this.currentCharacter) return
      
      const intimacyValue = this.intimacyData.value || 0
      
      // 相见恨晚（10级）或伯乐（100级）需要主动问候
      if (intimacyValue >= 10) {
        try {
          console.log('发送主动问候，亲密度等级:', intimacyValue)
          
          // 创建一个特殊的"主动问候"请求
          const greetingQuery = "【系统提示：这是角色的主动问候，请根据你们的亲密度等级主动向用户问好】"
          
          // 如果没有会话ID且用户已登录且不是游客模式，创建新会话
          if (!this.currentSessionId && this.isAuthenticated && !this.isGuestMode) {
            try {
              const sessionResponse = await apiService.createSession(this.currentCharacter.id)
              this.currentSessionId = sessionResponse.session_id
              console.log('为主动问候创建新会话:', this.currentSessionId)
            } catch (sessionError) {
              console.error('创建会话失败:', sessionError)
            }
          }

          let response
          if (this.currentSessionId && !this.isGuestMode) {
            // 使用会话上下文
            response = await apiService.characterChatById(
              this.currentCharacter.id,
              greetingQuery,
              'deepseek-v3',
              false,
              this.currentSessionId
            )
          } else {
            // 不使用会话上下文
            response = await apiService.characterChatById(
              this.currentCharacter.id,
              greetingQuery,
              'deepseek-v3',
              false
            )
          }

          if (response && response.content) {
            const greetingMessage = {
              id: Date.now(),
              content: response.content,
              isUser: false,
              timestamp: new Date().toLocaleTimeString(),
              characterId: this.currentCharacter.id,
              isActiveGreeting: true // 标记为主动问候
            }

            this.messages.push(greetingMessage)
            
            // 处理亲密度更新（如果响应中包含亲密度信息）
            if (response.intimacy && this.isAuthenticated && !this.isGuestMode) {
              this.handleIntimacyUpdate(response.intimacy)
            }

            // 保存状态
            this.saveCurrentCharacterState()

            // 滚动到底部
            this.$nextTick(() => {
              this.scrollToBottom()
            })
            
            console.log('主动问候发送成功')
          }
        } catch (error) {
          console.error('发送主动问候失败:', error)
        }
      }
    },

    // 加载亲密度数据
    async loadIntimacyData(characterId) {
      // 首先检查缓存
      if (this.intimacyCache[characterId]) {
        this.intimacyData = { ...this.intimacyCache[characterId] }
        console.log('从缓存加载亲密度数据:', this.intimacyData)
        return
      }
      
      try {
        const response = await apiService.getIntimacy(characterId)
        if (response.success) {
          const intimacyData = {
            intimacy: response.intimacy,
            level_progress: response.level_progress
          }
          
          // 更新当前数据和缓存
          this.intimacyData = intimacyData
          this.intimacyCache[characterId] = { ...intimacyData }
          
          console.log('亲密度数据加载成功:', this.intimacyData)
        } else {
          console.error('亲密度API返回失败:', response)
          // 只有在没有缓存和现有数据时才初始化为默认值
          if (!this.intimacyCache[characterId] && !this.intimacyData) {
            const defaultData = {
              intimacy: 0,
              level_progress: {
                current_level: '陌生人',
                next_level: '初次相识',
                current_threshold: 0,
                next_threshold: 1,
                progress: 0
              }
            }
            this.intimacyData = defaultData
            this.intimacyCache[characterId] = { ...defaultData }
          } else if (this.intimacyCache[characterId]) {
            // 使用缓存数据
            this.intimacyData = { ...this.intimacyCache[characterId] }
          }
        }
      } catch (error) {
        console.error('加载亲密度数据失败:', error)
        
        // 优先使用缓存数据
        if (this.intimacyCache[characterId]) {
          this.intimacyData = { ...this.intimacyCache[characterId] }
          console.log('API失败，使用缓存亲密度数据:', this.intimacyData)
        } else if (!this.intimacyData) {
          // 只有在没有任何数据时才初始化为默认值
          const defaultData = {
            intimacy: 0,
            level_progress: {
              current_level: '陌生人',
              next_level: '初次相识',
              current_threshold: 0,
              next_threshold: 1,
              progress: 0
            }
          }
          this.intimacyData = defaultData
          this.intimacyCache[characterId] = { ...defaultData }
          console.log('使用默认亲密度数据:', this.intimacyData)
        }
      }
    },

    // 处理亲密度更新
    handleIntimacyUpdate(intimacyInfo) {
      if (!this.intimacyData) return
      
      const oldIntimacy = this.intimacyData.intimacy
      const newIntimacy = parseInt(intimacyInfo.value) || 0
      
      // 更新亲密度数据 - 不再重新加载，直接更新本地数据
      const updatedIntimacyData = {
        intimacy: newIntimacy,
        level_progress: {
          current_level: intimacyInfo.level_name,
          next_level: this.getNextLevelName(newIntimacy),
          current_threshold: this.getCurrentThreshold(newIntimacy),
          next_threshold: this.getNextThreshold(newIntimacy),
          progress: this.calculateLevelProgress(newIntimacy)
        }
      }
      
      this.intimacyData = updatedIntimacyData
      
      // 同时更新缓存
      if (this.currentCharacter && this.currentCharacter.id) {
        this.intimacyCache[this.currentCharacter.id] = { ...updatedIntimacyData }
      }
      
      console.log('亲密度更新:', {
        old: oldIntimacy,
        new: newIntimacy,
        level: intimacyInfo.level_name
      })
      
      // 触发+1动画
      if (this.$refs.intimacyBar && newIntimacy > oldIntimacy) {
        this.$refs.intimacyBar.showPlusOneAnimation()
        // 检查是否达到新阶段并触发爱心动画
        this.$refs.intimacyBar.checkForThresholdReached(newIntimacy, oldIntimacy)
      }
      
      // 如果等级提升，显示提示
      if (intimacyInfo.level_up) {
        console.log(`亲密度等级提升！从 ${intimacyInfo.old_level} 升级到 ${intimacyInfo.level_name}`)
        // 可以在这里添加等级提升的提示或动画
      }
    },

    // 获取下一个等级名称
    getNextLevelName(intimacy) {
      const levels = {
        1: '初次相识',
        5: '聊得火热', 
        10: '相见恨晚',
        20: '亲密无间',
        50: '知音难觅',
        100: '伯乐'
      }
      
      const thresholds = Object.keys(levels).map(Number).sort((a, b) => a - b)
      for (const threshold of thresholds) {
        if (intimacy < threshold) {
          return levels[threshold]
        }
      }
      return '伯乐' // 已达到最高等级
    },

    // 获取当前阈值
    getCurrentThreshold(intimacy) {
      const thresholds = [0, 1, 5, 10, 20, 50, 100]
      for (let i = thresholds.length - 1; i >= 0; i--) {
        if (intimacy >= thresholds[i]) {
          return thresholds[i]
        }
      }
      return 0
    },

    // 获取下一个阈值
    getNextThreshold(intimacy) {
      const thresholds = [1, 5, 10, 20, 50, 100]
      for (const threshold of thresholds) {
        if (intimacy < threshold) {
          return threshold
        }
      }
      return 100 // 已达到最高等级
    },

    // 计算等级进度
    calculateLevelProgress(intimacy) {
      const currentThreshold = this.getCurrentThreshold(intimacy)
      const nextThreshold = this.getNextThreshold(intimacy)
      
      if (intimacy >= 100) return 100
      
      const progress = ((intimacy - currentThreshold) / (nextThreshold - currentThreshold)) * 100
      return Math.min(Math.max(progress, 0), 100)
    },

    // 开始语音录音
    async startVoiceRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        this.mediaRecorder = new MediaRecorder(stream)
        this.audioChunks = []
        
        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data)
          }
        }
        
        this.mediaRecorder.onstop = () => {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' })
          this.processVoiceInput(audioBlob)
          
          // 停止所有音频轨道
          stream.getTracks().forEach(track => track.stop())
        }
        
        this.mediaRecorder.start()
        this.isVoiceRecording = true
        console.log('开始录音')
      } catch (error) {
        console.error('无法访问麦克风:', error)
        alert('无法访问麦克风，请检查权限设置')
      }
    },

    // 停止语音录音
    stopVoiceRecording() {
      if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.stop()
        this.isVoiceRecording = false
        console.log('停止录音')
      }
    },

    // 处理语音输入（目前只是模拟功能）
    async processVoiceInput(audioBlob) {
      try {
        // 这里应该调用语音识别API，目前只是模拟
        console.log('处理语音输入，音频大小:', audioBlob.size)
        
        // 模拟语音识别结果
        const simulatedText = "这是模拟的语音识别结果"
        this.userInput = simulatedText
        
        // 可以选择自动发送消息
        // await this.sendMessage()
        
      } catch (error) {
        console.error('处理语音输入失败:', error)
        alert('语音处理失败，请重试')
      }
    }
  }
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-height: 100vh; /* 强制限制最大高度 */
  background-color: #f5f5f5;
  overflow: hidden; /* 防止整个页面滚动 */
  position: fixed; /* 固定定位，确保不滚动 */
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.chat-header {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  padding: 1rem 2rem;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  flex-shrink: 0; /* 防止头部被压缩 */
  position: relative;
  z-index: 10;
  gap: 1rem;
  height: 100px; /* 恢复原来的高度 */
  min-height: 100px;
  max-height: 100px;
}


.character-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-button {
  width: 40px;
  height: 40px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.back-button svg {
  width: 20px;
  height: 20px;
  color: white;
  transition: transform 0.3s ease;
}

.back-button:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateX(-2px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.back-button:hover svg {
  transform: translateX(-2px);
}

.back-button:active {
  transform: translateX(-1px) scale(0.95);
}

.character-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #007bff;
  flex-shrink: 0; /* 防止头像被压缩 */
}

.character-avatar.small {
  width: 30px;
  height: 30px;
  border-width: 2px;
}

.character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.character-details {
  flex: 1;
  min-width: 0; /* 允许文本截断 */
  overflow: hidden;
}

.character-details h2 {
  margin: 0 0 0.25rem 0;
  color: #333;
  font-size: 1.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.character-details p {
  margin: 0.25rem 0 0 0;
  color: #666;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.intimacy-section {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 0.2rem;
  flex: 1;
  max-width: 550px;
  min-width: 450px;
}

.chat-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0; /* 防止按钮区域被压缩 */
  align-items: center;
}

.action-button {
  padding: 0.6rem 1.2rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  white-space: nowrap; /* 防止按钮文字换行 */
  flex-shrink: 0; /* 防止按钮被压缩 */
}

.action-button:hover {
  background-color: #f0f0f0;
}

.action-button.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden; /* 防止水平滚动 */
  padding: 1rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 0; /* 确保flex子项可以收缩 */
  max-height: calc(100vh - 180px); /* 减去头部(100px)和输入区域(80px)的高度 */
}

.welcome-message {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 1rem;
  /* 介绍信息卡片直接居中 */
  align-self: center;
  max-width: 600px; /* 限制最大宽度，保持美观 */
  width: 100%;
}

.welcome-message p {
  margin: 0.5rem 0;
  color: #666;
  line-height: 1.6;
}

.welcome-message p:first-child {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  align-self: flex-start;
  max-width: 70%;
}

.typing-dots {
  display: flex;
  gap: 0.25rem;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background-color: #007bff;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input-area {
  padding: 1rem 2rem;
  background: white;
  border-top: 1px solid #e0e0e0;
  flex-shrink: 0; /* 防止输入区域被压缩 */
  position: relative;
  z-index: 10;
  height: 80px; /* 固定输入区域高度 */
  min-height: 80px;
  max-height: 80px;
}

.input-container {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.text-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 24px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
}

.text-input:focus {
  border-color: #007bff;
}

.text-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.send-button {
  padding: 0.75rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background-color: #0056b3;
}

.send-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 语音输入按钮样式 */
.voice-button {
  width: 44px;
  height: 44px;
  border: none;
  background-color: #28a745;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.voice-button:hover:not(:disabled) {
  background-color: #218838;
  transform: scale(1.05);
}

.voice-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.voice-button svg {
  color: white;
}

/* 语音输入容器样式 */
.voice-input-container {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 0.5rem;
}

.voice-wave-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24px;
  padding: 0.75rem 1rem;
  gap: 1rem;
}

.voice-wave {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 24px;
}

.wave-bar {
  width: 3px;
  background-color: white;
  border-radius: 2px;
  animation: wave 1.5s ease-in-out infinite;
  opacity: 0.7;
}

.wave-bar:nth-child(odd) {
  animation-delay: 0.1s;
}

.wave-bar:nth-child(even) {
  animation-delay: 0.3s;
}

@keyframes wave {
  0%, 100% {
    height: 8px;
  }
  50% {
    height: 24px;
  }
}

.voice-status {
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
}

.voice-stop-button {
  width: 44px;
  height: 44px;
  border: none;
  background-color: #dc3545;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.voice-stop-button:hover {
  background-color: #c82333;
  transform: scale(1.05);
}

.voice-stop-button svg {
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-header {
    display: flex;
    flex-direction: column;
    padding: 1rem;
    gap: 0.5rem;
    height: auto;
    min-height: auto;
    max-height: none;
  }
  
  .character-info {
    justify-content: center;
  }
  
  .chat-actions {
    justify-content: center;
  }
  
  .intimacy-section {
    padding: 0 0.2rem;
    max-width: 380px;
    min-width: 350px;
    margin: 0 auto;
  }
  
  .back-button {
    width: 36px;
    height: 36px;
  }
  
  .back-button svg {
    width: 18px;
    height: 18px;
  }
  
  .character-details h2 {
    font-size: 1.25rem;
  }
  
  .chat-messages {
    padding: 1rem;
    max-height: calc(100vh - 200px); /* 移动端的头部高度 + 输入80px */
  }
  
  .chat-input-area {
    padding: 1rem;
  }
  
  .input-container {
    flex-direction: row;
    gap: 0.5rem;
  }
  
  .text-input {
    flex: 1;
  }
  
  .voice-button {
    width: 40px;
    height: 40px;
  }
  
  .voice-stop-button {
    width: 40px;
    height: 40px;
  }
  
  .voice-wave-container {
    padding: 0.5rem 0.75rem;
  }
  
  .voice-status {
    font-size: 0.8rem;
  }
  
  .welcome-message {
    max-width: 90%; /* 小屏幕上限制宽度 */
  }
}

</style>
