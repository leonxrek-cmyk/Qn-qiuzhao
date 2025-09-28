<template>
  <div class="admin-users">
    <div class="users-header">
      <h2>用户管理</h2>
      <button @click="showAddUser = true" class="btn-primary">
        <span>➕</span>
        添加用户
      </button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="users-filters">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索用户名、邮箱或昵称..."
          @input="filterUsers"
        />
        <span 
          :class="['search-icon', { 'clear-icon': searchQuery.trim() }]"
          @click="clearSearch"
        >
          {{ searchQuery.trim() ? '✕' : '🔍' }}
        </span>
      </div>
      
      <select v-model="filterType" @change="filterUsers" class="filter-select">
        <option value="all">全部用户</option>
        <option value="admin">管理员</option>
        <option value="user">普通用户</option>
      </select>
    </div>

    <!-- 用户列表 -->
    <div class="users-table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>头像</th>
            <th>用户名</th>
            <th>昵称</th>
            <th>邮箱</th>
            <th>类型</th>
            <th>注册时间</th>
            <th>对话数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id" class="user-row">
            <td>
              <img :src="user.avatar || '/user-avatar.svg'" :alt="user.username" class="user-avatar" />
            </td>
            <td class="username">{{ user.username }}</td>
            <td>{{ user.nickname || user.username }}</td>
            <td>{{ user.email || '未设置' }}</td>
            <td>
              <span :class="['user-type', user.is_admin ? 'admin' : 'user']">
                {{ user.is_admin ? '管理员' : '普通用户' }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>{{ user.chat_sessions || 0 }}</td>
            <td>
              <div class="action-buttons">
                <button @click="editUser(user)" class="btn-edit" title="编辑">✏️</button>
                <button 
                  v-if="!user.is_admin" 
                  @click="deleteUser(user)" 
                  class="btn-delete" 
                  title="删除"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 用户编辑弹窗 -->
    <div v-if="showEditUser" class="modal-overlay" @click="closeEditUser">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingUser.id ? '编辑用户' : '添加用户' }}</h3>
          <button @click="closeEditUser" class="close-btn">✕</button>
        </div>
        
        <form @submit.prevent="saveUser" class="user-form">
          <div class="form-group">
            <label>用户名</label>
            <input 
              type="text" 
              v-model="editingUser.username" 
              required 
              :disabled="!!editingUser.id"
            />
          </div>
          
          <div class="form-group">
            <label>昵称</label>
            <input type="text" v-model="editingUser.nickname" />
          </div>
          
          <div class="form-group">
            <label>邮箱</label>
            <input type="email" v-model="editingUser.email" />
          </div>
          
          <div class="form-group">
            <label>{{ editingUser.id ? '新密码（留空则不修改）' : '密码' }}</label>
            <input 
              type="password" 
              v-model="editingUser.password" 
              :required="!editingUser.id"
              :placeholder="editingUser.id ? '留空则不修改密码' : '请输入密码'"
            />
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="editingUser.is_admin"
                :disabled="editingUser.username === 'admin'"
              />
              管理员权限
            </label>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeEditUser" class="btn-cancel">取消</button>
            <button type="submit" class="btn-save" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载用户数据中...</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import apiService from '../../apiService.js'

