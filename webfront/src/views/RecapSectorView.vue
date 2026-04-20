<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="sector-page">
    <RouterView />
  </div>
</template>

<style scoped>
.sector-page {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 60vh;
}
</style>
