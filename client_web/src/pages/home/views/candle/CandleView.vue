<script setup>
import HeatmapComponent from "../../../../components/HeatmapComponent.vue";

</script>

<template>
  <div class="container">
    <HeatmapComponent></HeatmapComponent>
    <HeatmapComponent style="background-color: #f9f9f9"></HeatmapComponent>
    <HeatmapComponent style="background-color: #FF8AA2"></HeatmapComponent>
  </div>
</template>


<style scoped>
.container {
  background-color: #880022;
  display: flex;
  flex-direction: column;
  height: 100vh;
}
</style>