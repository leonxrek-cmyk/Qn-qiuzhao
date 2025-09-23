<template>
  <div class="message-bubble" :class="{ 'user-message': isUser, 'character-message': !isUser }">
    <div v-if="!isUser" class="message-avatar">
      <img :src="character?.avatar || '/default-avatar.svg'" :alt="character?.name" />
    </div>
    <div class="message-content">
      <div v-if="!isUser" class="message-sender">{{ character?.name || '角色' }}</div>
      <div class="message-text">{{ message }}</div>
      <div class="message-time">{{ formatTime(timestamp) }}</div>
    </div>
    <div v-if="isUser" class="message-avatar user-avatar">
      <img src="/user-avatar.svg" alt="您" />
    </div>
  </div>
</template>

<script>
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
    }
  },
  methods: {
    formatTime(date) {
      const d = new Date(date)
      const hours = d.getHours().toString().padStart(2, '0')
      const minutes = d.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
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
</style>