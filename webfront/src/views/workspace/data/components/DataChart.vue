<script setup lang="ts">
import dataConfig from '../../../sidebar/component/data.json'
</script>

<template>
  <section class="chart-card" aria-label="当前面板图表">
    <header class="chart-card-header">
      <h2>图表1</h2>
    </header>
    <div class="chart-placeholder">
      <span class="chart-mark" aria-hidden="true">⌁</span>
      <strong>{{ dataConfig.sidebar.dataPagePlaceholder }}</strong>
    </div>
  </section>
</template>

<style scoped>
.chart-card {
  display: flex;
  min-height: 560px;
  flex: 1;
  flex-direction: column;
  padding: 18px;
  border: 1px solid #dfe6ef;
  border-radius: 11px;
  background: #fff;
}

.chart-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.chart-card-header h2 {
  margin: 0;
  color: #29364a;
  font-size: 17px;
  font-weight: 650;
}

.chart-placeholder {
  display: flex;
  min-height: 430px;
  flex: 1;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 10px;
  border: 1px dashed #d9e1ec;
  border-radius: 8px;
  background-color: #fcfdff;
  background-image: linear-gradient(#f2f5fa 1px, transparent 1px),
    linear-gradient(90deg, #f2f5fa 1px, transparent 1px);
  background-size: 54px 54px;
  color: #9aa5b2;
  font-size: 13px;
}

.chart-mark {
  color: #8cadf0;
  font-size: 30px;
}

@media (max-width: 760px) {
  .chart-card {
    min-height: 440px;
    padding: 14px;
  }

  .chart-card-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .chart-placeholder {
    min-height: 320px;
  }
}
</style>
