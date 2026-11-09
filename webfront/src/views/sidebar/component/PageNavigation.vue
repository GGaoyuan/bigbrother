<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { config } from '../../../common/config/config'

const emit = defineEmits<{
  'open-page': []
}>()
</script>

<template>
  <section class="pages-section workspace-pane">
    <div class="section-title pages-title">
      <span>页面导航</span>
      <span class="section-hint">
        {{ config.pagesConfig.length }} PAGES
      </span>
    </div>
    <nav class="sidebar-nav" aria-label="页面导航">
      <RouterLink
        v-for="page in config.pagesConfig"
        :key="page.id"
        :to="page.path"
        class="nav-item"
        exact-active-class="nav-item--exact-active"
        @click="emit('open-page')"
      >
        {{ page.name }}
      </RouterLink>
    </nav>
  </section>
</template>

<style>
.pages-section {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px 13px 8px;
}
.pages-title {
  padding: 0 5px 9px;
}
.sidebar-nav {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px 4px;
  padding: 0;
}
.nav-item {
  display: block;
  overflow: hidden;
  padding: 5px 7px !important;
  border: 0;
  border-radius: 5px;
  color: #788496 !important;
  font-size: 10px;
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
}
</style>
