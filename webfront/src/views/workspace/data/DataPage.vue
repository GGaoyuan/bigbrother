<script setup lang="ts">
import DataChart from './components/DataChart.vue'
import PanelManager from './components/PanelManager.vue'
</script>

<template>
  <section class="data-page">
    <PanelManager />
    <DataChart />
  </section>
</template>

<style scoped>
.data-page {
  display: flex;
  min-height: calc(100vh - 32px);
  flex-direction: column;
  gap: 16px;
  color: #202b3b;
}
</style>
