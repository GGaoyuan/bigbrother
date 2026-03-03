<script setup lang="ts">
import { ref } from 'vue'

const searchKeyword = ref('')
</script>

<template>
  <div class="theme-lib-page">
    <header class="page-header">
      <h1 class="page-title">题材库</h1>
      <div class="search-wrap">
        <input
          v-model="searchKeyword"
          type="search"
          class="search-input"
          placeholder="搜索题材、概念..."
          autocomplete="off"
        />
      </div>
    </header>
    <div class="page-placeholder">
      <p>题材库内容将在此展示</p>
    </div>
  </div>
</template>

<style scoped>
.theme-lib-page {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 60vh;
}

.page-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 1rem;
}

.search-wrap {
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 0.6rem 1rem;
  padding-left: 2.25rem;
  font-size: 0.95rem;
  color: var(--color-text);
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input::placeholder {
  color: var(--color-text);
  opacity: 0.6;
}

.search-input:hover {
  border-color: var(--color-border-hover);
}

.search-input:focus {
  border-color: #1565c0;
  box-shadow: 0 0 0 2px rgba(21, 101, 192, 0.2);
}

.page-placeholder {
  padding: 2rem;
  text-align: center;
  color: var(--color-text);
  opacity: 0.8;
}
</style>
