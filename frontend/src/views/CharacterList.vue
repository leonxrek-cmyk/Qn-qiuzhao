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
        <button class="search-button">🔍</button>
      </div>
    </div>

    <!-- 筛选标签 -->
    <div class="filter-tags">
      <button
        v-for="tag in allTags"
        :key="tag"
        :class="['tag-button', { active: selectedTags.includes(tag) }]"
        @click="toggleTag(tag)"
      >
        {{ tag }}
      </button>
      <button
        v-if="selectedTags.length > 0"
        class="clear-button"
        @click="clearFilters"
      >
        清除筛选
      </button>
    </div>

    <!-- 角色列表 -->
    <div class="characters-grid">
      <CharacterCard
        v-for="character in filteredCharacters"
        :key="character.id"
        :character="character"
        @select="selectCharacter"
      />
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
import charactersData from '../../../common/characters.json'

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
      allTags: new Set()
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
  mounted() {
    // 加载角色数据
    this.characters = charactersData
    
    // 收集所有标签
    this.collectAllTags()
  },
  methods: {
    // 收集所有角色的标签
    collectAllTags() {
      this.characters.forEach(character => {
        character.tags.forEach(tag => {
          this.allTags.add(tag)
        })
      })
      this.allTags = Array.from(this.allTags).sort()
    },
    
    // 处理搜索
    handleSearch() {
      // 可以在这里添加防抖逻辑
    },
    
    // 切换标签选择
    toggleTag(tag) {
      if (this.selectedTags.includes(tag)) {
        this.selectedTags = this.selectedTags.filter(t => t !== tag)
      } else {
        this.selectedTags.push(tag)
      }
    },
    
    // 清除所有筛选条件
    clearFilters() {
      this.selectedTags = []
      this.searchQuery = ''
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
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background-color: #3a6ed8;
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
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 12px;
  margin: 40px 0;
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
  
  .characters-grid {
    grid-template-columns: 1fr;
    margin: 0 20px 40px;
  }
}
</style>