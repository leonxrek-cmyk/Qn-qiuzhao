<template>
  <div class="character-list-page">
    <!-- 页面标题和搜索框 -->
    <div class="page-header">
      <h1>探索角色</h1>
      <p>选择或搜索你感兴趣的角色开始对话</p>
      <div class="search-container">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索角色名称或标签..."
          class="search-input"
          @input="handleSearch"
        />
        <button 
          class="search-button"
          :class="{ 'clear-button': searchQuery.trim() }"
          @click="clearSearch"
          :title="searchQuery.trim() ? '清空搜索' : '搜索'"
        >
          {{ searchQuery.trim() ? '✕' : '🔍' }}
        </button>
      </div>
    </div>

    <!-- 筛选标签 -->
    <div class="filter-tags">
      <button
        v-for="tag in allTags"
        :key="tag"
        :class="['tag-button', { 
          active: selectedTags.includes(tag),
          disabled: animationLocked
        }]"
        :disabled="animationLocked"
        @click="toggleTag(tag)"
      >
        {{ tag }}
      </button>
      <button
        v-if="selectedTags.length > 0"
        class="clear-button"
        :class="{ disabled: animationLocked }"
        :disabled="animationLocked"
        @click="clearFilters"
      >
        清除筛选
      </button>
    </div>

    <!-- 角色列表 -->
    <div class="characters-grid">
      <div class="character-grid-container" :class="{ 
        'filtering': isFiltering,
        'has-characters': filteredCharacters.length > 0
      }">
        <!-- 筛选加载指示器 -->
        <div v-if="isFiltering" class="filtering-indicator">
          <div class="loading-spinner"></div>
          <p>筛选中...</p>
        </div>
        
        <div class="character-wrapper">
          <CharacterCard
            v-for="(character, index) in filteredCharacters"
            :key="character.id"
            :character="character"
            :class="[
              'character-item',
              {
                'character-hidden': isFiltering || showCharacterAtIndex < index,
                'character-visible': !isFiltering && showCharacterAtIndex >= index
              }
            ]"
            @select="selectCharacter"
          />
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredCharacters.length === 0" class="empty-state">
      <div class="empty-icon">🔍</div>
      <h3>未找到角色</h3>
      <p>请尝试使用其他关键词或标签进行搜索</p>
    </div>
  </div>
</template>

<script>
import CharacterCard from '../components/CharacterCard.vue'
import apiService from '../apiService'

