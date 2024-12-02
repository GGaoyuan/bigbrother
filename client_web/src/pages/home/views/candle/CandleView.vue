<script setup>
import HeatmapComponent from "../../../../components/HeatmapComponent.vue";
import {nextTick, onMounted, ref} from "vue";

const heatmapData = ref(null);
// const hmData = ref(null);
const hm1 = ref(null);
const hm2 = ref(null);
const hm3 = ref(null);

function fetchHeatmapData() {
  fetch('http://127.0.0.1:5000/industry/heatmap')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        // heatmapData.value = '1111'
        heatmapData.value = json.data;
        console.log('json response');
        // console.log(heatmapData.value.data)
        // buildHeatmap()
      })
      .catch((error) => {
        console.error(error);
      })
}

onMounted(async () => {
  await nextTick(); // 确保DOM已经渲染完成
  fetchHeatmapData()
});


</script>

<template>
  <div class="container">
    <HeatmapComponent :heatmapData="heatmapData" ref="hm1" style="background-color: #880022"></HeatmapComponent>
<!--    <HeatmapComponent :heatmapData="heatmapData" ref="hm2" style="background-color: #f9f9f9"></HeatmapComponent>-->
<!--    <HeatmapComponent :heatmapData="heatmapData" ref="hm3" style="background-color: #FF8AA2"></HeatmapComponent>-->
  </div>
</template>


<style scoped>
.container {
  background-color: #646cff;
  display: flex;
  flex-direction: column;
  width: 100vw;
  overflow: auto;
}
</style>