<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

type TimeframeKey = '30m' | '1h' | 'day' | 'week' | 'month'

const TIMEFRAME_OPTIONS: { key: TimeframeKey; label: string }[] = [
  { key: '30m', label: '30分钟线' },
  { key: '1h', label: '1小时线' },
  { key: 'day', label: '日线' },
  { key: 'week', label: '周线' },
  { key: 'month', label: '月线' },
]

function getLabelsAndCount(tf: TimeframeKey): { labels: string[]; count: number } {
  const d = new Date()
  const labels: string[] = []
  let count: number
  if (tf === '30m') {
    count = 48
    for (let i = count - 1; i >= 0; i--) {
      const t = new Date(d)
      t.setMinutes(t.getMinutes() - i * 30)
      labels.push(`${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}`)
    }
  } else if (tf === '1h') {
    count = 24
    for (let i = count - 1; i >= 0; i--) {
      const t = new Date(d)
      t.setHours(t.getHours() - i)
      labels.push(`${String(t.getHours()).padStart(2, '0')}:00`)
    }
  } else if (tf === 'day') {
    count = 30
    for (let i = count - 1; i >= 0; i--) {
      const t = new Date(d)
      t.setDate(t.getDate() - i)
      labels.push(`${t.getMonth() + 1}/${t.getDate()}`)
    }
  } else if (tf === 'week') {
    count = 12
    for (let i = count - 1; i >= 0; i--) {
      const t = new Date(d)
      t.setDate(t.getDate() - i * 7)
      labels.push(`${t.getMonth() + 1}/${t.getDate()}`)
    }
  } else {
    count = 12
    for (let i = count - 1; i >= 0; i--) {
      const t = new Date(d)
      t.setMonth(t.getMonth() - i)
      labels.push(`${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, '0')}`)
    }
  }
  return { labels, count }
}

function mockLineData(count: number, base: number, seed: number): number[] {
  const data: number[] = []
  let v = base
  for (let i = 0; i < count; i++) {
    v = v + (Math.sin((i + seed) * 0.3) * 0.5 + (Math.random() - 0.5) * 0.8)
    data.push(v)
  }
  return data
}

const chartConfigs = [
  { id: 'copper_oil', title: '铜油比', hasOverlay: true },
  { id: 'a50', title: 'A50期指连续', hasOverlay: false },
  { id: 'active_cap', title: '活跃市值', hasOverlay: false },
  { id: 'nasdaq', title: '纳斯达克指数', hasOverlay: false },
  { id: 'gold', title: '伦敦金', hasOverlay: false },
  { id: 'oil', title: '原油', hasOverlay: false },
  { id: 'copper', title: '国际铜价', hasOverlay: false },
]

const group1Indices = [0, 1, 2, 3]
const group2Indices = [4, 5, 6]

const selectedTimeframes = ref<TimeframeKey[]>(Array.from({ length: chartConfigs.length }, () => 'day'))

type OverlayKey = 'hs300' | 'hsi' | 'nasdaq'
const overlayOptions: { key: OverlayKey; label: string }[] = [
  { key: 'hs300', label: '沪深300' },
  { key: 'hsi', label: '恒生指数' },
  { key: 'nasdaq', label: '纳斯达克指数' },
]
const selectedOverlays = ref<OverlayKey[]>(['hs300'])

function setTimeframe(index: number, key: TimeframeKey) {
  selectedTimeframes.value[index] = key
  selectedTimeframes.value = [...selectedTimeframes.value]
}

function toggleOverlay(key: OverlayKey) {
  const i = selectedOverlays.value.indexOf(key)
  if (i === -1) selectedOverlays.value.push(key)
  else selectedOverlays.value.splice(i, 1)
}

const chartRefs = ref<(HTMLElement | null)[]>(Array.from({ length: chartConfigs.length }, () => null))
const chartInstances = ref<(echarts.ECharts | null)[]>([])

function setChartRef(i: number, el: unknown) {
  if (el) (chartRefs.value as (HTMLElement | null)[])[i] = el as HTMLElement
}

function buildOption(index: number) {
  const tf = selectedTimeframes.value[index] ?? 'day'
  const { labels, count } = getLabelsAndCount(tf)
  const cfg = chartConfigs[index]
  if (!cfg) return null

  if (index === 0) {
    const mainData = mockLineData(count, 3.2, 1)
    const series: echarts.SeriesOption[] = [
      { name: '铜油比', type: 'line', data: mainData, smooth: true, symbol: 'none', lineStyle: { color: '#1565c0', width: 2 }, yAxisIndex: 0 },
    ]
    const colors = ['#2e7d32', '#ef6c00', '#7b1fa2']
    const overlayData: { name: string; data: number[] }[] = []
    if (selectedOverlays.value.includes('hs300')) overlayData.push({ name: '沪深300', data: mockLineData(count, 95, 2) })
    if (selectedOverlays.value.includes('hsi')) overlayData.push({ name: '恒生指数', data: mockLineData(count, 92, 3) })
    if (selectedOverlays.value.includes('nasdaq')) overlayData.push({ name: '纳斯达克指数', data: mockLineData(count, 98, 4) })
    overlayData.forEach((s, i) => {
      series.push({ name: s.name, type: 'line', data: s.data, smooth: true, symbol: 'none', lineStyle: { color: colors[i % colors.length], width: 1.5 }, yAxisIndex: 1 })
    })
    return {
      tooltip: { trigger: 'axis' },
      legend: { data: ['铜油比', ...overlayData.map((s) => s.name)], top: 8 },
      grid: { left: '10%', right: '14%', top: '20%', bottom: '15%' },
      xAxis: { type: 'category', data: labels, boundaryGap: false },
      yAxis: [
        { type: 'value', name: '铜油比', position: 'left', splitLine: { show: false } },
        { type: 'value', name: '指数(归一化)', position: 'right', splitLine: { lineStyle: { opacity: 0.2 } } },
      ],
      series,
    }
  }

  const bases: Record<string, number> = { a50: 12500, gold: 2650, oil: 72, active_cap: 45, nasdaq: 18500, copper: 9850 }
  const data = mockLineData(count, bases[cfg.id] ?? 100, index + 10)
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '10%', right: '8%', top: '15%', bottom: '15%' },
    xAxis: { type: 'category', data: labels, boundaryGap: false },
    yAxis: { type: 'value', splitLine: { lineStyle: { opacity: 0.2 } } },
    series: [{ name: cfg.title, type: 'line', data, smooth: true, symbol: 'none', lineStyle: { color: '#1565c0', width: 2 } }],
  }
}

