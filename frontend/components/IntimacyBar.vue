<template>
  <div class="intimacy-container">
    <!-- 水平布局：数值 - 进度条 - 等级标签 -->
    <div class="intimacy-horizontal-layout">
      <!-- 亲密度数值显示 -->
      <div class="intimacy-info">
        <!-- +1 动画 - 移动到数值左侧 -->
        <transition name="plus-one">
          <div v-if="showPlusOne" class="plus-one-animation-left">+1</div>
        </transition>
        <span class="intimacy-value">{{ intimacy }}</span>
        <span class="intimacy-next" v-if="nextThreshold">
          /{{ nextThreshold }}
        </span>
      </div>
      
      <!-- 亲密度进度条 -->
      <div class="intimacy-bar-wrapper">
        <div class="intimacy-bar">
          <div 
            class="intimacy-progress" 
            :style="{ width: progressPercent + '%' }"
          ></div>
          
          <!-- 等级标记 -->
          <div class="level-markers">
            <div 
              v-for="(level, threshold) in levelMarkers" 
              :key="threshold"
              class="level-marker"
              :class="{ 'reached': intimacy >= threshold }"
              :style="{ left: getMarkerPosition(threshold) + '%' }"
              :title="`${level} (${threshold}次)`"
            >
              <div class="marker-dot"></div>
              <div class="marker-label">{{ threshold }}</div>
              <!-- 爱心动画 -->
              <transition name="heart-animation">
                <div 
                  v-if="showHeartAnimation && recentlyReachedThreshold === threshold" 
                  class="heart-animation"
                >
                  ❤️
                </div>
              </transition>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 亲密度等级标签 -->
      <div class="intimacy-level">
        <transition name="level-fade" mode="out-in">
          <span :key="currentLevel" class="level-text">{{ currentLevel }}</span>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IntimacyBar',
  props: {
    intimacy: {
      type: Number,
      default: 0
    },
    levelProgress: {
      type: Object,
      default: () => ({
        current_level: '陌生人',
        next_level: null,
        current_threshold: 0,
        next_threshold: null,
        progress: 0
      })
    }
  },
  data() {
    return {
      showPlusOne: false,
      showHeartAnimation: false,
      recentlyReachedThreshold: null,
      currentLevel: '陌生人',
      levelMarkers: {
        1: '初次相识',
        5: '聊得火热',
        10: '相见恨晚',
        20: '亲密无间',
        50: '知音难觅',
        100: '伯乐'
      }
    }
  },
  computed: {
    progressPercent() {
      if (this.intimacy === 0) return 0
      
      // 使用线性计算，充分利用整个进度条（0-100%）
      const maxIntimacy = 100
      const maxProgress = 100 // 使用整个进度条
      
      const linearProgress = (this.intimacy / maxIntimacy) * maxProgress
      return Math.min(linearProgress, maxProgress)
    },
    nextThreshold() {
      return this.levelProgress.next_threshold
    }
  },
  watch: {
    intimacy(newVal, oldVal) {
      if (newVal > oldVal) {
        this.showPlusOneAnimation()
        this.checkForThresholdReached(newVal, oldVal)
      }
    },
    'levelProgress.current_level'(newLevel, oldLevel) {
      if (newLevel !== oldLevel && oldLevel) {
        // 等级提升动画
        this.currentLevel = newLevel
      } else {
        this.currentLevel = newLevel
      }
    }
  },
  mounted() {
    this.currentLevel = this.levelProgress.current_level || '陌生人'
  },
  methods: {
    showPlusOneAnimation() {
      this.showPlusOne = true
      setTimeout(() => {
        this.showPlusOne = false
      }, 2000)
    },
    getMarkerPosition(threshold) {
      // 线性分布标记位置，充分利用整个进度条
      const maxIntimacy = 100
      const maxProgress = 100 // 使用整个进度条
      
      return (threshold / maxIntimacy) * maxProgress
    },
    checkForThresholdReached(newVal, oldVal) {
      // 检查是否达到了新的阶段
      const thresholds = Object.keys(this.levelMarkers).map(Number).sort((a, b) => a - b)
      
      for (const threshold of thresholds) {
        if (newVal >= threshold && oldVal < threshold) {
          // 达到了新阶段，显示爱心动画
          this.showHeartAnimationForThreshold(threshold)
          break
        }
      }
    },
    showHeartAnimationForThreshold(threshold) {
      this.recentlyReachedThreshold = threshold
      this.showHeartAnimation = true
      
      setTimeout(() => {
        this.showHeartAnimation = false
        this.recentlyReachedThreshold = null
      }, 2500) // 爱心动画持续2.5秒
    }
  }
}
</script>

