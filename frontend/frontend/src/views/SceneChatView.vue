<template>
  <div class="scene-chat-container">
    <!-- 场景图视图 -->
    <div v-if="!currentScene" class="scene-graph-section">
      <div class="header">
        <h2>场景聊天</h2>
        <p>点击场景开始对话</p>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <div
        ref="graphContainer"
        class="graph-container"
        :class="{ 'loading': loading }"
      ></div>

      <div class="legend">
        <h4>图例</h4>
        <div class="legend-item">
          <div class="legend-node main-scene"></div>
          <span>主场景</span>
        </div>
        <div class="legend-item">
          <div class="legend-node root-scene"></div>
          <span>根场景</span>
        </div>
        <div class="legend-item">
          <div class="legend-node normal-scene"></div>
          <span>普通场景</span>
        </div>
      </div>
    </div>

    <!-- 聊天视图 -->
    <div v-else class="chat-section">
      <div class="chat-header">
        <button @click="backToGraph" class="back-btn">
          ← 返回场景图
        </button>
        <div class="scene-info">
          <h3>{{ currentScene.name }}</h3>
          <p>{{ currentScene.summary }}</p>
        </div>
        <div class="scene-navigation">
          <div class="previous-scene-selector" v-if="previousScenes.length > 0">
            <select v-if="previousScenes.length > 1" v-model="selectedPreviousSceneId" class="previous-scene-dropdown" @change="handlePreviousSceneSelect">
              <option value="">选择父情景...</option>
              <option v-for="scene in previousScenes" :key="scene.id" :value="scene.id">
                {{ scene.label }}
              </option>
            </select>
            <button @click="goToPreviousScene" class="nav-btn" :disabled="previousScenes.length === 0">
              ← 上一个
            </button>
          </div>
          <button @click="createNextScene" class="nav-btn create-btn">
            + 创建下一情景
          </button>
          <div class="next-scene-selector" v-if="nextScenes.length > 0">
            <button @click="goToNextScene" class="nav-btn" :disabled="nextScenes.length === 0">
              下一个 →
            </button>
            <select v-if="nextScenes.length > 1" v-model="selectedNextSceneId" class="next-scene-dropdown" @change="handleNextSceneSelect">
              <option value="">选择分支...</option>
              <option v-for="scene in nextScenes" :key="scene.id" :value="scene.id">
                {{ scene.label }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="chat-content">
        <!-- 移动端遮罩层 -->
        <div v-if="isMobile && !isSidebarCollapsed" class="mobile-overlay" @click="closeSidebar"></div>

        <!-- 左侧：场景角色管理 -->
        <div class="sidebar" :class="{
          'sidebar-collapsed': isSidebarCollapsed && !isMobile,
          'sidebar-open': !isSidebarCollapsed && isMobile
        }">
          <button v-if="!isMobile" class="sidebar-toggle" @click="toggleSidebar">
            <span v-if="!isSidebarCollapsed">←</span>
            <span v-else>→</span>
          </button>

          <div v-if="!isSidebarCollapsed" class="sidebar-content">
            <div class="sidebar-section">
              <h4>场景角色</h4>
              <div v-if="sceneCharacters.length <= 6" class="character-list">
                <div
                  v-for="char in sceneCharacters"
                  :key="char.character_id"
                  class="character-item"
                  :class="{ 'selected': selectedCharacterIds.includes(char.character_id) }"
                  @click="openCharacterModal(char)"
                >
                  <span>{{ char.name }}</span>
                  <div class="character-status">
                    <span v-if="char.is_visible" class="status-visible" title="可见">✓</span>
                    <span v-else class="status-invisible" title="不可见">✗</span>
                  </div>
                </div>
                <div v-if="sceneCharacters.length === 0" class="empty-text">
                  暂无角色
                </div>
              </div>
              <div v-else class="character-dropdown">
                <select
                  v-model="selectedCharacterIds"
                  multiple
                  class="form-control character-select"
                  @change="handleCharacterDropdownChange"
                >
                  <option
                    v-for="char in sceneCharacters"
                    :key="char.character_id"
                    :value="char.character_id"
                  >
                    {{ char.name }}
                  </option>
                </select>
                <div class="dropdown-hint">
                  已选择 {{ selectedCharacterIds.length }} 个角色
                </div>
              </div>
            </div>

            <div class="sidebar-section">
              <h4>添加角色</h4>
              <div class="add-character-form">
                <select v-model="selectedCharacterToAdd" class="form-control">
                  <option value="">选择角色</option>
                  <option
                    v-for="char in availableCharacters"
                    :key="char.character_id"
                    :value="char.character_id"
                  >
                    {{ char.name }}
                  </option>
                </select>
                <button
                  @click="addCharacterToScene"
                  :disabled="!selectedCharacterToAdd"
                  class="btn btn-sm btn-primary"
                >
                  添加
                </button>
              </div>
            </div>

            <div class="sidebar-section">
              <h4>创建新角色</h4>
              <div class="create-character-form">
                <input
                  v-model="newCharacterName"
                  type="text"
                  placeholder="角色名称"
                  class="form-control"
                />
                <button
                  @click="createNewCharacter"
                  :disabled="!newCharacterName.trim()"
                  class="btn btn-sm btn-success"
                >
                  创建并添加
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：聊天区域 -->
        <div class="chat-main">
          <!-- 角色选择 -->
          <div class="role-selection">
            <div class="role-select">
              <label>我的角色：</label>
              <select v-model="selectedUserCharacterId" class="form-control">
                <option value="">选择角色</option>
                <option
                  v-for="char in sceneCharacters"
                  :key="char.character_id"
                  :value="char.character_id"
                >
                  {{ char.name }}
                </option>
              </select>
            </div>

            <div class="role-select">
              <label>LLM扮演：</label>
              <select v-model="selectedLLMCharacterId" class="form-control">
                <option value="">选择角色</option>
                <option
                  v-for="char in sceneCharacters"
                  :key="char.character_id"
                  :value="char.character_id"
                >
                  {{ char.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- 输出模式选择 -->
          <div class="output-mode">
            <label class="streaming-toggle">
              <input
                type="checkbox"
                v-model="isStreaming"
                :disabled="isLLMReplying"
              />
              <span class="toggle-slider"></span>
              <span class="toggle-label">
                {{ isStreaming ? '流式输出' : '非流式输出' }}
              </span>
            </label>
            <span v-if="!isStreaming && isLLMReplying" class="replying-indicator">
              LLM正在回复...
            </span>
            <div v-if="isLLMReplying && isStreaming" class="streaming-indicator">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>

          <!-- 对话历史 -->
          <div class="chat-history" ref="chatHistoryRef">
            <div v-if="chatMessages.length > 0" class="chat-history-header">
              对话历史
            </div>
            <div
              v-for="msg in chatMessages"
              :key="msg.id"
              class="message"
              :class="{ 'user': msg.sender === 'user', 'assistant': msg.sender === 'assistant' }"
            >
              <div class="message-header">
                <div class="message-info">
                  <strong>{{ msg.senderName }}</strong>
                  <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
                </div>
                <div class="message-actions" v-if="!isLLMReplying">
                  <button
                    v-if="!msg.isEditing && msg.sender === 'user' && isLastUserMessage(msg)"
                    @click="regenerateMessage(msg)"
                    class="action-btn regenerate-btn"
                    title="重新生成"
                  >
                    ↻
                  </button>
                  <button
                    v-if="!msg.isEditing"
                    @click="startEditMessage(msg)"
                    class="action-btn edit-btn"
                    title="编辑"
                  >
                    ✎
                  </button>
                  <button
                    v-if="!msg.isEditing"
                    @click="deleteMessage(msg)"
                    class="action-btn delete-btn"
                    title="删除"
                  >
                    🗑
                  </button>
                  <button
                    v-if="msg.isEditing"
                    @click="saveEditMessage(msg)"
                    class="action-btn save-btn"
                    title="保存"
                  >
                    ✓
                  </button>
                  <button
                    v-if="msg.isEditing"
                    @click="cancelEditMessage(msg)"
                    class="action-btn cancel-btn"
                    title="取消"
                  >
                    ×
                  </button>
                </div>
              </div>
              <div class="message-content">
                <div v-if="!msg.isEditing">{{ msg.content }}</div>
                <textarea
                  v-else
                  v-model="msg.editContent"
                  @keydown="handleEditKeyDown($event, msg)"
                  class="edit-textarea"
                  rows="3"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input">
            <textarea
              v-model="inputMessage"
              @keydown="handleKeyDown"
              placeholder="输入消息..."
              class="form-control"
              rows="2"
              :disabled="!canSendMessage"
            ></textarea>
            <button
              @click="sendMessage"
              :disabled="!canSendMessageWithContent"
              class="btn btn-primary send-btn"
            >
              发送
            </button>
          </div>
        </div>

        <!-- 移动端侧边栏切换按钮 -->
        <button
          v-if="isMobile"
          class="mobile-sidebar-toggle"
          @click="toggleSidebar"
          title="切换侧边栏"
        >
          <span v-if="isSidebarCollapsed">+</span>
          <span v-else>−</span>
        </button>
      </div>
    </div>
  </div>

  <!-- 角色信息弹窗 -->
  <div v-if="showCharacterModal" class="modal-overlay" @click="closeCharacterModal">
    <div class="character-modal" @click.stop>
      <div class="modal-header">
        <h3>角色信息</h3>
        <button @click="closeCharacterModal" class="close-btn">×</button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label>角色名称</label>
          <input
            v-model="editingCharacter.name"
            type="text"
            class="form-control"
            placeholder="角色名称"
          />
        </div>

        <!-- <div class="form-group">
          <label>角色描述</label>
          <textarea
            v-model="editingCharacter.description"
            class="form-control"
            placeholder="角色描述"
            rows="3"
          ></textarea>
        </div> -->

        <div class="form-group">
          <label>角色设定</label>
          <textarea
            v-model="editingCharacter.personality"
            class="form-control"
            placeholder="角色设定、性格等"
            rows="4"
          ></textarea>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="editingCharacter.is_visible"
            />
            <span class="checkmark"></span>
            在场景中可见
          </label>
          <p class="help-text">取消勾选后，该角色在此场景中不可见，但仍会保留在角色列表中</p>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="removeCharacterFromScene" class="btn btn-danger">
          移除角色
        </button>
        <button @click="closeCharacterModal" class="btn btn-secondary">
          取消
        </button>
        <button @click="updateCharacter" class="btn btn-primary">
          保存
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import cytoscape, { type Core } from 'cytoscape'
import { useRoute, useRouter } from 'vue-router'
import { sceneApi } from '@/api/scene'
import { characterApi } from '@/api/character'
import { chatApi } from '@/api/chat'
import { conversationApi } from '@/api/conversation'
import { Scene, Character } from '@/beans'

const route = useRoute()
const router = useRouter()

const graphContainer = ref<HTMLElement>()
const chatHistoryRef = ref<HTMLElement>()
const loading = ref(false)
const error = ref('')
const currentScene = ref<Scene | null>(null)
const cy = ref<Core | null>(null)

// 数据
const sceneGraph = ref<any>(null)
const allCharacters = ref<Character[]>([])
const sceneCharacters = ref<Character[]>([])
const chatMessages = ref<any[]>([])

// 情景导航相关
const sceneHistory = ref<string[]>([]) // 访问历史
const sceneHistoryIndex = ref(-1) // 当前在历史中的位置
const nextScenes = ref<any[]>([]) // 当前情景的下一级情景（分支）
const previousScenes = ref<any[]>([]) // 当前情景的上一级情景（父情景）
const selectedNextSceneId = ref<string>('') // 用户选择的下一个情景ID
const selectedPreviousSceneId = ref<string>('') // 用户选择的父情景ID

// 表单数据
const selectedCharacterToAdd = ref<string>('')
const newCharacterName = ref('')
const selectedCharacterIds = ref<number[]>([])
const selectedUserCharacterId = ref<number | null>(null)
const selectedLLMCharacterId = ref<number | null>(null)
const inputMessage = ref('')
const isStreaming = ref(true) // 是否使用流式输出
const isLLMReplying = ref(false) // LLM是否正在回复

// 侧边栏相关
const isSidebarCollapsed = ref(false)
const isMobile = ref(false)

// 角色弹窗相关
const showCharacterModal = ref(false)
const editingCharacter = ref<any>({
  character_id: null,
  name: '',
  description: '',
  personality: '',
  is_visible: true
})

// 切换侧边栏
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

// 关闭侧边栏（移动端）
const closeSidebar = () => {
  isSidebarCollapsed.value = true
}

// 打开角色信息弹窗
const openCharacterModal = async (character: any) => {
  try {
    // 从API获取最新的角色信息
    const latestCharacter = await characterApi.getCharacterById(character.character_id)
    editingCharacter.value = {
      character_id: latestCharacter.character_id,
      name: latestCharacter.name || '',
      description: latestCharacter.prompt || '',
      personality: latestCharacter.prompt || '',
      is_visible: latestCharacter.is_visible !== false
    }
    showCharacterModal.value = true
  } catch (err) {
    console.error('Failed to load character:', err)
    // 如果获取失败，使用本地数据
    editingCharacter.value = {
      character_id: character.character_id,
      name: character.name || '',
      description: character.prompt || '',
      personality: character.prompt || '',
      is_visible: character.is_visible !== false
    }
    showCharacterModal.value = true
  }
}

// 关闭角色信息弹窗
const closeCharacterModal = () => {
  showCharacterModal.value = false
  editingCharacter.value = {
    character_id: null,
    name: '',
    description: '',
    personality: '',
    is_visible: true
  }
}

// 更新角色信息
const updateCharacter = async () => {
  if (!editingCharacter.value.character_id || !currentScene.value) {
    console.log(editingCharacter.value.character_id, currentScene.value)
    return
  }

  try {
    // 调用更新角色API
    await characterApi.updateCharacter(editingCharacter.value.character_id, {
      name: editingCharacter.value.name,
      prompt: editingCharacter.value.personality || editingCharacter.value.description,
      is_visible: editingCharacter.value.is_visible
    })

    // 重新加载所有角色和场景角色列表
    await loadAllCharacters()
    await loadSceneCharacters(currentScene.value.sid)

    closeCharacterModal()
  } catch (err) {
    console.error('Failed to update character:', err)
    alert('更新角色失败: ' + (err instanceof Error ? err.message : String(err)))
  }
}

// 从场景中移除角色
const removeCharacterFromScene = async () => {
  if (!editingCharacter.value.character_id || !currentScene.value) return

  // 确认对话框
  const confirmed = confirm('确定要从当前场景中移除这个角色吗？\n\n注意：这不会删除角色本身，只是将其从当前场景中移除。')
  if (!confirmed) return

  try {
    // 调用移除角色API
    await characterApi.disconnectCharacterFromScene(
      editingCharacter.value.character_id,
      currentScene.value.sid
    )

    // 重新加载场景角色列表
    await loadSceneCharacters(currentScene.value.sid)

    closeCharacterModal()
  } catch (err) {
    console.error('Failed to remove character from scene:', err)
    alert('移除角色失败: ' + (err instanceof Error ? err.message : String(err)))
  }
}

// 处理角色下拉选择变化
const handleCharacterDropdownChange = () => {
  // 多选下拉框变化处理
  console.log('Selected character IDs:', selectedCharacterIds.value)
}

// 检测移动端
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

// 计算属性
const availableCharacters = computed(() => {
  return allCharacters.value.filter(
    char => !sceneCharacters.value.find(sc => sc.character_id === char.character_id)
  )
})

const canSendMessage = computed(() => {
  return currentScene.value &&
         selectedUserCharacterId.value &&
         selectedLLMCharacterId.value
})

const canSendMessageWithContent = computed(() => {
  return canSendMessage.value && inputMessage.value.trim().length > 0
})

// 情景导航计算属性
const canGoPrevious = computed(() => {
  return previousScenes.value.length > 0
})

const canGoNext = computed(() => {
  return nextScenes.value.length > 0
})

// 监听路由参数变化
watch(() => route.query.sceneId, (newSceneId) => {
  if (newSceneId && sceneGraph.value) {
    // 找到对应的节点数据
    const node = sceneGraph.value.nodes.find((n: any) => n.sid === newSceneId)
    if (node) {
      // 转换为节点数据格式并选择场景
      const nodeData = {
        id: node.sid,
        label: node.name,
        is_main: node.is_main,
        is_root: node.is_root,
        summary: node.summary
      }
      selectScene(nodeData)
    }
  }
})

// 获取并渲染场景图
const loadGraph = async () => {
  if (!graphContainer.value) return

  loading.value = true
  error.value = ''

  try {
    const graph = await sceneApi.getScenesGraph()
    sceneGraph.value = graph

    // 转换为Cytoscape格式
    const elements = [
      ...graph.nodes.map((node: any) => ({
        data: {
          id: node.sid,
          label: node.name,
          is_main: node.is_main,
          is_root: node.is_root,
          summary: node.summary
        },
        classes: getNodeClass(node)
      })),
      ...graph.edges.map((edge: any) => ({
        data: {
          id: `${edge.source}-${edge.target}`,
          source: edge.source,
          target: edge.target
        }
      }))
    ]

    // 创建或更新Cytoscape实例
    if (cy.value) {
      cy.value.destroy()
    }

    cy.value = cytoscape({
      container: graphContainer.value,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#666',
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'color': '#fff',
            'text-outline-width': '2px',
            'text-outline-color': '#666',
            'font-size': '12px',
            'font-weight': 'bold',
            'width': '60px',
            'height': '60px',
            'cursor': 'pointer'
          } as any
        },
        {
          selector: 'node.main-scene',
          style: {
            'background-color': '#e74c3c',
            'text-outline-color': '#e74c3c'
          } as any
        },
        {
          selector: 'node.root-scene',
          style: {
            'background-color': '#f39c12',
            'text-outline-color': '#f39c12'
          } as any
        },
        {
          selector: 'node.normal-scene',
          style: {
            'background-color': '#3498db',
            'text-outline-color': '#3498db'
          } as any
        },
        {
          selector: ':selected',
          style: {
            'background-color': '#2ecc71',
            'line-color': '#2ecc71',
            'target-arrow-color': '#2ecc71',
            'text-outline-color': '#2ecc71'
          } as any
        }
      ],
      layout: {
        name: 'cose',
        idealEdgeLength: 100,
        nodeOverlap: 20,
        refresh: 20,
        fit: true,
        padding: 30,
        randomize: false,
        componentSpacing: 100,
        nodeRepulsion: 400000,
        edgeElasticity: 100,
        nestingFactor: 5,
        gravity: 80,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0
      },
      selectionType: 'single',
      boxSelectionEnabled: false,
      autoungrabify: false,
      autolock: false,
      panningEnabled: true,
      zoomingEnabled: true,
      userZoomingEnabled: true,
      userPanningEnabled: true,
    })

    // 添加点击事件
    cy.value.on('tap', 'node', (evt) => {
      const node = evt.target
      const data = node.data()
      selectScene(data)
    })

    cy.value.ready(() => {
      if (cy.value) {
        cy.value.fit()
      }
    })

  } catch (err) {
    error.value = '加载场景图失败: ' + (err instanceof Error ? err.message : String(err))
    console.error('Error loading scene graph:', err)
  } finally {
    loading.value = false
  }
}

