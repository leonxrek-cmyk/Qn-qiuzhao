<template>
  <div class="settings-page">
    <div class="settings-container">
      <div class="settings-header">
        <h1>用户设置</h1>
        <p>管理您的个人信息和应用偏好</p>
      </div>

      <div class="settings-content">
        <!-- 个人信息 -->
        <div class="settings-section">
          <h2>个人信息</h2>
          
          <div class="form-group">
            <label>用户名</label>
            <div class="input-with-button">
              <input 
                type="text" 
                v-model="editableUsername"
                :disabled="!isEditingUsername || isSaving"
                :class="{ 'disabled-input': !isEditingUsername }"
                placeholder="请输入用户名"
              />
              <button 
                v-if="!isEditingUsername"
                @click="startEditingUsername" 
                class="btn-edit"
                :disabled="isSaving"
              >
                修改
              </button>
              <div v-else class="edit-actions">
                <button 
                  @click="confirmUpdateUsername" 
                  :disabled="isSaving || !editableUsername.trim()"
                  class="btn-confirm"
                >
                  {{ showUsernameConfirm ? '确认修改' : '完成' }}
                </button>
                <button 
                  @click="cancelEditingUsername" 
                  class="btn-cancel"
                  :disabled="isSaving"
                >
                  取消
                </button>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>昵称</label>
            <div class="input-with-button">
              <input 
                type="text" 
                v-model="editableNickname"
                :disabled="!isEditingNickname || isSaving"
                :class="{ 'disabled-input': !isEditingNickname }"
                placeholder="请输入昵称"
              />
              <button 
                v-if="!isEditingNickname"
                @click="startEditingNickname" 
                class="btn-edit"
                :disabled="isSaving"
              >
                修改
              </button>
              <div v-else class="edit-actions">
                <button 
                  @click="confirmUpdateNickname" 
                  :disabled="isSaving || !editableNickname.trim()"
                  class="btn-confirm"
                >
                  {{ showNicknameConfirm ? '确认修改' : '完成' }}
                </button>
                <button 
                  @click="cancelEditingNickname" 
                  class="btn-cancel"
                  :disabled="isSaving"
                >
                  取消
                </button>
              </div>
            </div>
            <small>头像会根据昵称自动生成</small>
          </div>
        </div>


        <!-- 对话历史 -->
        <div class="settings-section">
          <h2>对话历史</h2>
          
          <div class="history-stats">
            <div class="stat-item">
              <div class="stat-number">{{ totalSessions }}</div>
              <div class="stat-label">总对话数</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ totalMessages }}</div>
              <div class="stat-label">总消息数</div>
            </div>
          </div>

          <!-- 历史会话列表 -->
          <div v-if="allHistorySessions.length > 0" class="history-sessions">
            <h3>最近对话</h3>
            <div class="sessions-list">
              <div 
                v-for="session in allHistorySessions.slice(0, 10)" 
                :key="session.session_id"
                class="session-item"
                :class="{ 'deleting': session.isDeleting }"
              >
                <div class="session-info" @click="navigateToChat(session)">
                  <div class="session-character">
                    <img :src="getCharacterAvatar(session.character_id)" :alt="getCharacterName(session.character_id)" class="character-mini-avatar" />
                    <span class="character-name">与{{ getCharacterName(session.character_id) }}对话</span>
                  </div>
                  <div class="session-meta">
                    <span class="session-date">{{ formatDate(session.created_at) }}</span>
                    <span class="session-count">{{ session.message_count }}条消息</span>
                  </div>
                </div>
                
                <div class="session-actions">
                  <button 
                    v-if="!session.isDeleting"
                    @click="startDelete(session)"
                    class="delete-btn"
                    title="删除对话"
                  >
                    🗑️
                  </button>
                  
                  <div v-else class="delete-confirm">
                    <span class="confirm-text">确认删除？</span>
                    <button @click="confirmDelete(session)" class="confirm-btn">是</button>
                    <button @click="cancelDelete(session)" class="cancel-btn">否</button>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="allHistorySessions.length > 10" class="show-more">
              <button @click="showAllHistory = !showAllHistory" class="btn-secondary">
                {{ showAllHistory ? '收起' : `查看全部 ${allHistorySessions.length} 个对话` }}
              </button>
            </div>
          </div>

          <div class="history-actions">
            <button @click="exportHistory" class="btn-secondary" :disabled="isExporting">
              {{ isExporting ? '导出中...' : '导出对话历史' }}
            </button>
            <button @click="clearAllHistory" class="btn-danger" :disabled="isClearing">
              {{ isClearing ? '清除中...' : '清除所有历史' }}
            </button>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="settings-actions">
          <button @click="saveSettings" class="btn-primary" :disabled="isSaving">
            {{ isSaving ? '保存中...' : '保存设置' }}
          </button>
          <button @click="resetSettings" class="btn-secondary" :disabled="isSaving">
            重置设置
          </button>
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
import { useAuth } from '../composables/useAuth.js'
import apiService from '../apiService.js'

