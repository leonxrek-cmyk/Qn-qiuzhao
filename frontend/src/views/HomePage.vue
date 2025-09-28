<template>
  <div class="home-page">

    <!-- 欢迎部分 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1>与历史名人、文学角色实时对话</h1>
        <p>通过AI技术，让你能够与任何你感兴趣的角色进行真实的对话体验</p>
        <div class="hero-actions">
          <router-link to="/characters" class="btn-primary">浏览角色</router-link>
          <router-link to="/characters" class="btn-secondary">开始聊天</router-link>
        </div>
      </div>
    </section>

    <!-- 特色部分 -->
    <section class="features-section">
      <h2>为什么选择我们</h2>
      <div class="features-carousel">
        <div class="carousel-container">
          <div class="carousel-track" ref="carouselTrack">
            <!-- 克隆的最后4个卡片（用于无缝循环） -->
            <div class="feature-item clone">
              <div class="feature-icon">🎨</div>
              <h3>个性化定制</h3>
              <p>根据用户喜好定制专属的对话风格和角色特性</p>
            </div>
            <div class="feature-item clone">
              <div class="feature-icon">📱</div>
              <h3>跨平台同步</h3>
              <p>支持多设备同步，随时随地继续你的对话</p>
            </div>
            <div class="feature-item clone">
              <div class="feature-icon">🚀</div>
              <h3>持续更新</h3>
              <p>定期更新角色库和功能，带来全新的体验</p>
            </div>
            <div class="feature-item clone">
              <div class="feature-icon">💡</div>
              <h3>智能推荐</h3>
              <p>基于用户兴趣智能推荐合适的角色和话题</p>
            </div>
            
            <!-- 原始卡片 -->
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
            <div class="feature-item">
              <div class="feature-icon">💖</div>
              <h3>亲密度系统</h3>
              <p>与角色建立深度连接，解锁不同层次的交流体验</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <h3>个人中心</h3>
              <p>查看亲密度排行、管理对话历史，追踪你的成长轨迹</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🔒</div>
              <h3>隐私保护</h3>
              <p>严格保护用户隐私，对话数据安全加密存储</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🌍</div>
              <h3>多语言支持</h3>
              <p>支持多种语言交流，打破语言障碍</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🎨</div>
              <h3>个性化定制</h3>
              <p>根据用户喜好定制专属的对话风格和角色特性</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📱</div>
              <h3>跨平台同步</h3>
              <p>支持多设备同步，随时随地继续你的对话</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🚀</div>
              <h3>持续更新</h3>
              <p>定期更新角色库和功能，带来全新的体验</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">💡</div>
              <h3>智能推荐</h3>
              <p>基于用户兴趣智能推荐合适的角色和话题</p>
            </div>
            
            <!-- 克隆的前4个卡片（用于无缝循环） -->
            <div class="feature-item clone">
              <div class="feature-icon">👥</div>
              <h3>丰富的角色库</h3>
              <p>包含历史人物、文学角色、科学家等多种类型的角色供你选择</p>
            </div>
            <div class="feature-item clone">
              <div class="feature-icon">💬</div>
              <h3>自然对话体验</h3>
              <p>基于先进的七牛云AI大模型，提供流畅自然的对话体验</p>
            </div>
            <div class="feature-item clone">
              <div class="feature-icon">🎙️</div>
              <h3>语音交互</h3>
              <p>支持语音输入和语音输出，让对话更加便捷自然</p>
            </div>
            <div class="feature-item clone">
              <div class="feature-icon">⚡</div>
              <h3>实时响应</h3>
              <p>流式传输技术，让你感受到实时的对话反馈</p>
            </div>
          </div>
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
      <div class="steps-flow">
        <!-- 使用网格布局 -->
        <div class="steps-grid">
          <!-- 第一行 -->
          <div class="step-item" style="grid-area: step1;">
            <div class="step-number">1</div>
            <h3>注册登录</h3>
            <p>创建账户或登录，享受完整功能体验</p>
          </div>
          
          <div class="arrow-horizontal" style="grid-area: arrow1;">
            <svg viewBox="0 0 120 40" class="arrow-svg">
              <defs>
                <marker id="arrowhead1" markerWidth="10" markerHeight="7" 
                        refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#4c84ff" />
                </marker>
              </defs>
              <line x1="10" y1="20" x2="110" y2="20" 
                    stroke="#4c84ff" stroke-width="2" 
                    stroke-dasharray="5,5" marker-end="url(#arrowhead1)" />
            </svg>
          </div>
          
          <div class="step-item" style="grid-area: step2;">
            <div class="step-number">2</div>
            <h3>选择角色</h3>
            <p>从丰富的角色库中选择你感兴趣的历史人物或文学角色</p>
          </div>
          
          <div class="arrow-horizontal" style="grid-area: arrow2;">
            <svg viewBox="0 0 120 40" class="arrow-svg">
              <defs>
                <marker id="arrowhead2" markerWidth="10" markerHeight="7" 
                        refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#4c84ff" />
                </marker>
              </defs>
              <line x1="10" y1="20" x2="110" y2="20" 
                    stroke="#4c84ff" stroke-width="2" 
                    stroke-dasharray="5,5" marker-end="url(#arrowhead2)" />
            </svg>
          </div>
          
          <div class="step-item" style="grid-area: step3;">
            <div class="step-number">3</div>
            <h3>开始对话</h3>
            <p>通过文字或语音与角色进行深度交流，探索他们的思想世界</p>
          </div>
          
          
          <!-- 第二行 -->
          <div class="step-item" style="grid-area: step4;">
            <div class="step-number">4</div>
            <h3>建立亲密度</h3>
            <p>每次成功对话都会增加亲密度，解锁更深层的交流体验</p>
          </div>
          
          <div class="arrow-horizontal" style="grid-area: arrow4;">
            <svg viewBox="0 0 120 40" class="arrow-svg">
              <defs>
                <marker id="arrowhead4" markerWidth="10" markerHeight="7" 
                        refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#4c84ff" />
                </marker>
              </defs>
              <line x1="10" y1="20" x2="110" y2="20" 
                    stroke="#4c84ff" stroke-width="2" 
                    stroke-dasharray="5,5" marker-end="url(#arrowhead4)" />
            </svg>
          </div>
          
          <div class="step-item" style="grid-area: step5;">
            <div class="step-number">5</div>
            <h3>查看排行</h3>
            <p>在个人中心查看亲密度排行，追踪与各角色的关系进展</p>
          </div>
          
          <div class="arrow-horizontal" style="grid-area: arrow5;">
            <svg viewBox="0 0 120 40" class="arrow-svg">
              <defs>
                <marker id="arrowhead5" markerWidth="10" markerHeight="7" 
                        refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#4c84ff" />
                </marker>
              </defs>
              <line x1="10" y1="20" x2="110" y2="20" 
                    stroke="#4c84ff" stroke-width="2" 
                    stroke-dasharray="5,5" marker-end="url(#arrowhead5)" />
            </svg>
          </div>
          
          <div class="step-item" style="grid-area: step6;">
            <div class="step-number">6</div>
            <h3>管理历史</h3>
            <p>随时查看对话历史，继续之前的精彩对话</p>
          </div>
          
        </div>
      </div>
    </section>

    <!-- 亲密度系统介绍 -->
    <section class="intimacy-system">
      <h2>💖 亲密度系统</h2>
      <div class="intimacy-content">
        <div class="intimacy-description">
          <div class="title-with-tooltip">
            <h3>与角色建立深度连接</h3>
            <div class="tooltip-container">
              <span class="question-mark">?</span>
              <div class="tooltip-content">
                <h4>深度连接的含义</h4>
                <p>当达成不同亲密度时，您可以解锁以下特殊体验：</p>
                <ul>
                  <li>🌟 <strong>个性化问候</strong>：角色会亲切地问候您，询问您最近如何、心情怎么样</li>
                  <li>💬 <strong>记忆延续</strong>：角色会记住之前的对话内容，让交流更加连贯</li>
                  <li>🎭 <strong>情感共鸣</strong>：根据亲密度等级，角色会展现不同的情感表达方式</li>
                  <li>🔓 <strong>深层话题</strong>：解锁更私密、更深入的对话主题和内容</li>
                </ul>
              </div>
            </div>
          </div>
          <p>每次成功的对话都会增加你与角色的亲密度，随着关系的深入，你将体验到不同层次的交流：</p>
        </div>
        <div class="intimacy-levels">
          <div class="level-item">
            <div class="level-badge-container">
              <div class="level-badge level-1">1</div>
              <div class="emoji-hover">👋</div>
            </div>
            <span class="level-name">初次相识</span>
          </div>
          <div class="level-arrow">→</div>
          <div class="level-item">
            <div class="level-badge-container">
              <div class="level-badge level-5">5</div>
              <div class="emoji-hover">🔥</div>
            </div>
            <span class="level-name">聊得火热</span>
          </div>
          <div class="level-arrow">→</div>
          <div class="level-item">
            <div class="level-badge-container">
              <div class="level-badge level-10">10</div>
              <div class="emoji-hover">💫</div>
            </div>
            <span class="level-name">相见恨晚</span>
          </div>
          <div class="level-arrow">→</div>
          <div class="level-item">
            <div class="level-badge-container">
              <div class="level-badge level-20">20</div>
              <div class="emoji-hover">💕</div>
            </div>
            <span class="level-name">亲密无间</span>
          </div>
          <div class="level-arrow">→</div>
          <div class="level-item">
            <div class="level-badge-container">
              <div class="level-badge level-50">50</div>
              <div class="emoji-hover">🎵</div>
            </div>
            <span class="level-name">知音难觅</span>
          </div>
          <div class="level-arrow">→</div>
          <div class="level-item">
            <div class="level-badge-container">
              <div class="level-badge level-100">100</div>
              <div class="emoji-hover">👑</div>
            </div>
            <span class="level-name">伯乐</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import CharacterCard from '../components/CharacterCard.vue'