// 选择场景
const selectScene = async (nodeData: any) => {
  const scene = new Scene({
    sid: nodeData.id,
    name: nodeData.label,
    is_main: nodeData.is_main,
    summary: nodeData.summary,
    is_root: nodeData.is_root
  })
  currentScene.value = scene

  // 更新访问历史
  if (sceneHistoryIndex.value < sceneHistory.value.length - 1) {
    // 如果当前不在历史末尾，截断历史
    sceneHistory.value = sceneHistory.value.slice(0, sceneHistoryIndex.value + 1)
  }
  sceneHistory.value.push(scene.sid)
  sceneHistoryIndex.value = sceneHistory.value.length - 1

  await loadAllCharacters()
  await loadSceneCharacters(scene.sid)
  // 确保角色加载完成后再加载对话历史
  await loadSceneConversations(scene.sid)
  // 加载下一级情景
  await loadNextScenes(scene.sid)
  // 加载上一级情景
  await loadPreviousScenes(scene.sid)
}

// 加载所有角色
const loadAllCharacters = async () => {
  try {
    allCharacters.value = await characterApi.getAllCharacters()
  } catch (err) {
    console.error('Failed to load characters:', err)
  }
}

// 加载场景角色
const loadSceneCharacters = async (sceneId: string) => {
  try {
    const characters = await sceneApi.getSceneCharacters(sceneId)
    console.log('Loaded scene characters:', characters)
    sceneCharacters.value = characters.map((c: any) => new Character(c.character))

    // 更新所有消息的发送者名称，以反映最新的角色信息
    updateAllMessageSenderNames()
  } catch (err) {
    console.error('Failed to load scene characters:', err)
  }
}

