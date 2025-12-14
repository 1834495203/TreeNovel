<template>
  <div class="scene-graph-container">
    <div class="header">
      <h2>场景关系图</h2>
      <div class="controls">
        <button @click="showCreateRootSceneDialog" :disabled="loading">
          创建根场景
        </button>
        <button @click="refreshGraph" :disabled="loading">
          {{ loading ? '加载中...' : '刷新' }}
        </button>
        <button @click="fitGraph">适应窗口</button>
        <button @click="centerGraph">居中</button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div
      ref="graphContainer"
      class="graph-container"
      :class="{ 'loading': loading }"
    ></div>

    <!-- 创建根场景弹窗 -->
    <div v-if="showCreateDialog" class="modal-overlay" @click="closeCreateDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>创建新根场景</h3>
          <button class="close-btn" @click="closeCreateDialog">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="sceneName">场景名称 *</label>
            <input
              id="sceneName"
              v-model="newRootScene.name"
              type="text"
              placeholder="请输入场景名称"
              required
            />
          </div>
          <div class="form-group">
            <label for="sceneSummary">场景描述</label>
            <textarea
              id="sceneSummary"
              v-model="newRootScene.summary"
              placeholder="请输入场景描述（可选）"
              rows="4"
            ></textarea>
          </div>
          <div class="form-group">
            <label>
              <input
                v-model="newRootScene.is_main"
                type="checkbox"
              />
              设为当前主场景
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeCreateDialog" :disabled="creating">
            取消
          </button>
          <button
            @click="createRootScene"
            :disabled="creating || !newRootScene.name.trim()"
            class="primary"
          >
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>

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
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import cytoscape, { type Core } from 'cytoscape'
import { useRouter } from 'vue-router'
import { sceneApi } from '@/api/scene'
import { SceneGraph } from '@/beans'

const router = useRouter()

const graphContainer = ref<HTMLElement>()
const loading = ref(false)
const error = ref('')
let cy: Core | null = null

// 创建根场景相关数据
const showCreateDialog = ref(false)
const creating = ref(false)
const newRootScene = ref({
  name: '',
  summary: '',
  is_main: false
})

// 获取并渲染场景图
const loadGraph = async () => {
  if (!graphContainer.value) return

  loading.value = true
  error.value = ''

  try {
    const sceneGraph: SceneGraph = await sceneApi.getScenesGraph()
    console.log('Fetched scene graph:', sceneGraph)

    // 转换为Cytoscape格式
    const elements = [
      ...sceneGraph.nodes.map(node => ({
        data: {
          id: node.sid,
          label: node.name,
          is_main: node.is_main,
          is_root: node.is_root,
          summary: node.summary
        },
        classes: getNodeClass(node)
      })),
      ...sceneGraph.edges.map(edge => ({
        data: {
          id: `${edge.source}-${edge.target}`,
          source: edge.source,
          target: edge.target
        }
      }))
    ]

    // 创建或更新Cytoscape实例
    if (cy) {
      cy.destroy()
    }

    cy = cytoscape({
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
            'height': '60px'
          }
        },
        {
          selector: 'node.main-scene',
          style: {
            'background-color': '#e74c3c',
            'text-outline-color': '#e74c3c'
          }
        },
        {
          selector: 'node.root-scene',
          style: {
            'background-color': '#f39c12',
            'text-outline-color': '#f39c12'
          }
        },
        {
          selector: 'node.normal-scene',
          style: {
            'background-color': '#3498db',
            'text-outline-color': '#3498db'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': '2px',
            'line-color': '#999',
            'target-arrow-color': '#999',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': ''
          }
        },
        {
          selector: ':selected',
          style: {
            'background-color': '#2ecc71',
            'line-color': '#2ecc71',
            'target-arrow-color': '#2ecc71',
            'text-outline-color': '#2ecc71'
          }
        },
        {
          selector: '.faded',
          style: {
            'opacity': 0.2,
            'text-opacity': 0.2
          }
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
      // 交互选项
      selectionType: 'single',
      boxSelectionEnabled: false,
      autoungrabify: false,
      autolock: false,
      panningEnabled: true,
      zoomingEnabled: true,
      userZoomingEnabled: true,
      userPanningEnabled: true,
    })

    // 添加事件监听
    cy.on('tap', 'node', (evt) => {
      const node = evt.target
      const data = node.data()
      // 点击节点跳转到对应场景的聊天页面
      router.push({
        name: 'scenes-chat',
        query: { sceneId: data.id }
      })
    })

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        clearSelection()
      }
    })

    // 鼠标悬停效果
    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target
      node.closedNeighborhood().removeClass('faded')
      node.addClass('highlighted')
    })

    cy.on('mouseout', 'node', (evt) => {
      const node = evt.target
      node.closedNeighborhood().removeClass('highlighted')
      if (cy) {
        cy.elements().removeClass('faded')
      }
    })

    // 自动居中
    cy.ready(() => {
      if (cy) {
        cy.fit()
      }
    })

  } catch (err) {
    error.value = '加载场景图失败: ' + (err instanceof Error ? err.message : String(err))
    console.error('Error loading scene graph:', err)
  } finally {
    loading.value = false
  }
}

