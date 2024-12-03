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
  const cellSize = 30;
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
      left: 'center',
    },
    tooltip: {
      position: 'top'
    },
    grid: {
      left: "20%",
      right: "20%",
      top: "30px",
      bottom: "60px",
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
      min: -3,
      max: 3,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0px',
      inRange: {
        color: [
          "#386aff",
          "#4168f3",
          "#4a65e8",
          "#5363dc",
          "#5c60d1",
          "#655ec5",
          "#386aff",
          "#4171ff",
          "#4a78ff",
          "#537eff",
          "#5c85ff",
          "#658cff",
          "#6e93ff",
          "#7799ff",
          "#80a0ff",
          "#89a7ff",
          "#92aeff",
          "#9bb5ff",
          "#a5bbff",
          "#aec2ff",
          "#b7c9ff",
          "#c0d0ff",
          "#c9d6ff",
          "#d2ddff",
          "#dbe4ff",
          "#e4ebff",
          "#edf1ff",
          "#f6f8ff",
          "#fbf3f3",
          "#f7e8e8",
          "#f3dcdc",
          "#f0d1d1",
          "#ecc5c5",
          "#e8b9b9",
          "#e4aeae",
          "#e0a2a2",
          "#dc9797",
          "#d88b8b",
          "#d47f7f",
          "#d17474",
          "#cd6868",
          "#c95d5d",
          "#c55151",
          "#c14646",
          "#bd3a3a",
          "#b92e2e",
          "#b62323",
          "#b21717",
          "#ae0c0c",
          "#aa0000"
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
