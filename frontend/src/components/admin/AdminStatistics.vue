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
          @click="showCharacterDetail(character)"
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
              <span class="metric-value">{{ character.totalIntimacy || 0 }}</span>
              <span class="metric-label">亲密度总和</span>
            </div>
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

    <!-- 角色详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeCharacterDetail">
      <div class="character-detail-modal" @click.stop>
        <div class="modal-header">
          <div class="character-header-info">
            <img :src="selectedCharacter.avatar" :alt="selectedCharacter.name" class="modal-character-avatar" />
            <div>
              <h3>{{ selectedCharacter.name }}</h3>
              <p>{{ selectedCharacter.description }}</p>
            </div>
          </div>
          <button @click="closeCharacterDetail" class="close-btn">✕</button>
        </div>
        
        <div class="modal-content">
          <div class="character-summary">
            <div class="summary-item">
              <span class="summary-label">总亲密度</span>
              <span class="summary-value">{{ selectedCharacter.totalIntimacy || 0 }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">总对话数</span>
              <span class="summary-value">{{ selectedCharacter.messageCount || 0 }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">用户数量</span>
              <span class="summary-value">{{ selectedCharacter.userCount || 0 }}</span>
            </div>
          </div>
          
          <div class="user-stats-section">
            <h4>用户详细统计</h4>
            <div v-if="loadingUserStats" class="loading-text">加载用户统计中...</div>
            <div v-else-if="userStats.length === 0" class="no-data">暂无用户数据</div>
            <div v-else class="user-stats-list">
              <div 
                v-for="userStat in userStats" 
                :key="userStat.userId"
                class="user-stat-item"
              >
                <div class="user-info">
                  <img :src="userStat.avatar || '/user-avatar.svg'" :alt="userStat.nickname" class="user-avatar" />
                  <div class="user-details">
                    <div class="user-name">{{ userStat.nickname || userStat.username }}</div>
                    <div class="user-username">@{{ userStat.username }}</div>
                  </div>
                </div>
                <div class="user-metrics">
                  <div class="user-metric">
                    <span class="metric-value">{{ userStat.intimacy || 0 }}</span>
                    <span class="metric-label">亲密度</span>
                  </div>
                  <div class="user-metric">
                    <span class="metric-value">{{ userStat.messageCount || 0 }}</span>
                    <span class="metric-label">对话数</span>
                  </div>
                </div>
              </div>
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
    
    // 弹窗相关数据
    const showDetailModal = ref(false)
    const selectedCharacter = ref({})
    const userStats = ref([])
    const loadingUserStats = ref(false)
    
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

    // 显示角色详情弹窗
    const showCharacterDetail = async (character) => {
      selectedCharacter.value = character
      showDetailModal.value = true
      await loadUserStats(character.id)
    }

    // 关闭角色详情弹窗
    const closeCharacterDetail = () => {
      showDetailModal.value = false
      selectedCharacter.value = {}
      userStats.value = []
    }

    // 加载用户统计数据
    const loadUserStats = async (characterId) => {
      try {
        loadingUserStats.value = true
        const response = await apiService.getCharacterUserStats(characterId)
        if (response.success) {
          userStats.value = response.data
        }
      } catch (error) {
        console.error('加载用户统计失败:', error)
        // 使用模拟数据
        userStats.value = [
          {
            userId: '1',
            username: 'admin',
            nickname: '系统管理员',
            avatar: '/user-avatar.svg',
            intimacy: 3,
            messageCount: 15
          },
          {
            userId: '2', 
            username: '123',
            nickname: '测试用户',
            avatar: '/user-avatar.svg',
            intimacy: 8,
            messageCount: 25
          }
        ]
      } finally {
        loadingUserStats.value = false
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
      loadStatistics,
      // 弹窗相关
      showDetailModal,
      selectedCharacter,
      userStats,
      loadingUserStats,
      showCharacterDetail,
      closeCharacterDetail
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
  transition: all 0.3s ease;
  cursor: pointer;
}

.character-stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
}

.character-stat-item:active {
  transform: translateY(0);
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
  gap: 1.5rem;
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

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    backdrop-filter: blur(0px);
  }
  to {
    opacity: 1;
    backdrop-filter: blur(8px);
  }
}

.character-detail-modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
}

.character-header-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.modal-character-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #667eea;
}

.modal-header h3 {
  margin: 0 0 0.25rem 0;
  color: #2d3748;
  font-size: 1.25rem;
}

.modal-header p {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #64748b;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #475569;
}

.modal-content {
  padding: 1.5rem;
  overflow-y: auto;
  max-height: calc(80vh - 120px);
}

.character-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.summary-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem;
  border-radius: 12px;
  text-align: center;
}

.summary-label {
  display: block;
  font-size: 0.75rem;
  opacity: 0.9;
  margin-bottom: 0.5rem;
}

.summary-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
}

.user-stats-section h4 {
  margin: 0 0 1rem 0;
  color: #2d3748;
  font-size: 1.125rem;
}

.loading-text, .no-data {
  text-align: center;
  color: #64748b;
  padding: 2rem;
  font-style: italic;
}

.user-stats-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
}

.user-stat-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 500;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.user-username {
  font-size: 0.75rem;
  color: #64748b;
}

.user-metrics {
  display: flex;
  gap: 1.5rem;
}

.user-metric {
  text-align: center;
}

.user-metric .metric-value {
  display: block;
  font-size: 1.125rem;
  font-weight: bold;
  color: #667eea;
}

.user-metric .metric-label {
  font-size: 0.75rem;
  color: #64748b;
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
  
  .character-detail-modal {
    width: 95%;
    max-height: 90vh;
  }
  
  .modal-header {
    padding: 1rem;
  }
  
  .character-header-info {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
  
  .character-summary {
    grid-template-columns: 1fr;
  }
  
  .user-metrics {
    gap: 1rem;
  }
}
</style>
