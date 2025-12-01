<script setup lang="ts">
import HelloWorld from './components/HelloWorld.vue'
import TheWelcome from './components/TheWelcome.vue'
import NavigatorBar from "@/components/NavigatorBar.vue";
</script>

<template>
  <keep-alive>
    <router-view />
  </keep-alive>
</template>

<style scoped>

</style>
