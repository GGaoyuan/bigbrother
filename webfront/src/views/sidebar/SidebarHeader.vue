<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { WorkspaceId, WorkspaceTabConfig } from '../../common/appConfig'

defineProps<{
  modelValue: WorkspaceId
  tabs: WorkspaceTabConfig[]
  homeLabel: string
  workspacesLabel: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: WorkspaceId]
}>()
</script>

<template>
  <header class="sidebar-header">
    <RouterLink to="/" class="avatar" :aria-label="homeLabel"
      ><img src="/favicon.png" alt=""
    /></RouterLink>
    <div class="mode-switch" role="tablist" :aria-label="workspacesLabel">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        role="tab"
        :aria-selected="modelValue === tab.id"
        class="mode-tab"
        :class="{ active: modelValue === tab.id }"
        @click="emit('update:modelValue', tab.id)"
      >
        {{ tab.label }}
      </button>
    </div>
  </header>
</template>

<style>
.sidebar-header {
  flex: none;
  display: flex;
  align-items: center;
  gap: 11px;
  height: 66px;
  padding: 0 16px;
  border-bottom: 1px solid var(--line);
}
.mode-switch {
  display: flex;
  flex: 1;
  padding: 3px;
  border: 1px solid #edf0f4;
  background: #f7f8fa;
  border-radius: 9px;
}
.mode-tab {
  flex: 1;
  padding: 6px 0;
  color: #718096;
  border: 0;
  border-radius: 6px;
  background: transparent;
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.mode-tab.active {
  color: #2266dc;
  background: #fff;
  box-shadow: 0 1px 3px #162b4d18;
}
.avatar {
  display: grid;
  place-items: center;
  flex: none;
  width: 34px;
  height: 34px;
  padding: 0 !important;
  border: 0;
  border-radius: 50%;
  background: #eaf1ff;
  cursor: pointer;
}
.avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}
.avatar:hover {
  background: transparent !important;
}
</style>
