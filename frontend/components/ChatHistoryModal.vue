<template>
  <div class="modal-content" @click.stop>
    <div class="modal-header">
      <h2>对话历史</h2>
      <button class="close-button" @click="$emit('close')">✕</button>
    </div>
    
    <div class="modal-body">
      <!-- 统计信息 -->
      <div class="history-stats">
        <div class="stat-item">
          <div class="stat-number">{{ totalSessions }}</div>
          <div class="stat-label">总对话数</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ totalMessages }}</div>
          <div class="stat-label">总消息数</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ characterConfigs.length }}</div>
          <div class="stat-label">角色数量</div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="history-actions">
        <button @click="exportHistory" :disabled="isExporting" class="btn-export">
          {{ isExporting ? '导出中...' : '📄 导出Markdown' }}
        </button>
        <button @click="clearAllHistory" :disabled="isClearing" class="btn-danger">
          {{ isClearing ? '清除中...' : '🗑️ 清空所有历史' }}
        </button>
      </div>

      <!-- 历史记录列表 -->
      <div class="history-section">
        <div class="section-header">
          <h3>所有对话记录</h3>
          <button @click="showAllHistory = !showAllHistory" class="toggle-button">
            {{ showAllHistory ? '收起' : '展开' }} ({{ allHistorySessions.length }})
          </button>
        </div>
        
        <div v-if="showAllHistory" class="history-list">
          <div v-if="allHistorySessions.length === 0" class="empty-state">
            <p>暂无对话历史</p>
          </div>
          <div 
            v-for="session in allHistorySessions" 
            :key="`${session.character_id}-${session.session_id}`"
            class="history-item"
          >
            <div class="history-info">
              <div class="character-avatar">
                <img :src="getCharacterAvatar(session.character_id)" :alt="getCharacterName(session.character_id)" />
              </div>
              <div class="history-details">
                <div class="history-title">
                  与{{ getCharacterName(session.character_id) }}对话
                </div>
                <div class="history-meta">
                  {{ session.message_count || session.messages?.length || 0 }}条消息 • {{ formatDate(session.lastMessageTime) }}
                </div>
              </div>
            </div>
            <div class="history-actions-item">
              <button @click="navigateToChat(session.character_id, session.session_id)" class="btn-continue">
                继续对话
              </button>
              <button 
                @click="startDelete(session)" 
                :class="['btn-delete', { 'confirming': session.showDeleteConfirm }]"
              >
                {{ session.showDeleteConfirm ? '确认删除' : '删除' }}
              </button>
              <button 
                v-if="session.showDeleteConfirm" 
                @click="cancelDelete(session)" 
                class="btn-cancel-delete"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息提示 -->
      <div v-if="message" class="message" :class="messageType">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../apiService.js'

