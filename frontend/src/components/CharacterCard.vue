<template>
  <div class="character-card" @click="handleClick">
    <div class="character-avatar">
      <img :src="character.avatar || '/default-avatar.png'" :alt="character.name" />
    </div>
    <div class="character-info">
      <h3 class="character-name">{{ character.name }}</h3>
      <p class="character-desc">{{ character.description.substring(0, 50) }}...</p>
      <div class="character-tags">
        <span v-for="tag in character.tags" :key="tag" class="tag">{{ tag }}</span>
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
}

.character-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
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
}

.character-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
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
}

.character-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  font-size: 12px;
  padding: 2px 8px;
  background-color: #f0f0f0;
  color: #666;
  border-radius: 12px;
}
</style>