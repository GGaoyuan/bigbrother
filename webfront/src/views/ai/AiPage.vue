<script setup lang="ts">
import { computed } from 'vue'
import { WORKSPACE_TYPE } from '../../common/appConfig'
import { useAppConfigStore } from '../../common/appConfigStore'

const appConfigStore = useAppConfigStore()
const config = computed(() => appConfigStore.config!)
const aiWorkspace = computed(
  () => config.value.workspaces.find((workspace) => workspace.type === WORKSPACE_TYPE.AI)!,
)
</script>

<template>
  <section class="ai-page">
    <div class="ai-page-card">
      <div class="ai-page-mark">✳</div>
      <h1>{{ aiWorkspace.containerTitle }}</h1>
      <p>{{ config.sidebar.aiPlaceholderDescription }}</p>
    </div>
  </section>
</template>

<style>
.ai-page {
  display: grid;
  min-height: calc(100vh - 32px);
  place-items: center;
}
.ai-page-card {
  display: grid;
  justify-items: center;
  gap: 8px;
  padding: 36px;
  color: #8b96a5;
  text-align: center;
}
.ai-page-card h1 {
  margin: 0;
  color: #526176;
  font-size: 18px;
  font-weight: 650;
}
.ai-page-card p {
  font-size: 13px;
}
.ai-page-mark {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  margin-bottom: 4px;
  border-radius: 14px;
  background: #f1f5fc;
  color: #7495d5;
  font-size: 24px;
}
</style>