// 更新所有消息的发送者名称
const updateAllMessageSenderNames = () => {
  chatMessages.value.forEach(msg => {
    if (msg.sender === 'user') {
      // 对于用户消息，根据 sender_id 查找角色名称
      const character = sceneCharacters.value.find(c => c.character_id === msg.sender_id)
      if (character) {
        msg.senderName = character.name
      }
    } else if (msg.sender === 'assistant') {
      // 对于助手消息，根据当前选择的LLM角色更新
      const llmChar = sceneCharacters.value.find(c => c.character_id === selectedLLMCharacterId.value)
      if (llmChar) {
        msg.senderName = llmChar.name
      }
    }
  })
}

// 加载场景对话历史
const loadSceneConversations = async (sceneId: string) => {
  try {
    const conversations = await conversationApi.getConversationsBySceneId(sceneId)
    chatMessages.value = conversations.map(conv => {
      // 根据 sender_id 查找角色
      const senderCharacter = sceneCharacters.value.find(
        c => c.character_id === conv.sender_id
      )
      // 如果找到了角色，使用角色名称，否则使用对话中保存的 role
      const senderName = senderCharacter ? senderCharacter.name : conv.role

      return {
        id: conv.conversation_id || Date.now(),
        sender: conv.role, // 历史对话都显示为assistant，避免与当前用户消息混淆
        senderName: senderName,
        content: conv.message,
        timestamp: new Date(),
        isEditing: false,
        editContent: '',
        conversationId: conv.conversation_id, // 保存原始对话ID以便编辑
        sender_id: conv.sender_id // 保存发送者ID以便后续更新发送者名称
      }
    })
    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error('Failed to load scene conversations:', err)
  }
}

// 加载下一级情景（分支）
const loadNextScenes = async (sceneId: string) => {
  if (!sceneGraph.value) return

  // 从场景图中找到当前情景的下一级情景
  const edges = sceneGraph.value.edges.filter((edge: any) => edge.source === sceneId)
  nextScenes.value = edges.map((edge: any) => {
    const node = sceneGraph.value.nodes.find((n: any) => n.sid === edge.target)
    return {
      id: node.sid,
      label: node.name,
      is_main: node.is_main,
      is_root: node.is_root,
      summary: node.summary
    }
  })
  // 重置选择
  selectedNextSceneId.value = ''
}

// 加载上一级情景（父情景）
const loadPreviousScenes = async (sceneId: string) => {
  if (!sceneGraph.value) return

  // 从场景图中找到指向当前情景的上一级情景
  const edges = sceneGraph.value.edges.filter((edge: any) => edge.target === sceneId)
  previousScenes.value = edges.map((edge: any) => {
    const node = sceneGraph.value.nodes.find((n: any) => n.sid === edge.source)
    return {
      id: node.sid,
      label: node.name,
      is_main: node.is_main,
      is_root: node.is_root,
      summary: node.summary
    }
  })
  // 重置选择
  selectedPreviousSceneId.value = ''
}

