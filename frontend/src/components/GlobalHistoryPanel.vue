<template>
  <div class="history-overlay" v-if="isVisible" @click="closePanel"></div>
  
  <!-- 左侧滑出箭头 - 游客模式下隐藏 -->
  <div 
    v-if="isAuthenticated && !isGuestMode"
    class="history-trigger" 
    :class="{ active: isVisible }"
    @click="togglePanel"
    @mouseenter="onHoverEnter"
    @mouseleave="onHoverLeave"
  >
    <div class="arrow-icon" :class="{ rotated: isVisible }">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
        <path d="M6 12l4-4-4-4v8z"/>
      </svg>
    </div>
    <div class="trigger-tooltip" :class="{ visible: showTooltip && !isVisible }">
      对话历史
    </div>
  </div>

  <!-- 历史记录面板 - 游客模式下隐藏 -->
  <div v-if="isAuthenticated && !isGuestMode" class="history-panel" :class="{ visible: isVisible }">
    <div class="panel-header">
      <h3>对话历史</h3>
      <button class="close-btn" @click="closePanel">✕</button>
    </div>
    
    <div class="panel-content">
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载历史记录中...</p>
      </div>
      
      <div v-else-if="historyList.length === 0" class="empty-state">
        <div class="empty-icon">📚</div>
        <p>暂无对话历史</p>
        <small>开始与角色对话后，历史记录会显示在这里</small>
      </div>
      
      <div v-else class="history-list">
        <div 
          v-for="session in historyList" 
          :key="session.session_id"
          class="history-item"
          :class="{ deleting: session.isDeleting }"
          @click="navigateToSession(session)"
        >
          <div class="session-info">
            <div class="session-header">
              <img 
                :src="getCharacterAvatar(session.character_id)" 
                :alt="getCharacterName(session.character_id)" 
                class="character-avatar"
              />
              <div class="session-details">
                <div class="character-name">{{ getCharacterName(session.character_id) }}</div>
                <div class="session-time">{{ formatDate(session.created_at) }}</div>
              </div>
            </div>
            <div class="session-summary">
              {{ session.context_summary || `${session.message_count} 条消息` }}
            </div>
          </div>
          
          <div class="session-actions">
            <button 
              v-if="!session.isDeleting"
              class="delete-btn" 
              @click.stop="startDelete(session)"
              title="删除对话"
            >
              🗑️
            </button>
            
            <div v-else class="delete-confirm" @click.stop>
              <span class="confirm-text">确认删除？</span>
              <button @click="confirmDelete(session)" class="confirm-btn">是</button>
              <button @click="cancelDelete(session)" class="cancel-btn">否</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import apiService from '../apiService.js'

export default {
  name: 'GlobalHistoryPanel',
  setup() {
    const router = useRouter()
    const { isAuthenticated, isGuestMode } = useAuth()
    
    const isVisible = ref(false)
    const isLoading = ref(false)
    const showTooltip = ref(false)
    const historyList = ref([])
    const characterConfigs = ref([])

    // 加载角色配置
    const loadCharacterConfigs = async () => {
      try {
        const configs = await apiService.getCharacterConfigs()
        characterConfigs.value = configs
      } catch (error) {
        console.error('加载角色配置失败:', error)
      }
    }

    // 加载全局历史记录
    const loadGlobalHistory = async () => {
      if (!isAuthenticated.value) return
      
      isLoading.value = true
      try {
        const response = await apiService.getUserSessions() // 不传character_id获取所有历史
        if (response.success) {
          historyList.value = response.sessions.map(session => ({
            ...session,
            isDeleting: false
          })).sort((a, b) => new Date(b.last_activity || b.created_at) - new Date(a.last_activity || a.created_at))
        }
      } catch (error) {
        console.error('加载历史记录失败:', error)
      } finally {
        isLoading.value = false
      }
    }

    // 切换面板显示
    const togglePanel = async () => {
      isVisible.value = !isVisible.value
      if (isVisible.value && isAuthenticated.value) {
        await loadGlobalHistory()
      }
    }

    // 关闭面板
    const closePanel = () => {
      isVisible.value = false
    }

    // 鼠标悬停效果
    const onHoverEnter = () => {
      showTooltip.value = true
    }

    const onHoverLeave = () => {
      showTooltip.value = false
    }

    // 获取角色名称
    const getCharacterName = (characterId) => {
      const character = characterConfigs.value.find(c => c.id === characterId)
      return character ? character.name : '未知角色'
    }

    // 获取角色头像
    const getCharacterAvatar = (characterId) => {
      const character = characterConfigs.value.find(c => c.id === characterId)
      return character ? character.avatar : '/default-avatar.svg'
    }

    // 跳转到对话
    const navigateToSession = (session) => {
      const targetRoute = `/chat/${session.character_id}?session=${session.session_id}`
      
      // 直接使用router.push，聊天页面现在有路由监听器会处理变化
      router.push(targetRoute)
      closePanel()
    }

    // 开始删除
    const startDelete = (session) => {
      session.isDeleting = true
    }

    // 取消删除
    const cancelDelete = (session) => {
      session.isDeleting = false
    }

    // 确认删除
    const confirmDelete = async (session) => {
      try {
        // 这里需要实现删除会话的API
        // await apiService.deleteSession(session.session_id)
        
        // 从列表中移除
        historyList.value = historyList.value.filter(s => s.session_id !== session.session_id)
      } catch (error) {
        console.error('删除会话失败:', error)
        session.isDeleting = false
      }
    }

    // 格式化日期
    const formatDate = (dateString) => {
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
        return '昨天'
      } else if (diffDays < 7) {
        return diffDays + '天前'
      } else {
        return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
      }
    }

    // 键盘事件处理
    const handleKeydown = (event) => {
      if (event.key === 'Escape' && isVisible.value) {
        closePanel()
      }
    }

    onMounted(() => {
      loadCharacterConfigs()
      document.addEventListener('keydown', handleKeydown)
    })

    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown)
    })

    return {
      isVisible,
      isLoading,
      showTooltip,
      historyList,
      isAuthenticated,
      isGuestMode,
      togglePanel,
      closePanel,
      onHoverEnter,
      onHoverLeave,
      getCharacterName,
      getCharacterAvatar,
      navigateToSession,
      startDelete,
      cancelDelete,
      confirmDelete,
      formatDate
    }
  }
}
</script>

