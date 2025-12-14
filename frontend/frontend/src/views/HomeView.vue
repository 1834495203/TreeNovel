<script setup lang="ts">
</script>

<template>
  <div class="home-view">
    <div class="hero">
      <h1>ReactNovel</h1>
      <p>欢迎来到ReactNovel互动小说平台</p>
      <div class="buttons">
        <router-link to="/characters" class="btn btn-primary">
          管理角色
        </router-link>
        <router-link to="/scenes" class="btn btn-secondary">
          管理场景
        </router-link>
        <router-link to="/scenes/graph" class="btn btn-tertiary">
          场景关系图
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #0a0a0a;
}

.hero {
  text-align: center;
  color: #e0e0e0;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: 300;
  letter-spacing: 2px;
  color: #6366f1;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  color: #a0a0a0;
  font-weight: 300;
}

.buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s;
  font-weight: 500;
}

.btn-primary {
  background-color: #6366f1;
  color: white;
}

.btn-primary:hover {
  background-color: #4f46e5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-secondary {
  background-color: #1a1a1a;
  color: #e0e0e0;
  border: 1px solid #2a2a2a;
}

.btn-secondary:hover {
  background-color: #252525;
  border-color: #3a3a3a;
}

.btn-tertiary {
  background-color: transparent;
  color: #a0a0a0;
  border: 1px solid #2a2a2a;
}

.btn-tertiary:hover {
  background-color: #1a1a1a;
  color: #e0e0e0;
  border-color: #3a3a3a;
}
</style>
