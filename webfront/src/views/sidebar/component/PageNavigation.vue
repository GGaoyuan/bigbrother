<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { sidebarPages } from '../pages'
</script>

<template>
  <nav class="sidebar-nav" aria-label="页面导航">
    <RouterLink
      v-for="page in sidebarPages"
      :key="page.id"
      :to="{ name: page.id }"
      class="nav-item"
    >
      {{ page.name }}
    </RouterLink>
  </nav>
</template>

<style>
.sidebar-nav {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  align-content: start;
  gap: 2px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px 13px 8px;
}
.nav-item {
  display: block;
  overflow: hidden;
  padding: 6px 9px !important;
  border: 0;
  border-radius: 5px;
  color: #788496 !important;
  font-size: 13px;
  line-height: 1.4;
  text-decoration: none;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.nav-item:hover {
  background: #f5f7fa !important;
  color: #3478f6 !important;
}
.nav-item.router-link-active {
  background: #eef4ff !important;
  color: #3478f6 !important;
  font-weight: 600;
}
</style>