// 获取节点样式类
const getNodeClass = (node: any): string => {
  if (node.is_main) return 'main-scene'
  if (node.is_root) return 'root-scene'
  return 'normal-scene'
}

// 显示节点信息（已废弃）
const showNodeInfo = (_data: any) => {
  // 功能已废弃，保留以避免编译错误
}

// 清除选择
const clearSelection = () => {
  if (cy) {
    cy.elements().removeClass('faded')
  }
}

// 刷新图
const refreshGraph = () => {
  loadGraph()
}

// 适应窗口
const fitGraph = () => {
  if (cy) {
    cy.fit()
  }
}

// 居中
const centerGraph = () => {
  if (cy) {
    cy.center()
  }
}

// 显示创建根场景弹窗
const showCreateRootSceneDialog = () => {
  showCreateDialog.value = true
}

// 关闭创建根场景弹窗
const closeCreateDialog = () => {
  showCreateDialog.value = false
  // 重置表单
  newRootScene.value = {
    name: '',
    summary: '',
    is_main: false
  }
}

// 创建根场景
const createRootScene = async () => {
  if (!newRootScene.value.name.trim()) {
    return
  }

  creating.value = true
  error.value = ''

  try {
    const sceneData = {
      new_scene: {
        sid: '', // 后端自动生成
        name: newRootScene.value.name.trim(),
        is_main: newRootScene.value.is_main,
        summary: newRootScene.value.summary.trim(),
        is_root: true // 明确设置为根场景
      }
    }

    await sceneApi.createScene(sceneData)

    // 创建成功后关闭弹窗并刷新图
    closeCreateDialog()
    await loadGraph()

  } catch (err) {
    error.value = '创建根场景失败: ' + (err instanceof Error ? err.message : String(err))
    console.error('Error creating root scene:', err)
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  nextTick(() => {
    loadGraph()
  })
})

onUnmounted(() => {
  if (cy) {
    cy.destroy()
  }
})
</script>

<style scoped>
.scene-graph-container {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #0a0a0a;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #e0e0e0;
  font-weight: 300;
}

.controls {
  display: flex;
  gap: 10px;
}

.controls button {
  padding: 8px 16px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  font-weight: 500;
}

.controls button:hover:not(:disabled) {
  background-color: #252525;
  border-color: #3a3a3a;
}

.controls button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.error-message {
  padding: 10px;
  margin-bottom: 10px;
  background-color: #1a1a1a;
  color: #ef4444;
  border: 1px solid #ef4444;
  border-radius: 6px;
}

.graph-container {
  flex: 1;
  border: 1px solid #1a1a1a;
  border-radius: 8px;
  position: relative;
  min-height: 500px;
  background-color: #0f0f0f;
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
  top: 100px;
  right: 20px;
  background: #1a1a1a;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  z-index: 1000;
  border: 1px solid #2a2a2a;
}

.legend h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #e0e0e0;
  font-weight: 400;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
}

.legend-node {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.legend-node.main-scene {
  background-color: #e74c3c;
}

.legend-node.root-scene {
  background-color: #f39c12;
}

.legend-node.normal-scene {
  background-color: #3498db;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #2a2a2a;
}

.modal-header h3 {
  margin: 0;
  color: #e0e0e0;
  font-weight: 500;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  color: #999;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #2a2a2a;
  color: #e0e0e0;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #e0e0e0;
  font-size: 14px;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  background-color: #0a0a0a;
  color: #e0e0e0;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.2s;
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.form-group label:has(input[type="checkbox"]) {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 400;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #2a2a2a;
}

.modal-footer button {
  padding: 10px 20px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  font-weight: 500;
}

.modal-footer button:hover:not(:disabled) {
  background-color: #252525;
  border-color: #3a3a3a;
}

.modal-footer button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.modal-footer button.primary {
  background-color: #6366f1;
  border-color: #6366f1;
}

.modal-footer button.primary:hover:not(:disabled) {
  background-color: #5558e6;
  border-color: #5558e6;
}
</style>