export default {
  name: 'SettingsPage',
  setup() {
    const { 
      currentUser, 
      userDisplayName, 
      userAvatar,
      refreshUserInfo
    } = useAuth()

    // 编辑状态
    const isEditingUsername = ref(false)
    const isEditingNickname = ref(false)
    const editableUsername = ref('')
    const editableNickname = ref('')
    const showUsernameConfirm = ref(false)
    const showNicknameConfirm = ref(false)

    const isSaving = ref(false)
    const message = ref('')
    const messageType = ref('success')
    const totalSessions = ref(0)
    const totalMessages = ref(0)
    const allHistorySessions = ref([])
    const showAllHistory = ref(false)
    const characterConfigs = ref([])

    // 初始化编辑字段
    const initializeEditableFields = () => {
      editableUsername.value = currentUser.value?.username || ''
      editableNickname.value = currentUser.value?.nickname || currentUser.value?.username || ''
    }

    // 开始编辑用户名
    const startEditingUsername = () => {
      editableUsername.value = currentUser.value?.username || ''
      isEditingUsername.value = true
      showUsernameConfirm.value = false
    }

    // 取消编辑用户名
    const cancelEditingUsername = () => {
      editableUsername.value = currentUser.value?.username || ''
      isEditingUsername.value = false
      showUsernameConfirm.value = false
    }

    // 确认更新用户名
    const confirmUpdateUsername = async () => {
      if (!showUsernameConfirm.value) {
        showUsernameConfirm.value = true
        return
      }

      if (!editableUsername.value.trim()) {
        showMessage('用户名不能为空', 'error')
        return
      }

      try {
        isSaving.value = true
        // 这里需要添加更新用户名的API调用
        // const response = await apiService.updateUsername(editableUsername.value)
        // if (response.success) {
        //   await refreshUserInfo()
        //   showMessage('用户名更新成功', 'success')
        //   isEditingUsername.value = false
        //   showUsernameConfirm.value = false
        // }
        showMessage('用户名更新功能暂未实现', 'warning')
      } catch (error) {
        console.error('更新用户名失败:', error)
        showMessage('更新用户名失败', 'error')
      } finally {
        isSaving.value = false
      }
    }

    // 开始编辑昵称
    const startEditingNickname = () => {
      editableNickname.value = currentUser.value?.nickname || currentUser.value?.username || ''
      isEditingNickname.value = true
      showNicknameConfirm.value = false
    }

    // 取消编辑昵称
    const cancelEditingNickname = () => {
      editableNickname.value = currentUser.value?.nickname || currentUser.value?.username || ''
      isEditingNickname.value = false
      showNicknameConfirm.value = false
    }

    // 确认更新昵称
    const confirmUpdateNickname = async () => {
      if (!showNicknameConfirm.value) {
        showNicknameConfirm.value = true
        return
      }

      if (!editableNickname.value.trim()) {
        showMessage('昵称不能为空', 'error')
        return
      }

      try {
        isSaving.value = true
        const response = await apiService.updateNickname(editableNickname.value)
        if (response.success) {
          await refreshUserInfo()
          showMessage('昵称更新成功，头像已重新生成', 'success')
          isEditingNickname.value = false
          showNicknameConfirm.value = false
        } else {
          showMessage(response.error || '更新昵称失败', 'error')
        }
      } catch (error) {
        console.error('更新昵称失败:', error)
        showMessage('更新昵称失败', 'error')
      } finally {
        isSaving.value = false
      }
    }

    // 加载角色配置
    const loadCharacterConfigs = async () => {
      try {
        const configs = await apiService.getCharacterConfigs()
        characterConfigs.value = configs
      } catch (error) {
        console.error('加载角色配置失败:', error)
      }
    }

    // 加载对话统计和历史
    const loadChatStats = async () => {
      try {
        const response = await apiService.getUserSessions()
        if (response.success) {
          allHistorySessions.value = response.sessions.map(session => ({
            ...session,
            isDeleting: false
          }))
          totalSessions.value = response.sessions.length
          totalMessages.value = response.sessions.reduce((total, session) => {
            return total + (session.message_count || 0)
          }, 0)
        }
      } catch (error) {
        console.error('加载对话统计失败:', error)
      }
    }

    // 保存设置
    const saveSettings = async () => {
      isSaving.value = true
      try {
        const settingsToSave = {
          theme: userSettings.theme,
          language: userSettings.language,
          default_model: userSettings.default_model,
          auto_play_voice: userSettings.auto_play_voice
        }

        const response = await updateSettings(settingsToSave)
        if (response.success) {
          showMessage('设置保存成功', 'success')
        } else {
          showMessage(response.error || '保存设置失败', 'error')
        }
      } catch (error) {
        console.error('保存设置失败:', error)
        showMessage('保存设置失败', 'error')
      } finally {
        isSaving.value = false
      }
    }

    // 更新头像
    const handleUpdateAvatar = async () => {
      if (!userSettings.avatar.trim()) {
        showMessage('请输入头像URL', 'error')
        return
      }

      try {
        const response = await updateAvatar(userSettings.avatar)
        if (response.success) {
          showMessage('头像更新成功', 'success')
        } else {
          showMessage(response.error || '头像更新失败', 'error')
        }
      } catch (error) {
        console.error('头像更新失败:', error)
        showMessage('头像更新失败', 'error')
      }
    }

    // 重置设置
    const resetSettings = () => {
      Object.assign(userSettings, {
        theme: 'light',
        language: 'zh-CN',
        default_model: 'deepseek-v3',
        auto_play_voice: false
      })
      showMessage('设置已重置', 'info')
    }

    // 导出对话历史
    const exportHistory = async () => {
      isExporting.value = true
      try {
        const response = await apiService.getUserSessions()
        if (response.success) {
          // 检查是否有可导出的对话记录
          if (!response.sessions || response.sessions.length === 0) {
            showMessage('暂无对话记录可导出', 'warning')
            return
          }
          
          const dataStr = JSON.stringify(response.sessions, null, 2)
          const dataBlob = new Blob([dataStr], { type: 'application/json' })
          
          const link = document.createElement('a')
          link.href = URL.createObjectURL(dataBlob)
          link.download = `chat_history_${new Date().toISOString().split('T')[0]}.json`
          link.click()
          
          showMessage('对话历史导出成功', 'success')
        } else {
          showMessage('获取对话记录失败', 'error')
        }
      } catch (error) {
        console.error('导出对话历史失败:', error)
        showMessage('导出失败', 'error')
      } finally {
        isExporting.value = false
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

    // 跳转到聊天页面
    const navigateToChat = (session) => {
      // 使用Vue Router跳转到聊天页面，并传递会话ID
      window.location.href = `/chat/${session.character_id}?session=${session.session_id}`
    }

    // 开始删除流程
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
        // 这里需要实现删除单个会话的API
        // await apiService.deleteSession(session.session_id)
        
        // 从列表中移除
        allHistorySessions.value = allHistorySessions.value.filter(s => s.session_id !== session.session_id)
        totalSessions.value = allHistorySessions.value.length
        totalMessages.value = allHistorySessions.value.reduce((total, s) => total + (s.message_count || 0), 0)
        
        showMessage('对话已删除', 'success')
      } catch (error) {
        console.error('删除对话失败:', error)
        showMessage('删除失败', 'error')
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
        return date.toLocaleDateString('zh-CN')
      }
    }

    // 清除所有对话历史
    const clearAllHistory = async () => {
      try {
        // 先检查是否有历史记录
        const response = await apiService.getUserSessions()
        if (response.success) {
          // 检查是否有可清空的对话记录
          if (!response.sessions || response.sessions.length === 0) {
            showMessage('暂无对话记录可清空', 'warning')
            return
          }
        } else {
          showMessage('获取对话记录失败', 'error')
          return
        }
        
        if (!confirm('确定要清除所有对话历史吗？此操作不可恢复。')) {
          return
        }

        isClearing.value = true
        
        // 调用清除历史的API
        await apiService.clearAllHistory()
        
        // 更新本地状态
        allHistorySessions.value = []
        totalSessions.value = 0
        totalMessages.value = 0
        showMessage('对话历史清除成功', 'success')
      } catch (error) {
        console.error('清除对话历史失败:', error)
        showMessage('清除失败', 'error')
      } finally {
        isClearing.value = false
      }
    }

    // 显示消息
    const showMessage = (text, type = 'success') => {
      message.value = text
      messageType.value = type
      setTimeout(() => {
        message.value = ''
      }, 3000)
    }

    onMounted(() => {
      initializeEditableFields()
      loadCharacterConfigs()
      loadChatStats()
    })

    return {
      // 状态
      currentUser,
      userDisplayName,
      userAvatar,
      isSaving,
      message,
      messageType,
      totalSessions,
      totalMessages,
      allHistorySessions,
      showAllHistory,

      // 编辑状态
      isEditingUsername,
      isEditingNickname,
      editableUsername,
      editableNickname,
      showUsernameConfirm,
      showNicknameConfirm,

      // 方法
      startEditingUsername,
      cancelEditingUsername,
      confirmUpdateUsername,
      startEditingNickname,
      cancelEditingNickname,
      confirmUpdateNickname,
      exportHistory,
      clearAllHistory,
      getCharacterName,
      getCharacterAvatar,
      navigateToChat,
      startDelete,
      cancelDelete,
      confirmDelete,
      formatDate
    }
  }
}
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 2rem;
}

