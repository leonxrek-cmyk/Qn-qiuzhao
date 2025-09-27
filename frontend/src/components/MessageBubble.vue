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
      <div class="message-text">{{ message }}</div>
    </div>
  </div>
</template>

<script>
import { useAuth } from '../composables/useAuth.js'

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
    // 移除 showVoicePlayer 属性
  },
  setup() {
    const { currentUser, userDisplayName, userAvatar } = useAuth()
    
    return {
      currentUser,
      userDisplayName,
      userAvatar
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
  }
  // 移除所有语音相关的方法和生命周期钩子
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

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
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
}
</style>
