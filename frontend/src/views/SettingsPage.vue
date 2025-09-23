<template>
  <div class="settings-page">
    <div class="settings-header">
      <h1>设置</h1>
      <p>配置您的AI角色扮演聊天体验</p>
    </div>

    <div class="settings-content">
      <!-- 通用设置 -->
      <div class="settings-section">
        <h2>通用设置</h2>
        <div class="setting-item">
          <label class="setting-label">语言设置</label>
          <select v-model="language" class="setting-select">
            <option value="zh-CN">简体中文</option>
            <option value="en-US">English</option>
          </select>
        </div>
        <div class="setting-item">
          <label class="setting-label">主题模式</label>
          <div class="theme-options">
            <button 
              :class="['theme-button', { active: theme === 'light' }]"
              @click="setTheme('light')"
            >
              浅色
            </button>
            <button 
              :class="['theme-button', { active: theme === 'dark' }]"
              @click="setTheme('dark')"
            >
              深色
            </button>
            <button 
              :class="['theme-button', { active: theme === 'system' }]"
              @click="setTheme('system')"
            >
              跟随系统
            </button>
          </div>
        </div>
      </div>

      <!-- AI设置 -->
      <div class="settings-section">
        <h2>AI设置</h2>
        <div class="setting-item">
          <label class="setting-label">默认AI模型</label>
          <select v-model="defaultModel" class="setting-select">
            <option v-for="model in availableModels" :key="model" :value="model">
              {{ model }}
            </option>
          </select>
          <p class="setting-description">选择默认使用的AI模型，不同模型可能有不同的表现</p>
        </div>
        <div class="setting-item">
          <label class="setting-label">响应速度</label>
          <div class="speed-options">
            <label class="speed-option">
              <input type="radio" value="fast" v-model="responseSpeed" />
              <span>快速</span>
            </label>
            <label class="speed-option">
              <input type="radio" value="balanced" v-model="responseSpeed" />
              <span>平衡</span>
            </label>
            <label class="speed-option">
              <input type="radio" value="quality" v-model="responseSpeed" />
              <span>高质量</span>
            </label>
          </div>
          <p class="setting-description">调整AI响应的速度和质量平衡</p>
        </div>
        <div class="setting-item">
          <label class="setting-label">启用流式响应</label>
          <label class="toggle-switch">
            <input type="checkbox" v-model="enableStreaming" />
            <span class="toggle-slider"></span>
          </label>
          <p class="setting-description">启用后，AI回复会实时逐字显示，提供更流畅的对话体验</p>
        </div>
      </div>

      <!-- 语音设置 -->
      <div class="settings-section">
        <h2>语音设置</h2>
        <div class="setting-item">
          <label class="setting-label">自动播放语音</label>
          <label class="toggle-switch">
            <input type="checkbox" v-model="autoPlayVoice" />
            <span class="toggle-slider"></span>
          </label>
          <p class="setting-description">启用后，AI的回复会自动通过语音播放</p>
        </div>
        <div class="setting-item">
          <label class="setting-label">语音识别语言</label>
          <select v-model="speechRecognitionLanguage" class="setting-select">
            <option value="zh-CN">中文 (简体)</option>
            <option value="en-US">English (US)</option>
            <option value="ja-JP">日本語</option>
            <option value="ko-KR">한국어</option>
          </select>
          <p class="setting-description">选择语音识别的语言</p>
        </div>
        <div class="setting-item">
          <label class="setting-label">角色语音</label>
          <select v-model="characterVoice" class="setting-select">
            <option value="default">默认</option>
            <option value="male-1">男声 - 类型1</option>
            <option value="male-2">男声 - 类型2</option>
            <option value="female-1">女声 - 类型1</option>
            <option value="female-2">女声 - 类型2</option>
          </select>
          <p class="setting-description">选择角色的语音类型（实际效果取决于TTS服务）</p>
        </div>
      </div>

      <!-- 关于 -->
      <div class="settings-section">
        <h2>关于</h2>
        <div class="about-info">
          <p>AI角色扮演聊天 v1.0.0</p>
          <p>基于七牛云AI大模型开发</p>
          <p>© 2025 AI角色扮演聊天团队</p>
        </div>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="settings-footer">
      <button class="save-button" @click="saveSettings">保存设置</button>
      <button class="reset-button" @click="resetSettings">恢复默认</button>
    </div>
  </div>
</template>

<script>
import apiService from '../apiService.js'

