<template>
  <div class="intraday-flow-view">
    <!-- 日历选择器 -->
    <div class="date-picker-section">
      <label for="date-picker">选择日期：</label>
      <input id="date-picker" type="date" v-model="selectedDate" class="date-picker" />
    </div>

    <!-- 折线图 -->
    <div class="chart-section">
      <div class="chart-legend">
        <span v-for="item in selectedItems" :key="item.id" class="legend-item">
          <span class="legend-dot" :style="{ background: item.color }"></span>
          {{ item.name }}
        </span>
        <span v-if="selectedItems.length === 0" class="legend-empty">请从下方选择题材或行业</span>
      </div>
      <div class="chart-container">
        <canvas ref="chartCanvas"></canvas>
      </div>
    </div>

    <!-- 题材Grid -->
    <div class="grid-section">
      <h2>题材</h2>
      <div class="item-grid">
        <div
          v-for="item in themeData"
          :key="item.id"
          class="grid-item"
          :class="{ 'grid-item--selected': item.selected }"
          @click="toggleItem(item)"
        >
          <div class="item-check">
            <div class="checkbox" :class="{ 'checkbox--checked': item.selected }">
              <svg v-if="item.selected" viewBox="0 0 12 12" fill="none">
                <path d="M2 6l3 3 5-5" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <div class="item-body">
            <div class="item-name">{{ item.name }}</div>
            <div class="item-meta">
              <span class="item-net" :class="item.net >= 0 ? 'pos' : 'neg'">
                {{ item.net >= 0 ? '+' : '' }}{{ (item.net / 10000).toFixed(2) }}亿
              </span>
              <span class="item-change" :class="item.change >= 0 ? 'pos' : 'neg'">
                {{ item.change >= 0 ? '+' : '' }}{{ item.change }}%
              </span>
            </div>
          </div>
          <div
            v-if="item.selected"
            class="item-color-bar"
            :style="{ background: item.color }"
          ></div>
        </div>
      </div>
    </div>

    <!-- 行业Grid -->
    <div class="grid-section">
      <h2>行业</h2>
      <div class="item-grid">
        <div
          v-for="item in industryData"
          :key="item.id"
          class="grid-item"
          :class="{ 'grid-item--selected': item.selected }"
          @click="toggleItem(item)"
        >
          <div class="item-check">
            <div class="checkbox" :class="{ 'checkbox--checked': item.selected }">
              <svg v-if="item.selected" viewBox="0 0 12 12" fill="none">
                <path d="M2 6l3 3 5-5" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <div class="item-body">
            <div class="item-name">{{ item.name }}</div>
            <div class="item-meta">
              <span class="item-net" :class="item.net >= 0 ? 'pos' : 'neg'">
                {{ item.net >= 0 ? '+' : '' }}{{ (item.net / 10000).toFixed(2) }}亿
              </span>
              <span class="item-change" :class="item.change >= 0 ? 'pos' : 'neg'">
                {{ item.change >= 0 ? '+' : '' }}{{ item.change }}%
              </span>
            </div>
          </div>
          <div
            v-if="item.selected"
            class="item-color-bar"
            :style="{ background: item.color }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

const selectedDate = ref(new Date().toISOString().split('T')[0])
const chartCanvas = ref<HTMLCanvasElement | null>(null)

const LINE_COLORS = [
  '#1565c0', '#e53935', '#2e7d32', '#f57c00', '#6a1b9a',
  '#00838f', '#ad1457', '#558b2f', '#4527a0', '#00695c',
]

let colorIndex = 0
function nextColor() {
  const c = LINE_COLORS[colorIndex % LINE_COLORS.length]
  colorIndex++
  return c
}

interface DataItem {
  id: string
  name: string
  inflow: number
  outflow: number
  net: number
  change: number
  selected: boolean
  color: string
  // 固定的模拟分时数据（210个点）
  series: number[]
}

