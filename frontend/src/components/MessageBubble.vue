<template>
  <div class="message-bubble" :class="{ 'user-message': isUser, 'character-message': !isUser }">
    <div v-if="!isUser" class="message-avatar">
      <img :src="character?.avatar || '/default-avatar.svg'" :alt="character?.name" />
    </div>
    <div class="message-content">
      <div v-if="!isUser" class="message-sender">{{ character?.name || '角色' }}</div>
      <div class="message-text">{{ message }}</div>
      
      <!-- 语音播放控件（仅用于AI角色的消息） -->
      <div v-if="!isUser && showVoicePlayer" class="voice-player">
        <button 
          class="play-button" 
          @click="togglePlayback"
          :disabled="isLoadingVoice"
        >
          {{ isPlaying ? '⏸️' : '▶️' }}
        </button>
        <div class="audio-wave">
          <span v-for="i in 8" :key="i" :style="{ height: (i % 3 + 1) * 10 + 'px' }" class="wave-bar"></span>
        </div>
        <div class="loading-indicator" v-if="isLoadingVoice">
          <div class="spinner"></div>
        </div>
      </div>
      
      <div class="message-time">{{ formatTime(timestamp) }}</div>
    </div>
    <div v-if="isUser" class="message-avatar user-avatar">
      <img src="/user-avatar.svg" alt="您" />
    </div>
  </div>
</template>

<script>
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
      type: Date,
      default: () => new Date()
    },
    showVoicePlayer: {
      type: Boolean,
      default: false
    },
    characterId: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      audio: null,
      isPlaying: false,
      isLoadingVoice: false,
      audioURL: null
    }
  },
  watch: {
    showVoicePlayer(newVal) {
      if (newVal && !this.isUser) {
        // 当显示语音播放器且消息不是用户发送的，自动加载并播放语音
        this.loadVoice()
      }
    }
  },
  methods: {
    formatTime(date) {
      const d = new Date(date)
      const hours = d.getHours().toString().padStart(2, '0')
      const minutes = d.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
    },
    
    // 加载语音文件
    async loadVoice() {
      if (!this.message || this.isLoadingVoice || this.audioURL) {
        return
      }
      
      this.isLoadingVoice = true
      
      try {
        // 使用apiService调用后端文字转语音接口
        const blob = await apiService.textToSpeech(this.message, this.characterId, 'zh-CN', 1.0)
        
        this.audioURL = URL.createObjectURL(blob)
        
        // 创建音频对象
        this.audio = new Audio(this.audioURL)
        
        // 监听音频事件
        this.audio.onended = () => {
          this.isPlaying = false
        }
        
        // 自动播放
        this.isPlaying = true
        await this.audio.play()
        
      } catch (error) {
        console.error('加载语音失败:', error)
      } finally {
        this.isLoadingVoice = false
      }
    },
    
    // 切换播放状态
    async togglePlayback() {
      if (this.isLoadingVoice) {
        return
      }
      
      if (!this.audio) {
        await this.loadVoice()
        return
      }
      
      if (this.isPlaying) {
        this.audio.pause()
      } else {
        await this.audio.play()
      }
      
      this.isPlaying = !this.isPlaying
    }
  }
}
</script>

<style scoped>
.message-bubble {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  max-width: 80%;
}

.user-message {
  margin-left: auto;
  flex-direction: row-reverse;
}

.character-message {
  margin-right: auto;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 8px;
  flex-shrink: 0;
}

.user-avatar {
  order: 2;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  flex: 1;
  position: relative;
}

.user-message .message-content {
  text-align: right;
}

.message-sender {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.message-text {
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.5;
  word-wrap: break-word;
}

.character-message .message-text {
  background-color: #f0f0f0;
  color: #333;
  border-bottom-left-radius: 4px;
}

.user-message .message-text {
  background-color: #4c84ff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

/* 语音播放器样式 */
.voice-player {
  display: flex;
  align-items: center;
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #f5f5f5;
  border-radius: 16px;
  max-width: 300px;
}

.play-button {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background-color: #4c84ff;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.play-button:hover:not(:disabled) {
  background-color: #3a6ed8;
  transform: scale(1.1);
}

.play-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.audio-wave {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.wave-bar {
  width: 4px;
  background-color: #4c84ff;
  border-radius: 2px;
  animation: wave 1.2s infinite ease-in-out;
}

.wave-bar:nth-child(2n) {
  animation-delay: 0.1s;
}

.wave-bar:nth-child(3n) {
  animation-delay: 0.2s;
}

@keyframes wave {
  0%, 100% {
    transform: scaleY(0.3);
  }
  50% {
    transform: scaleY(1);
  }
}

.loading-indicator {
  margin-left: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #4c84ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .voice-player {
    max-width: 200px;
  }
}
</style>