import apiService from '../apiService'
import { useRouter } from 'vue-router'

export default {
  name: 'HomePage',
  components: {
    CharacterCard
  },
  setup() {
    const router = useRouter()
    const popularCharacters = ref([])
    const carouselTrack = ref(null)
    const currentSlide = ref(0)
    const totalSlides = 3
    let carouselInterval = null

    // 加载热门角色
    const loadPopularCharacters = async () => {
      try {
        const configs = await apiService.getCharacterConfigs()
        // 按角色名称首字母排序，然后取前6个
        const sortedConfigs = configs.sort((a, b) => {
          return a.name.localeCompare(b.name, 'zh-CN', { sensitivity: 'base' })
        })
        popularCharacters.value = sortedConfigs.slice(0, 6)
      } catch (error) {
        console.error('加载角色数据失败:', error)
        popularCharacters.value = []
      }
    }

    // 选择角色
    const selectCharacter = (character) => {
      router.push({
        name: 'Chat',
        params: { characterId: character.id }
      })
    }

    // 更新卡片透明度的函数
    const updateCardOpacity = () => {
      if (!carouselTrack.value) return
      
      const cards = carouselTrack.value.querySelectorAll('.feature-item')
      const viewportWidth = window.innerWidth
      const viewportCenter = viewportWidth / 2
      
      // 定义渐变参数，基于视口宽度
      const fullVisibleDistance = Math.min(600, viewportWidth * 0.35) // 完全可见的距离范围，最大600px
      const fadeDistance = Math.min(400, viewportWidth * 0.25) // 渐变距离，最大400px
      
      cards.forEach(card => {
        const cardRect = card.getBoundingClientRect()
        const cardCenter = cardRect.left + cardRect.width / 2
        const distanceFromCenter = Math.abs(cardCenter - viewportCenter)
        
        let opacity = 1
        
        // 如果距离视口中心超过完全可见范围，开始渐隐
        if (distanceFromCenter > fullVisibleDistance) {
          const fadeProgress = (distanceFromCenter - fullVisibleDistance) / fadeDistance
          // 使用更平滑的缓动函数
          const clampedProgress = Math.min(1, Math.max(0, fadeProgress))
          const smoothProgress = 1 - Math.pow(1 - clampedProgress, 2) // 二次缓动，更柔和
          opacity = Math.max(0, 1 - smoothProgress)
        }
        
        card.style.opacity = opacity
        card.style.transition = 'opacity 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94), transform 0.3s ease, box-shadow 0.3s ease'
      })
    }

    // 轮播功能 - JavaScript控制的无缝循环
    const initCarousel = () => {
      try {
        console.log('轮播组件已初始化，使用JavaScript控制')
        if (carouselTrack.value) {
          console.log('轮播轨道元素已找到，开始JavaScript动画')
          
          // 检测是否为移动端
          const isMobile = window.innerWidth <= 768
          const cardWidth = isMobile ? 276 : 304 // 移动端276px，桌面端304px
          
          let currentOffset = -4 * cardWidth // 初始偏移量（跳过前4个克隆卡片）
          let isHovered = false
          
          // 监听鼠标悬停事件
          const carouselContainer = carouselTrack.value.parentElement.parentElement
          carouselContainer.addEventListener('mouseenter', () => {
            isHovered = true
          })
          carouselContainer.addEventListener('mouseleave', () => {
            isHovered = false
          })
          
          // 平滑滚动函数
          const smoothScroll = () => {
            if (!isHovered && carouselTrack.value) {
              currentOffset -= 2 // 每次移动2px，增加滚动速度
              
              // 检查是否需要重置位置（无缝循环）
              if (currentOffset <= -16 * cardWidth) { // 当移动到最后4个克隆卡片时
                // 瞬间重置到初始位置，创建无缝循环效果
                carouselTrack.value.style.transition = 'none'
                currentOffset = -4 * cardWidth
                carouselTrack.value.style.transform = `translateX(${currentOffset}px)`
                
                // 强制重绘
                carouselTrack.value.offsetHeight
                
                // 恢复过渡动画
                setTimeout(() => {
                  if (carouselTrack.value) {
                    carouselTrack.value.style.transition = 'transform 0.1s linear'
                  }
                }, 10)
              } else {
                carouselTrack.value.style.transform = `translateX(${currentOffset}px)`
              }
            }
          }
          
          // 启动滚动动画
          const scrollInterval = setInterval(smoothScroll, 50) // 每50ms移动一次
          
          // 启动透明度更新
          const updateInterval = setInterval(updateCardOpacity, 100)
          
          // 存储定时器ID以便清理
          carouselTrack.value._scrollInterval = scrollInterval
          carouselTrack.value._opacityInterval = updateInterval
        } else {
          console.error('轮播轨道元素未找到')
        }
      } catch (error) {
        console.error('轮播初始化错误:', error)
      }
    }

    onMounted(() => {
      loadPopularCharacters()
      // 初始化轮播
      setTimeout(() => {
        initCarousel()
      }, 200)
    })

    onUnmounted(() => {
      // 清理所有定时器
      if (carouselTrack.value) {
        if (carouselTrack.value._scrollInterval) {
          clearInterval(carouselTrack.value._scrollInterval)
        }
        if (carouselTrack.value._opacityInterval) {
          clearInterval(carouselTrack.value._opacityInterval)
        }
      }
    })

    return {
      // 数据
      popularCharacters,
      carouselTrack,
      
      // 方法
      selectCharacter
    }
  }
}
</script>

