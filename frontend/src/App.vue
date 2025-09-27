<template>
  <div class="app-container">
    <!-- 全局历史记录面板 -->
    <GlobalHistoryPanel />
    
    <!-- 导航栏 - 在聊天页面隐藏 -->
    <nav class="navbar" v-show="!isChatPage">
      <div class="navbar-brand">
        <h1>DeepTalk</h1>
      </div>
      <div class="navbar-menu">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/characters" class="nav-link">角色列表</router-link>
        <router-link v-if="isAdmin" to="/admin" class="nav-link admin-link">管理页面</router-link>
        
        <!-- 用户菜单区域 -->
        <div class="navbar-user-section">
          <!-- 未登录状态 -->
          <div v-if="!isAuthenticated" class="auth-buttons">
            <button @click="handleGuestLogin" class="nav-link guest-btn">游客体验</button>
            <router-link to="/login" class="nav-link login-btn">登录</router-link>
          </div>
          
          <!-- 已登录状态 -->
          <div v-else class="user-menu" ref="userMenuRef">
            <button class="user-avatar-btn" @click="toggleUserMenu">
              <img :src="userAvatar" :alt="userDisplayName" class="user-avatar" />
              <span class="user-name">{{ userDisplayName }}</span>
              <span class="dropdown-arrow">▼</span>
            </button>
            
            <!-- 下拉菜单 -->
            <div v-if="showUserMenu" class="user-dropdown">
              <div class="user-info">
                <img :src="userAvatar" :alt="userDisplayName" class="dropdown-avatar" />
                <div class="user-details">
                  <div class="username">{{ userDisplayName }}</div>
                  <div class="user-email">{{ currentUser.email || '未设置邮箱' }}</div>
                </div>
              </div>
              
              <div class="menu-divider"></div>
              
              <button v-if="!isGuestMode" class="menu-item" @click="openPersonalInfo">
                <span class="menu-icon">👤</span>
                <span>个人信息</span>
              </button>
              
              <button v-if="!isGuestMode" class="menu-item" @click="openChatHistory">
                <span class="menu-icon">💬</span>
                <span>对话历史</span>
              </button>
              
              <div v-if="isGuestMode" class="guest-notice">
                <span class="menu-icon">ℹ️</span>
                <span>游客模式 - 退出后数据将清除</span>
              </div>
              
              <button class="menu-item logout-item" @click="handleLogout">
                <span class="menu-icon">🚪</span>
                <span>退出登录</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-content">
      <transition name="page" mode="out-in">
        <router-view />
      </transition>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <p>&copy; 2025 DeepTalk - 基于七牛云AI大模型 | 作者：Leonxrek</p>
    </footer>

    <!-- 弹窗遮罩和内容 -->
    <div v-if="showPersonalInfoModal || showChatHistoryModal" class="modal-backdrop" @click="closeModals">
      <!-- 个人信息弹窗 -->
      <PersonalInfoModal 
        v-if="showPersonalInfoModal" 
        @close="closeModals"
        @click.stop
      />
      
      <!-- 对话历史弹窗 -->
      <ChatHistoryModal 
        v-if="showChatHistoryModal" 
        @close="closeModals"
        @click.stop
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GlobalHistoryPanel from './components/GlobalHistoryPanel.vue'
import PersonalInfoModal from './components/PersonalInfoModal.vue'
import ChatHistoryModal from './components/ChatHistoryModal.vue'
import { useAuth } from './composables/useAuth.js'

export default {
  name: 'App',
  components: {
    GlobalHistoryPanel,
    PersonalInfoModal,
    ChatHistoryModal
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const { 
      isAuthenticated, 
      isGuestMode,
      currentUser, 
      userDisplayName, 
      userAvatar,
      isAdmin,
      loginAsGuest,
      logout,
      initAuth
    } = useAuth()
    
    // 检测是否在聊天页面
    const isChatPage = computed(() => {
      return route.name === 'Chat'
    })
    
    const showUserMenu = ref(false)
    const userMenuRef = ref(null)
    
    // 弹窗状态
    const showPersonalInfoModal = ref(false)
    const showChatHistoryModal = ref(false)

    // 切换用户菜单
    const toggleUserMenu = () => {
      showUserMenu.value = !showUserMenu.value
    }

    // 关闭用户菜单
    const closeUserMenu = () => {
      showUserMenu.value = false
    }

    // 处理游客登录
    const handleGuestLogin = async () => {
      try {
        await loginAsGuest()
        console.log('游客登录成功')
      } catch (error) {
        console.error('游客登录失败:', error)
      }
    }

    // 处理登出
    const handleLogout = async () => {
      try {
        await logout(router)
        closeUserMenu()
      } catch (error) {
        console.error('登出失败:', error)
      }
    }

    // 打开个人信息弹窗
    const openPersonalInfo = () => {
      closeUserMenu()
      showPersonalInfoModal.value = true
    }

    // 打开对话历史弹窗
    const openChatHistory = () => {
      closeUserMenu()
      showChatHistoryModal.value = true
    }

    // 关闭弹窗
    const closeModals = () => {
      showPersonalInfoModal.value = false
      showChatHistoryModal.value = false
    }

    // 点击外部关闭菜单
    const handleClickOutside = (event) => {
      if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
        closeUserMenu()
      }
    }

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
      // 确保认证状态正确初始化
      initAuth()
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      // 认证状态
      isAuthenticated,
      isGuestMode,
      currentUser,
      userDisplayName,
      userAvatar,
      isAdmin,
      
      // 页面状态
      isChatPage,
      
      // 用户菜单状态
      showUserMenu,
      userMenuRef,
      
      // 弹窗状态
      showPersonalInfoModal,
      showChatHistoryModal,
      
      // 方法
      toggleUserMenu,
      closeUserMenu,
      handleGuestLogin,
      handleLogout,
      openPersonalInfo,
      openChatHistory,
      closeModals
    }
  }
}
</script>

