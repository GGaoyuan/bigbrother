<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'

const router = useRouter()

interface InfoItem {
  time: string
  title: string
  summary: string
  type: 'notice' | 'hot' | 'alert'
}
const infoList = ref<InfoItem[]>([
  { time: '10:25', title: '上证指数盘中跌破 4140', summary: '大盘异动，军工、农业种植等板块拉升', type: 'alert' },
  { time: '10:15', title: '两市成交额较昨日缩量', summary: '同比昨日约 -2.93%，观望情绪较浓', type: 'notice' },
  { time: '09:45', title: '光伏、电力物联网走弱', summary: '相关概念股集体回调', type: 'hot' },
  { time: '09:35', title: '火电板块异动', summary: '多只个股快速下探', type: 'alert' },
  { time: '09:30', title: '开盘涨跌分布', summary: '涨停 35 只，跌停 6 只，-4%～-2% 区间个股最多', type: 'notice' },
])

const chartRefMarket = ref<HTMLElement | null>(null)
let chartMarket: echarts.ECharts | null = null

function formatDate(d: Date) {
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
}

function initChart() {
  if (!chartRefMarket.value) return
  const timeAxis = ['09:30', '09:45', '10:00', '10:15', '10:30', '10:45', '11:00', '11:15', '11:30', '13:00', '14:00', '14:30', '15:00']
  const indexData = [0.38, 0.25, 0.05, -0.89, -0.65, -0.52, -0.48, -0.55, -0.62, -0.70, -0.75, -0.77, -0.77]
  const priceData = [4168, 4162, 4148, 4145.48, 4142, 4140, 4139, 4137, 4135, 4132, 4130, 4150.51, 4150.51]
  const volumeData = [2.1, 2.8, 3.2, 3.89, 4.1, 4.5, 4.8, 5.0, 5.2, 6.0, 6.5, 6.8, 7.0]
  const amountData = [35.2, 46.8, 53.5, 64.45, 68.2, 75.1, 80.2, 83.5, 86.8, 100, 108, 113, 118]
  const scatterPoints: { timeIdx: number; name: string; value: number; type: 'up' | 'down' }[] = [
    { timeIdx: 2, name: '光伏', value: 0.05, type: 'down' },
    { timeIdx: 3, name: '电力物联网', value: -0.89, type: 'down' },
    { timeIdx: 5, name: '火电', value: -0.52, type: 'down' },
    { timeIdx: 7, name: '军工', value: -0.55, type: 'up' },
    { timeIdx: 8, name: '农业种植', value: -0.62, type: 'up' },
    { timeIdx: 10, name: '教育', value: -0.75, type: 'up' },
  ]
  const scatterDown = scatterPoints.filter((p) => p.type === 'down').map((p) => [timeAxis[p.timeIdx], p.value, p.name] as [string, number, string])
  const scatterUp = scatterPoints.filter((p) => p.type === 'up').map((p) => [timeAxis[p.timeIdx], p.value, p.name] as [string, number, string])
  const dateStr = formatDate(new Date())

  chartMarket = echarts.init(chartRefMarket.value)
  chartMarket.setOption({
    title: { text: `大盘异动 - 上证指数 ${dateStr}`, left: 'center', textStyle: { fontSize: 14 } },
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

function resizeChart() {
  chartMarket?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  chartMarket?.dispose()
})
</script>

<template>
  <div class="today-trade-page">
    <section class="charts-row">
      <div class="chart-box chart-market chart-market-clickable" @click="router.push('/market_anomaly')">
        <div ref="chartRefMarket" class="chart-dom"></div>
      </div>
      <div class="info-list-panel">
        <h3 class="info-list-title">信息列表</h3>
        <ul class="info-list">
          <li v-for="(item, i) in infoList" :key="i" class="info-list-item" :class="`info-list-item--${item.type}`">
            <span class="info-list-time">{{ item.time }}</span>
            <div class="info-list-body">
              <div class="info-list-title-row">{{ item.title }}</div>
              <div class="info-list-summary">{{ item.summary }}</div>
            </div>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<style scoped>
.today-trade-page {
  min-height: 100vh;
  background: var(--color-background);
  color: var(--color-text);
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.chart-box {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-background-soft);
  overflow: hidden;
}

.chart-market {
  min-height: 320px;
}

.chart-market-clickable {
  cursor: pointer;
}

.chart-dom {
  width: 100%;
  height: 320px;
}

.info-list-panel {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-background-soft);
  padding: 1rem;
  min-height: 320px;
  display: flex;
  flex-direction: column;
}

.info-list-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.info-list {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
  overflow-y: auto;
}

.info-list-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.9rem;
}

.info-list-item:last-child {
  border-bottom: none;
}

.info-list-time {
  flex-shrink: 0;
  font-family: ui-monospace, monospace;
  color: var(--color-text);
  opacity: 0.8;
  font-size: 0.85rem;
}

.info-list-body {
  min-width: 0;
}

.info-list-title-row {
  font-weight: 500;
  color: var(--color-heading);
  margin-bottom: 0.2rem;
}

.info-list-summary {
  font-size: 0.85rem;
  color: var(--color-text);
  opacity: 0.85;
  line-height: 1.4;
}

.info-list-item--alert .info-list-title-row { color: #c62828; }
.info-list-item--hot .info-list-title-row { color: #ef6c00; }

@media (max-width: 768px) {
  .charts-row {
    grid-template-columns: 1fr;
  }

  .chart-dom {
    height: 280px;
  }
}
</style>