export default {
  name: 'ChatHistoryModal',
  emits: ['close'],
  setup(props, { emit }) {
    const router = useRouter()
    
    const isExporting = ref(false)
    const isClearing = ref(false)
    const message = ref('')
    const messageType = ref('success')
    const totalSessions = ref(0)
    const totalMessages = ref(0)
    const allHistorySessions = ref([])
    const showAllHistory = ref(false)
    const characterConfigs = ref([])

    // 显示消息
    const showMessage = (msg, type = 'success') => {
      message.value = msg
      messageType.value = type
      setTimeout(() => {
        message.value = ''
      }, 3000)
    }

    // 加载角色配置
    const loadCharacterConfigs = async () => {
      try {
        console.log('开始加载角色配置...')
        const configs = await apiService.getCharacterConfigs()
        console.log('getCharacterConfigs API响应:', configs)
        characterConfigs.value = configs
      } catch (error) {
        console.error('加载角色配置失败:', error)
        showMessage('加载角色配置失败', 'error')
      }
    }

    // 加载聊天统计
    const loadChatStats = async () => {
      try {
        console.log('开始加载用户会话历史...')
        const response = await apiService.getUserSessions()
        console.log('getUserSessions API响应:', response) // 调试日志
        
        // 处理API响应数据
        let sessions = []
        if (response && response.success && Array.isArray(response.sessions)) {
          sessions = response.sessions
        } else if (Array.isArray(response)) {
          sessions = response
        } else {
          console.warn('API返回数据格式异常:', response)
          sessions = []
        }
        
        allHistorySessions.value = sessions.map(session => ({
          ...session,
          showDeleteConfirm: false,
          // 确保有messages字段，如果没有则使用message_count
          messages: session.messages || new Array(session.message_count || 0).fill({}),
          // 添加lastMessageTime字段
          lastMessageTime: session.last_activity || session.created_at
        }))
        
        totalSessions.value = sessions.length
        totalMessages.value = sessions.reduce((total, session) => {
          return total + (session.message_count || session.messages?.length || 0)
        }, 0)
      } catch (error) {
        console.error('加载聊天统计失败:', error)
        showMessage('加载历史记录失败', 'error')
      }
    }

    // 导出历史
    const exportHistory = async () => {
      try {
        isExporting.value = true
        showMessage('正在获取对话详情...', 'info')
        
        const response = await apiService.getUserSessions()
        
        // 处理API响应数据
        let sessions = []
        if (response && response.success && Array.isArray(response.sessions)) {
          sessions = response.sessions
        } else if (Array.isArray(response)) {
          sessions = response
        } else {
          sessions = []
        }
        
        // 检查是否有可导出的对话记录
        if (sessions.length === 0) {
          showMessage('暂无对话记录可导出', 'warning')
          return
        }
        
        // 获取每个会话的详细消息内容
        const sessionsWithMessages = []
        let totalMessages = 0
        
        for (const session of sessions) {
          try {
            const messagesResponse = await apiService.getSessionMessages(session.session_id)
            let messages = []
            
            if (messagesResponse && messagesResponse.success && Array.isArray(messagesResponse.messages)) {
              messages = messagesResponse.messages
            } else if (Array.isArray(messagesResponse)) {
              messages = messagesResponse
            }
            
            sessionsWithMessages.push({
              ...session,
              messages: messages
            })
            
            totalMessages += messages.length
          } catch (error) {
            console.warn(`获取会话 ${session.session_id} 的消息失败:`, error)
            // 如果获取消息失败，仍然包含会话信息，但消息为空
            sessionsWithMessages.push({
              ...session,
              messages: []
            })
          }
        }
        
        // 生成Markdown内容
        const markdownContent = generateMarkdownReport(sessionsWithMessages, totalMessages)
        
        // 创建并下载Markdown文件
        const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `对话历史记录-${new Date().toISOString().split('T')[0]}.md`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        
        showMessage('历史记录导出成功', 'success')
      } catch (error) {
        console.error('导出历史失败:', error)
        showMessage('导出失败', 'error')
      } finally {
        isExporting.value = false
      }
    }

    // 生成Markdown格式的报告
    const generateMarkdownReport = (sessions, totalMessages) => {
      const now = new Date()
      const exportTime = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
      
      let markdown = `# AI角色对话历史记录\n\n`
      
      // 基本统计信息
      markdown += `## 📊 统计信息\n\n`
      markdown += `- **导出时间**: ${exportTime}\n`
      markdown += `- **总对话数**: ${sessions.length} 个\n`
      markdown += `- **总消息数**: ${totalMessages} 条\n`
      markdown += `- **涉及角色**: ${new Set(sessions.map(s => s.character_id)).size} 个\n\n`
      
      // 角色统计
      const characterStats = {}
      sessions.forEach(session => {
        const characterName = getCharacterName(session.character_id)
        if (!characterStats[characterName]) {
          characterStats[characterName] = {
            sessions: 0,
            messages: 0
          }
        }
        characterStats[characterName].sessions++
        characterStats[characterName].messages += session.messages.length
      })
      
      markdown += `## 🎭 角色对话统计\n\n`
      markdown += `| 角色名称 | 对话次数 | 消息数量 |\n`
      markdown += `|---------|---------|----------|\n`
      Object.entries(characterStats).forEach(([name, stats]) => {
        markdown += `| ${name} | ${stats.sessions} | ${stats.messages} |\n`
      })
      markdown += `\n`
      
      // 详细对话记录
      markdown += `## 💬 详细对话记录\n\n`
      
      // 按时间排序会话
      const sortedSessions = sessions.sort((a, b) => 
        new Date(b.last_activity || b.created_at) - new Date(a.last_activity || a.created_at)
      )
      
      sortedSessions.forEach((session, index) => {
        const characterName = getCharacterName(session.character_id)
        const sessionDate = new Date(session.created_at).toLocaleString('zh-CN')
        const lastActivity = new Date(session.last_activity || session.created_at).toLocaleString('zh-CN')
        
        markdown += `### ${index + 1}. 与${characterName}的对话\n\n`
        markdown += `- **开始时间**: ${sessionDate}\n`
        markdown += `- **最后活动**: ${lastActivity}\n`
        markdown += `- **消息数量**: ${session.messages.length} 条\n`
        markdown += `- **会话ID**: \`${session.session_id}\`\n\n`
        
        if (session.messages.length > 0) {
          markdown += `#### 对话内容\n\n`
          
          session.messages.forEach((message, msgIndex) => {
            const timestamp = message.timestamp ? 
              new Date(message.timestamp).toLocaleString('zh-CN', {
                month: '2-digit',
                day: '2-digit', 
                hour: '2-digit',
                minute: '2-digit'
              }) : ''
            
            const sender = message.isUser ? 
              (userDisplayName.value || '用户') : 
              characterName
            
            const timeStr = timestamp ? ` *${timestamp}*` : ''
            
            markdown += `**${sender}**${timeStr}:\n`
            markdown += `${message.content}\n\n`
          })
        } else {
          markdown += `*该会话暂无消息记录*\n\n`
        }
        
        markdown += `---\n\n`
      })
      
      // 页脚信息
      markdown += `## 📝 说明\n\n`
      markdown += `- 本文档由AI角色对话系统自动生成\n`
      markdown += `- 对话时间均为本地时间\n`
      markdown += `- 对话内容按会话分组，会话按最后活动时间倒序排列\n`
      markdown += `- 消息在会话内按时间顺序排列\n\n`
      markdown += `*导出完成于 ${exportTime}*\n`
      
      return markdown
    }

    // 清空所有历史
    const clearAllHistory = async () => {
      try {
        // 先检查是否有历史记录
        const response = await apiService.getUserSessions()
        let sessions = []
        if (response && response.success && Array.isArray(response.sessions)) {
          sessions = response.sessions
        } else if (Array.isArray(response)) {
          sessions = response
        } else {
          sessions = []
        }
        
        // 检查是否有可清空的对话记录
        if (sessions.length === 0) {
          showMessage('暂无对话记录可清空', 'warning')
          return
        }
        
        if (!confirm('确定要清空所有对话历史吗？此操作不可撤销。')) {
          return
        }
        
        isClearing.value = true
        await apiService.clearAllHistory()
        await loadChatStats()
        showMessage('所有历史记录已清空', 'success')
      } catch (error) {
        console.error('清空历史失败:', error)
        showMessage('清空失败', 'error')
      } finally {
        isClearing.value = false
      }
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

    // 导航到聊天页面
    const navigateToChat = (characterId, sessionId) => {
      emit('close')
      router.push(`/chat/${characterId}?session=${sessionId}`)
    }

    // 开始删除
    const startDelete = (session) => {
      if (session.showDeleteConfirm) {
        confirmDelete(session)
      } else {
        // 先关闭其他的确认状态
        allHistorySessions.value.forEach(s => s.showDeleteConfirm = false)
        session.showDeleteConfirm = true
      }
    }

    // 取消删除
    const cancelDelete = (session) => {
      session.showDeleteConfirm = false
    }

    // 确认删除
    const confirmDelete = async (session) => {
      try {
        await apiService.deleteSession(session.character_id, session.session_id)
        await loadChatStats()
        showMessage('对话记录已删除', 'success')
      } catch (error) {
        console.error('删除对话失败:', error)
        showMessage('删除失败', 'error')
      }
    }

    // 格式化日期
    const formatDate = (timestamp) => {
      if (!timestamp) return '未知时间'
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
      if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
      
      return date.toLocaleDateString()
    }

    onMounted(() => {
      loadCharacterConfigs()
      loadChatStats()
    })

    return {
      isExporting,
      isClearing,
      message,
      messageType,
      totalSessions,
      totalMessages,
      allHistorySessions,
      showAllHistory,
      characterConfigs,
      exportHistory,
      clearAllHistory,
      getCharacterName,
      getCharacterAvatar,
      navigateToChat,
      startDelete,
      cancelDelete,
      formatDate
    }
  }
}
</script>

<style scoped>
.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 700px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-button:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.history-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
}

