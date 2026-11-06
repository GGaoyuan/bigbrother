<template>
  <div class="app-container">
    <AppSidebar />
    <main class="main-content"><RouterView /></main>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppSidebar from './components/sidebar/AppSidebar.vue'
</script>

<style>
:root {
  --rail-width: 310px;
  --ink: #1e293b;
  --muted: #8792a2;
  --line: #e9edf2;
  --blue: #3478f6;
}
body {
  background: #f8fafc !important;
  color: var(--ink) !important;
}
.app-container {
  min-height: 100vh;
}
.main-content {
  width: calc(100% - var(--rail-width));
  min-height: 100vh;
  margin-left: var(--rail-width);
  padding: 16px 20px;
}
@media (max-width: 760px) {
  :root {
    --rail-width: 260px;
  }
  .main-content {
    width: 100%;
    margin-left: 0;
    padding: 12px;
  }
}
</style>