<style scoped>
/* 首页样式 */
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  overflow-x: hidden; /* 禁止水平滚动 */
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

/* 轮播容器 */
.features-carousel {
  position: relative;
  width: 100%; /* 移除宽度限制，让轮播占满整个屏幕宽度 */
  margin: 0;
  padding: 60px 0; /* 进一步增加上下内边距，确保阴影和特效不被遮挡 */
}

.carousel-container {
  overflow: visible; /* 允许阴影和特效完全显示 */
  padding: 0; /* 移除内边距限制 */
  margin: 0; /* 移除负边距 */
  position: relative;
  width: 100%; /* 占满整个宽度 */
}

/* 移除遮罩层，直接通过卡片透明度控制渐隐渐显 */

.carousel-track {
  display: flex;
  /* 总共20个卡片：4个克隆 + 12个原始 + 4个克隆 */
  width: calc(20 * 304px); /* 每个卡片304px宽度（包含间距） */
  /* 使用JavaScript控制的平滑动画 */
  transition: transform 0.1s linear;
  /* 初始位置偏移，跳过前4个克隆卡片 */
  transform: translateX(calc(-4 * 304px));
}

.carousel-track .feature-item {
  flex: 0 0 280px; /* 固定宽度，保持现有卡片大小 */
  margin: 0 12px; /* 左右间距 */
}

