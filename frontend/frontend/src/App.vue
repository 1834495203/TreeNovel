<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-brand">
          ReactNovel
        </router-link>

        <div class="nav-links">
          <router-link to="/" class="nav-link" active-class="active">
            首页
          </router-link>
          <router-link to="/characters" class="nav-link" active-class="active">
            角色管理
          </router-link>
        </div>
      </div>
    </nav>

    <!-- 主内容区域 -->
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  overflow-x: hidden;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}
</style>

<style scoped>
#app {
  min-height: 100vh;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background-color: #0f0f0f;
  border-bottom: 1px solid #1a1a1a;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: 600;
  color: #6366f1;
  text-decoration: none;
  letter-spacing: 0.5px;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-link {
  text-decoration: none;
  color: #a0a0a0;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.2s;
  font-weight: 400;
}

.nav-link:hover {
  background-color: #1a1a1a;
  color: #e0e0e0;
}

.nav-link.active {
  background-color: #1a1a1a;
  color: #6366f1;
  font-weight: 500;
}

.main-content {
  flex: 1;
  height: calc(100vh - 60px);
  background-color: #0a0a0a;
  overflow: hidden;
}
</style>
