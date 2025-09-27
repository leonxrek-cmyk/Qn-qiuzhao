<template>
  <div class="admin-statistics">
    <h2>数据统计</h2>
    
    <!-- 时间范围选择 -->
    <div class="time-range-selector">
      <button 
        v-for="range in timeRanges" 
        :key="range.key"
        :class="['range-button', { active: selectedRange === range.key }]"
        @click="selectTimeRange(range.key)"
      >
        {{ range.label }}
      </button>
      
      <div v-if="selectedRange === 'custom'" class="custom-range">
        <input 
          type="date" 
          v-model="customStartDate" 
          @change="loadStatistics"
        />
        <span>至</span>
        <input 
          type="date" 
          v-model="customEndDate" 
          @change="loadStatistics"
        />
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">💬</div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.totalMessages }}</div>
          <div class="stat-label">总对话数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.totalUsers }}</div>
          <div class="stat-label">用户总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🎭</div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.totalCharacters }}</div>
          <div class="stat-label">角色总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.todayMessages }}</div>
          <div class="stat-label">今日对话</div>
        </div>
      </div>
    </div>

    <!-- 热门角色统计 -->
    <div class="popular-characters-stats">
      <h3>热门角色统计</h3>
      <div class="character-stats-list">
        <div 
          v-for="character in statistics.popularCharacters" 
          :key="character.id"
          class="character-stat-item"
        >
          <div class="character-info">
            <img :src="character.avatar" :alt="character.name" class="character-avatar" />
            <div class="character-details">
              <div class="character-name">{{ character.name }}</div>
              <div class="character-desc">{{ character.description }}</div>
            </div>
          </div>
          <div class="character-metrics">
            <div class="metric">
              <span class="metric-value">{{ character.messageCount }}</span>
              <span class="metric-label">对话数</span>
            </div>
            <div class="metric">
              <span class="metric-value">{{ character.userCount }}</span>
              <span class="metric-label">用户数</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载统计数据中...</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiService from '../../apiService.js'

export default {
  name: 'AdminStatistics',
  setup() {
    const loading = ref(false)
    const selectedRange = ref('today')
    const customStartDate = ref('')
    const customEndDate = ref('')
    
    const statistics = ref({
      totalMessages: 0,
      totalUsers: 0,
      totalCharacters: 0,
      todayMessages: 0,
      popularCharacters: []
    })

    const timeRanges = [
      { key: 'today', label: '今天' },
      { key: 'week', label: '最近7天' },
      { key: 'month', label: '最近30天' },
      { key: 'custom', label: '自定义' }
    ]

    const selectTimeRange = (range) => {
      selectedRange.value = range
      if (range !== 'custom') {
        loadStatistics()
      }
    }

    const loadStatistics = async () => {
      try {
        loading.value = true
        
        // 模拟API调用，实际应该调用后端统计接口
        const response = await apiService.getStatistics({
          range: selectedRange.value,
          startDate: customStartDate.value,
          endDate: customEndDate.value
        })
        
        if (response.success) {
          statistics.value = response.data
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
        // 使用模拟数据
        statistics.value = {
          totalMessages: 1234,
          totalUsers: 56,
          totalCharacters: 20,
          todayMessages: 89,
          popularCharacters: [
            {
              id: 'confucius',
              name: '孔子',
              description: '春秋时期思想家、教育家',
              avatar: '/avatars/confucius.png',
              messageCount: 234,
              userCount: 45
            },
            {
              id: 'einstein',
              name: '爱因斯坦',
              description: '理论物理学家',
              avatar: '/avatars/einstein.png',
              messageCount: 189,
              userCount: 38
            }
          ]
        }
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadStatistics()
    })

    return {
      loading,
      selectedRange,
      customStartDate,
      customEndDate,
      statistics,
      timeRanges,
      selectTimeRange,
      loadStatistics
    }
  }
}
</script>

<style scoped>
.admin-statistics h2 {
  margin: 0 0 2rem 0;
  color: #2d3748;
}

.time-range-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.range-button {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.range-button:hover {
  border-color: #667eea;
  background: #f7fafc;
}

.range-button.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.custom-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.custom-range input {
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.stat-label {
  color: #64748b;
  font-size: 0.875rem;
}

.popular-characters-stats h3 {
  margin: 0 0 1.5rem 0;
  color: #2d3748;
}

.character-stats-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.character-stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s;
}

.character-stat-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.character-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.character-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.character-details {
  flex: 1;
}

.character-name {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.character-desc {
  color: #64748b;
  font-size: 0.875rem;
}

.character-metrics {
  display: flex;
  gap: 2rem;
}

.metric {
  text-align: center;
}

.metric-value {
  display: block;
  font-size: 1.25rem;
  font-weight: bold;
  color: #667eea;
}

.metric-label {
  font-size: 0.75rem;
  color: #64748b;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .character-stat-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .character-metrics {
    align-self: stretch;
    justify-content: space-around;
  }
}
</style>