<style scoped>
/* 遮罩层 */
.history-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 998;
  backdrop-filter: blur(2px);
}

/* 触发按钮 */
.history-trigger {
  position: fixed;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0 8px 8px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 999;
  transition: all 0.3s ease;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2);
}

.history-trigger:hover {
  width: 45px;
  box-shadow: 3px 0 15px rgba(0, 0, 0, 0.3);
}

.history-trigger.active {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.arrow-icon {
  color: white;
  transition: transform 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.arrow-icon.rotated {
  transform: rotate(180deg);
}

.trigger-tooltip {
  position: absolute;
  left: 50px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  white-space: nowrap;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
  pointer-events: none;
}

.trigger-tooltip.visible {
  opacity: 1;
  transform: translateX(0);
}

.trigger-tooltip::before {
  content: '';
  position: absolute;
  left: -5px;
  top: 50%;
  transform: translateY(-50%);
  border: 5px solid transparent;
  border-right-color: rgba(0, 0, 0, 0.8);
}

/* 历史记录面板 */
.history-panel {
  position: fixed;
  left: -350px;
  top: 0;
  width: 350px;
  height: 100vh;
  background: white;
  box-shadow: 2px 0 20px rgba(0, 0, 0, 0.15);
  z-index: 999;
  transition: left 0.3s ease;
  display: flex;
  flex-direction: column;
}

.history-panel.visible {
  left: 0;
}

.panel-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
}

.panel-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #666;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e9ecef;
  color: #333;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  color: #666;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f0f0f0;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
  color: #666;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state p {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 500;
}

.empty-state small {
  color: #999;
  line-height: 1.4;
}

/* 历史记录列表 */
.history-list {
  padding: 1rem 0;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.history-item:hover {
  background: #f8f9fa;
}

.history-item.deleting {
  background: linear-gradient(90deg, #fff 0%, #ffebee 100%);
  border-left: 3px solid #f44336;
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.character-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e0e0e0;
  flex-shrink: 0;
}

.session-details {
  flex: 1;
  min-width: 0;
}

.character-name {
  font-weight: 600;
  color: #333;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.1rem;
}

.session-summary {
  font-size: 0.85rem;
  color: #888;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-actions {
  display: flex;
  align-items: center;
  margin-left: 0.5rem;
}

.delete-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.history-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: #ffebee;
  transform: scale(1.1);
}

.delete-confirm {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  animation: slideIn 0.3s ease;
}

.confirm-text {
  font-size: 0.75rem;
  color: #d32f2f;
  font-weight: 500;
  white-space: nowrap;
}

.confirm-btn,
.cancel-btn {
  padding: 0.2rem 0.5rem;
  border: none;
  border-radius: 3px;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn {
  background: #f44336;
  color: white;
}

.confirm-btn:hover {
  background: #d32f2f;
}

.cancel-btn {
  background: #e0e0e0;
  color: #333;
}

.cancel-btn:hover {
  background: #bdbdbd;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-panel {
    width: 100vw;
    left: -100vw;
  }
  
  .history-trigger {
    width: 35px;
    height: 50px;
  }
  
  .history-trigger:hover {
    width: 38px;
  }
  
  .trigger-tooltip {
    display: none;
  }
  
  .history-item {
    padding: 1rem;
  }
  
  .character-avatar {
    width: 32px;
    height: 32px;
  }
}
</style>
