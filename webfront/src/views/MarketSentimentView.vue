<template>
  <div class="market-sentiment-container">
    <!-- 顶部：日历选择器 -->
    <div class="top-bar">
      <input type="date" class="date-picker" v-model="selectedDate" @change="onDateChange" />
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

const WEEK_DAYS = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']

function toLocalDateString(d: Date) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

// 用日期字符串做种子生成伪随机数，保证同一天数据一致
function seededRand(seed: string, index: number) {
  let h = index + 1
  for (let i = 0; i < seed.length; i++) {
    h = Math.imul(31, h) + seed.charCodeAt(i) | 0
  }
  return Math.abs(h % 1000) / 1000
}

function genDataForDate(date: string) {
  const r = (i: number, min: number, max: number) => Math.round(seededRand(date, i) * (max - min) + min)
  const rf = (i: number, min: number, max: number) => (seededRand(date, i) * (max - min) + min).toFixed(2)

  const up = r(0, 1200, 3000)
  const down = r(1, 800, 2500)
  const limitUp = r(2, 20, 150)
  const limitDown = r(3, 2, 40)
  const blowRate = (seededRand(date, 4) * 30 + 5).toFixed(1)
  const maxStreak = r(5, 1, 8)
  const volume = r(6, 5000, 15000)
  const sentimentScore = r(7, 10, 95)

  return {
    score: sentimentScore,
    grid: [
      { label: '上涨', value: String(up), color: '#e53935' },
      { label: '下跌', value: String(down), color: '#43a047' },
      { label: '涨跌对比', value: rf(8, 0.5, 2.5), color: up > down ? '#e53935' : '#43a047', sub: '涨/跌' },
      { label: '涨停', value: String(limitUp), color: '#e53935' },
      { label: '跌停', value: String(limitDown), color: '#43a047' },
      { label: '涨跌停对比', value: rf(9, 1, 10), color: limitUp > limitDown ? '#e53935' : '#43a047', sub: '涨停/跌停' },
      { label: '炸板率', value: `${blowRate}%`, color: '#fb8c00' },
      { label: '最高连板', value: `${maxStreak}板`, color: '#e53935' },
      { label: '成交量', value: `${volume}亿`, color: '#1565c0' },
    ],
  }
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

const currentData = ref(genDataForDate(selectedDate.value))
const gridItems = computed(() => currentData.value.grid)

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
  updateGauge(currentData.value.score)
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
  currentData.value = genDataForDate(selectedDate.value)
  updateGauge(currentData.value.score)
}

function onResize() {
  gaugeChart?.resize()
  lineChart?.resize()
}

onMounted(() => {
  initGauge()
  initLine()
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
