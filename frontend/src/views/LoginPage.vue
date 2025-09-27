<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1>AI角色扮演聊天系统</h1>
          <p>登录以保存您的对话历史和个人设置</p>
        </div>

        <div class="login-tabs">
          <button 
            class="tab-button" 
            :class="{ active: activeTab === 'login' }"
            @click="activeTab = 'login'"
          >
            登录
          </button>
          <button 
            class="tab-button" 
            :class="{ active: activeTab === 'register' }"
            @click="activeTab = 'register'"
          >
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="login-form">
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
        </form>

        <!-- 注册表单 -->
        <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="login-form">
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
        </form>

        <div class="login-footer">
          <button class="guest-button" @click="continueAsGuest" :disabled="isLoading">
            以游客身份继续
          </button>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <!-- 成功提示 -->
        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import apiService from '../apiService.js'

export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter()
    const { login, register } = useAuth()
    
    const activeTab = ref('login')
    const isLoading = ref(false)
    const errorMessage = ref('')
    const successMessage = ref('')
    
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

    // 继续作为游客
    const continueAsGuest = () => {
      // 清除可能存在的认证信息
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_info')
      
      // 跳转到主页
      router.push('/')
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

    return {
      activeTab,
      isLoading,
      errorMessage,
      successMessage,
      loginForm,
      registerForm,
      handleLogin,
      handleRegister,
      continueAsGuest,
      clearMessages,
      resetForms
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.login-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.login-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  opacity: 0.9;
  font-size: 0.9rem;
}

.login-tabs {
  display: flex;
  background: #f8f9fa;
}

.tab-button {
  flex: 1;
  padding: 1rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.tab-button.active {
  background: white;
  color: #667eea;
  font-weight: 600;
}

.tab-button:hover:not(.active) {
  background: #e9ecef;
}

.login-form {
  padding: 2rem;
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
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.submit-button {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.submit-button:hover:not(:disabled) {
  opacity: 0.9;
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-footer {
  padding: 1rem 2rem 2rem;
  text-align: center;
}

.guest-button {
  color: #666;
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: underline;
  font-size: 0.9rem;
}

.guest-button:hover:not(:disabled) {
  color: #333;
}

.error-message {
  margin: 1rem 2rem;
  padding: 0.75rem;
  background: #fee;
  color: #c33;
  border: 1px solid #fcc;
  border-radius: 6px;
  font-size: 0.9rem;
}

.success-message {
  margin: 1rem 2rem;
  padding: 0.75rem;
  background: #efe;
  color: #363;
  border: 1px solid #cfc;
  border-radius: 6px;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-page {
    padding: 1rem;
  }
  
  .login-header {
    padding: 1.5rem;
  }
  
  .login-header h1 {
    font-size: 1.25rem;
  }
  
  .login-form {
    padding: 1.5rem;
  }
}
</style>
