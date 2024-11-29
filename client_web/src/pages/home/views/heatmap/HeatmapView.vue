<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';

// 创建一个响应式引用来保存DOM元素
const chartDom = ref(null);
const heatmapData = ref(null);

let chartInstance = null;

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
        heatmapData.value.data = heatmapData.value.data.map(function (item) {
          return [item[1], item[0], item[2] || '-'];
        })
        console.log(heatmapData.value.data)
        buildHeatmap()
      })
      .catch((error) => {
        console.error(error);
      })
}

function buildHeatmap() {
  chartInstance = echarts.init(chartDom.value)
  console.log(heatmapData.value.title)
  const option = {
    title: {
      text: heatmapData.value.title
    },
    tooltip: {
      position: 'top'
    },
    grid: {
      height: '50%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: heatmapData.value.xAxis,
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: heatmapData.value.yAxis,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: 0,
      max: 10,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '15%'
    },
    series: [
      {
        name: 'Punch Card',
        type: 'heatmap',
        data: heatmapData.value.data,
        label: {
          show: true
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };
  chartInstance.setOption(option);
}

// 初始化ECharts实例并设置配置项（这里以折线图为例，但可灵活替换）
onMounted(async () => {
  await nextTick(); // 确保DOM已经渲染完成
  fetchHeatmapData()
});



// 销毁ECharts实例
onUnmounted(() => {
  if (chartInstance != null && chartInstance.dispose) {
    chartInstance.dispose();
  }
  if (chartInstance == null) {
    console.log('chartInstance 已销毁')
  } else {
    console.log('chartInstance 未销毁')
  }
  //flex-direction: column
});
</script>


<template>
  <div ref="chartDom" style="width: 1000px; height: 400px;"></div>
</template>


<style scoped>

/* 添加一些CSS样式来美化图表容器（可选） */
</style>
