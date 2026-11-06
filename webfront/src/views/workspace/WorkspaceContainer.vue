<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import AiPage from './ai/AiPage.vue'
import DataPage from './data/DataPage.vue'

defineProps<{
  content: 'data' | 'ai' | 'route'
}>()

const route = useRoute()
</script>

<template>
  <section class="workspace-container" aria-live="polite">
    <RouterView v-slot="{ Component }">
      <KeepAlive :max="32">
        <component
          :is="DataPage"
          v-if="content === 'data'"
          key="data-workspace"
        />
        <component
          :is="AiPage"
          v-else-if="content === 'ai'"
          key="ai-workspace"
        />
        <component
          :is="Component"
          v-else-if="content === 'route' && Component"
          :key="route.path"
        />
      </KeepAlive>
    </RouterView>
  </section>
</template>

<style>
.workspace-container {
  min-width: 0;
  min-height: 100vh;
}
</style>
