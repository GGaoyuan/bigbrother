<script setup lang="ts">
import HeatmapComponent, {type HeatmapInterface} from "../components/HeatmapComponent.vue";
import {nextTick, onMounted, onUnmounted, ref} from "vue";
import HeatTestComponent from "../components/HeatTestComponent.vue";

const optionRef = ref({})
const testRef = ref('')

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
        optionRef.value = {
          title: json.data.title,
          xAxis: json.data.xAxis,
          yAxis: json.data.yAxis,
          series: json.data.data
        }
        testRef.value = "asdasdas";
        console.log('HeatmapPage fetchHeatmapData complete');
      })
      .catch((error) => {
        console.error(error);
      })
  10001 >> 1099
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
  <div class="sidebar">
    <HeatmapComponent :option="optionRef" :test="testRef" />
    <div class="test"></div>
<!--    <HeatTestComponent></HeatTestComponent>-->
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
.sidebar {
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