// 添加角色到场景
const addCharacterToScene = async () => {
  if (!currentScene.value || !selectedCharacterToAdd.value) return

  try {
    await sceneApi.connectCharacterToScene(currentScene.value.sid, {
      character_id: Number(selectedCharacterToAdd.value),
      is_visible: true
    })
    await loadSceneCharacters(currentScene.value.sid)
    selectedCharacterToAdd.value = ''
  } catch (err) {
    console.error('Failed to add character:', err)
  }
}

// 创建新角色
const createNewCharacter = async () => {
  if (!currentScene.value || !newCharacterName.value.trim()) return

  try {
    const character = await characterApi.createCharacterByName({
      name: newCharacterName.value.trim(),
      is_visible: true
    })

    await sceneApi.connectCharacterToScene(currentScene.value.sid, {
      character_id: character.character_id,
      is_visible: true
    })

    await loadAllCharacters()
    await loadSceneCharacters(currentScene.value.sid)
    newCharacterName.value = ''
  } catch (err) {
    console.error('Failed to create character:', err)
  }
}

// 发送消息
const sendMessage = async () => {
  if (!canSendMessageWithContent.value) return

  const userChar = sceneCharacters.value.find(c => c.character_id === selectedUserCharacterId.value)
  const llmChar = sceneCharacters.value.find(c => c.character_id === selectedLLMCharacterId.value)

  if (!userChar || !llmChar || !currentScene.value || !selectedUserCharacterId.value || !selectedLLMCharacterId.value) return

  const sentMessage = inputMessage.value

  // 添加用户消息（conversationId稍后从响应中获取）
  // 使用Date.now() + 随机数确保唯一性
  const userMessageId = Date.now() + Math.floor(Math.random() * 1000)
  const userMessage = {
    id: userMessageId,
    sender: 'user',
    senderName: userChar.name,
    content: sentMessage,
    timestamp: new Date(),
    isEditing: false,
    editContent: '',
    conversationId: null,
    sender_id: selectedUserCharacterId.value // 保存发送者ID以便后续更新发送者名称
  }
  chatMessages.value.push(userMessage)
  inputMessage.value = ''

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // 非流式模式下显示"LLM正在回复..."
  if (!isStreaming.value) {
    isLLMReplying.value = true
  }

  try {
    if (isStreaming.value) {
      // 流式输出模式
      isLLMReplying.value = true
      // 使用Date.now() + 随机数确保唯一性
      const assistantMessageId = Date.now() + Math.floor(Math.random() * 1000) + 1

      // 创建初始的空回复消息
      const initialMessage = {
        id: assistantMessageId,
        sender: 'assistant',
        senderName: llmChar.name,
        content: '',
        timestamp: new Date(),
        isEditing: false,
        editContent: '',
        conversationId: null, // 初始消息没有conversationId
        sender_id: selectedLLMCharacterId.value // 保存发送者ID以便后续更新发送者名称
      }
      chatMessages.value.push(initialMessage)
      await nextTick()
      scrollToBottom()

      // 调用流式聊天API
      const stream = await chatApi.sendMessageStream({
        roleplay_id: selectedLLMCharacterId.value,
        conversation: {
          message: sentMessage,
          sid: currentScene.value.sid,
          sender_id: selectedUserCharacterId.value,
          role: "user"
        },
        stream: true
      })

      // 处理流式数据
      let hasReceivedContent = false
      let currentContent = ''
      let userConversationId: number | null = null
      let assistantConversationId: number | null = null

      try {
        for await (const chunk of stream) {
          if (chunk && chunk.type === 'ids') {
            // 第一个数据包包含conversation_id
            userConversationId = chunk.user_conversation_id || null
            assistantConversationId = chunk.assistant_conversation_id || null

            // 更新用户消息的conversationId
            const userMessageIndex = chatMessages.value.findIndex(m => m.id === userMessage.id)
            if (userMessageIndex !== -1 && userConversationId) {
              chatMessages.value[userMessageIndex] = {
                ...chatMessages.value[userMessageIndex],
                conversationId: userConversationId
              }
            }

            // 更新助手消息的conversationId
            const assistantMessageIndex = chatMessages.value.findIndex(m => m.id === assistantMessageId)
            if (assistantMessageIndex !== -1 && assistantConversationId) {
              chatMessages.value[assistantMessageIndex] = {
                ...chatMessages.value[assistantMessageIndex],
                conversationId: assistantConversationId
              }
            }
          } else if (chunk && chunk.data && chunk.data.content) {
            hasReceivedContent = true
            currentContent += chunk.data.content

            // 找到chatMessages中的assistantMessage并更新它
            const messageIndex = chatMessages.value.findIndex(m => m.id === assistantMessageId)
            if (messageIndex !== -1) {
              // 重新构建整个消息对象，触发Vue的响应式更新
              chatMessages.value[messageIndex] = {
                id: assistantMessageId,
                sender: 'assistant',
                senderName: llmChar.name,
                content: currentContent,
                timestamp: chatMessages.value[messageIndex].timestamp,
                isEditing: false,
                editContent: '',
                conversationId: chatMessages.value[messageIndex].conversationId, // 保持现有的conversationId
                sender_id: chatMessages.value[messageIndex].sender_id // 保持现有的sender_id
              }
            }

            await nextTick()
            scrollToBottom()
          }
        }
      } catch (streamError) {
        console.error('流式读取错误:', streamError)
        throw streamError
      } finally {
        isLLMReplying.value = false
      }

      // 如果没有接收到任何内容，显示提示
      if (!hasReceivedContent) {
        const messageIndex = chatMessages.value.findIndex(m => m.id === assistantMessageId)
        if (messageIndex !== -1) {
          chatMessages.value[messageIndex] = {
            id: assistantMessageId,
            sender: 'assistant',
            senderName: llmChar.name,
            content: '抱歉，没有收到回复内容',
            timestamp: chatMessages.value[messageIndex].timestamp,
            isEditing: false,
            editContent: '',
            conversationId: null,
            sender_id: chatMessages.value[messageIndex].sender_id // 保持现有的sender_id
          }
        }
      }
    } else {
      // 非流式输出模式
      isLLMReplying.value = true

      const result = await chatApi.sendMessage({
        roleplay_id: selectedLLMCharacterId.value,
        conversation: {
          message: sentMessage,
          sid: currentScene.value.sid,
          sender_id: selectedUserCharacterId.value,
          role: "user"
        },
        stream: false
      })

      isLLMReplying.value = false

      if (result.code === 200 && result.data) {
        // 使用后端返回的conversation_id
        const userConversationId = result.data.user_conversation_id || null
        const assistantConversationId = result.data.assistant_conversation_id || null

        // 更新用户消息的conversationId
        const userMessageIndex = chatMessages.value.findIndex(m => m.id === userMessage.id)
        if (userMessageIndex !== -1 && userConversationId) {
          chatMessages.value[userMessageIndex] = {
            ...chatMessages.value[userMessageIndex],
            conversationId: userConversationId
          }
        }

        // 添加LLM回复
        // 使用Date.now() + 随机数确保唯一性
        const assistantMessageId = Date.now() + Math.floor(Math.random() * 1000) + 2
        const assistantMessage = {
          id: assistantMessageId,
          sender: 'assistant',
          senderName: llmChar.name,
          content: result.data.response || '',
          timestamp: new Date(),
          isEditing: false,
          editContent: '',
          conversationId: assistantConversationId,
          sender_id: selectedLLMCharacterId.value // 保存发送者ID以便后续更新发送者名称
        }
        chatMessages.value.push(assistantMessage)
      } else {
        throw new Error(result.message || '聊天失败')
      }
    }

    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error('Failed to send message:', err)
    isLLMReplying.value = false
    // 添加错误消息
    // 使用Date.now() + 随机数确保唯一性
    const errorMessageId = Date.now() + Math.floor(Math.random() * 1000) + 3
    chatMessages.value.push({
      id: errorMessageId,
      sender: 'assistant',
      senderName: '系统',
      content: '发送失败: ' + (err instanceof Error ? err.message : String(err)),
      timestamp: new Date(),
      isEditing: false,
      editContent: '',
      conversationId: null // 错误消息不需要保存到数据库
    })
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatHistoryRef.value) {
    chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
  }
}

