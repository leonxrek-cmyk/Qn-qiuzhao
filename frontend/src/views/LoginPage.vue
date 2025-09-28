<template>
  <div class="login-page">
    <!-- 背景模糊层 -->
    <div class="background-blur"></div>
    
    <!-- 登录卡片容器 -->
    <div class="login-container">
      <div class="login-card" ref="loginCard">
        <div class="login-header">
          <h1>DeepTalk</h1>
          <p>登录以保存您的对话历史和个人设置</p>
        </div>

        <div class="login-tabs">
          <button 
            class="tab-button" 
            :class="{ active: activeTab === 'login' }"
            @click="switchTab('login')"
          >
            登录
          </button>
          <button 
            class="tab-button" 
            :class="{ active: activeTab === 'register' }"
            @click="switchTab('register')"
          >
            注册
          </button>
        </div>

        <!-- 表单容器，添加过渡动效 -->
        <div class="form-container">
          <transition name="form-slide" mode="out-in">
            <!-- 登录表单 -->
            <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="login-form" key="login">
              <div class="form-group">
                <label for="login-username">用户名</label>
                <input
                  id="login-username"
                  v-model="loginForm.username"
                  type="text"
                  placeholder="请输入用户名"
                  required
                  :disabled="isLoading"
                />
              </div>

              <div class="form-group">
                <label for="login-password">密码</label>
                <input
                  id="login-password"
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  required
                  :disabled="isLoading"
                />
              </div>

              <button type="submit" class="submit-button" :disabled="isLoading">
                <span v-if="isLoading">登录中...</span>
                <span v-else>登录</span>
              </button>
              
              <!-- 登录表单的错误和成功提示 -->
              <div v-if="errorMessage && activeTab === 'login'" class="form-message error-message">
                {{ errorMessage }}
              </div>
              <div v-if="successMessage && activeTab === 'login'" class="form-message success-message">
                {{ successMessage }}
              </div>
            </form>

            <!-- 注册表单 -->
            <form v-else @submit.prevent="handleRegister" class="login-form" key="register">
              <div class="form-group">
                <label for="register-username">用户名</label>
                <input
                  id="register-username"
                  v-model="registerForm.username"
                  type="text"
                  placeholder="请输入用户名（至少3个字符）"
                  required
                  :disabled="isLoading"
                />
              </div>

              <div class="form-group">
                <label for="register-email">邮箱（可选）</label>
                <input
                  id="register-email"
                  v-model="registerForm.email"
                  type="email"
                  placeholder="请输入邮箱地址"
                  :disabled="isLoading"
                />
              </div>

              <div class="form-group">
                <label for="register-password">密码</label>
                <input
                  id="register-password"
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请输入密码（至少6个字符）"
                  required
                  :disabled="isLoading"
                />
              </div>

              <div class="form-group">
                <label for="register-confirm-password">确认密码</label>
                <input
                  id="register-confirm-password"
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入密码"
                  required
                  :disabled="isLoading"
                />
              </div>

              <button type="submit" class="submit-button" :disabled="isLoading">
                <span v-if="isLoading">注册中...</span>
                <span v-else>注册</span>
              </button>
              
              <!-- 注册表单的错误和成功提示 -->
              <div v-if="errorMessage && activeTab === 'register'" class="form-message error-message">
                {{ errorMessage }}
              </div>
              <div v-if="successMessage && activeTab === 'register'" class="form-message success-message">
                {{ successMessage }}
              </div>
            </form>
          </transition>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import apiService from '../apiService.js'

