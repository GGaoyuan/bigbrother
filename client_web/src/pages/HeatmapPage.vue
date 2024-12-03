<script setup lang="ts">
import HeatmapComponent from "../components/HeatmapComponent.vue";
import {nextTick, onMounted, onUnmounted, ref} from "vue";

const heatmapData = ref(null);

function fetchHeatmapData() {
  console.log('HeatmapPage fetchHeatmapData begin');
  fetch('http://127.0.0.1:5000/industry/heatmap')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        heatmapData.value = json.data;
        console.log('HeatmapPage fetchHeatmapData complete');
      })
      .catch((error) => {
        console.error(error);
      })
}

onMounted(async ()=>{
  await nextTick();
  console.log('HeatmapPage onMounted');
  fetchHeatmapData()
})

onUnmounted(()=>{

})

</script>

<template>
  <div class="container">
    <HeatmapComponent :heatmapData="heatmapData"/>
    <div class="test"></div>
    <div class="test2"></div>
    <div class="test"></div>
    <div class="test2"></div>
    <div class="test"></div>
    <div class="test2"></div>
    <div class="test"></div>
    <div class="test2"></div>
    <div class="test"></div>
    <div class="test2"></div>
    <div class="test"></div>
    <div class="test2"></div>
    <div class="test"></div>
    <div class="test2"></div>
    <div class="test"></div>
    <div class="test2"></div>
    <div class="test"></div>
    <div class="test2"></div>
    <div class="test"></div>
    <div class="test2"></div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  background-color: #646cff;
  overflow: auto;
  width: 100vw;
  height: auto;
}
.test {
  background-color: #FF8AA2;
  width: 100%;
  height: 100px;
}
.test2 {
  background-color: #99FF22;
  width: 90%;
  height: 100px;
}
</style>