<style>
/* 全局样式 */
:root {
  --primary-color: #4c84ff;
  --secondary-color: #6c757d;
  --background-color: #f5f5f5;
  --text-color: #333;
  --border-radius: 8px;
  --box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.6;
  color: var(--text-color);
  background-color: var(--background-color);
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 导航栏样式 */
.navbar {
  background-color: white;
  box-shadow: var(--box-shadow);
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-brand h1 {
  font-size: 20px;
  color: var(--primary-color);
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: 20px;
}

.navbar-user-section {
  display: flex;
  align-items: center;
  margin-left: 20px;
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-link {
  text-decoration: none;
  color: var(--text-color);
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: #f0f0f0;
  color: var(--primary-color);
}

.nav-link.router-link-active {
  color: var(--primary-color);
  background-color: #f0f8ff;
}

.admin-link {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.admin-link:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 登录按钮样式 */
.login-btn {
  background: var(--primary-color);
  color: white !important;
}

.login-btn:hover {
  background: #3a6fe6 !important;
  color: white !important;
}

/* 游客按钮样式 */
.guest-btn {
  background: #6c757d;
  color: white !important;
}

.guest-btn:hover {
  background: #5a6268 !important;
  color: white !important;
}

/* 用户菜单样式 */
.user-menu {
  position: relative;
}

.user-avatar-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.user-avatar-btn:hover {
  background: #f5f5f5;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e0e0e0;
}

.user-name {
  font-weight: 500;
  color: #333;
}

.dropdown-arrow {
  font-size: 0.8rem;
  color: #666;
  transition: transform 0.2s;
}

.user-avatar-btn:hover .dropdown-arrow {
  transform: rotate(180deg);
}

/* 用户下拉菜单 */
.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 250px;
  z-index: 1000;
  overflow: hidden;
  margin-top: 0.5rem;
}

.user-info {
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f8f9fa;
}

.dropdown-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e0e0e0;
}

.user-details {
  flex: 1;
}

.username {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
}

.user-email {
  font-size: 0.875rem;
  color: #666;
}

.menu-divider {
  height: 1px;
  background: #e0e0e0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #333;
  text-decoration: none;
  background: none;
  border: none;
  width: 100%;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.9rem;
}

.menu-item:hover {
  background: #f5f5f5;
}

.logout-item {
  color: #dc3545;
}

.logout-item:hover {
  background: #fee;
}

.menu-icon {
  width: 16px;
  text-align: center;
}

/* 游客提示样式 */
.guest-notice {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #666;
  font-size: 0.85rem;
  background: #f8f9fa;
  border-left: 3px solid #28a745;
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

/* 页面过渡效果 */
.page-enter-active,
.page-leave-active {
  transition: all 0.4s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.page-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 弹窗样式 */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: backdropFadeIn 0.3s ease-out;
}

@keyframes backdropFadeIn {
  from {
    opacity: 0;
    backdrop-filter: blur(0px);
  }
  to {
    opacity: 1;
    backdrop-filter: blur(8px);
  }
}

.page-enter-to,
.page-leave-from {
  opacity: 1;
  transform: translateX(0);
}

/* 页脚样式 */
.footer {
  background-color: white;
  padding: 20px;
  text-align: center;
  color: var(--secondary-color);
  font-size: 14px;
  border-top: 1px solid #e0e0e0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    height: auto;
    padding: 10px;
  }
  
  .navbar-menu {
    margin-top: 10px;
    justify-content: center;
    flex-wrap: wrap;
    width: 100%;
  }
  
  .navbar-user-section {
    margin-left: 0;
    margin-top: 10px;
  }
  
  .user-dropdown {
    right: auto;
    left: 50%;
    transform: translateX(-50%);
  }
  
  .main-content {
    padding: 10px;
  }
  
  .page-enter-from,
  .page-leave-to {
    transform: translateY(20px);
  }
  
  .page-leave-to {
    transform: translateY(-20px);
  }
}
</style>