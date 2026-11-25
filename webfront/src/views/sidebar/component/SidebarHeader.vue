<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="sidebar-header">
    <RouterLink to="/" class="avatar" aria-label="首页">
      <img src="/favicon.png" alt="" />
    </RouterLink>
  </header>
</template>

<style>
.sidebar-header {
  flex: none;
  display: flex;
  align-items: center;
  height: 66px;
  padding: 0 16px;
  border-bottom: 1px solid var(--line);
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