function makeSeries(seed: number): number[] {
  let v = seed
  return Array.from({ length: 210 }, (_, i) => {
    v += Math.sin(i / 15 + seed) * 800 + (Math.random() - 0.48) * 600
    return v
  })
}

const themeData = ref<DataItem[]>([
  { id: 'theme-1', name: '人工智能', inflow: 123400, outflow: 89200, net: 34200, change: 2.35, selected: false, color: '', series: makeSeries(1.2) },
  { id: 'theme-2', name: '新能源车', inflow: 98700, outflow: 112000, net: -13300, change: -0.87, selected: false, color: '', series: makeSeries(2.5) },
  { id: 'theme-3', name: '半导体', inflow: 156000, outflow: 103000, net: 53000, change: 3.12, selected: false, color: '', series: makeSeries(0.7) },
  { id: 'theme-4', name: '医疗器械', inflow: 67800, outflow: 71000, net: -3200, change: -0.21, selected: false, color: '', series: makeSeries(3.1) },
  { id: 'theme-5', name: '军工', inflow: 89000, outflow: 65000, net: 24000, change: 1.56, selected: false, color: '', series: makeSeries(1.8) },
  { id: 'theme-6', name: '数字经济', inflow: 110000, outflow: 95000, net: 15000, change: 0.92, selected: false, color: '', series: makeSeries(4.0) },
  { id: 'theme-7', name: '储能', inflow: 78000, outflow: 82000, net: -4000, change: -0.35, selected: false, color: '', series: makeSeries(2.2) },
  { id: 'theme-8', name: '机器人', inflow: 134000, outflow: 88000, net: 46000, change: 2.78, selected: false, color: '', series: makeSeries(5.0) },
])

const industryData = ref<DataItem[]>([
  { id: 'ind-1', name: '电子', inflow: 234000, outflow: 189000, net: 45000, change: 1.89, selected: false, color: '', series: makeSeries(0.3) },
  { id: 'ind-2', name: '汽车', inflow: 178000, outflow: 192000, net: -14000, change: -0.65, selected: false, color: '', series: makeSeries(1.1) },
  { id: 'ind-3', name: '医药生物', inflow: 145000, outflow: 123000, net: 22000, change: 0.98, selected: false, color: '', series: makeSeries(3.5) },
  { id: 'ind-4', name: '计算机', inflow: 196000, outflow: 154000, net: 42000, change: 2.14, selected: false, color: '', series: makeSeries(0.9) },
  { id: 'ind-5', name: '国防军工', inflow: 112000, outflow: 98000, net: 14000, change: 0.73, selected: false, color: '', series: makeSeries(2.8) },
  { id: 'ind-6', name: '有色金属', inflow: 88000, outflow: 102000, net: -14000, change: -0.54, selected: false, color: '', series: makeSeries(4.4) },
  { id: 'ind-7', name: '食品饮料', inflow: 76000, outflow: 69000, net: 7000, change: 0.41, selected: false, color: '', series: makeSeries(1.6) },
  { id: 'ind-8', name: '银行', inflow: 201000, outflow: 185000, net: 16000, change: 0.28, selected: false, color: '', series: makeSeries(3.8) },
])

const selectedItems = computed(() =>
  [...themeData.value, ...industryData.value].filter(i => i.selected)
)

function toggleItem(item: DataItem) {
  item.selected = !item.selected
  if (item.selected) {
    item.color = nextColor()
  } else {
    item.color = ''
  }
}

// ─── 绘图 ─────────────────────────────────────────────────────────────────────

const PAD = { l: 60, r: 20, t: 20, b: 40 }
const TIME_LABELS = ['9:30', '10:30', '11:30', '13:00', '14:00', '15:00']
const TIME_IDXS   = [0, 42, 84, 120, 162, 209]