export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter()
    const { login, register, isAuthenticated } = useAuth()
    
    const activeTab = ref('login')
    const isLoading = ref(false)
    const errorMessage = ref('')
    const successMessage = ref('')
    const loginCard = ref(null)
    
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    const registerForm = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    })

    // 清除消息
    const clearMessages = () => {
      errorMessage.value = ''
      successMessage.value = ''
    }

    // 处理登录
    const handleLogin = async () => {
      clearMessages()
      
      if (!loginForm.username.trim() || !loginForm.password.trim()) {
        errorMessage.value = '请填写用户名和密码'
        return
      }

      isLoading.value = true

      try {
        const result = await login(loginForm.username, loginForm.password)
        
        if (result.success) {
          successMessage.value = '登录成功！正在跳转...'
          
          // 跳转到主页
          setTimeout(() => {
            router.push('/')
          }, 1000)
        } else {
          errorMessage.value = result.error || '登录失败'
        }
      } catch (error) {
        console.error('登录错误:', error)
        errorMessage.value = '登录失败，请检查网络连接'
      } finally {
        isLoading.value = false
      }
    }

    // 处理注册
    const handleRegister = async () => {
      clearMessages()
      
      // 表单验证
      if (!registerForm.username.trim()) {
        errorMessage.value = '请输入用户名'
        return
      }
      
      if (registerForm.username.trim().length < 3) {
        errorMessage.value = '用户名至少需要3个字符'
        return
      }
      
      if (!registerForm.password.trim()) {
        errorMessage.value = '请输入密码'
        return
      }
      
      if (registerForm.password.length < 6) {
        errorMessage.value = '密码至少需要6个字符'
        return
      }
      
      if (registerForm.password !== registerForm.confirmPassword) {
        errorMessage.value = '两次输入的密码不一致'
        return
      }

      isLoading.value = true

      try {
        const result = await register(
          registerForm.username,
          registerForm.password,
          registerForm.email
        )
        
        if (result.success) {
          successMessage.value = '注册成功！请登录'
          activeTab.value = 'login'
          resetForms()
        } else {
          errorMessage.value = result.error || '注册失败'
        }
      } catch (error) {
        console.error('注册错误:', error)
        errorMessage.value = '注册失败，请检查网络连接'
      } finally {
        isLoading.value = false
      }
    }


    // 重置表单
    const resetForms = () => {
      loginForm.username = ''
      loginForm.password = ''
      registerForm.username = ''
      registerForm.email = ''
      registerForm.password = ''
      registerForm.confirmPassword = ''
    }

    // 监听标签切换
    const switchTab = async (tab) => {
      console.log(`准备切换到: ${tab}表单 (当前: ${activeTab.value}表单)`)
      
      // 如果切换到相同标签，不需要处理
      if (activeTab.value === tab) return
      
      if (!loginCard.value) return
      
      // 获取当前高度
      const currentHeight = loginCard.value.offsetHeight
      console.log(`当前高度: ${currentHeight}px`)
      
      // 锁定当前高度，防止内容切换时跳变
      loginCard.value.style.height = currentHeight + 'px'
      
      // 切换内容
      activeTab.value = tab
      clearMessages()
      
      // 等待DOM更新
      await nextTick()
      
      // 测量新内容的实际高度
      loginCard.value.style.height = 'auto'
      const targetHeight = loginCard.value.scrollHeight
      
      console.log(`目标高度: ${targetHeight}px, 变化: ${targetHeight - currentHeight}px`)
      
      // 如果高度没有明显变化，直接完成
      if (Math.abs(targetHeight - currentHeight) < 10) {
        console.log('高度变化很小，直接完成')
        return
      }
      
      // 恢复起始高度，准备动画
      loginCard.value.style.height = currentHeight + 'px'
      
      // 强制重绘，确保起始状态生效
      loginCard.value.offsetHeight
      
      // 使用requestAnimationFrame确保动画触发
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          if (loginCard.value) {
            console.log(`开始动画: ${currentHeight}px → ${targetHeight}px`)
            
            // 检查transition样式是否正确应用
            const computedStyle = window.getComputedStyle(loginCard.value)
            console.log(`当前transition: ${computedStyle.transition}`)
            
            loginCard.value.style.height = targetHeight + 'px'
          }
        })
      })
      
      // 动画完成后，移除固定高度
      setTimeout(() => {
        if (loginCard.value) {
          loginCard.value.style.height = 'auto'
          console.log('动画完成，恢复自适应高度')
        }
      }, 1300) // 等待1.2s transition完成
    }

    // 组件挂载后初始化高度
    onMounted(async () => {
      // 检查用户是否已登录，如果已登录则跳转到首页
      if (isAuthenticated.value) {
        router.push('/')
        return
      }
      
      // 等待DOM完全渲染
      await nextTick()
      
      // 初始化时设置固定高度，确保后续动画能正常工作
      if (loginCard.value) {
        // 先让元素自适应高度
        loginCard.value.style.height = 'auto'
        const initialHeight = loginCard.value.scrollHeight
        
        // 设置固定高度，这样第一次切换时就能获取到正确的currentHeight
        loginCard.value.style.height = initialHeight + 'px'
        
        console.log(`初始化${activeTab.value}表单高度: ${initialHeight}px (已设置为固定高度)`)
      }
    })

    return {
      activeTab,
      isLoading,
      errorMessage,
      successMessage,
      loginForm,
      registerForm,
      loginCard,
      handleLogin,
      handleRegister,
      clearMessages,
      resetForms,
      switchTab
    }
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  width: 100vw;
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  overflow: hidden; /* 移除滚动 */
  /* 全屏背景图案 */
  background: 
    radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(120, 219, 255, 0.3) 0%, transparent 50%),
    linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 背景模糊层 */