export default {
  name: 'CharacterList',
  components: {
    CharacterCard
  },
  data() {
    return {
      characters: [],
      searchQuery: '',
      selectedTags: [],
      allTags: [],
      loading: true,
      isFiltering: false, // 筛选动画状态
      animationLocked: false, // 动画锁定状态
      showCharacterAtIndex: -1 // 控制卡片依次显示的索引
    }
  },
  computed: {
    // 获取所有可用标签
    uniqueTags() {
      return Array.from(this.allTags)
    },
    // 根据搜索和筛选条件过滤角色
    filteredCharacters() {
      let results = [...this.characters]
      
      // 根据搜索关键词过滤
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        results = results.filter(character => 
          character.name.toLowerCase().includes(query) ||
          character.description.toLowerCase().includes(query) ||
          character.tags.some(tag => tag.toLowerCase().includes(query))
        )
      }
      
      // 根据选择的标签过滤
      if (this.selectedTags.length > 0) {
        results = results.filter(character =>
          this.selectedTags.every(tag => character.tags.includes(tag))
        )
      }
      
      return results
    }
  },
  async mounted() {
    // 从API加载角色配置数据
    await this.loadCharacters()
    // 初始加载完成后依次显示卡片
    this.showCharactersSequentially()
  },
  methods: {
    // 从API加载角色数据
    async loadCharacters() {
      this.loading = true
      try {
        const configs = await apiService.getCharacterConfigs()
        // 提取所需的基本信息，保持向后兼容
        this.characters = configs.map(config => ({
          id: config.id,
          name: config.name,
          description: config.description,
          tags: config.tags,
          avatar: config.avatar
        }))
        // 收集所有标签
        this.collectAllTags()
      } catch (error) {
        console.error('加载角色配置失败:', error)
        // 出错时使用备用数据
        this.characters = this.getFallbackCharacters()
        this.collectAllTags()
      } finally {
        this.loading = false
      }
    },
    
    // 备用角色数据（当API调用失败时使用）
    getFallbackCharacters() {
      return [
        {
          id: 'harry-potter',
          name: '哈利·波特',
          description: '霍格沃茨魔法学校的学生，勇敢善良',
          tags: ['文学', '奇幻', '魔法'],
          avatar: '/harry-potter.png'
        },
        {
          id: 'socrates',
          name: '苏格拉底',
          description: '古希腊哲学家，西方哲学的奠基人之一',
          tags: ['哲学', '历史', '教育'],
          avatar: '/socrates.png'
        },
        {
          id: 'marie-curie',
          name: '玛丽·居里',
          description: '物理学家和化学家，首位获得两次诺贝尔奖的人',
          tags: ['科学', '历史', '教育'],
          avatar: '/marie-curie.png'
        },
        {
          id: 'albert-einstein',
          name: '阿尔伯特·爱因斯坦',
          description: '理论物理学家，相对论的创立者',
          tags: ['科学', '历史', '教育'],
          avatar: '/albert-einstein.png'
        },
        {
          id: 'leonardo-da-vinci',
          name: '列奥纳多·达·芬奇',
          description: '意大利文艺复兴时期的艺术家、科学家和发明家',
          tags: ['艺术', '科学', '历史'],
          avatar: '/leonardo-da-vinci.png'
        },
        {
          id: 'shakespeare',
          name: '威廉·莎士比亚',
          description: '英国文学史上最杰出的戏剧家和诗人',
          tags: ['文学', '艺术', '历史'],
          avatar: '/shakespeare.png'
        }
      ]
    },
    
    // 收集所有角色的标签
    collectAllTags() {
      this.characters.forEach(character => {
        character.tags.forEach(tag => {
          if (!this.allTags.includes(tag)) {
            this.allTags.push(tag)
          }
        })
      })
      this.allTags.sort()
    },
    
    // 处理搜索
    handleSearch() {
      // 可以在这里添加防抖逻辑
    },

    // 清空搜索
    clearSearch() {
      if (this.searchQuery.trim()) {
        this.searchQuery = ''
        // 触发搜索更新
        this.handleSearch()
      }
    },

    // 依次显示卡片动画
    async showCharactersSequentially() {
      this.showCharacterAtIndex = -1
      
      for (let i = 0; i < this.filteredCharacters.length; i++) {
        this.showCharacterAtIndex = i
        // 每个卡片间隔100ms显示
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
      // 所有卡片显示完成后，等待最后一个卡片的动画完成
      await new Promise(resolve => setTimeout(resolve, 400))
      
      // 动画完成后，清理will-change属性以优化性能
      this.$nextTick(() => {
        const characterItems = document.querySelectorAll('.character-item')
        characterItems.forEach(item => {
          item.style.willChange = 'auto'
        })
      })
    },
    
    // 切换标签选择
    async toggleTag(tag) {
      // 如果动画正在进行，忽略点击
      if (this.animationLocked) {
        return
      }
      
      // 锁定动画
      this.animationLocked = true
      
      try {
        // 开始筛选动画
        this.isFiltering = true
        
        // 等待卡片消失动画完成
        await new Promise(resolve => setTimeout(resolve, 350))
        
        // 更新筛选条件
        if (this.selectedTags.includes(tag)) {
          this.selectedTags = this.selectedTags.filter(t => t !== tag)
        } else {
          this.selectedTags.push(tag)
        }
        
        // 等待Vue更新DOM
        await this.$nextTick()
        
        // 结束筛选动画，开始依次显示卡片
        this.isFiltering = false
        
        // 提前解锁按钮，让用户可以继续操作
        setTimeout(() => {
          this.animationLocked = false
        }, 200)
        
        // 依次显示卡片（不阻塞按钮）
        this.showCharactersSequentially()
        
      } catch (error) {
        // 出错时立即解锁
        this.animationLocked = false
      }
    },
    
    // 清除所有筛选条件
    async clearFilters() {
      // 如果动画正在进行，忽略点击
      if (this.animationLocked) {
        return
      }
      
      // 锁定动画
      this.animationLocked = true
      
      try {
        // 开始筛选动画
        this.isFiltering = true
        
        // 等待卡片消失动画完成
        await new Promise(resolve => setTimeout(resolve, 350))
        
        // 清除筛选条件
        this.selectedTags = []
        this.searchQuery = ''
        
        // 等待Vue更新DOM
        await this.$nextTick()
        
        // 结束筛选动画，开始依次显示卡片
        this.isFiltering = false
        
        // 提前解锁按钮，让用户可以继续操作
        setTimeout(() => {
          this.animationLocked = false
        }, 200)
        
        // 依次显示卡片（不阻塞按钮）
        this.showCharactersSequentially()
        
      } catch (error) {
        // 出错时立即解锁
        this.animationLocked = false
      }
    },
    
    // 选择角色，跳转到聊天页面
    selectCharacter(character) {
      this.$router.push({
        name: 'Chat',
        params: { characterId: character.id }
      })
    }
  }
}
</script>

