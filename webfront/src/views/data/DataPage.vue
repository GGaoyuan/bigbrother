<script setup lang="ts">
import { computed } from 'vue'
import { WORKSPACE_TYPE } from '../../common/appConfig'
import { useAppConfigStore } from '../../common/appConfigStore'

const appConfigStore = useAppConfigStore()
const config = computed(() => appConfigStore.config!)
const dataWorkspace = computed(
  () => config.value.workspaces.find((workspace) => workspace.type === WORKSPACE_TYPE.DATA)!,
)
</script>

<template>
  <section class="data-page">
    <header class="data-page-header">
      <div>
        <p class="eyebrow">{{ config.sidebar.marketDataHint }}</p>
        <h1>{{ dataWorkspace.containerTitle }}</h1>
        <p class="description">{{ config.sidebar.dataPageDescription }}</p>
      </div>
    </header>
    <div class="chart-placeholder">
      <span class="chart-mark">⌁</span>
      <strong>{{ config.sidebar.dataPagePlaceholder }}</strong>
    </div>
  </section>
</template>

<style>
.data-page {
  display: flex;
  min-height: calc(100vh - 32px);
  flex-direction: column;
  gap: 18px;
  color: #1e293b;
}
.data-page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 22px;
  border: 1px solid #e7edf5;
  border-radius: 10px;
  background: #fff;
}
.eyebrow {
  margin-bottom: 4px;
  color: #8792a2;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
}
.data-page h1 {
  margin: 0;
  color: #253348;
  font-size: 20px;
  font-weight: 650;
}
.description {
  margin-top: 5px;
  color: #8792a2;
  font-size: 12px;
}
.chart-placeholder {
  display: flex;
  min-height: 360px;
  flex: 1;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 10px;
  border: 1px dashed #d9e1ec;
  border-radius: 10px;
  background: #fff;
  color: #9aa5b2;
  font-size: 13px;
}
.chart-mark {
  color: #8cadf0;
  font-size: 28px;
}
</style>