// 开始编辑消息
const startEditMessage = (msg: any) => {
  const index = chatMessages.value.findIndex(m => m.id === msg.id)
  if (index !== -1) {
    // 重新构建消息对象以触发响应式更新
    chatMessages.value[index] = {
      ...chatMessages.value[index],
      isEditing: true,
      editContent: msg.content
    }
  }
}

// 保存编辑
const saveEditMessage = async (msg: any) => {
  if (!msg.editContent.trim()) {
    alert('消息内容不能为空')
    return
  }

  // 如果是历史对话（从数据库加载的），需要调用API更新
  if (msg.conversationId && currentScene.value) {
    try {
      // 找到发送者角色
      const senderCharacter = sceneCharacters.value.find(
        c => c.name === msg.senderName
      )

      if (senderCharacter) {
        await conversationApi.updateConversation(msg.conversationId, {
          message: msg.editContent.trim(),
          sid: currentScene.value.sid,
          sender_id: senderCharacter.character_id,
          role: msg.sender
        })
      }
    } catch (err) {
      console.error('Failed to update conversation:', err)
      alert('更新对话失败: ' + (err instanceof Error ? err.message : String(err)))
      return
    }
  }

  // 更新本地消息内容 - 重新构建消息对象以触发响应式更新
  const index = chatMessages.value.findIndex(m => m.id === msg.id)
  if (index !== -1) {
    chatMessages.value[index] = {
      ...chatMessages.value[index],
      content: msg.editContent.trim(),
      isEditing: false,
      editContent: ''
    }
  }
}

// 取消编辑
const cancelEditMessage = (msg: any) => {
  const index = chatMessages.value.findIndex(m => m.id === msg.id)
  if (index !== -1) {
    // 重新构建消息对象以触发响应式更新
    chatMessages.value[index] = {
      ...chatMessages.value[index],
      isEditing: false,
      editContent: ''
    }
  }
}

// 创建下一个情景
const createNextScene = async () => {
  if (!currentScene.value) return

  try {
    // 生成新场景名称
    const newSceneNumber = nextScenes.value.length + 1
    const newSceneName = `${currentScene.value.name}_分支${newSceneNumber}`

    // 获取当前场景的角色ID列表
    const characterIds = sceneCharacters.value.map(char => char.character_id)

    // 调用创建场景API
    const newScene = await sceneApi.createScene({
      new_scene: {
        name: newSceneName,
        summary: `${currentScene.value.name}的分支情景`,
        is_main: false,
        is_root: false,
        sid: '' // 让后端自动生成
      },
      current_scenes_id: currentScene.value.sid,
      character_ids: characterIds
    })

    // 重新加载场景图
    await loadGraph()

    // 导航到新创建的场景
    if (newScene) {
      selectScene({
        id: newScene.sid,
        label: newScene.name,
        is_main: newScene.is_main,
        summary: newScene.summary,
        is_root: newScene.is_root
      })
    }

    alert(`成功创建新情景：${newSceneName}`)
  } catch (err) {
    console.error('Failed to create next scene:', err)
    alert('创建下一情景失败: ' + (err instanceof Error ? err.message : String(err)))
  }
}

// 返回上一个情景
const goToPreviousScene = () => {
  if (!currentScene.value || !canGoPrevious.value) return

  if (previousScenes.value.length === 0) {
    alert('当前情景没有上一级情景')
    return
  }

  if (previousScenes.value.length === 1) {
    // 只有一个父情景，直接进入
    const previousScene = previousScenes.value[0]
    selectScene(previousScene)
  } else if (previousScenes.value.length > 1) {
    // 多个父情景，提示用户使用下拉选择器
    if (!selectedPreviousSceneId.value) {
      alert('请先从左侧下拉菜单中选择要返回的父情景')
      return
    }
    const selectedScene = previousScenes.value.find(s => s.id === selectedPreviousSceneId.value)
    if (selectedScene) {
      selectScene(selectedScene)
    }
  }
}

// 进入下一个情景
const goToNextScene = () => {
  if (!currentScene.value) return

  if (nextScenes.value.length === 0) {
    alert('当前情景没有下一级情景')
    return
  }

  if (nextScenes.value.length === 1) {
    // 只有一个分支，直接进入
    const nextScene = nextScenes.value[0]
    selectScene(nextScene)
  } else if (nextScenes.value.length > 1) {
    // 多个分支，提示用户使用下拉选择器
    if (!selectedNextSceneId.value) {
      alert('请先从右侧下拉菜单中选择要进入的分支情景')
      return
    }
    const selectedScene = nextScenes.value.find(s => s.id === selectedNextSceneId.value)
    if (selectedScene) {
      selectScene(selectedScene)
    }
  }
}

// 处理下一个情景下拉选择
const handleNextSceneSelect = () => {
  if (selectedNextSceneId.value) {
    const selectedScene = nextScenes.value.find(s => s.id === selectedNextSceneId.value)
    if (selectedScene) {
      selectScene(selectedScene)
    }
  }
}

// 处理上一个情景下拉选择
const handlePreviousSceneSelect = () => {
  if (selectedPreviousSceneId.value) {
    const selectedScene = previousScenes.value.find(s => s.id === selectedPreviousSceneId.value)
    if (selectedScene) {
      selectScene(selectedScene)
    }
  }
}

// 处理编辑框的键盘事件
const handleEditKeyDown = (e: KeyboardEvent, msg: any) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    saveEditMessage(msg)
  } else if (e.key === 'Escape') {
    e.preventDefault()
    cancelEditMessage(msg)
  }
}

// 删除消息
const deleteMessage = async (msg: any) => {
  // 确认对话框
  const confirmed = confirm('确定要删除这条消息吗？')
  if (!confirmed) return

  console.log('Deleting message:', msg)

  // 如果是历史对话（从数据库加载的），需要调用API删除
  if (msg.conversationId) {
    try {
      await conversationApi.deleteConversation(msg.conversationId)
    } catch (err) {
      console.error('Failed to delete conversation:', err)
      alert('删除对话失败: ' + (err instanceof Error ? err.message : String(err)))
      return
    }
  }

  // 从本地消息列表中移除
  const index = chatMessages.value.findIndex(m => m.id === msg.id)
  if (index !== -1) {
    chatMessages.value.splice(index, 1)
  }
}

// 检查是否是最后一条用户消息
const isLastUserMessage = (msg: any) => {
  // 从后往前找，找到第一个用户消息
  for (let i = chatMessages.value.length - 1; i >= 0; i--) {
    if (chatMessages.value[i].sender === 'user') {
      // 如果这条消息就是要检查的消息，且不是正在编辑中，则显示重新生成按钮
      return chatMessages.value[i].id === msg.id && !msg.isEditing
    }
  }
  return false
}

// 重新生成消息
const regenerateMessage = async (msg: any) => {
  if (!canSendMessage.value) {
    alert('请先选择用户角色和LLM角色')
    return
  }

  // 确认对话框
  const confirmed = confirm('确定要重新生成回复吗？')
  if (!confirmed) return

  const userChar = sceneCharacters.value.find(c => c.character_id === selectedUserCharacterId.value)
  const llmChar = sceneCharacters.value.find(c => c.character_id === selectedLLMCharacterId.value)

  if (!userChar || !llmChar || !currentScene.value || !selectedUserCharacterId.value || !selectedLLMCharacterId.value) {
    alert('角色信息不完整')
    return
  }

  // 找到当前用户消息的索引
  const messageIndex = chatMessages.value.findIndex(m => m.id === msg.id)
  if (messageIndex === -1) return

  // 如果是历史对话（从数据库加载的），需要调用API删除原始用户消息
  if (msg.conversationId) {
    try {
      await conversationApi.deleteConversation(msg.conversationId)
    } catch (err) {
      console.error('Failed to delete conversation:', err)
      alert('删除原始对话失败: ' + (err instanceof Error ? err.message : String(err)))
      return
    }
  }

  // 如果该用户消息后面还有assistant消息，则删除它们
  for (let i = messageIndex + 1; i < chatMessages.value.length; i++) {
    const nextMsg = chatMessages.value[i]
    if (nextMsg.sender === 'assistant') {
      // 如果是历史对话，需要调用API删除
      if (nextMsg.conversationId) {
        try {
          await conversationApi.deleteConversation(nextMsg.conversationId)
        } catch (err) {
          console.error('Failed to delete conversation:', err)
        }
      }
      chatMessages.value.splice(i, 1)
      i-- // 调整索引，因为删除了一个元素
    } else if (nextMsg.sender === 'user') {
      // 如果后面还有用户消息，停止删除
      break
    }
  }

  // 从本地消息列表中移除原始用户消息
  chatMessages.value.splice(messageIndex, 1)

  // 重新发送该用户消息
  inputMessage.value = msg.content
  await nextTick()
  scrollToBottom()

  // 调用发送消息逻辑
  isStreaming.value ? await sendMessageStream() : await sendMessageNonStream()
}

