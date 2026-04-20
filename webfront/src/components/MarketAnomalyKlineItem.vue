<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

export interface AnomalyNode {
  timeIdx: number
  name: string
  value: number
  type: 'up' | 'down'
}

const props = defineProps<{ node: AnomalyNode }>()

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

// 生成 mock 走势数据（单值序列）
function makeTrendData(bars = 20, base = 100) {
  const data: number[] = []
  let v = base
  for (let i = 0; i < bars; i++) {
    v = v + (Math.random() - 0.48) * 4
    data.push(v)
  }
  return data
}

function initChart() {
  if (!chartRef.value) return
  const trendData = makeTrendData(20, 100)
  const dates = trendData.map((_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (19 - i))
    return `${d.getMonth() + 1}/${d.getDate()}`
  })

  const isUp = props.node.type === 'up'
  const lineColor = isUp ? '#43a047' : '#e53935'
  const areaColor = isUp ? 'rgba(67, 160, 71, 0.2)' : 'rgba(229, 57, 53, 0.2)'

  chart = echarts.init(chartRef.value)
  chart.setOption({
    title: { text: props.node.name, left: 'center', textStyle: { fontSize: 13 } },
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    grid: { left: '8%', right: '5%', top: '20%', bottom: '15%' },
    xAxis: { type: 'category', data: dates, boundaryGap: false, axisLabel: { fontSize: 10 } },
    yAxis: { type: 'value', scale: true, splitLine: { lineStyle: { opacity: 0.3 } } },
    series: [
      {
        type: 'line',
        data: trendData,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: lineColor, width: 2 },
        areaStyle: { color: areaColor },
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

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  chart?.dispose()
})

watch(() => props.node, () => {
  if (chart && chartRef.value) initChart()
}, { deep: true })
</script>

<template>
  <div class="trend-item">
    <div ref="chartRef" class="trend-chart"></div>
  </div>
</template>

<style scoped>
.trend-item {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-background-soft);
  overflow: hidden;
}

.trend-chart {
  width: 100%;
  height: 220px;
}
</style>
