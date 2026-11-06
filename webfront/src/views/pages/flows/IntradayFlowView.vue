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
        <span v-if="loading" class="legend-loading">加载中...</span>
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

const BASE_URL = 'http://0.0.0.0:80/api/v1'
const HEADERS = {
  'Content-Type': 'application/json',
  'token': 'gaoyuanzuishuai',
  'uid': '1993',
}

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

interface TodayBillItem {
  time: string
  main_net_inflow: number
  small_net_inflow: number
  medium_net_inflow: number
  large_net_inflow: number
  super_large_net_inflow: number
}

interface DataItem {
  id: string
  code: string
  name: string
  selected: boolean
  color: string
  series: number[]
}

const timeLabels = ref<string[]>([])
const loading = ref(false)

async function fetchBillData(codes: string[]): Promise<Record<string, TodayBillItem[]>> {
  const res = await fetch(`${BASE_URL}/stock/today-bill`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({ codes }),
  })
  if (!res.ok) throw new Error(`请求失败: ${res.status}`)
  const json = await res.json()
  return json.data
}

const themeData = ref<DataItem[]>([
  { id: 'theme-1', code: 'BK0457', name: '人工智能', selected: false, color: '', series: [] },
  { id: 'theme-2', code: 'BK0021', name: '新能源车', selected: false, color: '', series: [] },
  { id: 'theme-3', code: 'BK0447', name: '半导体', selected: false, color: '', series: [] },
  { id: 'theme-4', code: 'BK0438', name: '医疗器械', selected: false, color: '', series: [] },
  { id: 'theme-5', code: 'BK0428', name: '军工', selected: false, color: '', series: [] },
  { id: 'theme-6', code: 'BK0975', name: '数字经济', selected: false, color: '', series: [] },
  { id: 'theme-7', code: 'BK1012', name: '储能', selected: false, color: '', series: [] },
  { id: 'theme-8', code: 'BK0952', name: '机器人', selected: false, color: '', series: [] },
])

const industryData = ref<DataItem[]>([
  { id: 'ind-1', code: 'BK0448', name: '电子', selected: false, color: '', series: [] },
  { id: 'ind-2', code: 'BK0481', name: '汽车', selected: false, color: '', series: [] },
  { id: 'ind-3', code: 'BK0465', name: '医药生物', selected: false, color: '', series: [] },
  { id: 'ind-4', code: 'BK0447', name: '计算机', selected: false, color: '', series: [] },
  { id: 'ind-5', code: 'BK0428', name: '国防军工', selected: false, color: '', series: [] },
  { id: 'ind-6', code: 'BK0478', name: '有色金属', selected: false, color: '', series: [] },
  { id: 'ind-7', code: 'BK0456', name: '食品饮料', selected: false, color: '', series: [] },
  { id: 'ind-8', code: 'BK0475', name: '银行', selected: false, color: '', series: [] },
])

const selectedItems = computed(() =>
  [...themeData.value, ...industryData.value].filter(i => i.selected)
)

async function toggleItem(item: DataItem) {
  item.selected = !item.selected
  if (item.selected) {
    item.color = nextColor()
    loading.value = true
    try {
      const data = await fetchBillData([item.code])
      const bills: TodayBillItem[] = data[item.code] || []
      item.series = bills.map(b => b.main_net_inflow)
      if (timeLabels.value.length === 0 && bills.length > 0) {
        timeLabels.value = bills.map(b => b.time)
      }
    } catch (e) {
      console.error(e)
      item.series = []
    } finally {
      loading.value = false
    }
    await nextTick()
    drawChart()
  } else {
    item.color = ''
    item.series = []
    drawChart()
  }
}

// ─── 绘图 ─────────────────────────────────────────────────────────────────────

const PAD = { l: 60, r: 20, t: 20, b: 40 }

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

  const active = selectedItems.value.filter(i => i.series.length > 0)
  if (active.length === 0) {
    ctx.fillStyle = '#aaa'
    ctx.font = '14px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('请从下方选择题材或行业以显示折线', W / 2, H / 2)
    return
  }

  const maxLen = Math.max(...active.map(i => i.series.length))
  const allValues = active.flatMap(i => i.series)
  const minVal = Math.min(...allValues)
  const maxVal = Math.max(...allValues)
  const range = maxVal - minVal || 1

  const toX = (i: number) => l + (i / (maxLen - 1 || 1)) * (W - l - r)
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

  // X 轴标签（从 timeLabels 中均匀取 6 个）
  ctx.textAlign = 'center'
  ctx.fillStyle = '#888'
  const labels = timeLabels.value
  if (labels.length > 0) {
    const n = labels.length
    const step = Math.max(1, Math.floor(n / 5))
    const idxs = [...new Set([0, step, step * 2, step * 3, step * 4, n - 1])]
    idxs.forEach(idx => {
      ctx.fillText(labels[idx], toX(idx), H - b + 16)
    })
  }
}

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

.legend-loading {
  font-size: 0.8rem;
  color: #888;
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

/* 选中时底部颜色条 */
.item-color-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
}
</style>
