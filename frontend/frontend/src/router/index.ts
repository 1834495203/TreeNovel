import { createRouter, createWebHistory } from 'vue-router'
import CharacterView from '../views/CharacterView.vue'
import SceneView from '../views/SceneView.vue'
import SceneGraphView from '../views/SceneGraphView.vue'
import SceneChatView from '../views/SceneChatView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/characters',
      name: 'characters',
      component: CharacterView
    },
    {
      path: '/scenes',
      name: 'scenes',
      component: SceneView
    },
    {
      path: '/scenes/graph',
      name: 'scenes-graph',
      component: SceneGraphView
    },
    {
      path: '/scenes/chat',
      name: 'scenes-chat',
      component: SceneChatView
    }
  ],
})

export default router
