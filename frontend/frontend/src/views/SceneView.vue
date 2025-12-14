<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { sceneApi } from '../api/scene'
import {
  Scene,
  CreateSceneByCurrentRequest,
  CreateSceneRequest,
} from '../beans'

// 响应式数据
const scenes = ref<Scene[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const showCreateForm = ref(false)
const showEditForm = ref(false)
const editingScene = ref<Scene | null>(null)
const router = useRouter()

// 表单数据
const formData = ref<CreateSceneByCurrentRequest>(
  new CreateSceneByCurrentRequest({
    new_scene: new CreateSceneRequest({
      sid: '',
      name: '',
      is_main: false,
      summary: '',
      is_root: false
    }),
    current_scenes_id: undefined,
    character_ids: undefined
  })
)

// 表单验证
const formErrors = ref<Record<string, string>>({})

// 加载场景列表
const loadScenes = async () => {
  loading.value = true
  error.value = null
  try {
    scenes.value = await sceneApi.getAllScenes()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载场景列表失败'
  } finally {
    loading.value = false
  }
}

// 显示创建表单
const showCreate = () => {
  formData.value = new CreateSceneByCurrentRequest({
    new_scene: new CreateSceneRequest({
      sid: '',
      name: '',
      is_main: false,
      summary: '',
      is_root: false
    }),
    current_scenes_id: undefined,
    character_ids: undefined
  })
  formErrors.value = {}
  showCreateForm.value = true
}

// 显示编辑表单
const showEdit = (scene: Scene) => {
  editingScene.value = scene
  formData.value = new CreateSceneByCurrentRequest({
    new_scene: new CreateSceneRequest({
      sid: scene.sid,
      name: scene.name,
      is_main: scene.is_main,
      summary: scene.summary,
      is_root: scene.is_root
    })
  })
  formErrors.value = {}
  showEditForm.value = true
}

// 显示图形视图
const showGraph = () => {
  router.push('/scenes/graph')
}

// 隐藏表单
const hideForm = () => {
  showCreateForm.value = false
  showEditForm.value = false
  editingScene.value = null
  formErrors.value = {}
}

// 验证表单
const validateForm = (): boolean => {
  formErrors.value = {}

  if (!formData.value.new_scene.sid.trim()) {
    formErrors.value.sid = '场景ID不能为空'
  }

  if (!formData.value.new_scene.name.trim()) {
    formErrors.value.name = '场景名称不能为空'
  }

  if (!formData.value.new_scene.summary.trim()) {
    formErrors.value.summary = '场景摘要不能为空'
  }

  return Object.keys(formErrors.value).length === 0
}

// 创建场景
const createScene = async () => {
  if (!validateForm()) {
    return
  }

  try {
    loading.value = true
    await sceneApi.createScene(formData.value)
    await loadScenes()
    hideForm()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '创建场景失败'
  } finally {
    loading.value = false
  }
}

// 更新场景
const updateScene = async () => {
  if (!validateForm() || !editingScene.value) {
    return
  }

  try {
    loading.value = true
    const updateData = {
      name: formData.value.new_scene.name,
      is_main: formData.value.new_scene.is_main,
      summary: formData.value.new_scene.summary,
      is_root: formData.value.new_scene.is_root
    }
    await sceneApi.updateScene(editingScene.value.sid, updateData)
    await loadScenes()
    hideForm()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '更新场景失败'
  } finally {
    loading.value = false
  }
}

// 删除场景
const deleteScene = async (scene: Scene) => {
  if (!confirm(`确定要删除场景"${scene.name}"吗？`)) {
    return
  }

  try {
    loading.value = true
    await sceneApi.deleteScene(scene.sid)
    await loadScenes()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除场景失败'
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadScenes()
})
</script>

<template>
  <div class="scene-list">
    <!-- 页面标题和操作按钮 -->
    <div class="header">
      <h1>场景管理</h1>
      <div class="actions">
        <button
          @click="showGraph"
          class="btn btn-secondary"
          :disabled="loading"
        >
          查看场景图
        </button>
        <button
          @click="showCreate"
          class="btn btn-primary"
          :disabled="loading"
        >
          创建新场景
        </button>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && !scenes.length" class="loading">
      正在加载场景列表...
    </div>

    <!-- 场景列表 -->
    <div v-if="scenes.length > 0" class="scenes-grid">
      <div
        v-for="scene in scenes"
        :key="scene.sid"
        class="scene-card"
      >
        <div class="scene-header">
          <h3>{{ scene.name }}</h3>
          <div class="badges">
            <span v-if="scene.is_main" class="badge badge-primary">主场景</span>
            <span v-if="scene.is_root" class="badge badge-success">根场景</span>
          </div>
        </div>

        <div class="scene-summary">
          <p>{{ scene.summary }}</p>
        </div>

        <div class="scene-meta">
          <small>ID: {{ scene.sid }}</small>
        </div>

        <div class="scene-actions">
          <button
            @click="showEdit(scene)"
            class="btn btn-sm btn-secondary"
            :disabled="loading"
          >
            编辑
          </button>
          <button
            @click="deleteScene(scene)"
            class="btn btn-sm btn-danger"
            :disabled="loading"
          >
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && scenes.length === 0" class="empty-state">
      <p>暂无场景，点击"创建新场景"开始创建</p>
    </div>

    <!-- 创建/编辑表单模态框 -->
    <div v-if="showCreateForm || showEditForm" class="modal-overlay" @click="hideForm">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>{{ showCreateForm ? '创建场景' : '编辑场景' }}</h2>
          <button @click="hideForm" class="close-btn">&times;</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label for="sid">场景ID *</label>
            <input
              id="sid"
              v-model="formData.new_scene.sid"
              type="text"
              class="form-control"
              :class="{ 'error': formErrors.sid }"
              placeholder="请输入场景ID"
              :disabled="showEditForm"
            />
            <span v-if="formErrors.sid" class="error-text">{{ formErrors.sid }}</span>
          </div>

          <div class="form-group">
            <label for="name">场景名称 *</label>
            <input
              id="name"
              v-model="formData.new_scene.name"
              type="text"
              class="form-control"
              :class="{ 'error': formErrors.name }"
              placeholder="请输入场景名称"
            />
            <span v-if="formErrors.name" class="error-text">{{ formErrors.name }}</span>
          </div>

          <div class="form-group">
            <label for="summary">场景摘要 *</label>
            <textarea
              id="summary"
              v-model="formData.new_scene.summary"
              class="form-control"
              :class="{ 'error': formErrors.summary }"
              rows="4"
              placeholder="请输入场景摘要"
            ></textarea>
            <span v-if="formErrors.summary" class="error-text">{{ formErrors.summary }}</span>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="formData.new_scene.is_main"
                type="checkbox"
                class="checkbox"
              />
              为主场景
            </label>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="formData.new_scene.is_root"
                type="checkbox"
                class="checkbox"
              />
              为根场景
            </label>
          </div>

          <div v-if="showCreateForm" class="form-group">
            <label for="current_scenes_id">基于场景创建（可选）</label>
            <input
              id="current_scenes_id"
              v-model="formData.current_scenes_id"
              type="text"
              class="form-control"
              placeholder="输入父场景ID（可选）"
            />
          </div>
        </div>

        <div class="modal-footer">
          <button @click="hideForm" class="btn btn-secondary">取消</button>
          <button
            @click="showCreateForm ? createScene : updateScene"
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
.scene-list {
  height: 100%;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  overflow-y: auto;
  background-color: #0a0a0a;
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

.actions {
  display: flex;
  gap: 10px;
}

.scenes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.scene-card {
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  padding: 16px;
  background: #1a1a1a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.3s;
}

.scene-card:hover {
  border-color: #3a3a3a;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  transform: translateY(-2px);
}

.scene-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.scene-header h3 {
  margin: 0;
  color: #e0e0e0;
  font-weight: 500;
}

.badges {
  display: flex;
  gap: 6px;
}

.badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-primary {
  background-color: #1e293b;
  color: #3b82f6;
  border: 1px solid #3b82f6;
}

.badge-success {
  background-color: #1e293b;
  color: #10b981;
  border: 1px solid #10b981;
}

.scene-summary {
  margin-bottom: 12px;
  color: #a0a0a0;
  font-size: 14px;
  line-height: 1.5;
}

.scene-summary p {
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.scene-meta {
  margin-bottom: 12px;
  color: #666;
  font-size: 12px;
}

.scene-actions {
  display: flex;
  gap: 8px;
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

.modal.large {
  max-width: 800px;
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

.form-control:disabled {
  background-color: #0f0f0f;
  cursor: not-allowed;
  color: #666;
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
