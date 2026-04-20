<script setup lang="ts">
/**
 * 等高原色柱状图（ECharts 柱状图）
 * 6 根柱子等高；从左到右颜色：上三红（深红→红→红）、下三绿（绿→绿→深绿）
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const BAR_COLORS = [
  '#b71c1c', // 1 深红
  '#c62828', // 2 红
  '#d32f2f', // 3 红
  '#43a047', // 4 绿
  '#2e7d32', // 5 绿
  '#1b5e20', // 6 深绿
] as const

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const props = withDefaults(
  defineProps<{
    /** 柱子高度（统一数值），默认 100 */
    barValue?: number
    /** 类目名，默认 6 个空标签 */
    categories?: string[]
    /** 图表高度（px），默认 200 */
    height?: number
  }>(),
  {
    barValue: 100,
    categories: () => [] as string[],
    height: 200,
  }
)

const categories = computed(() => {
  const c = props.categories.length ? props.categories : ['', '', '', '', '', '']
  return c.length >= 6 ? c.slice(0, 6) : [...c, ...Array(6 - c.length).fill('')]
})

function initChart() {
  if (!chartRef.value) return
  const cats = categories.value
  const data = cats.map((_, i) => ({
    value: props.barValue,
    itemStyle: { color: BAR_COLORS[i] },
  }))

  chart = echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: '12%', right: '8%', top: '10%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: cats,
      axisLabel: { fontSize: 11 },
      axisLine: { lineStyle: { color: '#ddd' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: props.barValue,
      splitLine: { lineStyle: { opacity: 0.2 } },
      axisLabel: { fontSize: 10 },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [
      {
        type: 'bar',
        data,
        barWidth: '60%',
        barGap: '30%',
      },
    ],
  })
}

function onResize() {
  chart?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', onResize)
})

watch(
  () => [props.barValue, props.categories, props.height],
  () => {
    if (chart && chartRef.value) initChart()
  },
  { deep: true }
)

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  chart?.dispose()
})
</script>

<template>
  <div class="equal-bar-chart" role="img" aria-label="等高原色柱状图">
    <div ref="chartRef" class="chart-dom" :style="{ height: `${height}px` }"></div>
  </div>
</template>

<style scoped>
.equal-bar-chart {
  width: 100%;
  padding: 0.5rem 0;
}

.chart-dom {
  width: 100%;
  min-height: 160px;
}
</style>
