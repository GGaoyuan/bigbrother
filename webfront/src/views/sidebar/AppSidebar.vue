<script setup lang="ts">
import { computed } from 'vue'
import AiWorkspace from '../ai/AiWorkspace.vue'
import DataWorkspace from '../data/DataWorkspace.vue'
import PageNavigation from '../pages/PageNavigation.vue'
import { useAppConfigStore } from '../../common/appConfigStore'
import { WORKSPACE_TYPE, type WorkspaceId } from '../../common/appConfig'
import { useContainerQueueStore } from '../../common/containerQueue'
import SidebarHeader from './SidebarHeader.vue'

const appConfigStore = useAppConfigStore()
const containerQueue = useContainerQueueStore()
const config = computed(() => appConfigStore.config!)
const activeWorkspace = computed(
  () =>
    config.value.workspaces.find((item) => item.id === containerQueue.activeWorkspaceId) ?? null,
)

function selectWorkspace(workspaceId: WorkspaceId) {
  const workspace = config.value.workspaces.find((item) => item.id === workspaceId)
  if (workspace) containerQueue.activateWorkspace(workspace)
}
</script>

<template>
  <aside class="sidebar">
    <SidebarHeader
      :model-value="containerQueue.activeWorkspaceId"
      :tabs="config.workspaces"
      :home-label="config.sidebar.homeLabel"
      :workspaces-label="config.sidebar.workspacesLabel"
      @update:model-value="selectWorkspace"
    />
    <DataWorkspace v-if="activeWorkspace?.type === WORKSPACE_TYPE.DATA" />
    <AiWorkspace v-else-if="activeWorkspace?.type === WORKSPACE_TYPE.AI" />
    <PageNavigation v-else-if="activeWorkspace?.type === WORKSPACE_TYPE.PAGES" />
    <footer class="sidebar-footer">
      <span class="status-dot"></span>
      {{ config.sidebar.footerLabel }}
      <span class="version">{{ config.sidebar.footerVersion }}</span>
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
