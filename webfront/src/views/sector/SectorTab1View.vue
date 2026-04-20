<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const xLabels = ['周一', '周二', '周三', '周四', '周五']
const yLabels = ['银行', '地产', '医药', '消费', '科技', '新能源', '军工', '有色', '煤炭', '电力']

function getMockHeatmapData(): [number, number, number][] {
  const data: [number, number, number][] = []
  for (let j = 0; j < yLabels.length; j++) {
    for (let i = 0; i < xLabels.length; i++) {
      const value = Math.round((Math.random() * 12 - 4) * 10) / 10
      data.push([i, j, value])
    }
  }
  return data
}

const heatmapData = ref<[number, number, number][]>(getMockHeatmapData())

function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  chart.setOption({
    title: { text: '板块涨跌幅热力图', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      position: 'top',
      formatter: (params: { data: [number, number, number] }) => {
        const [x, y, v] = params.data
        return `${yLabels[y]} · ${xLabels[x]}<br/>涨跌幅: ${v}%`
      },
    },
    grid: { left: '12%', right: '8%', top: '15%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: xLabels, splitArea: { show: false } },
    yAxis: { type: 'category', data: yLabels, splitArea: { show: false } },
    visualMap: {
      min: -4,
      max: 8,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: {
        color: ['#1565c0', '#42a5f5', '#e3f2fd', '#fff9c4', '#ffb74d', '#e53935'],
      },
      text: ['高', '低'],
      textStyle: { color: 'var(--color-text)' },
    },
    series: [
      {
        name: '涨跌幅',
        type: 'heatmap',
        data: heatmapData.value,
        label: { show: true, formatter: (params: { data: [number, number, number] }) => `${params.data[2]}%` },
        emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } },
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
</script>

<template>
  <div class="heatmap-page">
    <div class="chart-wrap">
      <div ref="chartRef" class="chart-dom"></div>
    </div>
  </div>
</template>

<style scoped>
.heatmap-page {
  padding: 1rem 0;
}

.chart-wrap {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-background-soft);
  overflow: hidden;
}

.chart-dom {
  width: 100%;
  height: 420px;
}
</style>