/* 悬停时暂停动画 */
.features-carousel:hover .carousel-track {
  transition: transform 0.3s ease;
}

.feature-item {
  background-color: white;
  padding: 32px;
  border-radius: 16px; /* 增加卡片圆角，与容器协调 */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease, opacity 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.8); /* 轻微的边框增强层次 */
  position: relative; /* 确保z-index生效 */
  opacity: 1; /* 默认完全可见 */
}

.feature-item:hover {
  transform: translateY(-12px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  z-index: 20; /* 提高z-index，确保悬停的卡片在遮罩之上 */
  position: relative; /* 确保z-index生效 */
}

/* 确保悬停效果不被裁剪 */
.carousel-track .feature-item {
  position: relative;
  /* 增加额外的边距确保阴影空间 */
  margin-top: 20px;
  margin-bottom: 20px;
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

/* 步骤流程容器 */
.steps-flow {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.steps-grid {
  display: grid;
  grid-template-columns: 1fr 120px 1fr 120px 1fr;
  grid-template-rows: auto 40px auto;
  grid-template-areas: 
    "step1 arrow1 step2 arrow2 step3"
    ". . . . ."
    "step4 arrow4 step5 arrow5 step6";
  gap: 20px;
  justify-items: center;
  align-items: center;
}


.step-item {
  position: relative;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  min-width: 220px;
  max-width: 240px;
  text-align: center;
}

.step-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
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

/* 水平箭头 */
.arrow-horizontal {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
  height: 40px;
}

.arrow-horizontal .arrow-svg {
  width: 120px;
  height: 40px;
}

/* 垂直箭头 */
.arrow-vertical {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 120px;
}

.arrow-vertical .arrow-svg {
  width: 40px;
  height: 120px;
}

/* 返回箭头 */
.arrow-back {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 300px;
  height: 40px;
}

.arrow-back .arrow-svg {
  width: 300px;
  height: 40px;
}

/* 亲密度系统介绍 */
.intimacy-system {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
  color: white;
  padding: 60px 40px;
  border-radius: 16px;
  margin-top: 40px;
  text-align: center;
}

.intimacy-system h2 {
  font-size: 28px;
  margin-bottom: 32px;
}

.intimacy-content {
  max-width: 1000px;
  margin: 0 auto;
}

.intimacy-description h3 {
  font-size: 22px;
  margin-bottom: 16px;
}

/* 标题与提示框容器 */
.title-with-tooltip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
  text-align: center;
}

.title-with-tooltip h3 {
  margin-bottom: 0;
}

/* 问号标识 */
.tooltip-container {
  position: relative;
  display: inline-block;
}

.question-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
  color: white;
  cursor: help;
  transition: all 0.3s ease;
}

.question-mark:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* 提示框内容 */
.tooltip-content {
  position: absolute;
  top: 50%;
  left: 100%;
  margin-left: 12px;
  transform: translateY(-50%) translateX(-10px);
  width: 480px;
  background: white;
  color: #333;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  z-index: 1000;
}

.tooltip-container:hover .tooltip-content {
  opacity: 1;
  visibility: visible;
  transform: translateY(-50%) translateX(0);
}

.tooltip-content h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.tooltip-content p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.5;
}