.history-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.btn-export {
  padding: 0.75rem 1.5rem;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-export:hover {
  background: #218838;
  transform: translateY(-1px);
}

.btn-export:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.btn-danger {
  padding: 0.75rem 1.5rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-danger:hover {
  background: #c82333;
  transform: translateY(-1px);
}

.btn-danger:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.history-section {
  margin-bottom: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.25rem;
}

.toggle-button {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.toggle-button:hover {
  background: #5a6fd8;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  transition: all 0.2s;
}

.history-item:hover {
  background: #f8f9fa;
  border-color: #667eea;
}

.history-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.character-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.history-details {
  flex: 1;
}

.history-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 0.25rem;
}

.history-meta {
  font-size: 0.875rem;
  color: #666;
}

.history-actions-item {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-continue {
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-continue:hover {
  background: #5a6fd8;
}

.btn-delete {
  padding: 0.5rem 1rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-delete:hover {
  background: #5a6268;
}

.btn-delete.confirming {
  background: #dc3545;
}

.btn-delete.confirming:hover {
  background: #c82333;
}

.btn-cancel-delete {
  padding: 0.5rem 1rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-cancel-delete:hover {
  background: #5a6268;
}

.message {
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 1rem;
  font-size: 0.875rem;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.message.warning {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-stats {
    grid-template-columns: 1fr;
  }
  
  .history-actions {
    flex-direction: column;
  }
  
  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .history-actions-item {
    align-self: stretch;
    justify-content: flex-end;
  }
}
</style>
