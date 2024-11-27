<template>
  <div ref="heatmapChart" style="width: 600px; height: 400px;"></div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import Plotly from 'plotly.js-dist';

const heatmapChart = ref(null);

const data = [
  {
    z: [[1, null, 30, 50, 1], [20, 1, 60, 80, 30], [30, 60, 1, -10, 20]],
    x: ['Morning', 'Afternoon', 'Evening'],
    y: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    type: 'heatmap',
    hoverongaps: false
  }
];


onMounted(() => {
  Plotly.newPlot(heatmapChart.value, data);
});
</script>

<style>
/* 可以在这里添加一些样式 */
</style>