// 流式发送消息的内部方法
const sendMessageStream = async () => {
  if (!canSendMessageWithContent.value) return

  const userChar = sceneCharacters.value.find(c => c.character_id === selectedUserCharacterId.value)
  const llmChar = sceneCharacters.value.find(c => c.character_id === selectedLLMCharacterId.value)

  if (!userChar || !llmChar || !currentScene.value || !selectedUserCharacterId.value || !selectedLLMCharacterId.value) return

  const sentMessage = inputMessage.value

  // 添加用户消息
  const userMessageId = Date.now() + Math.floor(Math.random() * 1000)
  const userMessage = {
    id: userMessageId,
    sender: 'user',
    senderName: userChar.name,
    content: sentMessage,
    timestamp: new Date(),
    isEditing: false,
    editContent: '',
    conversationId: null,
    sender_id: selectedUserCharacterId.value // 保存发送者ID以便后续更新发送者名称
  }
  chatMessages.value.push(userMessage)
  inputMessage.value = ''

  await nextTick()
  scrollToBottom()

  // 显示LLM正在回复
  isLLMReplying.value = true

  try {
    // 创建初始的空回复消息
    const assistantMessageId = Date.now() + Math.floor(Math.random() * 1000) + 1
    const initialMessage = {
      id: assistantMessageId,
      sender: 'assistant',
      senderName: llmChar.name,
      content: '',
      timestamp: new Date(),
      isEditing: false,
      editContent: '',
      conversationId: null,
      sender_id: selectedLLMCharacterId.value // 保存发送者ID以便后续更新发送者名称
    }
    chatMessages.value.push(initialMessage)
    await nextTick()
    scrollToBottom()

    // 调用流式聊天API
    const stream = await chatApi.sendMessageStream({
      roleplay_id: selectedLLMCharacterId.value,
      conversation: {
        message: sentMessage,
        sid: currentScene.value.sid,
        sender_id: selectedUserCharacterId.value,
        role: "user"
      },
      stream: true
    })

    // 处理流式数据
    let hasReceivedContent = false
    let currentContent = ''
    let userConversationId: number | null = null
    let assistantConversationId: number | null = null

    try {
      for await (const chunk of stream) {
        if (chunk && chunk.type === 'ids') {
          userConversationId = chunk.user_conversation_id || null
          assistantConversationId = chunk.assistant_conversation_id || null

          // 更新用户消息的conversationId
          const userMessageIndex = chatMessages.value.findIndex(m => m.id === userMessage.id)
          if (userMessageIndex !== -1 && userConversationId) {
            chatMessages.value[userMessageIndex] = {
              ...chatMessages.value[userMessageIndex],
              conversationId: userConversationId
            }
          }

          // 更新助手消息的conversationId
          const assistantMessageIndex = chatMessages.value.findIndex(m => m.id === assistantMessageId)
          if (assistantMessageIndex !== -1 && assistantConversationId) {
            chatMessages.value[assistantMessageIndex] = {
              ...chatMessages.value[assistantMessageIndex],
              conversationId: assistantConversationId
            }
          }
        } else if (chunk && chunk.data && chunk.data.content) {
          hasReceivedContent = true
          currentContent += chunk.data.content

          // 更新assistantMessage
          const messageIndex = chatMessages.value.findIndex(m => m.id === assistantMessageId)
          if (messageIndex !== -1) {
            chatMessages.value[messageIndex] = {
              id: assistantMessageId,
              sender: 'assistant',
              senderName: llmChar.name,
              content: currentContent,
              timestamp: chatMessages.value[messageIndex].timestamp,
              isEditing: false,
              editContent: '',
              conversationId: chatMessages.value[messageIndex].conversationId,
              sender_id: chatMessages.value[messageIndex].sender_id // 保持现有的sender_id
            }
          }

          await nextTick()
          scrollToBottom()
        }
      }
    } catch (streamError) {
      console.error('流式读取错误:', streamError)
      throw streamError
    } finally {
      isLLMReplying.value = false
    }

    // 如果没有接收到任何内容，显示提示
    if (!hasReceivedContent) {
      const messageIndex = chatMessages.value.findIndex(m => m.id === assistantMessageId)
      if (messageIndex !== -1) {
        chatMessages.value[messageIndex] = {
          id: assistantMessageId,
          sender: 'assistant',
          senderName: llmChar.name,
          content: '抱歉，没有收到回复内容',
          timestamp: chatMessages.value[messageIndex].timestamp,
          isEditing: false,
          editContent: '',
          conversationId: null,
          sender_id: chatMessages.value[messageIndex].sender_id // 保持现有的sender_id
        }
      }
    }

    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error('Failed to send message:', err)
    isLLMReplying.value = false
    // 添加错误消息
    const errorMessageId = Date.now() + Math.floor(Math.random() * 1000) + 3
    chatMessages.value.push({
      id: errorMessageId,
      sender: 'assistant',
      senderName: '系统',
      content: '发送失败: ' + (err instanceof Error ? err.message : String(err)),
      timestamp: new Date(),
      isEditing: false,
      editContent: '',
      conversationId: null
    })
  }
}

// 非流式发送消息的内部方法
const sendMessageNonStream = async () => {
  if (!canSendMessageWithContent.value) return

  const userChar = sceneCharacters.value.find(c => c.character_id === selectedUserCharacterId.value)
  const llmChar = sceneCharacters.value.find(c => c.character_id === selectedLLMCharacterId.value)

  if (!userChar || !llmChar || !currentScene.value || !selectedUserCharacterId.value || !selectedLLMCharacterId.value) return

  const sentMessage = inputMessage.value

  // 添加用户消息
  const userMessageId = Date.now() + Math.floor(Math.random() * 1000)
  const userMessage = {
    id: userMessageId,
    sender: 'user',
    senderName: userChar.name,
    content: sentMessage,
    timestamp: new Date(),
    isEditing: false,
    editContent: '',
    conversationId: null,
    sender_id: selectedUserCharacterId.value // 保存发送者ID以便后续更新发送者名称
  }
  chatMessages.value.push(userMessage)
  inputMessage.value = ''

  await nextTick()
  scrollToBottom()

  // 显示"LLM正在回复..."
  isLLMReplying.value = true

  try {
    const result = await chatApi.sendMessage({
      roleplay_id: selectedLLMCharacterId.value,
      conversation: {
        message: sentMessage,
        sid: currentScene.value.sid,
        sender_id: selectedUserCharacterId.value,
        role: "user"
      },
      stream: false
    })

    isLLMReplying.value = false

    if (result.code === 200 && result.data) {
      // 使用后端返回的conversation_id
      const userConversationId = result.data.user_conversation_id || null
      const assistantConversationId = result.data.assistant_conversation_id || null

      // 更新用户消息的conversationId
      const userMessageIndex = chatMessages.value.findIndex(m => m.id === userMessage.id)
      if (userMessageIndex !== -1 && userConversationId) {
        chatMessages.value[userMessageIndex] = {
          ...chatMessages.value[userMessageIndex],
          conversationId: userConversationId
        }
      }

      // 添加LLM回复
      const assistantMessageId = Date.now() + Math.floor(Math.random() * 1000) + 2
      const assistantMessage = {
        id: assistantMessageId,
        sender: 'assistant',
        senderName: llmChar.name,
        content: result.data.response || '',
        timestamp: new Date(),
        isEditing: false,
        editContent: '',
        conversationId: assistantConversationId,
        sender_id: selectedLLMCharacterId.value // 保存发送者ID以便后续更新发送者名称
      }
      chatMessages.value.push(assistantMessage)
    } else {
      throw new Error(result.message || '聊天失败')
    }

    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error('Failed to send message:', err)
    isLLMReplying.value = false
    // 添加错误消息
    const errorMessageId = Date.now() + Math.floor(Math.random() * 1000) + 3
    chatMessages.value.push({
      id: errorMessageId,
      sender: 'assistant',
      senderName: '系统',
      content: '发送失败: ' + (err instanceof Error ? err.message : String(err)),
      timestamp: new Date(),
      isEditing: false,
      editContent: '',
      conversationId: null
    })
  }
}

