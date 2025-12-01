<script setup lang="ts">
import type { RaceItemBean, RaceViewBean } from "@/components/sector/race/RaceViewBean";
import { ref, onMounted, onBeforeUnmount } from "vue";
import * as echarts from 'echarts';
import type { EChartsOption } from 'echarts';


function prepare() {

}

function addPairs(raceItemBean: RaceItemBean) {
  console.log("addPairs 方法被调用", raceItemBean);

  // 添加新的时间点
  timeIndex++;
  const currentTime = `T${timeIndex}`;
  timePoints.value.push(currentTime);

  // 获取数据值：优先使用 raceItemBean.value，如果没有则使用随机值
  const dataValue = raceItemBean.value !== undefined
      ? raceItemBean.value
      : Math.floor(Math.random() * 100) + 50;

  // 为每个现有系列添加新时间点的数据
  seriesData.value.forEach((values, name) => {
    // 如果这是新系列，初始化数据数组
    if (values.length === 0) {
      // 为新系列填充之前时间点的0值
      for (let i = 0; i < timePoints.value.length - 1; i++) {
        values.push(0);
      }
    }

    // 如果当前系列名称匹配 raceItemBean.name，使用传入的值，否则使用0或保持原值
    if (name === raceItemBean.name) {
      values.push(dataValue);
    } else {
      // 其他系列在当前时间点使用0值（或可以保持最后一个值）
      const lastValue = values.length > 0 ? values[values.length - 1] : 0;
      values.push(lastValue); // 保持上一个值，或者使用 0
    }
  });

  // 如果 raceItemBean 代表新的系列，添加新系列
  if (raceItemBean.name && !seriesData.value.has(raceItemBean.name)) {
    const newSeriesValues: number[] = [];
    // 为新系列填充之前时间点的0值
    for (let i = 0; i < timePoints.value.length - 1; i++) {
      newSeriesValues.push(0);
    }
    // 添加当前时间点的值
    newSeriesValues.push(dataValue);

    seriesData.value.set(raceItemBean.name, newSeriesValues);

    // 分配颜色
    const colorIndex = seriesData.value.size - 1;
    seriesColors.value.set(raceItemBean.name, colorPool[colorIndex % colorPool.length]);
  } else if (raceItemBean.name && seriesData.value.has(raceItemBean.name)) {
    // 如果系列已存在，更新最后一个时间点的值
    const values = seriesData.value.get(raceItemBean.name);
    if (values && values.length > 0) {
      values[values.length - 1] = dataValue;
    }
  }

  // 更新图表
  updateChart();
}



// 使用 defineExpose 暴露方法给父组件
defineExpose({
  addPairs
})

const chartRef = ref<HTMLDivElement>();
let chartInstance: echarts.ECharts | null = null;

// 图表数据管理
const timePoints = ref<string[]>([]);
const seriesData = ref<Map<string, number[]>>(new Map()); // key: 系列名称, value: 该系列在各个时间点的值
const seriesColors = ref<Map<string, string>>(new Map()); // key: 系列名称, value: 颜色
let timeIndex = 0;

// 颜色池，用于自动分配颜色
const colorPool = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#ff9f7f'];

function initChart() {
  if (!chartRef.value) return;
  
  chartInstance = echarts.init(chartRef.value);
  updateChart();
  
  // 窗口大小变化时调整图表
  window.addEventListener('resize', handleResize);
}

function handleResize() {
  chartInstance?.resize();
}

function updateChart() {
  if (!chartInstance) return;
  
  // 构建系列数据
  const series: any[] = [];
  const seriesNames = Array.from(seriesData.value.keys());
  
  seriesNames.forEach((name, index) => {
    const data = seriesData.value.get(name) || [];
    const color = seriesColors.value.get(name) || colorPool[index % colorPool.length];
    
    series.push({
      name: name,
      type: 'line',
      data: data,
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        width: 3,
        color: color
      },
      itemStyle: {
        color: color
      },
      label: {
        show: true,
        position: 'top',
        formatter: (params: any) => {
          return params.value;
        }
      },
      emphasis: {
        focus: 'series'
      }
    });
  });
  
  const option: EChartsOption = {
    title: {
      text: '动态排序折线图 (Line Race Chart)',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: seriesNames,
      top: 40,
      left: 'center',
      type: 'scroll'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: timePoints.value,
      axisLabel: {
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      name: '数值',
      axisLabel: {
        fontSize: 12
      }
    },
    series: series,
    animation: true,
    animationDuration: 1000,
    animationEasing: 'cubicOut'
  };
  
  chartInstance.setOption(option, true);
}



onMounted(() => {
  console.log("RaceView onMounted");
  initChart();
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
})

</script>

<template>
  <div class="race-view">
    <div class="chart-container">
      <div ref="chartRef" class="chart"></div>
    </div>
  </div>
</template>

<style scoped>
.race-view {
  width: 100%;
  padding: 20px;
}

.chart-container {
  width: 100%;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart {
  width: 100%;
  height: 500px;
}
</style>