export default {
  name: 'SettingsPage',
  data() {
    return {
      // 通用设置
      language: 'zh-CN',
      theme: 'system',
      
      // AI设置
      availableModels: ['deepseek-v3', 'gpt-3.5-turbo', 'gpt-4', 'claude-3-opus'],
      defaultModel: 'deepseek-v3',
      responseSpeed: 'balanced',
      enableStreaming: true,
      
      // 语音设置
      autoPlayVoice: true,
      speechRecognitionLanguage: 'zh-CN',
      characterVoice: 'default'
    }
  },
  mounted() {
    // 加载保存的设置
    this.loadSettings()
    
    // 获取可用的AI模型
    this.fetchAvailableModels()
  },
  methods: {
    // 加载保存的设置
    loadSettings() {
      const savedSettings = localStorage.getItem('appSettings')
      if (savedSettings) {
        try {
          const settings = JSON.parse(savedSettings)
          Object.assign(this.$data, settings)
        } catch (error) {
          console.error('加载设置失败:', error)
        }
      }
    },
    
    // 保存设置
    saveSettings() {
      try {
        const settings = {
          language: this.language,
          theme: this.theme,
          defaultModel: this.defaultModel,
          responseSpeed: this.responseSpeed,
          enableStreaming: this.enableStreaming,
          autoPlayVoice: this.autoPlayVoice,
          speechRecognitionLanguage: this.speechRecognitionLanguage,
          characterVoice: this.characterVoice
        }
        
        localStorage.setItem('appSettings', JSON.stringify(settings))
        
        // 应用主题设置
        this.applyTheme()
        
        // 显示保存成功提示
        alert('设置已保存')
      } catch (error) {
        console.error('保存设置失败:', error)
        alert('保存设置失败，请重试')
      }
    },
    
    // 恢复默认设置
    resetSettings() {
      if (confirm('确定要恢复默认设置吗？')) {
        localStorage.removeItem('appSettings')
        
        // 重置为默认值
        this.language = 'zh-CN'
        this.theme = 'system'
        this.defaultModel = 'deepseek-v3'
        this.responseSpeed = 'balanced'
        this.enableStreaming = true
        this.autoPlayVoice = true
        this.speechRecognitionLanguage = 'zh-CN'
        this.characterVoice = 'default'
        
        // 应用默认主题
        this.applyTheme()
        
        alert('已恢复默认设置')
      }
    },
    
    // 设置主题
    setTheme(theme) {
      this.theme = theme
      this.applyTheme()
    },
    
    // 应用主题
    applyTheme() {
      document.documentElement.classList.remove('dark-theme', 'light-theme')
      
      if (this.theme === 'dark') {
        document.documentElement.classList.add('dark-theme')
      } else if (this.theme === 'light') {
        document.documentElement.classList.add('light-theme')
      } else {
        // 跟随系统
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
          document.documentElement.classList.add('dark-theme')
        } else {
          document.documentElement.classList.add('light-theme')
        }
      }
    },
    
    // 获取可用的AI模型
    async fetchAvailableModels() {
      try {
        const response = await apiService.getModels()
        if (response.models && response.models.length > 0) {
          this.availableModels = response.models
        }
      } catch (error) {
        console.error('获取模型列表失败:', error)
        // 使用默认模型列表
      }
    }
  }
}
</script>

<style scoped>
/* 设置页面样式 */
.settings-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

/* 页面头部 */
.settings-header {
  text-align: center;
  margin-bottom: 40px;
}

.settings-header h1 {
  font-size: 32px;
  margin-bottom: 8px;
  color: #333;
}

.settings-header p {
  font-size: 16px;
  color: #666;
}

/* 设置内容 */
.settings-content {
  margin-bottom: 40px;
}

/* 设置区域 */
.settings-section {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.settings-section h2 {
  font-size: 20px;
  margin-bottom: 20px;
  color: #333;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 12px;
}

/* 设置项 */
.setting-item {
  margin-bottom: 20px;
}

.setting-label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
  font-size: 16px;
}

/* 选择框 */
.setting-select {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.setting-select:focus {
  outline: none;
  border-color: #4c84ff;
}

/* 设置描述 */
.setting-description {
  font-size: 14px;
  color: #666;
  margin-top: 8px;
  margin-bottom: 0;
}

/* 主题选项 */
.theme-options {
  display: flex;
  gap: 12px;
}

.theme-button {
  padding: 8px 20px;
  border: 1px solid #ddd;
  background-color: white;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.theme-button:hover {
  border-color: #4c84ff;
  color: #4c84ff;
}

.theme-button.active {
  background-color: #4c84ff;
  color: white;
  border-color: #4c84ff;
}

/* 速度选项 */
.speed-options {
  display: flex;
  gap: 24px;
}

.speed-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.speed-option input[type="radio"] {
  cursor: pointer;
}

.speed-option span {
  font-size: 16px;
  color: #333;
}

/* 开关按钮 */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 30px;
  cursor: pointer;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 30px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #4c84ff;
}

input:focus + .toggle-slider {
  box-shadow: 0 0 1px #4c84ff;
}

input:checked + .toggle-slider:before {
  transform: translateX(30px);
}

/* 关于信息 */
.about-info {
  text-align: center;
  padding: 20px;
  color: #666;
  line-height: 1.8;
}

.about-info p {
  margin-bottom: 8px;
}

/* 底部按钮 */
.settings-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 40px;
}

.save-button,
.reset-button {
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.save-button {
  background-color: #4c84ff;
  color: white;
}

.save-button:hover {
  background-color: #3a6ed8;
  transform: translateY(-1px);
}

.reset-button {
  background-color: white;
  color: #666;
  border: 1px solid #ddd;
}

.reset-button:hover {
  background-color: #f5f5f5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-page {
    padding: 16px;
  }
  
  .settings-header h1 {
    font-size: 28px;
  }
  
  .settings-section {
    padding: 20px;
  }
  
  .theme-options,
  .speed-options {
    flex-direction: column;
    gap: 8px;
  }
  
  .settings-footer {
    flex-direction: column;
  }
  
  .save-button,
  .reset-button {
    width: 100%;
  }
}
</style>