export default {
  name: 'AdminUsers',
  setup() {
    const loading = ref(false)
    const saving = ref(false)
    const users = ref([])
    const searchQuery = ref('')
    const filterType = ref('all')
    const showEditUser = ref(false)
    const showAddUser = ref(false)
    
    const editingUser = ref({
      id: '',
      username: '',
      nickname: '',
      email: '',
      password: '',
      is_admin: false
    })

    const filteredUsers = computed(() => {
      let result = users.value

      // 类型筛选
      if (filterType.value !== 'all') {
        result = result.filter(user => {
          if (filterType.value === 'admin') return user.is_admin
          if (filterType.value === 'user') return !user.is_admin
          return true
        })
      }

      // 搜索筛选
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(user => 
          user.username.toLowerCase().includes(query) ||
          (user.nickname || '').toLowerCase().includes(query) ||
          (user.email || '').toLowerCase().includes(query)
        )
      }

      return result
    })

    const loadUsers = async () => {
      try {
        loading.value = true
        const response = await apiService.getAllUsers()
        if (response.success) {
          users.value = response.users
        }
      } catch (error) {
        console.error('加载用户列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    const filterUsers = () => {
      // 触发计算属性重新计算
    }

    const clearSearch = () => {
      if (searchQuery.value.trim()) {
        searchQuery.value = ''
        filterUsers()
      }
    }

    const editUser = (user) => {
      editingUser.value = {
        id: user.id,
        username: user.username,
        nickname: user.nickname || '',
        email: user.email || '',
        password: '',
        is_admin: user.is_admin
      }
      showEditUser.value = true
    }

    const deleteUser = async (user) => {
      if (!confirm(`确定要删除用户 "${user.username}" 吗？此操作不可撤销。`)) {
        return
      }

      try {
        const response = await apiService.deleteUser(user.id)
        if (response.success) {
          await loadUsers()
        } else {
          alert('删除失败：' + response.error)
        }
      } catch (error) {
        console.error('删除用户失败:', error)
        alert('删除失败，请稍后重试')
      }
    }

    const saveUser = async () => {
      try {
        saving.value = true
        
        let response
        if (editingUser.value.id) {
          // 更新用户
          response = await apiService.updateUser(editingUser.value.id, editingUser.value)
        } else {
          // 创建用户
          response = await apiService.createUser(editingUser.value)
        }

        if (response.success) {
          const action = editingUser.value.id ? '修改' : '添加'
          alert(`${action}成功！`)
          closeEditUser()
          await loadUsers()
        } else {
          alert('保存失败：' + response.error)
        }
      } catch (error) {
        console.error('保存用户失败:', error)
        alert('保存失败，请稍后重试')
      } finally {
        saving.value = false
      }
    }

    const closeEditUser = () => {
      showEditUser.value = false
      showAddUser.value = false
      editingUser.value = {
        id: '',
        username: '',
        nickname: '',
        email: '',
        password: '',
        is_admin: false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return '未知'
      return new Date(dateString).toLocaleDateString('zh-CN')
    }

    // 监听添加用户
    const handleAddUser = () => {
      editingUser.value = {
        id: '',
        username: '',
        nickname: '',
        email: '',
        password: '',
        is_admin: false
      }
      showEditUser.value = true
    }
    
    // 监听showAddUser变化
    watch(showAddUser, (newValue) => {
      if (newValue) {
        handleAddUser()
        showAddUser.value = false
      }
    })

    onMounted(() => {
      loadUsers()
    })

    return {
      loading,
      saving,
      users,
      filteredUsers,
      searchQuery,
      filterType,
      showEditUser,
      showAddUser,
      editingUser,
      loadUsers,
      filterUsers,
      clearSearch,
      editUser,
      deleteUser,
      saveUser,
      closeEditUser,
      formatDate,
      handleAddUser
    }
  }
}
</script>

<style scoped>
.admin-users {
  position: relative;
}

.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.users-header h2 {
  margin: 0;
  color: #2d3748;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.users-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: center;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
}

.search-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.search-icon:hover {
  background: rgba(0, 0, 0, 0.05);
}

.search-icon.clear-icon {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  animation: fadeToRed 0.3s ease;
}

.search-icon.clear-icon:hover {
  color: #dc2626;
  background: rgba(239, 68, 68, 0.2);
  transform: translateY(-50%) scale(1.1);
}

@keyframes fadeToRed {
  from {
    color: #64748b;
    background: transparent;
  }
  to {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
}

.users-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #475569;
  border-bottom: 1px solid #e2e8f0;
}

.user-row {
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s;
}

.user-row:hover {
  background: #f8fafc;
}

.users-table td {
  padding: 1rem;
  vertical-align: middle;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.username {
  font-weight: 500;
  color: #2d3748;
}

.user-type {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.user-type.admin {
  background: #fef3c7;
  color: #d97706;
}

.user-type.user {
  background: #dbeafe;
  color: #2563eb;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-edit, .btn-delete {
  padding: 0.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit {
  background: #f0f9ff;
  color: #0369a1;
}

.btn-edit:hover {
  background: #0369a1;
  color: white;
}

.btn-delete {
  background: #fef2f2;
  color: #dc2626;
}

.btn-delete:hover {
  background: #dc2626;
  color: white;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  color: #2d3748;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #64748b;
}

.user-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input {
  width: auto !important;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-cancel, .btn-save {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-cancel {
  background: #f1f5f9;
  color: #64748b;
}

.btn-save {
  background: #667eea;
  color: white;
}

.btn-save:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .users-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .users-table-container {
    overflow-x: auto;
  }
  
  .users-table {
    min-width: 800px;
  }
}
</style>
