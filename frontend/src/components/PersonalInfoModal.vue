<template>
  <div class="modal-content" @click.stop>
    <div class="modal-header">
      <h2>个人信息</h2>
      <button class="close-button" @click="$emit('close')">✕</button>
    </div>
    
    <div class="modal-body">
      <div class="personal-info-section">
        <!-- 用户头像显示 -->
        <div class="avatar-display">
          <img :src="userAvatar" :alt="userDisplayName" class="user-avatar-large" />
          <p class="avatar-info">头像会根据昵称自动生成</p>
        </div>
        
        <!-- 邮箱编辑 -->
        <div class="form-group">
          <label>邮箱</label>
          <div class="input-with-button">
            <input 
              type="email" 
              v-model="editableEmail"
              :disabled="!isEditingEmail || isSaving"
              :class="{ 'disabled-input': !isEditingEmail }"
              placeholder="请输入邮箱地址"
            />
            <button 
              v-if="!isEditingEmail"
              @click="startEditingEmail" 
              class="btn-edit"
              :disabled="isSaving"
            >
              修改
            </button>
            <div v-else class="edit-actions">
              <button 
                @click="confirmUpdateEmail" 
                :disabled="isSaving || !editableEmail.trim() || !isValidEmail"
                class="btn-confirm"
              >
                {{ showEmailConfirm ? '确认修改' : '完成' }}
              </button>
              <button 
                @click="cancelEditingEmail" 
                class="btn-cancel"
                :disabled="isSaving"
              >
                取消
              </button>
            </div>
          </div>
          <small v-if="isEditingEmail && editableEmail.trim() && !isValidEmail" class="error-text">
            请输入有效的邮箱地址
          </small>
        </div>

        <!-- 昵称编辑 -->
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

        <!-- 消息提示 -->
        <div v-if="message" class="message" :class="messageType">
          {{ message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useAuth } from '../composables/useAuth.js'
import apiService from '../apiService.js'

export default {
  name: 'PersonalInfoModal',
  emits: ['close'],
  setup() {
    const { 
      currentUser, 
      userDisplayName, 
      userAvatar,
      refreshUserInfo
    } = useAuth()

    // 编辑状态
    const isEditingEmail = ref(false)
    const isEditingNickname = ref(false)
    const editableEmail = ref('')
    const editableNickname = ref('')
    const showEmailConfirm = ref(false)
    const showNicknameConfirm = ref(false)
    const isSaving = ref(false)
    const message = ref('')
    const messageType = ref('success')

    // 邮箱验证
    const isValidEmail = computed(() => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(editableEmail.value)
    })

    // 初始化编辑字段
    const initializeEditableFields = () => {
      editableEmail.value = currentUser.value?.email || ''
      editableNickname.value = currentUser.value?.nickname || currentUser.value?.username || ''
    }

    // 显示消息
    const showMessage = (msg, type = 'success') => {
      message.value = msg
      messageType.value = type
      setTimeout(() => {
        message.value = ''
      }, 3000)
    }

    // 开始编辑邮箱
    const startEditingEmail = () => {
      editableEmail.value = currentUser.value?.email || ''
      isEditingEmail.value = true
      showEmailConfirm.value = false
    }

    // 取消编辑邮箱
    const cancelEditingEmail = () => {
      editableEmail.value = currentUser.value?.email || ''
      isEditingEmail.value = false
      showEmailConfirm.value = false
    }

    // 确认更新邮箱
    const confirmUpdateEmail = async () => {
      if (!showEmailConfirm.value) {
        showEmailConfirm.value = true
        return
      }

      if (!editableEmail.value.trim()) {
        showMessage('邮箱不能为空', 'error')
        return
      }

      if (!isValidEmail.value) {
        showMessage('请输入有效的邮箱地址', 'error')
        return
      }

      try {
        isSaving.value = true
        const response = await apiService.updateEmail(editableEmail.value)
        if (response.success) {
          await refreshUserInfo()
          showMessage('邮箱更新成功', 'success')
          isEditingEmail.value = false
          showEmailConfirm.value = false
        } else {
          showMessage(response.error || '更新邮箱失败', 'error')
        }
      } catch (error) {
        console.error('更新邮箱失败:', error)
        showMessage('更新邮箱失败', 'error')
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

    onMounted(() => {
      initializeEditableFields()
    })

    return {
      currentUser,
      userDisplayName,
      userAvatar,
      isEditingEmail,
      isEditingNickname,
      editableEmail,
      editableNickname,
      showEmailConfirm,
      showNicknameConfirm,
      isValidEmail,
      isSaving,
      message,
      messageType,
      startEditingEmail,
      cancelEditingEmail,
      confirmUpdateEmail,
      startEditingNickname,
      cancelEditingNickname,
      confirmUpdateNickname
    }
  }
}
</script>

<style scoped>
.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 500px;
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

.avatar-display {
  text-align: center;
  margin-bottom: 2rem;
}

.user-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e0e0e0;
  margin-bottom: 0.5rem;
}

.avatar-info {
  color: #666;
  font-size: 0.875rem;
  margin: 0;
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

.input-with-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.input-with-button input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.input-with-button input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.disabled-input {
  background: #f8f9fa;
  cursor: not-allowed;
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

.form-group small {
  display: block;
  margin-top: 0.25rem;
  color: #666;
  font-size: 0.875rem;
}

.form-group small.error-text {
  color: #dc3545;
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

.message.warning {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}
</style>
