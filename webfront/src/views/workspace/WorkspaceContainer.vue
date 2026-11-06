<script setup lang="ts">
import { computed, watch } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import { CONTAINER_TYPE } from '../../common/appConfig'
import { useAppConfigStore } from '../../common/appConfigStore'
import { useContainerQueueStore } from '../../common/containerQueue'
import AiPage from '../ai/AiPage.vue'
import DataPage from '../data/DataPage.vue'

const route = useRoute()
const appConfigStore = useAppConfigStore()
const containerQueue = useContainerQueueStore()
const config = computed(() => appConfigStore.config!)

watch(
  () => route.name,
  (routeName) => {
    if (typeof routeName === 'string') {
      containerQueue.syncRoute(routeName, config.value.pages)
    }
  },
)
</script>

<template>
  <section class="workspace-container" aria-live="polite">
    <RouterView v-slot="{ Component }">
      <KeepAlive :max="32">
        <component
          :is="DataPage"
          v-if="containerQueue.activeContainer?.type === CONTAINER_TYPE.DATA"
          :key="containerQueue.activeContainer.id"
        />
        <component
          :is="AiPage"
          v-else-if="containerQueue.activeContainer?.type === CONTAINER_TYPE.AI"
          :key="containerQueue.activeContainer.id"
        />
        <component
          :is="Component"
          v-else-if="containerQueue.activeContainer?.type === CONTAINER_TYPE.ROUTE && Component"
          :key="containerQueue.activeContainer.id"
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
