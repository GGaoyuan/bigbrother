<script setup lang="ts">
import EqualBarChartView from '@/components/EqualBarChartView.vue'
</script>

<template>
  <div class="market-quotes-page">
    <header class="page-header">
      <h1 class="page-title">行情</h1>
    </header>
    <div class="chart-demo">
      <EqualBarChartView />
    </div>
    <div class="page-placeholder">
      <p>行情内容将在此展示</p>
    </div>
  </div>
</template>

<style scoped>
.market-quotes-page {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-heading);
}

.chart-demo {
  margin-bottom: 1.5rem;
}

.page-placeholder {
  padding: 3rem 2rem;
  text-align: center;
  color: var(--color-text-muted);
  background: var(--color-background-soft);
  border-radius: 8px;
}
</style>
