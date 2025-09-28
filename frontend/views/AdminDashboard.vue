<template>
  <div class="admin-dashboard">
    <div class="admin-header">
      <h1>系统管理后台</h1>
      <div class="admin-info">
        <span>欢迎，{{ userDisplayName }}</span>
        <span class="admin-badge">管理员</span>
      </div>
    </div>

    <div class="admin-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        :class="['tab-button', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <div class="admin-content">
      <!-- 数据统计 -->
      <div v-if="activeTab === 'statistics'" class="tab-content">
        <AdminStatistics />
      </div>

      <!-- 用户管理 -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <AdminUsers />
      </div>

      <!-- 角色管理 -->
      <div v-if="activeTab === 'characters'" class="tab-content">
        <AdminCharacters />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import AdminStatistics from '../components/admin/AdminStatistics.vue'
import AdminUsers from '../components/admin/AdminUsers.vue'
import AdminCharacters from '../components/admin/AdminCharacters.vue'

export default {
  name: 'AdminDashboard',
  components: {
    AdminStatistics,
    AdminUsers,
    AdminCharacters
  },
  setup() {
    const router = useRouter()
    const { isAuthenticated, isAdmin, userDisplayName } = useAuth()
    
    const activeTab = ref('statistics')
    
    const tabs = [
      { key: 'statistics', label: '数据统计', icon: '📊' },
      { key: 'users', label: '用户管理', icon: '👥' },
      { key: 'characters', label: '角色管理', icon: '🎭' }
    ]

    // 权限检查
    const checkPermission = () => {
      if (!isAuthenticated.value || !isAdmin.value) {
        router.push('/')
        return false
      }
      return true
    }

    // 监听权限变化
    watch([isAuthenticated, isAdmin], () => {
      checkPermission()
    }, { immediate: true })

    onMounted(() => {
      checkPermission()
    })

    return {
      activeTab,
      tabs,
      userDisplayName,
      checkPermission
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 2rem;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1.5rem 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
}

.admin-header h1 {
  margin: 0;
  color: #2d3748;
  font-size: 1.75rem;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.admin-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.admin-tabs {
  display: flex;
  background: white;
  border-radius: 12px;
  padding: 0.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
  gap: 0.5rem;
}

.tab-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #64748b;
  font-weight: 500;
}

.tab-button:hover {
  background: #f1f5f9;
  color: #475569;
}

.tab-button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.tab-icon {
  font-size: 1.25rem;
}

.admin-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  min-height: 600px;
}

.tab-content {
  padding: 2rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-dashboard {
    padding: 1rem;
  }
  
  .admin-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .admin-tabs {
    flex-direction: column;
  }
  
  .tab-button {
    justify-content: flex-start;
  }
}
</style>
