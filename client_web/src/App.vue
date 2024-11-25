<script setup>
import VerticalMenu from "./components/VerticalMenu.vue";


</script>

<template>
  <div class="container">
    <div class="vertical_menu">
      <VerticalMenu/>
    </div>
    <div class="content_area">
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.vertical_menu {
  background-color: #f0f0f0;
}

.content_area {
  flex-grow: 1;
  background-color: #998922;
  /*overflow-y: auto;  如果内容超出，显示滚动条 */
}
</style>