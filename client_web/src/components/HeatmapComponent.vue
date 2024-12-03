<script setup>
import {ref, onMounted, onUnmounted, nextTick, watch} from 'vue';
import * as echarts from 'echarts';

const chartDom = ref(null);
let chartInstance = null;

const heatmapData = ref(null)
const props = defineProps(['heatmapData'])

watch(props,(New, Old)=>{
  heatmapData.value = props.heatmapData;
  console.log(heatmapData.value);
  // console.log(chartHeight);
  buildHeatmap()
})

function buildHeatmap() {
  if (!chartInstance) {
    chartInstance = echarts.init(chartDom.value);
  }
  console.log("heatmapData.value.yAxis")
  console.log(heatmapData.value.yAxis)
  const rows = heatmapData.value.yAxis.length

  // 每个格子的大小（可根据需要调整）
  const cellSize = 20;
  // const width = cols * cellSize;
  const height = rows * cellSize;
  console.log("width", chartDom.value.parentElement.offsetWidth);
  console.log("height", height);
  // 设置图表宽高
  chartInstance.resize({
    // width: Math.max(chartDom.value.parentElement.offsetWidth, 100), // 最小宽度
    height: Math.max(height, 300), // 最小高度
  });
  console.log(heatmapData.value.title)
  const option = {
    title: {
      text: heatmapData.value.title
    },
    tooltip: {
      position: 'top'
    },
    grid: {
      left: "10%",
      right: "20%",
      top: "30%",
      bottom: "40%",
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
      min: -10,
      max: 10,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0px'
    },
    series: [
      {
        name: 'Punch Card\n222\n33333333\naaaaaaaaaa\n00000000000000',
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
  // buildHeatmap()
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
});

</script>

<template>
  <div ref="chartDom" style="width: 100%; min-height: 100px; background-color: #213547"></div>
</template>

<style scoped>
div {
  width: 100%;
  height: 100%;
}
</style>
