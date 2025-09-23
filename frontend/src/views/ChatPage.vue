<template>
  <div class="chat-page">
    <!-- 顶部角色信息栏 -->
    <div class="chat-header">
      <div class="character-info">
        <div class="character-avatar">
          <img :src="currentCharacter?.avatar || '/default-avatar.png'" :alt="currentCharacter?.name" />
        </div>
        <div class="character-details">
          <h2>{{ currentCharacter?.name || '选择一个角色开始对话' }}</h2>
          <p>{{ currentCharacter?.description || '请从左侧选择一个角色或搜索角色' }}</p>
        </div>
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
        <button 
          class="voice-button" 
          @click="toggleVoiceRecording"
          :disabled="!currentCharacter || isRecording"
          :class="{ recording: isRecording }"
        >
          {{ isRecording ? '🛑' : '🎤' }}
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
      </div>
      <div v-if="isRecording" class="recording-indicator">
        <p>正在录音... 点击麦克风按钮停止</p>
      </div>
    </div>
  </div>
</template>

<script>
import MessageBubble from '../components/MessageBubble.vue'
import charactersData from '../../../common/characters.json'
import apiService from '../apiService.js'

export default {
  name: 'ChatPage',
  components: {
    MessageBubble
  },
  props: {
    characterId: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      messages: [],
      userInput: '',
      currentCharacter: null,
      isTyping: false,
      isRecording: false,
      mediaRecorder: null,
      audioChunks: []
    }
  },
  mounted() {
    // 如果有characterId参数，加载对应角色
    if (this.characterId) {
      this.loadCharacter(this.characterId)
    }
  },
  watch: {
    // 监听characterId变化
    characterId(newId) {
      if (newId) {
        this.loadCharacter(newId)
      }
    }
  },
  methods: {
    // 加载角色信息
    loadCharacter(characterId) {
      const character = charactersData.find(c => c.id === characterId)
      if (character) {
        this.currentCharacter = character
        // 清空历史消息
        this.messages = []
      }
    },

    // 获取欢迎消息
    getWelcomeMessage() {
      if (!this.currentCharacter) return ''
      
      const welcomeMessages = {
        'harry-potter': '我刚从霍格沃茨魔法学校毕业，对抗伏地魔的经历让我成长了许多。',
        'socrates': '我喜欢通过提问来引导人们思考哲学问题。什么问题困扰着你？',
        'albert-einstein': '宇宙的奥秘总是令我着迷，尤其是相对论和量子力学。',
        'confucius': '三人行必有我师焉。让我们一起探讨伦理和道德的问题。'
      }
      
      return welcomeMessages[this.currentCharacter.id] || '有什么我可以帮助你的吗？'
    },

    // 发送消息
    async sendMessage() {
      if (!this.currentCharacter || !this.userInput.trim()) return

      const userMessage = this.userInput.trim()
      
      // 添加用户消息到消息列表
      this.addMessage(userMessage, true)
      
      // 清空输入框
      this.userInput = ''
      
      // 显示正在输入
      this.isTyping = true
      
      try {
        // 调用AI API获取角色回复
        const response = await apiService.characterChat(
          this.currentCharacter.name,
          this.currentCharacter.description,
          userMessage,
          'x-ai/grok-4-fast',
          false // 非流式响应
        )
        
        // 添加角色回复到消息列表
        this.addMessage(response.content, false)
      } catch (error) {
        console.error('发送消息失败:', error)
        this.addMessage('抱歉，我暂时无法回复，请稍后再试。', false)
      } finally {
        // 隐藏正在输入
        this.isTyping = false
        // 滚动到底部
        this.scrollToBottom()
      }
    },

    // 添加消息到列表
    addMessage(content, isUser) {
      this.messages.push({
        id: Date.now() + Math.random(),
        content: content,
        isUser: isUser,
        timestamp: new Date()
      })
      // 滚动到底部
      this.scrollToBottom()
    },

    // 滚动到消息底部
    scrollToBottom() {
      setTimeout(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      }, 100)
    },

    // 清空对话
    clearChat() {
      if (confirm('确定要清空当前对话吗？')) {
        this.messages = []
      }
    },

    // 返回角色列表
    backToCharacters() {
      this.$router.push('/characters')
    },

    // 切换录音状态
    async toggleVoiceRecording() {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('您的浏览器不支持语音录制功能')
        return
      }

      if (this.isRecording) {
        // 停止录音
        this.stopRecording()
      } else {
        // 开始录音
        await this.startRecording()
      }
    },

    // 开始录音
    async startRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        this.mediaRecorder = new MediaRecorder(stream)
        this.audioChunks = []

        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data)
          }
        }

        this.mediaRecorder.onstop = async () => {
          // 停止所有音轨
          stream.getTracks().forEach(track => track.stop())
          
          // 处理录音数据
          await this.processRecording()
        }

        this.mediaRecorder.start()
        this.isRecording = true
      } catch (error) {
        console.error('开始录音失败:', error)
        alert('无法访问麦克风，请确保已授权')
      }
    },

    // 停止录音
    stopRecording() {
      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop()
        this.isRecording = false
      }
    },

    // 处理录音数据
    async processRecording() {
      try {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' })
        
        // 调用语音识别API
        // 注意：这里是简化实现，实际项目中应该调用后端API
        
        // 模拟识别结果（因为前端无法直接处理语音识别）
        setTimeout(() => {
          const simulatedText = '这是一段模拟的语音识别结果，实际项目中应该调用后端API进行语音识别'
          this.userInput = simulatedText
        }, 1000)
        
        // 实际项目中应该这样调用
        // const formData = new FormData()
        // formData.append('audio', audioBlob, 'recording.wav')
        // const response = await apiService.voiceRecognition(formData)
        // this.userInput = response.text
      } catch (error) {
        console.error('处理录音失败:', error)
        alert('语音识别失败，请重试')
      }
    }
  }
}
</script>

