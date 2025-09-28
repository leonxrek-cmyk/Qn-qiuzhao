<template>
  <div class="admin-characters">
    <div class="characters-header">
      <h2>角色管理</h2>
      <button @click="addCharacter" class="btn-primary">
        <span>➕</span>
        添加角色
      </button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="characters-filters">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索角色名称或描述..."
          @input="filterCharacters"
        />
        <span 
          :class="['search-icon', { 'clear-icon': searchQuery.trim() }]"
          @click="clearSearch"
        >
          {{ searchQuery.trim() ? '✕' : '🔍' }}
        </span>
      </div>
      
      <select v-model="filterTag" @change="filterCharacters" class="filter-select">
        <option value="">全部标签</option>
        <option v-for="tag in allTags" :key="tag" :value="tag">{{ tag }}</option>
      </select>
    </div>

    <!-- 角色网格 -->
    <div class="characters-grid">
      <div 
        v-for="character in filteredCharacters" 
        :key="character.id"
        class="character-card"
      >
        <div class="character-header">
          <img :src="character.avatar" :alt="character.name" class="character-avatar" />
          <div class="character-info">
            <h3>{{ character.name }}</h3>
            <p>{{ character.description }}</p>
          </div>
        </div>
        
        <div class="character-tags">
          <span v-for="tag in character.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
        
        <div class="character-actions">
          <button @click="editCharacter(character)" class="btn-edit">编辑</button>
          <button @click="deleteCharacter(character)" class="btn-delete">删除</button>
        </div>
      </div>
    </div>

    <!-- 角色编辑弹窗 -->
    <div v-if="showEditCharacter" class="modal-overlay" @click="closeEditCharacter">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingCharacter.id ? '编辑角色' : '添加角色' }}</h3>
          <button @click="closeEditCharacter" class="close-btn">✕</button>
        </div>
        
        <form @submit.prevent="saveCharacter" class="character-form">
          <div class="form-row">
            <div class="form-group">
              <label>角色ID</label>
              <input 
                type="text" 
                v-model="editingCharacter.id" 
                required 
                :disabled="!!originalCharacterId"
                placeholder="唯一标识符，如：confucius"
              />
            </div>
            
            <div class="form-group">
              <label>角色名称</label>
              <input 
                type="text" 
                v-model="editingCharacter.name" 
                required 
                placeholder="如：孔子"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>角色描述</label>
            <textarea 
              v-model="editingCharacter.description" 
              required 
              rows="3"
              placeholder="简要描述角色背景和特点"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>头像URL</label>
            <input 
              type="text" 
              v-model="editingCharacter.avatar" 
              placeholder="/avatars/character.png"
            />
          </div>
          
          <div class="form-group">
            <label>标签</label>
            <div class="tags-input">
              <div class="selected-tags">
                <span 
                  v-for="tag in editingCharacter.tags" 
                  :key="tag" 
                  class="selected-tag"
                >
                  {{ tag }}
                  <button type="button" @click="removeTag(tag)">✕</button>
                </span>
              </div>
              <input 
                type="text" 
                v-model="newTag" 
                @keydown.enter.prevent="addTag"
                placeholder="输入标签后按回车添加"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>系统提示词</label>
            <textarea 
              v-model="editingCharacter.prompt" 
              required 
              rows="5"
              placeholder="定义角色的行为和回答风格"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>语言风格</label>
            <select v-model="editingCharacter.language_style">
              <option value="formal">正式</option>
              <option value="casual">随意</option>
              <option value="ancient">古典</option>
              <option value="modern">现代</option>
            </select>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeEditCharacter" class="btn-cancel">取消</button>
            <button type="submit" class="btn-save" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载角色数据中...</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import apiService from '../../apiService.js'

