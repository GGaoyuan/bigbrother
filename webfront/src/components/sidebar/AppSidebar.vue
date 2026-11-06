<script setup lang="ts">
import { ref } from 'vue'
import AiWorkspace from './AiWorkspace.vue'
import DataWorkspace from './DataWorkspace.vue'
import PageNavigation from './PageNavigation.vue'
import SidebarHeader from './SidebarHeader.vue'

const activeTab = ref<'数据' | 'AI' | '页面'>('数据')
</script>

<template>
  <aside class="sidebar">
    <SidebarHeader v-model="activeTab" />
    <DataWorkspace v-if="activeTab === '数据'" />
    <AiWorkspace v-else-if="activeTab === 'AI'" />
    <PageNavigation v-else />
    <footer class="sidebar-footer">
      <span class="status-dot"></span> 数据工作台 <span class="version">v1.0</span>
    </footer>
  </aside>
</template>

<style>
.sidebar {
  position: fixed;
  z-index: 100;
  top: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  width: var(--rail-width);
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
  background: #fff;
  border-right: 1px solid var(--line);
}
.sidebar-footer {
  display: flex;
  flex: none;
  align-items: center;
  gap: 7px;
  height: 36px;
  margin-top: auto;
  padding: 0 17px;
  border-top: 1px solid var(--line);
  color: #8490a0;
  font-size: 10px;
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #63bf8b;
}
.version {
  margin-left: auto;
  color: #b0b8c3;
}
.sidebar button:focus-visible,
.sidebar a:focus-visible,
.sidebar input:focus-visible {
  outline: 2px solid #3478f6;
  outline-offset: 2px;
}
@media (max-width: 760px) {
  .sidebar {
    width: var(--rail-width);
    transform: translateX(-100%);
    transition: transform 0.2s ease;
  }
  .sidebar:focus-within,
  .sidebar:hover {
    transform: translateX(0);
  }
  .sidebar::after {
    content: '';
    position: fixed;
    left: 100%;
    top: 50%;
    width: 12px;
    height: 60px;
    border-radius: 0 8px 8px 0;
    background: #3478f6;
  }
}
</style>