<style scoped>
/* 聊天页面样式 */
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1000px;
  margin: 0 auto;
  background-color: white;
}

/* 聊天头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.character-info {
  display: flex;
  align-items: center;
}

.character-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 16px;
}

.character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.character-details h2 {
  font-size: 20px;
  margin-bottom: 4px;
  color: #333;
}

.character-details p {
  font-size: 14px;
  color: #666;
  max-width: 500px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-actions {
  display: flex;
  gap: 12px;
}

.action-button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background-color: white;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button:hover {
  background-color: #f0f0f0;
}

/* 聊天消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: #fafafa;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.welcome-message p {
  margin-bottom: 12px;
  color: #666;
  line-height: 1.6;
}

.typing-indicator {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.character-avatar.small {
  width: 40px;
  height: 40px;
  margin-right: 12px;
}

.typing-dots {
  display: flex;
  gap: 6px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background-color: #4c84ff;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1.0);
  }
}

/* 输入区域 */
.chat-input-area {
  padding: 16px 24px;
  background-color: white;
  border-top: 1px solid #e0e0e0;
}

.input-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.voice-button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background-color: #f0f0f0;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.voice-button:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.voice-button.recording {
  background-color: #ff4d4f;
  color: white;
}

.voice-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.text-input {
  flex: 1;
  padding: 12px 20px;
  border: 1px solid #ddd;
  border-radius: 24px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s ease;
}

.text-input:focus {
  border-color: #4c84ff;
}

.text-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.send-button {
  padding: 12px 24px;
  background-color: #4c84ff;
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background-color: #3a6ed8;
  transform: translateY(-1px);
}

.send-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.recording-indicator {
  margin-top: 8px;
  text-align: center;
  color: #ff4d4f;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .character-details p {
    max-width: 100%;
    white-space: normal;
  }
  
  .chat-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .chat-messages {
    padding: 16px;
  }
  
  .chat-input-area {
    padding: 12px 16px;
  }
  
  .voice-button {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .text-input {
    font-size: 14px;
  }
  
  .send-button {
    padding: 8px 16px;
    font-size: 14px;
  }
}
</style>