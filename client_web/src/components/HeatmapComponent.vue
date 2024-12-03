<script setup lang="ts">
import {ref, onMounted, onUnmounted, nextTick, watch} from 'vue';
import * as echarts from 'echarts';

export interface HeatmapInterface {
  option: {
    title: string;
    xAxis: string[];
    yAxis: string[];
    series: number[][];
  }
  test: string
}

const props = withDefaults(defineProps<HeatmapInterface>(), {
  option: {
    title: '默认的',
    xAxis: [],
    yAxis: [],
    series: [
      []
    ]
  },
  test: 'dataSource'
})
const heatmap_data = ref(null)

watch(props, (newValue, oldValue)=>{
  heatmap_data.value = newValue.option
  buildHeatmap()
  console.log('111111')
  console.log(newValue.option.title)
  console.log(newValue.option.xAxis)
  console.log(newValue.option.yAxis)
  console.log(newValue.test)
})

const chartDom = ref(null);
let chartInstance = null;


// const props = defineProps(['heatmapData'])
//
// watch(props,(New, Old)=>{
//   heatmapData.value = props.heatmapData;
//   console.log(heatmapData.value);
//   // console.log(chartHeight);
//   buildHeatmap()
// })

function buildHeatmap() {
  if (!chartInstance) {
    chartInstance = echarts.init(chartDom.value);
  }
  // console.log("heatmapData.value.yAxis")
  // console.log(heatmapData.value.yAxis)

  const rows = heatmap_data.value.yAxis.length

  // 每个格子的大小（可根据需要调整）
  const cellSize = 50;
  // const width = cols * cellSize;
  const height = rows * cellSize;
  console.log("width", chartDom.value.parentElement.offsetWidth);
  console.log("height", height);
  // 设置图表宽高
  chartInstance.resize({
    // width: Math.max(chartDom.value.parentElement.offsetWidth, 100), // 最小宽度
    height: Math.max(height, 300), // 最小高度
  });
  console.log(heatmap_data.value.title)
  const option = {
    title: {
      text: heatmap_data.value.title,
      // position: "center",
    },
    tooltip: {
      position: 'top'
    },
    grid: {
      left: "20%",
      right: "20%",
      top: "0%",
      bottom: "100px",
    },
    xAxis: {
      type: 'category',
      data: heatmap_data.value.xAxis,
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: heatmap_data.value.yAxis,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: -5,
      max: 5,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0px',
      inRange: {
        color: [
          '#0000FF', // 深蓝
          '#0055FF', // 蓝色
          '#00AAFF', // 浅蓝
          '#00FFFF', // 青色
          '#55FFAA', // 浅绿色
          '#00FF00', // 绿色
          '#AAFF00', // 黄绿色
          '#FFFF00', // 黄色
          '#FFAA00', // 橙黄色
          '#FF5500', // 橙色
          '#FF0000', // 红色
          '#AA0000', // 深红
        ]
      }
    },
    series: [
      {
        name: 'Punch Card\n222\n33333333\naaaaaaaaaa\n00000000000000',
        type: 'heatmap',
        data: heatmap_data.value.series,
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
  console.log('HeatmapComponent onMounted');
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