<style scoped>
.intimacy-container {
  margin: 0;
  padding: 0.25rem 0;
  width: 100%;
}

.intimacy-horizontal-layout {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: space-between;
  width: 100%;
}

.intimacy-bar-wrapper {
  position: relative;
  flex: 1;
  min-width: 280px;
  max-width: 380px;
}

.intimacy-bar {
  position: relative;
  width: 100%;
  height: 8px;
  background: linear-gradient(90deg, #f0f0f0 0%, #e0e0e0 100%);
  border-radius: 4px;
  overflow: visible;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}

.intimacy-progress {
  height: 100%;
  background: linear-gradient(90deg, #ff6b6b 0%, #ff8e8e 50%, #ffb3b3 100%);
  border-radius: 4px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  box-shadow: 0 2px 4px rgba(255, 107, 107, 0.3);
}

.intimacy-progress::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
  border-radius: 4px;
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.level-markers {
  position: absolute;
  top: -8px;
  left: 0;
  right: 0;
  height: 24px;
  pointer-events: none;
}

.level-marker {
  position: absolute;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.marker-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
  border: 2px solid white;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.level-marker.reached .marker-dot {
  background: #ff6b6b;
  transform: scale(1.2);
  box-shadow: 0 2px 6px rgba(255, 107, 107, 0.4);
}

.marker-label {
  font-size: 10px;
  color: #666;
  margin-top: 2px;
  font-weight: 500;
}

.level-marker.reached .marker-label {
  color: #ff6b6b;
  font-weight: 600;
}

.intimacy-level {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  min-width: 70px;
  max-width: 80px;
  flex-shrink: 0;
}

.level-text {
  font-size: 12px;
  font-weight: 600;
  color: #ff6b6b;
  text-shadow: 0 1px 2px rgba(255, 107, 107, 0.2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.intimacy-info {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #666;
  min-width: 35px;
  max-width: 45px;
  justify-content: flex-end;
  flex-shrink: 0;
  position: relative;
}

.intimacy-value {
  font-weight: 600;
  color: #ff6b6b;
}

.intimacy-next {
  color: #999;
}

.plus-one-animation-left {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  color: #ff6b6b;
  font-weight: bold;
  font-size: 16px;
  pointer-events: none;
  text-shadow: 0 2px 6px rgba(255, 107, 107, 0.5);
  z-index: 10;
  background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 2px 4px rgba(255, 107, 107, 0.3));
}

.heart-animation {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 16px;
  pointer-events: none;
  z-index: 10;
}

/* 动画效果 */
.plus-one-enter-active {
  transition: all 2s cubic-bezier(0.4, 0, 0.2, 1);
}

.plus-one-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.plus-one-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(10px) scale(0.6);
}

.plus-one-enter-to {
  opacity: 1;
  transform: translateX(-50%) translateY(-20px) scale(1.3);
}

.plus-one-leave-from {
  opacity: 1;
  transform: translateX(-50%) translateY(-20px) scale(1.3);
}

.plus-one-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-40px) scale(0.8);
}

.level-fade-enter-active,
.level-fade-leave-active {
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.level-fade-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(10px);
}

.level-fade-leave-to {
  opacity: 0;
  transform: scale(1.2) translateY(-10px);
}

/* 爱心动画效果 */
.heart-animation-enter-active {
  transition: all 2.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.heart-animation-leave-active {
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.heart-animation-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(20px) scale(0.5);
}

.heart-animation-enter-to {
  opacity: 1;
  transform: translateX(-50%) translateY(-30px) scale(1.2);
}

.heart-animation-leave-from {
  opacity: 1;
  transform: translateX(-50%) translateY(-30px) scale(1.2);
}

.heart-animation-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-50px) scale(0.8);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .intimacy-container {
    margin: 0.25rem 0;
    padding: 0.125rem;
  }
  
  .intimacy-horizontal-layout {
    gap: 0.5rem;
  }
  
  .intimacy-bar-wrapper {
    min-width: 180px;
    max-width: 220px;
  }
  
  .intimacy-bar {
    height: 6px;
  }
  
  .marker-dot {
    width: 5px;
    height: 5px;
  }
  
  .marker-label {
    font-size: 8px;
  }
  
  .level-text {
    font-size: 10px;
  }
  
  .intimacy-info {
    font-size: 11px;
    min-width: 30px;
    max-width: 40px;
  }
  
  .intimacy-level {
    min-width: 55px;
    max-width: 65px;
  }
  
  .level-text {
    font-size: 10px;
  }
  
  .intimacy-horizontal-layout {
    gap: 0.8rem;
  }
  
  .plus-one-animation-left {
    font-size: 14px;
    top: -20px;
  }
}
</style>
