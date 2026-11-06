<template>
  <div class="app-container">
    <AppSidebar
      :active-workspace-id="activeWorkspaceId"
      @select-workspace="selectWorkspace"
      @open-page="activatePagesContent"
    />
    <main class="main-content">
      <WorkspaceContainer :content="activeContent" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './views/sidebar/AppSidebar.vue'
import WorkspaceContainer from './views/workspace/WorkspaceContainer.vue'
import { config } from './common/config/config'

type WorkspaceContent = 'data' | 'ai' | 'route'

const route = useRoute()
const activeWorkspaceId = ref(config.tabsConfig[0]!.id)
const activeContent = ref<WorkspaceContent>('data')

function selectWorkspace(workspaceId: number) {
  activeWorkspaceId.value = workspaceId

  const workspaceIndex = config.tabsConfig.findIndex((workspace) => workspace.id === workspaceId)

  if (workspaceIndex === 0) activeContent.value = 'data'
  if (workspaceIndex === 1) activeContent.value = 'ai'
}

function activatePagesContent() {
  activeWorkspaceId.value = config.tabsConfig[2]!.id
  activeContent.value = 'route'
}

watch(
  () => route.path,
  (path) => {
    if (path !== config.pagesConfig[0]?.path || activeContent.value === 'route') {
      activatePagesContent()
    }
  },
  { immediate: true },
)
</script>

<style>
:root {
  --rail-width: 310px;
  --ink: #1e293b;
  --muted: #8792a2;
  --line: #e9edf2;
  --blue: #3478f6;
}
body {
  background: #f8fafc !important;
  color: var(--ink) !important;
}
.app-container {
  min-height: 100vh;
}
.main-content {
  width: calc(100% - var(--rail-width));
  min-height: 100vh;
  margin-left: var(--rail-width);
  padding: 16px 20px;
}
@media (max-width: 760px) {
  :root {
    --rail-width: 260px;
  }
  .main-content {
    width: 100%;
    margin-left: 0;
    padding: 12px;
  }
}
</style>