function updateChart(i: number) {
  const inst = chartInstances.value[i]
  if (!inst) return
  const opt = buildOption(i)
  if (opt) inst.setOption(opt, { replaceMerge: ['series'] })
}

function updateAllCharts() {
  chartConfigs.forEach((_, i) => updateChart(i))
}

function onResize() {
  chartInstances.value.forEach((c) => c?.resize())
}

onMounted(() => {
  nextTick(() => {
    const refs = chartRefs.value as (HTMLElement | null)[]
    chartInstances.value = chartConfigs.map((_, i) => {
      const el = refs[i]
      if (!el) return null
      return echarts.init(el)
    })
    updateAllCharts()
  })
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  chartInstances.value.forEach((c) => c?.dispose())
})

watch(
  () => [...selectedTimeframes.value],
  () => updateAllCharts(),
  { deep: true }
)
watch(selectedOverlays, () => updateChart(0), { deep: true })
</script>

<template>
  <div class="indicators-page">
    <section class="chart-group">
      <h2 class="group-title">铜油比 / A50期指连续 / 活跃市值 / 纳斯达克指数</h2>
      <div class="grid-wrap">
        <div v-for="idx in group1Indices" :key="chartConfigs[idx].id" class="grid-item">
          <h3 class="grid-item-title">{{ chartConfigs[idx].title }}</h3>
          <div class="grid-item-row">
            <div class="grid-item-selectors">
              <button
                v-for="t in TIMEFRAME_OPTIONS"
                :key="t.key"
                type="button"
                class="selector-btn"
                :class="{ active: selectedTimeframes[idx] === t.key }"
                @click="setTimeframe(idx, t.key)"
              >
                {{ t.label }}
              </button>
            </div>
            <div v-if="chartConfigs[idx].hasOverlay" class="grid-item-selectors">
              <button
                v-for="opt in overlayOptions"
                :key="opt.key"
                type="button"
                class="selector-btn overlay-btn"
                :class="{ active: selectedOverlays.includes(opt.key) }"
                @click="toggleOverlay(opt.key)"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>
          <div :ref="(el) => setChartRef(idx, el)" class="grid-item-chart"></div>
        </div>
      </div>
    </section>
    <section class="chart-group">
      <h2 class="group-title">伦敦金 / 原油 / 国际铜价</h2>
      <div class="grid-wrap">
        <div v-for="idx in group2Indices" :key="chartConfigs[idx].id" class="grid-item">
          <h3 class="grid-item-title">{{ chartConfigs[idx].title }}</h3>
          <div class="grid-item-row">
            <div class="grid-item-selectors">
              <button
                v-for="t in TIMEFRAME_OPTIONS"
                :key="t.key"
                type="button"
                class="selector-btn"
                :class="{ active: selectedTimeframes[idx] === t.key }"
                @click="setTimeframe(idx, t.key)"
              >
                {{ t.label }}
              </button>
            </div>
          </div>
          <div :ref="(el) => setChartRef(idx, el)" class="grid-item-chart"></div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.indicators-page {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 60vh;
}

.chart-group {
  margin-bottom: 2rem;
}

.chart-group:last-child {
  margin-bottom: 0;
}

.group-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 0.75rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid var(--color-border);
}

.grid-wrap {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.grid-item {
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: var(--color-background-soft);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.grid-item-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 0.75rem;
  flex-shrink: 0;
}

.grid-item-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex-shrink: 0;
}

.grid-item-selectors {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.selector-btn {
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  color: var(--color-text);
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}

.selector-btn:hover {
  border-color: var(--color-border-hover);
  color: var(--color-heading);
}

.selector-btn.active {
  color: #1565c0;
  border-color: #1565c0;
  background: rgba(21, 101, 192, 0.08);
}

.selector-btn.overlay-btn.active {
  color: #2e7d32;
  border-color: #2e7d32;
  background: rgba(46, 125, 50, 0.08);
}

.grid-item-chart {
  width: 100%;
  height: 280px;
  min-height: 0;
}

@media (max-width: 768px) {
  .grid-wrap {
    grid-template-columns: 1fr;
  }
}
</style>
