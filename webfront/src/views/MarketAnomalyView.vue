<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import MarketAnomalyKlineItem from '../components/MarketAnomalyKlineItem.vue'

export interface AnomalyNode {
  timeIdx: number
  name: string
  value: number
  type: 'up' | 'down'
}

const timeAxis = ['09:30', '09:45', '10:00', '10:15', '10:30', '10:45', '11:00', '11:15', '11:30', '13:00', '14:00', '14:30', '15:00']
const indexData = [0.38, 0.25, 0.05, -0.89, -0.65, -0.52, -0.48, -0.55, -0.62, -0.70, -0.75, -0.77, -0.77]
const priceData = [4168, 4162, 4148, 4145.48, 4142, 4140, 4139, 4137, 4135, 4132, 4130, 4150.51, 4150.51]
const volumeData = [2.1, 2.8, 3.2, 3.89, 4.1, 4.5, 4.8, 5.0, 5.2, 6.0, 6.5, 6.8, 7.0]
const amountData = [35.2, 46.8, 53.5, 64.45, 68.2, 75.1, 80.2, 83.5, 86.8, 100, 108, 113, 118]

const anomalyNodes = ref<AnomalyNode[]>([
  { timeIdx: 2, name: '光伏', value: 0.05, type: 'down' },
  { timeIdx: 3, name: '电力物联网', value: -0.89, type: 'down' },
  { timeIdx: 5, name: '火电', value: -0.52, type: 'down' },
  { timeIdx: 7, name: '军工', value: -0.55, type: 'up' },
  { timeIdx: 8, name: '农业种植', value: -0.62, type: 'up' },
  { timeIdx: 10, name: '教育', value: -0.75, type: 'up' },
])

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null
const selectedDate = ref(formatDate(new Date()))

function formatDate(d: Date) {
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
}

function initChart() {
  if (!chartRef.value) return
  const scatterDown = anomalyNodes.value.filter((p) => p.type === 'down').map((p) => [timeAxis[p.timeIdx], p.value, p.name] as [string, number, string])
  const scatterUp = anomalyNodes.value.filter((p) => p.type === 'up').map((p) => [timeAxis[p.timeIdx], p.value, p.name] as [string, number, string])

  chart = echarts.init(chartRef.value)
  chart.setOption({
    title: { text: `大盘异动 - 上证指数 ${selectedDate.value}`, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      trigger: 'axis',
      formatter: (params: unknown) => {
        const p = Array.isArray(params) ? params[0] : null
        if (!p || p.dataIndex == null) return ''
        const i = p.dataIndex as number
        return `时间: ${timeAxis[i]}<br/>涨幅: ${indexData[i].toFixed(2)}%<br/>价格: ${priceData[i]}<br/>成交量: ${volumeData[i]}亿<br/>成交额: ${amountData[i]}亿`
      },
    },
    grid: { left: '10%', right: '8%', top: '18%', bottom: '15%' },
    xAxis: { type: 'category', data: timeAxis, boundaryGap: false },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}%' }, min: -1.2, max: 0.6, splitLine: { show: true, lineStyle: { type: 'dashed', opacity: 0.3 } } },
    series: [
      { type: 'line', data: indexData, smooth: true, symbol: 'none', lineStyle: { color: '#2196f3', width: 2 }, areaStyle: { color: 'rgba(33, 150, 243, 0.1)' } },
      { type: 'scatter', data: scatterDown, symbol: 'circle', symbolSize: 10, itemStyle: { color: '#e53935' }, label: { show: true, formatter: (params: { data: [string, number, string] }) => (params.data && params.data[2]) || '', position: 'top', fontSize: 10 } },
      { type: 'scatter', data: scatterUp, symbol: 'circle', symbolSize: 10, itemStyle: { color: '#43a047' }, label: { show: true, formatter: (params: { data: [string, number, string] }) => (params.data && params.data[2]) || '', position: 'top', fontSize: 10 } },
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
  <div class="market-anomaly-page">
    <div class="chart-box">
      <div ref="chartRef" class="chart-dom"></div>
    </div>
    <section class="anomaly-list">
      <h2 class="anomaly-list-title">异动节点 走势图</h2>
      <ul class="anomaly-list-inner">
        <li v-for="node in anomalyNodes" :key="node.name" class="anomaly-list-item">
          <MarketAnomalyKlineItem :node="node" />
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.market-anomaly-page {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 60vh;
}

.chart-box {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-background-soft);
  overflow: hidden;
}

.chart-dom {
  width: 100%;
  height: 420px;
}

.anomaly-list {
  margin-top: 1.5rem;
}

.anomaly-list-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 1rem;
}

.anomaly-list-inner {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.anomaly-list-item {
  min-width: 0;
}
</style>
