<template>
  <div class="market-sentiment-container">
    <!-- 顶部：日历选择器 -->
    <div class="top-bar">
      <input type="date" class="date-picker" v-model="selectedDate" @change="onDateChange" />
      <span v-if="loading" class="status-text">加载中...</span>
      <span v-if="error" class="status-text error">{{ error }}</span>
    </div>

    <!-- 仪表盘区域 -->
    <div class="gauge-section">
      <div class="gauge-header">
        <div class="gauge-title">市场情绪</div>
        <div class="gauge-date">{{ formattedDate }}</div>
      </div>
      <div ref="gaugeRef" class="gauge-chart"></div>
    </div>

    <!-- Grid 瀑布流 -->
    <div class="grid-waterfall">
      <div class="grid-item" v-for="item in gridItems" :key="item.label">
        <div class="grid-item-label">{{ item.label }}</div>
        <div class="grid-item-value" :style="{ color: item.color }">{{ item.value }}</div>
        <div class="grid-item-sub" v-if="item.sub">{{ item.sub }}</div>
      </div>
    </div>

    <!-- 情绪走势折线图 -->
    <div ref="lineRef" class="line-chart"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { fetchMarketSentiment, type GridItem } from '@/api/marketSentiment'

const WEEK_DAYS = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']

function toLocalDateString(d: Date) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const selectedDate = ref(toLocalDateString(new Date()))

const formattedDate = computed(() => {
  const d = new Date(selectedDate.value + 'T00:00:00')
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day} ${WEEK_DAYS[d.getDay()]}`
})

const gaugeRef = ref<HTMLElement | null>(null)
const lineRef = ref<HTMLElement | null>(null)
let gaugeChart: echarts.ECharts | null = null
let lineChart: echarts.ECharts | null = null

const loading = ref(false)
const error = ref<string | null>(null)
const sentimentScore = ref(0)
const gridItems = ref<GridItem[]>([])

async function loadData(date: string) {
  loading.value = true
  error.value = null
  try {
    const data = await fetchMarketSentiment(date)
    sentimentScore.value = data.score
    gridItems.value = data.grid
    updateGauge(data.score)
  } catch (e) {
    error.value = '数据加载失败，请确认后端服务已启动'
  } finally {
    loading.value = false
  }
}

function getGaugeLabel(val: number) {
  if (val < 20) return '极度悲观'
  if (val < 40) return '悲观'
  if (val < 60) return '中性'
  if (val < 80) return '乐观'
  return '极度乐观'
}

function initGauge() {
  if (!gaugeRef.value) return
  gaugeChart = echarts.init(gaugeRef.value)
  updateGauge(0)
}

function updateGauge(score: number) {
  if (!gaugeChart) return
  gaugeChart.setOption({
    series: [
      {
        type: 'gauge',
        startAngle: 200,
        endAngle: -20,
        min: 0,
        max: 100,
        splitNumber: 10,
        radius: '65%',
        center: ['50%', '60%'],
        axisLine: {
          lineStyle: {
            width: 20,
            color: [
              [0.1, '#0d47a1'],
              [0.2, '#1565c0'],
              [0.3, '#1976d2'],
              [0.4, '#42a5f5'],
              [0.5, '#90caf9'],
              [0.6, '#ef9a9a'],
              [0.7, '#e57373'],
              [0.8, '#ef5350'],
              [0.9, '#e53935'],
              [1.0, '#b71c1c'],
            ],
          },
        },
        pointer: {
          itemStyle: { color: 'auto' },
          length: '60%',
          width: 6,
        },
        axisTick: { distance: -24, length: 5, lineStyle: { color: '#fff', width: 1 } },
        splitLine: { distance: -28, length: 11, lineStyle: { color: '#fff', width: 2 } },
        axisLabel: {
          color: 'inherit',
          distance: 52,
          fontSize: 11,
          formatter: (val: number) => {
            if (val === 0) return '极度\n悲观'
            if (val === 50) return '中性'
            if (val === 100) return '极度\n乐观'
            return ''
          },
        },
        detail: {
          valueAnimation: true,
          formatter: (val: number) => `${val}\n${getGaugeLabel(val)}`,
          color: 'inherit',
          fontSize: 18,
          fontWeight: 'bold',
          lineHeight: 24,
          offsetCenter: [0, '25%'],
        },
        data: [{ value: score, name: '' }],
        title: { show: false },
      },
    ],
  })
}

function initLine() {
  if (!lineRef.value) return
  lineChart = echarts.init(lineRef.value)
  const dates = ['04-14', '04-15', '04-16', '04-17', '04-18', '04-21', '04-22', '04-23']
  const values = [45, 52, 48, 55, 60, 58, 65, 62]
  lineChart.setOption({
    title: { text: '情绪走势', left: 'center', textStyle: { fontSize: 15 } },
    tooltip: { trigger: 'axis' },
    grid: { left: '5%', right: '5%', bottom: '18%', top: '15%', containLabel: true },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', bottom: 12, height: 20, start: 0, end: 100 },
    ],
    xAxis: { type: 'category', data: dates, boundaryGap: false },
    yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { type: 'dashed' } } },
    series: [
      {
        name: '情绪指数',
        type: 'line',
        data: values,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(197,57,41,0.4)' },
            { offset: 1, color: 'rgba(21,101,192,0.1)' },
          ]),
        },
        itemStyle: {
          color: (params: any) => {
            const v = params.data
            if (v >= 60) return '#e53935'
            if (v >= 40) return '#fb8c00'
            return '#1565c0'
          },
        },
      },
    ],
  })
}

function onDateChange() {
  loadData(selectedDate.value)
}

function onResize() {
  gaugeChart?.resize()
  lineChart?.resize()
}

onMounted(() => {
  initGauge()
  initLine()
  loadData(selectedDate.value)
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  gaugeChart?.dispose()
  lineChart?.dispose()
})
</script>

<style scoped>
.market-sentiment-container {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.top-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-text {
  font-size: 0.85rem;
  color: var(--color-text);
  opacity: 0.6;
}

.status-text.error {
  color: #e53935;
  opacity: 1;
}

.date-picker {
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background-soft);
  color: var(--color-text);
  font-size: 0.9rem;
  cursor: pointer;
}

.gauge-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.gauge-header {
  text-align: center;
  margin-bottom: 0.25rem;
}

.gauge-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-heading);
}

.gauge-date {
  font-size: 0.9rem;
  color: var(--color-text);
  opacity: 0.7;
  margin-top: 0.2rem;
}

.gauge-chart {
  width: 100%;
  height: 360px;
}

.grid-waterfall {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
}

.grid-item {
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.grid-item-label {
  font-size: 0.8rem;
  color: var(--color-text);
  opacity: 0.7;
}

.grid-item-value {
  font-size: 1.5rem;
  font-weight: 700;
}

.grid-item-sub {
  font-size: 0.75rem;
  color: var(--color-text);
  opacity: 0.5;
}

.line-chart {
  width: 100%;
  height: 320px;
}
</style>