.background-blur {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.1);
  z-index: 1;
}

.login-container {
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 2;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  overflow: hidden;
  animation: cardSlideIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  flex-direction: column;
  /* 添加高度过渡动画 - 使用!important确保不被覆盖 */
  transition: height 1.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  /* 确保高度变化时有过渡 */
  will-change: height;
  /* 设置一个合理的初始高度 */
  height: auto;
}

@keyframes cardSlideIn {
  0% {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.login-header {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: white;
  padding: 2.5rem 2rem;
  text-align: center;
  position: relative;
}

.login-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  pointer-events: none;
}

.login-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.75rem;
  font-weight: 700;
  position: relative;
  z-index: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login-header p {
  margin: 0;
  opacity: 0.95;
  font-size: 0.95rem;
  position: relative;
  z-index: 1;
  font-weight: 400;
}

.login-tabs {
  display: flex;
  background: rgba(248, 249, 250, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  position: relative;
}

.tab-button {
  flex: 1;
  padding: 1.2rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  color: rgba(0, 0, 0, 0.7);
}

.tab-button.active {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-button:hover:not(.active) {
  background: rgba(233, 236, 239, 0.8);
  color: rgba(0, 0, 0, 0.8);
}

/* 表单容器 */
.form-container {
  position: relative;
  overflow: hidden;
  flex: 1; /* 占据剩余空间 */
  display: flex;
  flex-direction: column;
}

.login-form {
  padding: 2.5rem;
  background: rgba(255, 255, 255, 0.1);
}

/* 表单切换过渡动效 */
.form-slide-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  transition-delay: 0.2s; /* 延迟让高度变化先进行 */
}

.form-slide-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.form-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.form-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.form-slide-enter-to,
.form-slide-leave-from {
  opacity: 1;
  transform: translateY(0);
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

.form-group input {
  width: 100%;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
  color: rgba(0, 0, 0, 0.8);
}

.form-group input::placeholder {
  color: rgba(0, 0, 0, 0.5);
}

.form-group input:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 
    0 0 0 3px rgba(102, 126, 234, 0.1),
    0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.form-group input:disabled {
  background: rgba(248, 249, 250, 0.6);
  cursor: not-allowed;
  opacity: 0.7;
}

.submit-button {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.submit-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.submit-button:hover:not(:disabled)::before {
  left: 100%;
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}


/* 表单内的提示信息样式 */
.form-message {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  animation: messageSlideIn 0.3s ease-out;
}

.form-message.error-message {
  background: rgba(254, 238, 238, 0.9);
  color: #dc3545;
  border: 1px solid rgba(220, 53, 69, 0.3);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.1);
}

.form-message.success-message {
  background: rgba(238, 254, 238, 0.9);
  color: #28a745;
  border: 1px solid rgba(40, 167, 69, 0.3);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.1);
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-page {
    padding: 1rem;
    height: 100vh; /* 确保移动端也是全屏 */
    width: 100vw;
  }
  
  .login-container {
    max-width: 100%;
    width: 100%;
  }
  
  .login-card {
    border-radius: 16px;
    margin: 0;
    /* 移除固定最小高度，让内容决定 */
    /* min-height: 450px; */
    /* 确保移动端也有transition - 使用!important确保不被覆盖 */
    transition: height 1.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    will-change: height;
  }
  
  .login-header {
    padding: 2rem 1.5rem;
  }
  
  .login-header h1 {
    font-size: 1.5rem;
  }
  
  .login-header p {
    font-size: 0.9rem;
  }
  
  .tab-button {
    padding: 1rem;
    font-size: 0.9rem;
  }
  
  .login-form {
    padding: 2rem 1.5rem;
  }
  
  .form-group input {
    padding: 0.9rem;
  }
  
  .submit-button {
    padding: 0.9rem;
  }
  
  .form-message {
    padding: 0.9rem;
    font-size: 0.85rem;
  }
}
</style>
