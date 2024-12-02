<script setup>
import {ref, onMounted, onUnmounted, nextTick, watch} from 'vue';
import * as echarts from 'echarts';

const chartDom = ref(null);
// const chartHeight = ref('0px');
let chartInstance = null;
let chartHeight = '400px';
let titleHeight = '50px';
let bottomHeight = '50px';
const heatmapData = ref(null)
const props = defineProps(['heatmapData'])

// console.log('------')
// console.log(heatmapData)
watch(props,(New, Old)=>{
  heatmapData.value = props.heatmapData;
  chartHeight = String(heatmapData.value.yAxis.length * 50 + 100) + 'px'
  console.log(chartHeight);
  buildHeatmap()
})

//
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
      height: chartHeight,
      top: '0px'
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
<!--  <div class="myChart" ref="chartDom" :style="{width: '100vw', height: chartHeight, background:'#AAA172'}"></div>-->
  <div class="myChart" ref="chartDom" :style="{width: '100vw', height: '4400px', background:'#AAA172'}"></div>
</template>

<style scoped>

</style>