.tooltip-content ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.tooltip-content li {
  margin-bottom: 8px;
  font-size: 13px;
  line-height: 1.4;
  color: #374151;
  display: flex;
  align-items: flex-start;
  gap: 6px;
  white-space: nowrap;
}

.tooltip-content li:last-child {
  margin-bottom: 0;
}

.tooltip-content strong {
  color: #1f2937;
}

/* 提示框箭头 */
.tooltip-content::before {
  content: '';
  position: absolute;
  top: 50%;
  left: -6px;
  transform: translateY(-50%) rotate(45deg);
  width: 12px;
  height: 12px;
  background: white;
  box-shadow: -2px -2px 4px rgba(0, 0, 0, 0.1);
}

.intimacy-description p {
  font-size: 16px;
  margin-bottom: 40px;
  opacity: 0.9;
}

.intimacy-levels {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.level-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 80px;
}

.level-badge-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.level-badge {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.level-badge.level-1 {
  background: linear-gradient(135deg, #94a3b8, #cbd5e1);
}

.level-badge.level-5 {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.level-badge.level-10 {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.level-badge.level-20 {
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
}

.level-badge.level-50 {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.level-badge.level-100 {
  background: linear-gradient(135deg, #ef4444, #f87171);
}

/* Emoji悬停效果 */
.emoji-hover {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 24px;
  opacity: 0;
  transition: all 0.3s ease;
  pointer-events: none;
  z-index: 10;
}

.level-badge-container:hover .emoji-hover {
  opacity: 1;
  transform: translateX(-50%) translateY(-5px);
}

.level-badge-container:hover .level-badge {
  transform: scale(1.1);
  transition: transform 0.3s ease;
}

.level-badge {
  transition: transform 0.3s ease;
}

.level-name {
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  opacity: 0.9;
}

.level-arrow {
  color: rgba(255, 255, 255, 0.7);
  font-size: 20px;
  font-weight: bold;
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
  .how-it-works h2,
  .intimacy-system h2 {
    font-size: 24px;
  }
  
  /* 移动端轮播适配 */
  .features-carousel {
    width: 100vw; /* 移动端占满整个视口宽度 */
    padding: 50px 0; /* 移动端也增加上下空间 */
    margin: 0; /* 移除边距限制 */
  }
  
  .carousel-container {
    overflow: visible; /* 移动端也允许阴影完全显示 */
    padding: 0; /* 移除内边距限制 */
    margin: 0; /* 移除负边距 */
    position: relative;
    width: 100%; /* 占满整个宽度 */
  }

  /* 移动端也移除遮罩，直接使用卡片透明度控制 */
  
  .carousel-track {
    /* 移动端使用更小的卡片宽度重新计算 */
    width: calc(20 * 276px); /* 260px卡片 + 16px间距 */
    /* 移动端也使用JavaScript控制 */
    transition: transform 0.1s linear;
    /* 移动端初始位置偏移 */
    transform: translateX(calc(-4 * 276px));
  }
  
  .carousel-track .feature-item {
    flex: 0 0 260px; /* 移动端稍微减小卡片宽度 */
    margin: 0 8px;
  }
  
  .feature-item {
    padding: 24px 20px;
  }
  
  .feature-icon {
    font-size: 36px;
  }
  
  .feature-item h3 {
    font-size: 18px;
  }
  
  .feature-item p {
    font-size: 14px;
  }
  
  
  
  .steps-flow {
    padding: 10px;
  }
  
  .steps-grid {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .arrow-horizontal {
    transform: rotate(90deg);
    min-width: 40px;
    height: 60px;
  }
  
  .arrow-horizontal .arrow-svg {
    width: 40px;
    height: 60px;
  }
  
  .arrow-vertical {
    transform: rotate(0deg);
    width: 40px;
    height: 60px;
  }
  
  .arrow-vertical .arrow-svg {
    width: 40px;
    height: 60px;
  }
  
  .arrow-back {
    transform: rotate(90deg);
    width: 40px;
    height: 60px;
  }
  
  .arrow-back .arrow-svg {
    width: 40px;
    height: 60px;
  }
  
  
  .intimacy-system {
    padding: 40px 20px;
  }
  
  /* 移动端提示框适配 */
  .tooltip-content {
    width: 320px;
    left: auto;
    right: 100%;
    margin-left: 0;
    margin-right: 12px;
    padding: 16px;
  }
  
  .tooltip-content::before {
    left: auto;
    right: -6px;
    transform: translateY(-50%) rotate(45deg);
  }
  
  .intimacy-levels {
    flex-direction: column;
    gap: 20px;
  }
  
  .level-item {
    flex-direction: row;
    gap: 12px;
    min-width: auto;
  }
  
  .level-arrow {
    transform: rotate(90deg);
    margin: 8px 0;
  }
}
</style>