<script setup lang="ts">
import Sidebar from '@/components/layout/Sidebar.vue'
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-background text-foreground">
    <Sidebar />
    <main class="flex-1 overflow-y-auto p-8">
      <router-view />
    </main>
  </div>
</template>