<style scoped>
/* 角色列表页面样式 */
.character-list-page {
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面标题和搜索 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 32px;
  margin-bottom: 8px;
  color: #333;
}

.page-header p {
  font-size: 16px;
  color: #666;
  margin-bottom: 24px;
}

.search-container {
  display: flex;
  max-width: 500px;
  margin: 0 auto;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-input {
  flex: 1;
  padding: 12px 20px;
  border: none;
  outline: none;
  font-size: 16px;
}

.search-button {
  background-color: #4c84ff;
  color: white;
  border: none;
  padding: 0 20px;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.3s ease;
  min-width: 60px;
}

.search-button:hover {
  background-color: #3a6ed8;
}

.search-button.clear-button {
  background-color: #dc3545;
  font-size: 16px;
  font-weight: bold;
}

.search-button.clear-button:hover {
  background-color: #c82333;
  transform: scale(1.05);
}

/* 筛选标签 */
.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 32px;
  justify-content: center;
  padding: 0 20px;
}

.tag-button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background-color: white;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tag-button:hover {
  border-color: #4c84ff;
  color: #4c84ff;
}

.tag-button.active {
  background-color: #4c84ff;
  color: white;
  border-color: #4c84ff;
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(76, 132, 255, 0.3);
}

.tag-button.disabled,
.clear-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
  transform: none !important;
}

.clear-button {
  padding: 8px 16px;
  border: 1px solid #ff4d4f;
  background-color: white;
  color: #ff4d4f;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-button:hover {
  background-color: #ff4d4f;
  color: white;
}

/* 角色网格 */
.characters-grid {
  margin-bottom: 40px;
}

.character-grid-container {
  position: relative;
  transition: opacity 0.35s ease;
}

.character-grid-container.has-characters {
  min-height: 200px;
}

.character-grid-container.filtering {
  opacity: 0;
}

.character-wrapper {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  /* 确保Grid容器稳定，避免高度变化导致的抖动 */
  align-items: start;
  /* 使用transform进行动画，避免影响布局 */
  transform: translateZ(0); /* 启用硬件加速 */
}

.character-item {
  /* 默认状态：占据空间但不可见 */
  opacity: 0;
  transform: translateY(20px);
  transition: none;
  /* 确保卡片始终占据Grid空间，避免布局重排 */
  visibility: visible;
  position: relative;
  /* 启用硬件加速，减少重绘 */
  transform: translateY(20px) translateZ(0);
  will-change: opacity, transform;
  /* 确保卡片有稳定的最小高度，与CharacterCard组件的高度一致 */
  min-height: 130px;
  height: 130px;
  /* 防止内容变化导致的尺寸抖动 */
  box-sizing: border-box;
}

/* 隐藏状态：占据空间但完全不可见 */
.character-item.character-hidden {
  opacity: 0;
  transform: translateY(20px) translateZ(0);
  /* 保持在文档流中，避免Grid重新计算 */
  visibility: visible;
  pointer-events: none;
  will-change: opacity, transform;
}

/* 可见状态：执行淡入动画 */
.character-item.character-visible {
  animation: fadeInUp 0.4s ease forwards;
  visibility: visible;
  pointer-events: auto;
  will-change: opacity, transform;
}

/* 筛选时的淡出效果 */
.character-grid-container.filtering .character-item {
  opacity: 0;
  transform: translateY(-10px) translateZ(0);
  transition: opacity 0.35s ease, transform 0.35s ease;
  visibility: visible;
  pointer-events: none;
  will-change: opacity, transform;
}

/* 简化的过渡动画 */
.character-fade-enter-active,
.character-fade-leave-active {
  transition: all 0.4s ease;
}

.character-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.character-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 淡入向上动画 - 优化版本，避免布局抖动 */
@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(20px) translateZ(0);
  }
  100% {
    opacity: 1;
    transform: translateY(0) translateZ(0);
  }
}

/* 筛选指示器 */
.filtering-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4c84ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.filtering-indicator p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 30px;
  background-color: white;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 20px;
  margin-bottom: 8px;
  color: #333;
}

.empty-state p {
  font-size: 14px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header h1 {
    font-size: 28px;
  }
  
  .search-container {
    max-width: 100%;
    margin: 0 20px;
  }
  
  .character-grid-container {
    grid-template-columns: 1fr;
    margin: 0 20px;
  }
  
  .characters-grid {
    margin: 0 0 40px;
  }
}
</style>