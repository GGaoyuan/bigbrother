<script setup>
import {ref} from "vue";
import HPMenu from "./HomeMenu.vue";

</script>

<template>
  <div class="container">
    <HPMenu></HPMenu>
    <div class="content"></div>
  </div>
</template>


<style scoped>
.container {
  background-color: #880022;
  display: flex;
  height: 100vh;
  width: 100vw;
}

.content {
  flex-grow: 1;
  background-color: #998922;
  /*overflow-y: auto;  如果内容超出，显示滚动条 */
}


</style>