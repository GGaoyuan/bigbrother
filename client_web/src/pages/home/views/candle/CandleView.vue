<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import HeatmapComponent from "../../../../components/HeatmapComponent.vue";

const heatmapData = ref(null);

function fetchHeatmapData() {
  fetch('http://127.0.0.1:5000/industry/heatmap')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        heatmapData.value = json.data;
        console.log(heatmapData.value.data)
      })
      .catch((error) => {
        console.error(error);
      })
}

// 初始化ECharts实例并设置配置项（这里以折线图为例，但可灵活替换）
onMounted(async () => {
  await nextTick(); // 确保DOM已经渲染完成
  fetchHeatmapData()
});



// 销毁ECharts实例
onUnmounted(() => {

});
</script>


<template>
  <HeatmapComponent :heatmapData="heatmapData" style="width: 100%; height: 100%"></HeatmapComponent>
</template>


<style scoped>

/* 添加一些CSS样式来美化图表容器（可选） */
</style>
