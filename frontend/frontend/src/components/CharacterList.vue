<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { characterApi } from '../api/character'
import { Character, CreateCharacterRequest } from '../beans'

// 响应式数据
const characters = ref<Character[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const showCreateForm = ref(false)
const showEditForm = ref(false)
const editingCharacter = ref<Character | null>(null)

// 创建/编辑表单数据
const formData = ref<CreateCharacterRequest>(
  new CreateCharacterRequest({
    name: '',
    prompt: '',
    is_visible: true
  })
)

// 表单验证
const formErrors = ref<Record<string, string>>({})

// 加载角色列表
const loadCharacters = async () => {
  loading.value = true
  error.value = null
  try {
    characters.value = await characterApi.getAllCharacters()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载角色列表失败'
  } finally {
    loading.value = false
  }
}

// 显示创建表单
const showCreate = () => {
  formData.value = new CreateCharacterRequest({
    name: '',
    prompt: '',
    is_visible: true
  })
  formErrors.value = {}
  showCreateForm.value = true
}

// 显示编辑表单
const showEdit = (character: Character) => {
  editingCharacter.value = character
  formData.value = new CreateCharacterRequest({
    name: character.name,
    prompt: character.prompt,
    is_visible: character.is_visible
  })
  formErrors.value = {}
  showEditForm.value = true
}

// 隐藏表单
const hideForm = () => {
  showCreateForm.value = false
  showEditForm.value = false
  editingCharacter.value = null
  formErrors.value = {}
}

// 验证表单
const validateForm = (): boolean => {
  formErrors.value = {}

  if (!formData.value.name.trim()) {
    formErrors.value.name = '角色名称不能为空'
  }

  if (!formData.value.prompt.trim()) {
    formErrors.value.prompt = '角色设定不能为空'
  }

  return Object.keys(formErrors.value).length === 0
}

// 创建角色
const createCharacter = async () => {
  if (!validateForm()) {
    return
  }

  try {
    loading.value = true
    await characterApi.createCharacter(formData.value)
    await loadCharacters()
    hideForm()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '创建角色失败'
  } finally {
    loading.value = false
  }
}

// 更新角色
const updateCharacter = async () => {
  if (!validateForm() || !editingCharacter.value) {
    return
  }

  try {
    loading.value = true
    const updateData = {
      name: formData.value.name,
      prompt: formData.value.prompt,
      is_visible: formData.value.is_visible
    }
    await characterApi.updateCharacter(editingCharacter.value.character_id, updateData)
    await loadCharacters()
    hideForm()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '更新角色失败'
  } finally {
    loading.value = false
  }
}

// 删除角色
const deleteCharacter = async (character: Character) => {
  if (!confirm(`确定要删除角色"${character.name}"吗？`)) {
    return
  }

  try {
    loading.value = true
    await characterApi.deleteCharacter(character.character_id)
    await loadCharacters()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除角色失败'
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadCharacters()
})
</script>

<template>
  <div class="character-list">
    <!-- 页面标题和操作按钮 -->
    <div class="header">
      <h1>角色管理</h1>
      <button
        @click="showCreate"
        class="btn btn-primary"
        :disabled="loading"
      >
        创建新角色
      </button>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && !characters.length" class="loading">
      正在加载角色列表...
    </div>

    <!-- 角色列表 -->
    <div v-if="characters.length > 0" class="characters-grid">
      <div
        v-for="character in characters"
        :key="character.character_id"
        class="character-card"
      >
        <div class="character-header">
          <h3>{{ character.name }}</h3>
          <span
            class="badge"
            :class="character.is_visible ? 'badge-success' : 'badge-secondary'"
          >
            {{ character.is_visible ? '可见' : '隐藏' }}
          </span>
        </div>

        <div class="character-prompt">
          <p>{{ character.prompt }}</p>
        </div>

        <div class="character-actions">
          <button
            @click="showEdit(character)"
            class="btn btn-sm btn-secondary"
            :disabled="loading"
          >
            编辑
          </button>
          <button
            @click="deleteCharacter(character)"
            class="btn btn-sm btn-danger"
            :disabled="loading"
          >
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && characters.length === 0" class="empty-state">
      <p>暂无角色，点击"创建新角色"开始创建</p>
    </div>

    <!-- 创建/编辑表单模态框 -->
    <div v-if="showCreateForm || showEditForm" class="modal-overlay" @click="hideForm">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>{{ showCreateForm ? '创建角色' : '编辑角色' }}</h2>
          <button @click="hideForm" class="close-btn">&times;</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label for="name">角色名称 *</label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              class="form-control"
              :class="{ 'error': formErrors.name }"
              placeholder="请输入角色名称"
            />
            <span v-if="formErrors.name" class="error-text">{{ formErrors.name }}</span>
          </div>

          <div class="form-group">
            <label for="prompt">角色设定 *</label>
            <textarea
              id="prompt"
              v-model="formData.prompt"
              class="form-control"
              :class="{ 'error': formErrors.prompt }"
              rows="4"
              placeholder="请输入角色设定prompt"
            ></textarea>
            <span v-if="formErrors.prompt" class="error-text">{{ formErrors.prompt }}</span>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="formData.is_visible"
                type="checkbox"
                class="checkbox"
              />
              角色可见
            </label>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="hideForm" class="btn btn-secondary">取消</button>
          <button
            @click="showCreateForm ? createCharacter : updateCharacter"
            class="btn btn-primary"
            :disabled="loading"
          >
            {{ loading ? '处理中...' : (showCreateForm ? '创建' : '更新') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.character-list {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #0a0a0a;
  min-height: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
  color: #e0e0e0;
  font-weight: 300;
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.character-card {
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  padding: 16px;
  background: #1a1a1a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.3s;
}

.character-card:hover {
  border-color: #3a3a3a;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  transform: translateY(-2px);
}

.character-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.character-header h3 {
  margin: 0;
  color: #e0e0e0;
  font-weight: 500;
}

.character-prompt {
  margin-bottom: 16px;
  color: #a0a0a0;
  font-size: 14px;
  line-height: 1.5;
}

.character-prompt p {
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.character-actions {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-success {
  background-color: #1e293b;
  color: #10b981;
  border: 1px solid #10b981;
}

.badge-secondary {
  background-color: #1e293b;
  color: #6b7280;
  border: 1px solid #6b7280;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  font-weight: 500;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #6366f1;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #4f46e5;
}

.btn-secondary {
  background-color: #1a1a1a;
  color: #e0e0e0;
  border: 1px solid #2a2a2a;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #252525;
  border-color: #3a3a3a;
}

.btn-danger {
  background-color: #1a1a1a;
  color: #ef4444;
  border: 1px solid #ef4444;
}

.btn-danger:hover:not(:disabled) {
  background-color: #252525;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.alert {
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.alert-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.loading, .empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
  background-color: #0a0a0a;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: #1a1a1a;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid #2a2a2a;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #2a2a2a;
}

.modal-header h2 {
  margin: 0;
  color: #e0e0e0;
  font-weight: 400;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #e0e0e0;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #2a2a2a;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #a0a0a0;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  font-size: 14px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  transition: all 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #6366f1;
  background-color: #252525;
}

.form-control.error {
  border-color: #ef4444;
}

.error-text {
  color: #ef4444;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox {
  width: 16px;
  height: 16px;
}
</style>
