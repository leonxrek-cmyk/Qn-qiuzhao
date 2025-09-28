<template>
  <div class="intimacy-ranking-modal" @click.stop>
    <div class="modal-header">
      <h2>💖 亲密度排行</h2>
      <button class="close-button" @click="$emit('close')" title="关闭">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
    
    <div class="modal-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在加载亲密度数据...</p>
      </div>
      
      <!-- 排行列表 -->
      <div v-else-if="rankingList.length > 0" class="ranking-list">
        <div 
          v-for="(item, index) in rankingList" 
          :key="item.characterId"
          class="ranking-item"
          :class="{ 
            'top-rank': index < 3,
            'rank-1': index === 0,
            'rank-2': index === 1,
            'rank-3': index === 2
          }"
        >
          <!-- 排名 -->
          <div class="rank-number">
            <span v-if="index === 0" class="rank-crown">👑</span>
            <span v-else-if="index === 1" class="rank-medal">🥈</span>
            <span v-else-if="index === 2" class="rank-medal">🥉</span>
            <span v-else class="rank-text">{{ index + 1 }}</span>
          </div>
          
          <!-- 角色信息 -->
          <div class="character-info">
            <div class="character-avatar">
              <img :src="item.avatar" :alt="item.name" />
            </div>
            <div class="character-details">
              <h3 class="character-name">{{ item.name }}</h3>
              <p class="character-description">{{ item.description }}</p>
            </div>
          </div>
          
          <!-- 亲密度信息 -->
          <div class="intimacy-info">
            <div class="intimacy-value">{{ item.intimacy }}</div>
            <div class="intimacy-label">{{ item.levelName }}</div>
            <div class="intimacy-progress">
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: getProgressPercent(item.intimacy) + '%' }"
                ></div>
              </div>
              <div class="progress-text">{{ getProgressPercent(item.intimacy) }}%</div>
            </div>
          </div>
          
          <!-- 快速跳转按钮 -->
          <div class="action-buttons">
            <button 
              class="chat-button" 
              @click="goToChat(item.characterId)"
              title="开始对话"
            >
              💬
            </button>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">💔</div>
        <h3>暂无亲密度记录</h3>
        <p>开始与角色对话来建立亲密度吧！</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../apiService.js'

export default {
  name: 'IntimacyRankingModal',
  emits: ['close'],
  setup(props, { emit }) {
    const router = useRouter()
    const loading = ref(true)
    const rankingList = ref([])
    const characterConfigs = ref([])
    
    // 亲密度等级配置
    const intimacyLevels = {
      1: '初次相识',
      5: '聊得火热',
      10: '相见恨晚',
      20: '亲密无间',
      50: '知音难觅',
      100: '伯乐'
    }
    
    // 获取亲密度等级名称
    const getLevelName = (intimacy) => {
      const thresholds = [100, 50, 20, 10, 5, 1]
      for (const threshold of thresholds) {
        if (intimacy >= threshold) {
          return intimacyLevels[threshold]
        }
      }
      return '陌生人'
    }
    
    // 计算进度百分比（线性分布）
    const getProgressPercent = (intimacy) => {
      if (intimacy === 0) return 0
      const maxIntimacy = 100
      return Math.min((intimacy / maxIntimacy) * 100, 100)
    }
    
    // 加载角色配置
    const loadCharacterConfigs = async () => {
      try {
        const configs = await apiService.getCharacterConfigs()
        characterConfigs.value = configs
      } catch (error) {
        console.error('加载角色配置失败:', error)
      }
    }
    
    // 加载亲密度排行数据
    const loadIntimacyRanking = async () => {
      loading.value = true
      try {
        // 并行加载角色配置和亲密度数据
        await loadCharacterConfigs()
        const response = await apiService.getAllIntimacy()
        
        if (response.success && response.intimacy_data) {
          // 转换数据格式并排序
          const intimacyData = response.intimacy_data
          const ranking = []
          
          for (const [characterId, intimacyInfo] of Object.entries(intimacyData)) {
            const intimacy = intimacyInfo.intimacy || 0
            if (intimacy > 0) { // 只显示有亲密度的角色
              const character = characterConfigs.value.find(c => c.id === characterId)
              if (character) {
                ranking.push({
                  characterId,
                  name: character.name,
                  description: character.description,
                  avatar: character.avatar,
                  intimacy,
                  levelName: intimacyInfo.level_progress?.current_level || getLevelName(intimacy)
                })
              }
            }
          }
          
          // 按亲密度降序排序
          ranking.sort((a, b) => b.intimacy - a.intimacy)
          rankingList.value = ranking
          
          console.log('亲密度排行加载成功:', ranking)
        }
      } catch (error) {
        console.error('加载亲密度排行失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 跳转到角色对话页面
    const goToChat = (characterId) => {
      emit('close')
      router.push(`/chat/${characterId}`)
    }
    
    onMounted(() => {
      loadIntimacyRanking()
    })
    
    return {
      loading,
      rankingList,
      getProgressPercent,
      goToChat
    }
  }
}
</script>

<style scoped>
.intimacy-ranking-modal {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 90vw;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.close-button svg {
  width: 20px;
  height: 20px;
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #ff6b6b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 排行列表 */
.ranking-list {
  padding: 16px;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 16px;
  margin-bottom: 12px;
  border-radius: 12px;
  background: #f8f9fa;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.ranking-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.ranking-item.top-rank {
  background: linear-gradient(135deg, #fff, #f8f9fa);
  border-color: #ddd;
}

.ranking-item.rank-1 {
  background: linear-gradient(135deg, #fff9c4, #fef3c7);
  border-color: #f59e0b;
}

.ranking-item.rank-2 {
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  border-color: #9ca3af;
}

.ranking-item.rank-3 {
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  border-color: #f87171;
}

/* 排名显示 */
.rank-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  margin-right: 16px;
  font-weight: bold;
  font-size: 18px;
}

.rank-crown {
  font-size: 24px;
}

.rank-medal {
  font-size: 22px;
}

.rank-text {
  background: #6b7280;
  color: white;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

/* 角色信息 */
.character-info {
  display: flex;
  align-items: center;
  flex: 1;
  margin-right: 16px;
}

.character-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 12px;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.character-details h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.character-details p {
  margin: 0;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
}

/* 亲密度信息 */
.intimacy-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 16px;
  min-width: 120px;
}

.intimacy-value {
  font-size: 24px;
  font-weight: bold;
  color: #ff6b6b;
  margin-bottom: 4px;
}

.intimacy-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
  text-align: center;
}

.intimacy-progress {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff6b6b, #ff8e8e);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 10px;
  color: #9ca3af;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-button {
  background: #4c84ff;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-button:hover {
  background: #3a6ed8;
  transform: scale(1.05);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #6b7280;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #374151;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .intimacy-ranking-modal {
    width: 95vw;
    max-height: 85vh;
  }
  
  .ranking-item {
    flex-direction: column;
    text-align: center;
    padding: 16px 12px;
  }
  
  .character-info {
    margin: 12px 0;
    flex-direction: column;
    text-align: center;
  }
  
  .character-avatar {
    margin: 0 0 8px 0;
  }
  
  .intimacy-info {
    margin: 12px 0;
  }
  
  .rank-number {
    margin: 0 0 12px 0;
  }
}
</style>
