<template>
  <div
    class="app-container"
    :style="`--rail-width: ${sidebarWidth}px`"
  >
    <AppSidebar v-model:width="sidebarWidth" />
    <main class="main-content">
      <WorkspaceContainer />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import AppSidebar from './views/sidebar/AppSidebar.vue'
import WorkspaceContainer from './views/workspace/WorkspaceContainer.vue'

const sidebarWidth = ref(310)

// Active charts use the window resize event to fit their containers.
watch(sidebarWidth, () => window.dispatchEvent(new Event('resize')), {
  flush: 'post',
})
</script>

<style>
:root {
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
  .main-content {
    width: 100%;
    margin-left: 0;
    padding: 12px;
  }
}
</style>
