<template>
  <div class="app-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-brand">
        <h1>AI角色扮演聊天</h1>
      </div>
      <div class="navbar-menu">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/characters" class="nav-link">角色列表</router-link>
        <router-link to="/settings" class="nav-link">设置</router-link>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <p>&copy; 2025 AI角色扮演聊天 - 基于七牛云AI大模型</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
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
}

.navbar-brand h1 {
  font-size: 20px;
  color: var(--primary-color);
}

.navbar-menu {
  display: flex;
  gap: 20px;
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

/* 主内容区样式 */
.main-content {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
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
  }
  
  .main-content {
    padding: 10px;
  }
}
</style>