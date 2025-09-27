<template>
  <div class="character-card" @click="handleClick">
    <div class="character-avatar">
      <img :src="character.avatar || '/default-avatar.png'" :alt="character.name" />
    </div>
    <div class="character-info">
      <h3 class="character-name">{{ character.name }}</h3>
      <p class="character-desc">{{ character.description.substring(0, 50) }}...</p>
      <div class="character-tags">
        <span v-for="tag in character.tags.slice(0, 6)" :key="tag" class="tag">{{ tag }}</span>
        <span v-if="character.tags.length > 6" class="tag tag-more">+{{ character.tags.length - 6 }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CharacterCard',
  props: {
    character: {
      type: Object,
      required: true
    }
  },
  methods: {
    handleClick() {
      this.$emit('select', this.character)
    }
  }
}
</script>

<style scoped>
.character-card {
  display: flex;
  align-items: center;
  padding: 16px;
  margin-bottom: 12px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  /* 设置固定高度确保卡片大小一致，增加高度以容纳更多标签 */
  height: 130px;
  min-height: 130px;
  max-height: 130px;
  box-sizing: border-box;
}

.character-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(76, 132, 255, 0.1), transparent);
  transition: left 0.6s ease;
}

.character-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.character-card:hover::before {
  left: 100%;
}

.character-card:active {
  transform: translateY(-2px);
  transition: transform 0.1s ease;
}


.character-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 16px;
  flex-shrink: 0;
}

.character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.character-info {
  flex: 1;
  min-width: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  /* 恢复居中对齐，让内容分布更均匀 */
  overflow: visible; /* 改为visible让标签能完全显示 */
}

.character-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
  /* 确保名称不会换行，超出部分显示省略号 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}

.character-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  /* 恢复为两行显示 */
  flex-shrink: 0;
  min-height: 34px;
  max-height: 34px;
  line-height: 1.2;
}

.character-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  /* 确保标签能完全展示 */
  flex: 1;
  min-height: 20px;
  max-height: 48px; /* 允许显示2行标签，增加空间 */
  overflow: visible; /* 改为visible确保标签不被截断 */
  align-items: flex-start;
  align-content: flex-start;
}

.tag {
  font-size: 12px;
  padding: 2px 8px;
  background-color: #f0f0f0;
  color: #666;
  border-radius: 12px;
  /* 恢复标签原始大小 */
  height: 20px;
  line-height: 16px;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
  flex-shrink: 0;
}

.tag-more {
  background-color: #e0e0e0;
  color: #999;
  font-weight: 500;
}

</style>