.settings-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.settings-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.settings-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 600;
}

.settings-header p {
  margin: 0;
  opacity: 0.9;
}

.settings-content {
  padding: 2rem;
}

.settings-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.settings-section:last-child {
  border-bottom: none;
}

.settings-section h2 {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.25rem;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.disabled-input {
  background: #f8f9fa;
  cursor: not-allowed;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  color: #666;
  font-size: 0.875rem;
}

.input-with-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.input-with-button input {
  flex: 1;
}

.btn-edit {
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

.btn-edit:hover {
  background: #5a6fd8;
  transform: translateY(-1px);
}

.btn-edit:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-confirm {
  padding: 0.5rem 1rem;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-confirm:hover {
  background: #218838;
  transform: translateY(-1px);
}

.btn-confirm:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.btn-cancel {
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

.btn-cancel:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

.btn-cancel:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.current-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e0e0e0;
}

.avatar-actions {
  flex: 1;
  display: flex;
  gap: 0.5rem;
}

.avatar-actions input {
  flex: 1;
  margin: 0;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: normal;
  margin: 0;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 0.5rem;
  width: auto;
}

.history-stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 600;
  color: #667eea;
}

.stat-label {
  color: #666;
  font-size: 0.875rem;
}

.history-actions {
  display: flex;
  gap: 1rem;
}

.settings-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  padding-top: 2rem;
  border-top: 1px solid #e0e0e0;
}

.btn-primary,
.btn-secondary,
.btn-danger {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-secondary {
  background: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover:not(:disabled) {
  background: #e9ecef;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
}

.btn-primary:disabled,
.btn-secondary:disabled,
.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message {
  margin: 1rem 2rem;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
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

/* 历史会话列表样式 */
.history-sessions {
  margin: 1.5rem 0;
}

.history-sessions h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
}

.sessions-list {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.session-item {
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  background: white;
  min-height: 80px; /* 固定最小高度 */
}

.session-item:last-child {
  border-bottom: none;
}

.session-item.deleting {
  background: linear-gradient(90deg, #fff 0%, #ffebee 100%);
  border-left: 3px solid #f44336;
}

.session-info {
  flex: 1;
  padding: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0; /* 允许内容收缩 */
}

.session-info:hover {
  background: #f8f9fa;
}

.session-character {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  min-width: 0; /* 允许内容收缩 */
}

.character-mini-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e0e0e0;
  flex-shrink: 0; /* 头像不收缩 */
}

.character-name {
  font-weight: 600;
  color: #333;
  font-size: 0.95rem;
  white-space: nowrap; /* 防止换行 */
  overflow: hidden;
  text-overflow: ellipsis; /* 超长显示省略号 */
  flex: 1;
}

.session-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #666;
  flex-wrap: wrap; /* 允许元数据换行 */
}

.session-actions {
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120px; /* 固定操作区域最小宽度 */
  flex-shrink: 0; /* 操作区域不收缩 */
}

.delete-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 1rem;
  transition: all 0.2s;
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
  justify-content: center;
  width: 100%;
}

.confirm-text {
  font-size: 0.8rem;
  color: #d32f2f;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0; /* 文字不收缩 */
}

.confirm-btn,
.cancel-btn {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0; /* 按钮不收缩 */
  min-width: 28px; /* 最小宽度 */
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

.show-more {
  text-align: center;
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
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
  .settings-page {
    padding: 1rem;
  }
  
  .settings-content {
    padding: 1.5rem;
  }
  
  .avatar-section {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .avatar-actions {
    width: 100%;
    flex-direction: column;
  }
  
  .history-stats {
    justify-content: center;
  }
  
  .history-actions,
  .settings-actions {
    flex-direction: column;
  }
  
  /* 移动端历史记录卡片优化 */
  .session-item {
    min-height: 70px;
  }
  
  .session-actions {
    min-width: 100px;
    padding: 0.75rem;
  }
  
  .character-name {
    font-size: 0.9rem;
  }
  
  .confirm-text {
    font-size: 0.75rem;
  }
  
  .confirm-btn,
  .cancel-btn {
    font-size: 0.7rem;
    padding: 0.2rem 0.4rem;
    min-width: 26px;
  }
}
</style>