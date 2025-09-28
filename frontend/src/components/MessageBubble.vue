<template>
  <div class="message-bubble" :class="{ 'user-message': isUser, 'ai-message': !isUser }">
    <div class="message-header">
      <div class="avatar">
        <img :src="avatarSrc" :alt="displayName" />
      </div>
      <div class="message-info">
        <span class="sender-name">{{ displayName }}</span>
        <span class="timestamp">{{ timestamp }}</span>
      </div>
    </div>
    <div class="message-content">
      <div class="message-text-container">
        <div class="message-text">{{ message }}</div>
        <!-- 只在AI消息中显示扬声器按钮，放在文本右侧 -->
        <button 
          v-if="!isUser && message.trim()"
          class="speaker-button inline-speaker" 
          @click="playTTS"
          :disabled="isPlaying || isLoading"
          :title="isPlaying ? '正在播放...' : isLoading ? '正在生成语音...' : '播放语音'"
        >
          <svg v-if="!isLoading && !isPlaying" width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
          </svg>
          <svg v-else-if="isLoading" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" class="loading-icon">
            <path d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuth } from '../composables/useAuth.js'
import apiService from '../apiService.js'

export default {
  name: 'MessageBubble',
  props: {
    message: {
      type: String,
      required: true
    },
    isUser: {
      type: Boolean,
      default: false
    },
    character: {
      type: Object,
      default: null
    },
    timestamp: {
      type: String,
      default: ''
    },
    characterId: {
      type: String,
      default: null
    }
  },
  setup() {
    const { currentUser, userDisplayName, userAvatar } = useAuth()
    
    return {
      currentUser,
      userDisplayName,
      userAvatar
    }
  },
  data() {
    return {
      isPlaying: false,
      isLoading: false,
      currentAudio: null
    }
  },
  computed: {
    displayName() {
      if (this.isUser) {
        // 使用登录用户的昵称，如果没有昵称则使用用户名，最后才使用"我"
        return this.userDisplayName || '我'
      }
      return this.character?.name || '助手'
    },
    avatarSrc() {
      if (this.isUser) {
        // 使用登录用户的头像，如果没有则使用默认头像
        return this.userAvatar || '/user-avatar.svg'
      }
      return this.character?.avatar || '/default-avatar.svg'
    }
  },
  methods: {
    async playTTS() {
      if (this.isPlaying || this.isLoading) return
      
      try {
        this.isLoading = true
        
        // 停止其他正在播放的音频
        this.stopAllAudio()
        
        console.log('开始TTS请求:', {
          text: this.message,
          characterId: this.characterId
        })
        
        // 调用TTS API
        const result = await apiService.textToSpeech(this.message, this.characterId)
        
        if (result.success && result.audio_data) {
          console.log('TTS成功:', {
            voice_type: result.voice_type,
            speed_ratio: result.speed_ratio,
            cleaned_text: result.cleaned_text
          })
          
          // 将base64音频数据转换为Blob
          const audioBlob = this.base64ToBlob(result.audio_data, 'audio/mp3')
          const audioUrl = URL.createObjectURL(audioBlob)
          
          // 创建音频对象并播放
          this.currentAudio = new Audio(audioUrl)
          
          this.currentAudio.onloadstart = () => {
            this.isLoading = false
            this.isPlaying = true
          }
          
          this.currentAudio.onended = () => {
            this.isPlaying = false
            URL.revokeObjectURL(audioUrl)
            this.currentAudio = null
          }
          
          this.currentAudio.onerror = (error) => {
            console.error('音频播放错误:', error)
            this.isPlaying = false
            this.isLoading = false
            URL.revokeObjectURL(audioUrl)
            this.currentAudio = null
            alert('音频播放失败')
          }
          
          await this.currentAudio.play()
          
        } else {
          console.error('TTS失败:', result.error)
          alert('语音合成失败: ' + (result.error || '未知错误'))
        }
        
      } catch (error) {
        console.error('TTS请求失败:', error)
        alert('语音合成请求失败，请重试')
      } finally {
        this.isLoading = false
      }
    },
    
    stopAllAudio() {
      // 停止当前组件的音频
      if (this.currentAudio) {
        this.currentAudio.pause()
        this.currentAudio = null
        this.isPlaying = false
      }
      
      // 通知其他组件停止播放
      this.$emit('stop-all-audio')
    },
    
    base64ToBlob(base64Data, contentType = '') {
      const byteCharacters = atob(base64Data)
      const byteNumbers = new Array(byteCharacters.length)
      
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      
      const byteArray = new Uint8Array(byteNumbers)
      return new Blob([byteArray], { type: contentType })
    }
  },
  
  beforeUnmount() {
    // 组件销毁前停止音频播放
    if (this.currentAudio) {
      this.currentAudio.pause()
      this.currentAudio = null
    }
  }
}
</script>

<style scoped>
.message-bubble {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
  max-width: 70%;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  align-self: flex-end;
}

.ai-message {
  align-self: flex-start;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  gap: 0.5rem;
}

.user-message .message-header {
  flex-direction: row-reverse;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.user-message .message-info {
  align-items: flex-end;
}

.sender-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #333;
}

.timestamp {
  font-size: 0.75rem;
  color: #666;
}

.message-content {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: relative;
}

.user-message .message-content {
  background: #007bff;
  color: white;
}

.user-message .message-content::after {
  content: '';
  position: absolute;
  top: 10px;
  right: -8px;
  width: 0;
  height: 0;
  border-left: 8px solid #007bff;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
}

.ai-message .message-content::after {
  content: '';
  position: absolute;
  top: 10px;
  left: -8px;
  width: 0;
  height: 0;
  border-right: 8px solid white;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
}

.message-text-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
  flex: 1;
  min-height: 1.6em; /* 确保单行文本有足够高度用于居中对齐 */
  display: flex;
  align-items: center;
}

.speaker-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  color: #666;
}

.speaker-button.inline-speaker {
  padding: 0.2rem;
  flex-shrink: 0;
  opacity: 0.7;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  align-self: center;
}

.speaker-button:hover:not(:disabled) {
  background-color: rgba(0,0,0,0.1);
  color: #333;
}

.speaker-button.inline-speaker:hover:not(:disabled) {
  opacity: 1;
  background-color: rgba(0,0,0,0.08);
  transform: scale(1.1);
}

.speaker-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.user-message .speaker-button {
  color: rgba(255,255,255,0.8);
}

.user-message .speaker-button:hover:not(:disabled) {
  background-color: rgba(255,255,255,0.2);
  color: white;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .message-bubble {
    max-width: 85%;
  }
  
  .message-content {
    padding: 0.75rem;
  }
  
  .avatar {
    width: 28px;
    height: 28px;
  }
  
  .message-text-container {
    gap: 0.3rem;
  }
  
  .speaker-button.inline-speaker {
    width: 24px;
    height: 24px;
    padding: 0.15rem;
  }
  
  .speaker-button.inline-speaker svg {
    width: 12px;
    height: 12px;
  }
}
</style>
