<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <section class="workspace-container" aria-live="polite">
    <RouterView v-slot="{ Component }">
      <KeepAlive :max="32">
        <component
          :is="Component"
          v-if="Component"
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