function drawChart() {
  const canvas = chartCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const dpr = window.devicePixelRatio || 1
  const rect = canvas.parentElement!.getBoundingClientRect()
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  canvas.style.width = rect.width + 'px'
  canvas.style.height = rect.height + 'px'
  ctx.scale(dpr, dpr)

  const W = rect.width
  const H = rect.height
  const { l, r, t, b } = PAD

  ctx.clearRect(0, 0, W, H)

  const active = selectedItems.value
  if (active.length === 0) {
    ctx.fillStyle = '#aaa'
    ctx.font = '14px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('请从下方选择题材或行业以显示折线', W / 2, H / 2)
    return
  }

  // 全局 min/max（跨所有选中 series）
  const allValues = active.flatMap(i => i.series)
  const minVal = Math.min(...allValues)
  const maxVal = Math.max(...allValues)
  const range = maxVal - minVal || 1

  const toX = (i: number) => l + (i / 209) * (W - l - r)
  const toY = (v: number) => t + (1 - (v - minVal) / range) * (H - t - b)

  // 零线
  const zeroY = toY(0)
  if (zeroY >= t && zeroY <= H - b) {
    ctx.strokeStyle = 'rgba(150,150,150,0.4)'
    ctx.setLineDash([4, 4])
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(l, zeroY)
    ctx.lineTo(W - r, zeroY)
    ctx.stroke()
    ctx.setLineDash([])
  }

  // 每条折线
  active.forEach(item => {
    ctx.strokeStyle = item.color
    ctx.lineWidth = 1.5
    ctx.beginPath()
    item.series.forEach((v, i) => {
      i === 0 ? ctx.moveTo(toX(i), toY(v)) : ctx.lineTo(toX(i), toY(v))
    })
    ctx.stroke()
  })

  // Y 轴标签
  ctx.fillStyle = '#888'
  ctx.font = '11px sans-serif'
  ctx.textAlign = 'right'
  const yTicks = [minVal, (minVal + maxVal) / 2, maxVal]
  yTicks.forEach(v => {
    ctx.fillText((v / 10000).toFixed(1) + '亿', l - 6, toY(v) + 4)
  })

  // X 轴标签
  ctx.textAlign = 'center'
  ctx.fillStyle = '#888'
  TIME_LABELS.forEach((label, i) => {
    ctx.fillText(label, toX(TIME_IDXS[i]), H - b + 16)
  })
}

// 选中项变化或日期变化时重绘
watch(selectedItems, () => nextTick(drawChart), { deep: true })
watch(selectedDate, () => nextTick(drawChart))

const handleResize = () => drawChart()

onMounted(() => {
  drawChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.intraday-flow-view {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 日期选择 */
.date-picker-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
  color: var(--color-text);
}

.date-picker {
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.9rem;
  cursor: pointer;
}

/* 折线图 */
.chart-section {
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  min-height: 22px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--color-text);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-empty {
  font-size: 0.8rem;
  color: #aaa;
}

.chart-container {
  width: 100%;
  height: 280px;
}

.chart-container canvas {
  display: block;
}

/* Grid 区块 */
.grid-section {
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
}

.grid-section h2 {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-heading);
  margin: 0 0 0.75rem;
}

.item-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.5rem;
}

/* 每个 item 卡片 */
.grid-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  background: var(--color-background);
  transition: border-color 0.15s, box-shadow 0.15s, background 0.15s;
  overflow: hidden;
  user-select: none;
}

.grid-item:hover {
  border-color: #90caf9;
  background: var(--color-background-mute);
}

.grid-item--selected {
  border-color: transparent;
  box-shadow: 0 0 0 2px currentColor;
}

/* checkbox */
.item-check {
  flex-shrink: 0;
}

.checkbox {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1.5px solid var(--color-border);
  background: var(--color-background);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, border-color 0.15s;
}

.checkbox--checked {
  background: #1565c0;
  border-color: #1565c0;
}

.checkbox svg {
  width: 10px;
  height: 10px;
}

/* item 内容 */
.item-body {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-heading);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-meta {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.2rem;
}

.item-net,
.item-change {
  font-size: 0.72rem;
}

.pos { color: #c62828; }
.neg { color: #2e7d32; }

/* 选中时底部颜色条 */
.item-color-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
}
</style>