export default {
  name: 'AdminCharacters',
  setup() {
    const loading = ref(false)
    const saving = ref(false)
    const characters = ref([])
    const searchQuery = ref('')
    const filterTag = ref('')
    const showEditCharacter = ref(false)
    const originalCharacterId = ref('')
    const newTag = ref('')
    
    const editingCharacter = ref({
      id: '',
      name: '',
      description: '',
      avatar: '',
      tags: [],
      prompt: '',
      language_style: 'formal',
      voice_params: {}
    })

    const allTags = computed(() => {
      const tags = new Set()
      characters.value.forEach(character => {
        character.tags.forEach(tag => tags.add(tag))
      })
      return Array.from(tags).sort()
    })

    const filteredCharacters = computed(() => {
      let result = characters.value

      // 标签筛选
      if (filterTag.value) {
        result = result.filter(character => 
          character.tags.includes(filterTag.value)
        )
      }

      // 搜索筛选
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(character => 
          character.name.toLowerCase().includes(query) ||
          character.description.toLowerCase().includes(query)
        )
      }

      return result
    })

    const loadCharacters = async () => {
      try {
        loading.value = true
        const configs = await apiService.getCharacterConfigs()
        characters.value = configs
      } catch (error) {
        console.error('加载角色列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    const filterCharacters = () => {
      // 触发计算属性重新计算
    }

    const clearSearch = () => {
      if (searchQuery.value.trim()) {
        searchQuery.value = ''
        filterCharacters()
      }
    }

    const addCharacter = () => {
      editingCharacter.value = {
        id: '',
        name: '',
        description: '',
        avatar: '',
        tags: [],
        prompt: '',
        language_style: 'formal',
        voice_params: {}
      }
      originalCharacterId.value = ''
      showEditCharacter.value = true
    }

    const editCharacter = (character) => {
      editingCharacter.value = {
        ...character,
        tags: [...character.tags]
      }
      originalCharacterId.value = character.id
      showEditCharacter.value = true
    }

    const deleteCharacter = async (character) => {
      if (!confirm(`确定要删除角色 "${character.name}" 吗？此操作不可撤销。`)) {
        return
      }

      try {
        const response = await apiService.deleteCharacter(character.id)
        if (response.success) {
          await loadCharacters()
        } else {
          alert('删除失败：' + response.error)
        }
      } catch (error) {
        console.error('删除角色失败:', error)
        alert('删除失败，请稍后重试')
      }
    }

    const saveCharacter = async () => {
      try {
        saving.value = true
        
        let response
        if (originalCharacterId.value) {
          // 更新角色
          response = await apiService.updateCharacter(originalCharacterId.value, editingCharacter.value)
        } else {
          // 创建角色
          response = await apiService.createCharacter(editingCharacter.value)
        }

        if (response.success) {
          const action = originalCharacterId.value ? '修改' : '添加'
          alert(`${action}成功！`)
          closeEditCharacter()
          await loadCharacters()
        } else {
          alert('保存失败：' + response.error)
        }
      } catch (error) {
        console.error('保存角色失败:', error)
        alert('保存失败，请稍后重试')
      } finally {
        saving.value = false
      }
    }

    const closeEditCharacter = () => {
      showEditCharacter.value = false
      originalCharacterId.value = ''
      newTag.value = ''
    }

    const addTag = () => {
      const tag = newTag.value.trim()
      if (tag && !editingCharacter.value.tags.includes(tag)) {
        editingCharacter.value.tags.push(tag)
        newTag.value = ''
      }
    }

    const removeTag = (tag) => {
      const index = editingCharacter.value.tags.indexOf(tag)
      if (index > -1) {
        editingCharacter.value.tags.splice(index, 1)
      }
    }

    onMounted(() => {
      loadCharacters()
    })

    return {
      loading,
      saving,
      characters,
      filteredCharacters,
      allTags,
      searchQuery,
      filterTag,
      showEditCharacter,
      editingCharacter,
      originalCharacterId,
      newTag,
      loadCharacters,
      filterCharacters,
      clearSearch,
      addCharacter,
      editCharacter,
      deleteCharacter,
      saveCharacter,
      closeEditCharacter,
      addTag,
      removeTag
    }
  }
}
</script>

<style scoped>
.admin-characters {
  position: relative;
}

.characters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.characters-header h2 {
  margin: 0;
  color: #2d3748;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.characters-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: center;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
}

.search-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.search-icon:hover {
  background: rgba(0, 0, 0, 0.05);
}

.search-icon.clear-icon {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  animation: fadeToRed 0.3s ease;
}

.search-icon.clear-icon:hover {
  color: #dc2626;
  background: rgba(239, 68, 68, 0.2);
  transform: translateY(-50%) scale(1.1);
}

@keyframes fadeToRed {
  from {
    color: #64748b;
    background: transparent;
  }
  to {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.character-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.character-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.character-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.character-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.character-info {
  flex: 1;
}

.character-info h3 {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
  font-size: 1.125rem;
}

.character-info p {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1.4;
}

.character-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tag {
  background: #f1f5f9;
  color: #475569;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.character-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-edit, .btn-delete {
  flex: 1;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-edit {
  background: #f0f9ff;
  color: #0369a1;
}

.btn-edit:hover {
  background: #0369a1;
  color: white;
}

.btn-delete {
  background: #fef2f2;
  color: #dc2626;
}

.btn-delete:hover {
  background: #dc2626;
  color: white;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  color: #2d3748;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #64748b;
}

.character-form {
  padding: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
}

.form-group textarea {
  resize: vertical;
}

.tags-input {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 0.5rem;
  min-height: 80px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.selected-tag {
  background: #667eea;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.selected-tag button {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 0.75rem;
}

.tags-input input {
  border: none;
  outline: none;
  padding: 0.25rem;
  width: 100%;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-cancel, .btn-save {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-cancel {
  background: #f1f5f9;
  color: #64748b;
}

.btn-save {
  background: #667eea;
  color: white;
}

.btn-save:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
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
  .characters-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .characters-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
