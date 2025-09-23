<template>
  <div class="home-page">
    <!-- 欢迎部分 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1>与历史名人、文学角色实时对话</h1>
        <p>通过AI技术，让你能够与任何你感兴趣的角色进行真实的语音聊天体验</p>
        <div class="hero-actions">
          <router-link to="/characters" class="btn-primary">浏览角色</router-link>
          <router-link to="/chat" class="btn-secondary">开始聊天</router-link>
        </div>
      </div>
    </section>

    <!-- 特色部分 -->
    <section class="features-section">
      <h2>为什么选择我们</h2>
      <div class="features-grid">
        <div class="feature-item">
          <div class="feature-icon">👥</div>
          <h3>丰富的角色库</h3>
          <p>包含历史人物、文学角色、科学家等多种类型的角色供你选择</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">💬</div>
          <h3>自然对话体验</h3>
          <p>基于先进的七牛云AI大模型，提供流畅自然的对话体验</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🎙️</div>
          <h3>语音交互</h3>
          <p>支持语音输入和语音输出，让对话更加便捷自然</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">⚡</div>
          <h3>实时响应</h3>
          <p>流式传输技术，让你感受到实时的对话反馈</p>
        </div>
      </div>
    </section>

    <!-- 热门角色 -->
    <section class="popular-characters">
      <h2>热门角色</h2>
      <div class="characters-container">
        <CharacterCard
          v-for="character in popularCharacters"
          :key="character.id"
          :character="character"
          @select="selectCharacter"
        />
      </div>
      <div class="view-more">
        <router-link to="/characters">查看更多角色 →</router-link>
      </div>
    </section>

    <!-- 使用说明 -->
    <section class="how-it-works">
      <h2>如何使用</h2>
      <div class="steps-container">
        <div class="step-item">
          <div class="step-number">1</div>
          <h3>选择角色</h3>
          <p>从角色列表中选择你感兴趣的角色，或搜索特定角色</p>
        </div>
        <div class="step-item">
          <div class="step-number">2</div>
          <h3>开始对话</h3>
          <p>通过文字或语音与角色进行交流，提出你的问题</p>
        </div>
        <div class="step-item">
          <div class="step-number">3</div>
          <h3>获得回复</h3>
          <p>角色会以符合其身份的方式回你的问题</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import CharacterCard from '../components/CharacterCard.vue'
import apiService from '../apiService'

export default {
  name: 'HomePage',
  components: {
    CharacterCard
  },
  data() {
    return {
      popularCharacters: []
    }
  },
  async mounted() {
    try {
      // 加载热门角色（使用apiService获取角色数据，并取前4个作为热门角色）
      const configs = await apiService.getCharacterConfigs()
      this.popularCharacters = configs.slice(0, 4)
    } catch (error) {
      console.error('加载热门角色失败:', error)
    }
  },
  methods: {
    selectCharacter(character) {
      // 跳转到与该角色的聊天页面
      this.$router.push({
        name: 'Chat',
        params: { characterId: character.id }
      })
    }
  }
}
</script>

<style scoped>
/* 首页样式 */
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}

/* 英雄区域 */
.hero-section {
  background: linear-gradient(135deg, #4c84ff 0%, #7a5cf0 100%);
  color: white;
  border-radius: 16px;
  padding: 80px 40px;
  margin-bottom: 40px;
  text-align: center;
}

.hero-content h1 {
  font-size: 36px;
  margin-bottom: 16px;
  font-weight: 700;
}

.hero-content p {
  font-size: 18px;
  margin-bottom: 32px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background-color: white;
  color: #4c84ff;
}

.btn-primary:hover {
  background-color: #f0f0f0;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* 特色区域 */
.features-section {
  margin-bottom: 60px;
  text-align: center;
}

.features-section h2 {
  font-size: 28px;
  margin-bottom: 32px;
  color: #333;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.feature-item {
  background-color: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.feature-item h3 {
  font-size: 20px;
  margin-bottom: 12px;
  color: #333;
}

.feature-item p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

/* 热门角色区域 */
.popular-characters {
  margin-bottom: 60px;
}

.popular-characters h2 {
  font-size: 28px;
  margin-bottom: 24px;
  color: #333;
  text-align: center;
}

.characters-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.view-more {
  text-align: center;
}

.view-more a {
  color: #4c84ff;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.view-more a:hover {
  color: #3a6ed8;
  text-decoration: underline;
}

/* 使用说明区域 */
.how-it-works {
  background-color: white;
  padding: 60px 40px;
  border-radius: 16px;
  text-align: center;
}

.how-it-works h2 {
  font-size: 28px;
  margin-bottom: 32px;
  color: #333;
}

.steps-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 32px;
  max-width: 900px;
  margin: 0 auto;
}

.step-item {
  position: relative;
  padding: 0 20px;
}

.step-number {
  width: 60px;
  height: 60px;
  background-color: #4c84ff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  margin: 0 auto 20px;
}

.step-item h3 {
  font-size: 20px;
  margin-bottom: 12px;
  color: #333;
}

.step-item p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-section {
    padding: 60px 20px;
  }
  
  .hero-content h1 {
    font-size: 28px;
  }
  
  .hero-content p {
    font-size: 16px;
  }
  
  .features-section h2,
  .popular-characters h2,
  .how-it-works h2 {
    font-size: 24px;
  }
  
  .steps-container {
    gap: 24px;
  }
}
</style>