// 键盘事件
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 返回场景图
const backToGraph = () => {
  currentScene.value = null
  chatMessages.value = []
  selectedUserCharacterId.value = null
  selectedLLMCharacterId.value = null
  selectedCharacterIds.value = []
  selectedCharacterToAdd.value = ''
  router.push({ name: 'scenes-graph' })
}

// 格式化时间
const formatTime = (date: Date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// 获取节点样式类
const getNodeClass = (node: any): string => {
  if (node.is_main) return 'main-scene'
  if (node.is_root) return 'root-scene'
  return 'normal-scene'
}

onMounted(() => {
  nextTick(() => {
    loadGraph().then(() => {
      // 检查路由参数中是否有sceneId
      const sceneId = route.query.sceneId as string
      if (sceneId && sceneGraph.value) {
        // 找到对应的节点数据
        const node = sceneGraph.value.nodes.find((n: any) => n.sid === sceneId)
        if (node) {
          // 转换为节点数据格式并选择场景
          const nodeData = {
            id: node.sid,
            label: node.name,
            is_main: node.is_main,
            is_root: node.is_root,
            summary: node.summary
          }
          selectScene(nodeData)
        }
      }
    })
  })

  // 初始化移动端检测
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  if (cy.value) {
    cy.value.destroy()
  }
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.scene-chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #0a0a0a;
  overflow: hidden;
}

/* 场景图视图 */
.scene-graph-section {
  padding: 15px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header {
  margin-bottom: 15px;
  flex-shrink: 0;
}

.header h2 {
  margin: 0 0 5px 0;
  color: #e0e0e0;
  font-weight: 300;
}

.header p {
  margin: 0;
  color: #888;
  font-size: 14px;
}

.graph-container {
  flex: 1;
  border: 1px solid #1a1a1a;
  border-radius: 8px;
  position: relative;
  min-height: 500px;
  background-color: #0f0f0f;
  overflow: auto;
}

.graph-container.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 40px;
  margin: -20px 0 0 -20px;
  border: 3px solid #1a1a1a;
  border-top: 3px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.legend {
  position: absolute;
  top: 80px;
  right: 20px;
  background: #1a1a1a;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  z-index: 1000;
  border: 1px solid #2a2a2a;
}

.legend h4 {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #e0e0e0;
  font-weight: 400;
  letter-spacing: 0.5px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 12px;
}

.legend-node {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #0a0a0a;
}

.legend-node.main-scene {
  background-color: #ef4444;
}

.legend-node.root-scene {
  background-color: #f59e0b;
}

.legend-node.normal-scene {
  background-color: #3b82f6;
}

/* 聊天视图 */
.chat-section {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #0a0a0a;
}

.chat-header {
  padding: 12px 20px;
  border-bottom: 1px solid #1a1a1a;
  display: flex;
  align-items: center;
  gap: 20px;
  background-color: #0f0f0f;
  flex-shrink: 0;
}

.back-btn {
  padding: 8px 16px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.back-btn:hover {
  background-color: #2a2a2a;
  border-color: #3a3a3a;
}

.scene-navigation {
  display: flex;
  gap: 10px;
  margin-left: auto;
  align-items: center;
}

.previous-scene-selector,
.next-scene-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.previous-scene-dropdown,
.next-scene-dropdown {
  padding: 8px 12px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 150px;
}

.previous-scene-dropdown:hover,
.next-scene-dropdown:hover {
  background-color: #252525;
  border-color: #3a3a3a;
}

.previous-scene-dropdown:focus,
.next-scene-dropdown:focus {
  outline: none;
  border-color: #6366f1;
  background-color: #252525;
}

.previous-scene-dropdown option,
.next-scene-dropdown option {
  background-color: #1a1a1a;
  color: #e0e0e0;
  padding: 8px;
}

.nav-btn {
  padding: 8px 16px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  white-space: nowrap;
}

.nav-btn:hover:not(:disabled) {
  background-color: #2a2a2a;
  border-color: #3a3a3a;
}

.nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-btn.create-btn {
  background-color: #6366f1;
  border-color: #6366f1;
  color: white;
}

.nav-btn.create-btn:hover:not(:disabled) {
  background-color: #4f46e5;
  border-color: #4f46e5;
}

.scene-info h3 {
  margin: 0 0 5px 0;
  color: #e0e0e0;
  font-weight: 300;
}

.scene-info p {
  margin: 0;
  color: #888;
  font-size: 14px;
}

.chat-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 280px;
  border-right: 1px solid #1a1a1a;
  padding: 20px;
  overflow-y: auto;
  background-color: #0f0f0f;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: width 0.3s ease;
}

.sidebar.sidebar-collapsed {
  width: 60px;
  padding: 20px 10px;
}

.sidebar-toggle {
  position: absolute;
  top: 15px;
  right: 10px;
  width: 30px;
  height: 30px;
  background-color: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  color: #e0e0e0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.2s;
  z-index: 10;
}

.sidebar-toggle:hover {
  background-color: #2a2a2a;
  border-color: #3a3a3a;
}

.sidebar-content {
  transition: opacity 0.3s ease;
}

.sidebar-collapsed .sidebar-content {
  opacity: 0;
  pointer-events: none;
}

.sidebar-section {
  margin-top: 20px;
  margin-bottom: 18px;
}

.sidebar-section h4 {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #a0a0a0;
  font-weight: 400;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.character-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  /* max-height: 150px; */
  /* overflow: hidden; */
}

.character-dropdown {
  margin-top: 8px;
}

.character-select {
  width: 100%;
  min-height: 120px;
  font-size: 13px;
}

.character-select option {
  padding: 8px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  border-bottom: 1px solid #2a2a2a;
}

.character-select option:checked {
  background-color: #6366f1;
}

.dropdown-hint {
  margin-top: 6px;
  font-size: 12px;
  color: #888;
  text-align: center;
}

.empty-text {
  text-align: center;
  color: #666;
  padding: 20px;
  font-size: 13px;
}

.add-character-form,
.create-character-form {
  display: flex;
  gap: 8px;
}

/* 聊天主体 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #0a0a0a;
}

.role-selection {
  padding: 15px;
  border-bottom: 1px solid #1a1a1a;
  display: flex;
  gap: 20px;
  background-color: #0f0f0f;
  flex-shrink: 0;
}

.role-select {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.role-select label {
  font-size: 13px;
  color: #888;
  font-weight: 400;
}

/* 输出模式选择 */
.output-mode {
  padding: 12px 15px;
  border-bottom: 1px solid #1a1a1a;
  display: flex;
  align-items: center;
  gap: 15px;
  background-color: #0f0f0f;
  flex-shrink: 0;
}

.streaming-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.streaming-toggle input[type="checkbox"] {
  display: none;
}

.toggle-slider {
  position: relative;
  width: 44px;
  height: 22px;
  background-color: #2a2a2a;
  border-radius: 22px;
  transition: background-color 0.3s;
  border: 1px solid #3a3a3a;
}

.toggle-slider:before {
  content: '';
  position: absolute;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: #888;
  top: 2px;
  left: 2px;
  transition: all 0.3s;
}

.streaming-toggle input[type="checkbox"]:checked + .toggle-slider {
  background-color: #6366f1;
  border-color: #6366f1;
}

.streaming-toggle input[type="checkbox"]:checked + .toggle-slider:before {
  transform: translateX(22px);
  background-color: white;
}

.toggle-label {
  font-size: 13px;
  color: #a0a0a0;
  font-weight: 400;
}

.replying-indicator {
  font-size: 13px;
  color: #f59e0b;
  font-weight: 400;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.streaming-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.streaming-indicator .dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: #6366f1;
  animation: bounce 1.4s ease-in-out infinite;
}

.streaming-indicator .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.streaming-indicator .dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.4;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #0a0a0a;
  display: flex;
  flex-direction: column;
}

.chat-history-header {
  text-align: center;
  padding: 10px;
  margin-bottom: 15px;
  color: #666;
  font-size: 12px;
  border-bottom: 1px solid #1a1a1a;
  font-weight: 400;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.message {
  margin-bottom: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  max-width: 70%;
  border: 1px solid transparent;
  font-size: 13px;
  line-height: 1.4;
}

.message.user {
  margin-left: auto;
  background-color: #1e293b;
  color: #e0e0e0;
  border-color: #334155;
}

.message.assistant {
  margin-right: auto;
  background-color: #1a1a1a;
  border-color: #2a2a2a;
  color: #d0d0d0;
}

.message-header {
  margin-bottom: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-info strong {
  font-size: 13px;
  color: #a0a0a0;
  font-weight: 500;
}

.message-time {
  font-size: 11px;
  opacity: 0.5;
}

.message-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.message:hover .message-actions {
  opacity: 1;
}

.action-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  background-color: #2a2a2a;
  color: #a0a0a0;
}

.action-btn:hover {
  transform: scale(1.1);
}

.edit-btn:hover {
  background-color: #3b82f6;
  color: white;
}

.delete-btn:hover {
  background-color: #ef4444;
  color: white;
}

.save-btn:hover {
  background-color: #10b981;
  color: white;
}

.cancel-btn:hover {
  background-color: #f59e0b;
  color: white;
}

.regenerate-btn:hover {
  background-color: #8b5cf6;
  color: white;
}

.edit-textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #3a3a3a;
  border-radius: 4px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  font-size: 13px;
  font-family: inherit;
  resize: vertical;
  min-height: 60px;
}

.edit-textarea:focus {
  outline: none;
  border-color: #6366f1;
}

.message-content {
  line-height: 1.4;
  white-space: pre-wrap;
  font-size: 13px;
}

.chat-input {
  padding: 15px;
  border-top: 1px solid #1a1a1a;
  display: flex;
  gap: 12px;
  background-color: #0f0f0f;
  flex-shrink: 0;
}

.chat-input textarea {
  flex: 1;
  resize: none;
}

.send-btn {
  min-width: 80px;
}

/* 通用样式 */
.form-control {
  padding: 12px 12px;
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

.form-control::placeholder {
  color: #666;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  font-weight: 400;
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

.btn-success {
  background-color: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #059669;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.error-message {
  padding: 12px;
  margin-bottom: 10px;
  background-color: #1a1a1a;
  color: #ef4444;
  border: 1px solid #ef4444;
  border-radius: 6px;
}

/* 滚动条样式 */
.chat-history::-webkit-scrollbar,
.sidebar::-webkit-scrollbar {
  width: 8px;
}

.chat-history::-webkit-scrollbar-track,
.sidebar::-webkit-scrollbar-track {
  background: #0f0f0f;
}

.chat-history::-webkit-scrollbar-thumb,
.sidebar::-webkit-scrollbar-thumb {
  background: #2a2a2a;
  border-radius: 4px;
}

.chat-history::-webkit-scrollbar-thumb:hover,
.sidebar::-webkit-scrollbar-thumb:hover {
  background: #3a3a3a;
}

/* 响应式布局 */
@media (max-width: 1024px) {
  .sidebar {
    width: 240px;
  }

  .role-selection {
    flex-direction: column;
    gap: 12px;
  }

  .role-select {
    width: 100%;
  }

  .message {
    max-width: 85%;
  }

  .scene-navigation {
    flex-wrap: wrap;
    gap: 8px;
  }

  .nav-btn {
    padding: 6px 12px;
    font-size: 13px;
  }

  .previous-scene-dropdown,
  .next-scene-dropdown {
    min-width: 120px;
    font-size: 13px;
    padding: 6px 10px;
  }
}

@media (max-width: 768px) {
  .chat-content {
    position: relative;
  }

  .sidebar {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sidebar.sidebar-open {
    transform: translateX(0);
    width: 280px;
    padding: 20px;
    border-right: 1px solid #1a1a1a;
  }

  .sidebar.sidebar-collapsed {
    transform: translateX(-100%);
    width: 0;
    padding: 0;
    border-right: none;
  }

  .chat-main {
    width: 100%;
  }

  .mobile-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.6);
    z-index: 99;
    display: none;
  }

  .mobile-overlay.show {
    display: block;
  }

  .mobile-sidebar-toggle {
    display: block;
  }

  .role-selection {
    padding: 10px;
  }

  .output-mode {
    padding: 10px;
  }

  .chat-input {
    padding: 10px;
  }

  .message {
    max-width: 90%;
  }

  .message-actions {
    opacity: 1; /* 在移动端总是显示操作按钮 */
  }

  .action-btn {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }

  .scene-navigation {
    flex-direction: column;
    gap: 6px;
  }

  .nav-btn {
    width: 100%;
    padding: 8px;
  }

  .previous-scene-selector,
  .next-scene-selector {
    width: 100%;
  }

  .previous-scene-dropdown,
  .next-scene-dropdown {
    width: 100%;
    min-width: 0;
  }
}

@media (max-width: 480px) {
  .chat-header {
    padding: 10px 15px;
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .scene-info {
    flex: 1;
    min-width: 200px;
  }

  .header h2 {
    font-size: 20px;
  }

  .scene-info h3 {
    font-size: 16px;
  }

  .scene-navigation {
    width: 100%;
    margin-top: 10px;
  }

  .nav-btn {
    padding: 6px 10px;
    font-size: 12px;
  }

  .role-selection {
    padding: 8px;
  }

  .chat-history {
    padding: 15px;
  }

  .message {
    padding: 8px 12px;
    font-size: 12px;
  }

  .chat-input textarea {
    font-size: 14px;
  }

  .btn {
    padding: 6px 12px;
    font-size: 13px;
  }
}

.mobile-sidebar-toggle {
  display: none;
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  background-color: #6366f1;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  z-index: 1000;
  transition: all 0.3s;
}

.mobile-sidebar-toggle:hover {
  background-color: #4f46e5;
  transform: scale(1.1);
}

/* 角色信息弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.character-modal {
  background-color: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #2a2a2a;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #0f0f0f;
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  color: #e0e0e0;
  font-size: 18px;
  font-weight: 500;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 28px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #2a2a2a;
  color: #e0e0e0;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #a0a0a0;
  font-size: 13px;
  font-weight: 500;
}

.form-group .form-control {
  width: 100%;
}

.form-group textarea.form-control {
  resize: vertical;
  min-height: 80px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
  margin-bottom: 8px;
}

.checkbox-label input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid #3a3a3a;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  background-color: #1a1a1a;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark {
  background-color: #6366f1;
  border-color: #6366f1;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.help-text {
  margin: 0;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #2a2a2a;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background-color: #0f0f0f;
  border-radius: 0 0 12px 12px;
}

.btn-secondary {
  background-color: #2a2a2a;
  color: #e0e0e0;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #3a3a3a;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #dc2626;
}

.character-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.status-visible {
  color: #10b981;
  font-weight: bold;
}

.status-invisible {
  color: #ef4444;
  font-weight: bold;
}

.character-item {
  padding: 8px 10px;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
  color: #e0e0e0;
  font-size: 13px;
}

.character-item:hover {
  background-color: #252525;
  border-color: #3a3a3a;
}

.character-item.selected {
  background-color: #1e293b;
  border-color: #6366f1;
}
</style>
