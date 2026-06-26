<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import {
  createChart,
  CandlestickSeries,
  LineSeries,
  type IChartApi,
  type CandlestickData,
  type LineData,
} from 'lightweight-charts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { RefreshCw, Plus, Trash2 } from '@lucide/vue'
import {
  indexApi,
  type IndexInfo,
  type IndexKlineBar,
} from '@/lib/api'

// ═══ 周期 ════════════════════════════════════════════════════════════
type Period = 'day' | 'week' | 'month'
const PERIODS: { value: Period; label: string }[] = [
  { value: 'day', label: '日线' },
  { value: 'week', label: '周线' },
  { value: 'month', label: '月线' },
]

// ═══ 均线配置 ════════════════════════════════════════════════════════
interface MaConfig {
  id: number
  days: number // X 日均线
  offset: number // 偏移量（点数，正上浮 / 负下浮）
  color: string
}

const MA_STORAGE_KEY = 'index-chart-ma-config'
const DEFAULT_MA: MaConfig[] = [{ id: 1, days: 30, offset: 0, color: '#f59e0b' }]

function loadMaConfig(): MaConfig[] {
  try {
    const raw = localStorage.getItem(MA_STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw) as MaConfig[]
      if (Array.isArray(parsed) && parsed.length > 0) return parsed
    }
  } catch {
    // 忽略损坏的缓存
  }
  return JSON.parse(JSON.stringify(DEFAULT_MA))
}

const maConfigs = ref<MaConfig[]>(loadMaConfig())
let maIdCursor = Math.max(0, ...maConfigs.value.map((m) => m.id)) + 1

// 持久化 + 重绘：均线配置变化即写入 localStorage 并重算曲线（不重新拉数据）
watch(
  maConfigs,
  (val) => {
    try {
      localStorage.setItem(MA_STORAGE_KEY, JSON.stringify(val))
    } catch {
      // 忽略写入失败
    }
    renderAllMaLines()
  },
  { deep: true },
)

function addMa() {
  if (maConfigs.value.length >= 3) return
  const palette = ['#f59e0b', '#3b82f6', '#ec4899']
  maConfigs.value.push({
    id: maIdCursor++,
    days: 60,
    offset: 0,
    color: palette[maConfigs.value.length % palette.length],
  })
}

function removeMa(id: number) {
  maConfigs.value = maConfigs.value.filter((m) => m.id !== id)
}

// ═══ 指数状态管理 ════════════════════════════════════════════════════════
interface IndexChartState {
  symbol: string
  name: string
  period: Period
  loading: boolean
  error: string | null
  bars: IndexKlineBar[]
  chart: IChartApi | null
  candleSeries: any
  maSeries: Map<number, any>
  chartContainer: HTMLElement | null
}

const indices = ref<IndexInfo[]>([])
const indexStates = ref<Map<string, IndexChartState>>(new Map())

// ═══ 滚动相关 ════════════════════════════════════════════════════════
const navSticky = ref(false)
const scrollContainerRef = ref<HTMLElement | null>(null)
// sectionRefs: 每个指数区块的外层容器（用于滚动定位）
// chartRefs:   每个指数的图表挂载容器（用于 createChart）
// 两者必须分开，否则后绑定的 ref 会覆盖前者
const sectionRefs = ref<Record<string, HTMLElement | null>>({})
const chartRefs = ref<Record<string, HTMLElement | null>>({})

function scrollToIndex(symbol: string) {
  const el = sectionRefs.value[symbol]
  if (!el) return

  // 滚动到对应区块位置
  el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function handleScroll() {
  if (!scrollContainerRef.value) return
  // 顶部导航悬浮判断
  navSticky.value = scrollContainerRef.value.scrollTop > 100
}

// ═══ 图表工具函数 ════════════════════════════════════════════════════
function toCandles(src: IndexKlineBar[]): CandlestickData[] {
  return src
    .filter((b) => b.trade_date && b.close !== null)
    .map((b) => ({
      time: b.trade_date as string,
      open: b.open ?? 0,
      high: b.high ?? 0,
      low: b.low ?? 0,
      close: b.close ?? 0,
    }))
}

function computeMa(src: IndexKlineBar[], days: number, offset: number): LineData[] {
  // 强制数值化：输入框清空时 v-model.number 会给出空字符串，
  // 直接参与运算会触发字符串拼接，导致 LineSeries 报 "value must be a number"
  const d = Math.max(1, Math.floor(Number(days) || 1))
  const off = Number(offset) || 0
  const valid = src.filter(
    (b) => b.trade_date && b.close !== null && b.close !== undefined && !isNaN(Number(b.close)),
  )
  const out: LineData[] = []
  let sum = 0
  for (let i = 0; i < valid.length; i++) {
    sum += Number(valid[i].close)
    if (i >= d) sum -= Number(valid[i - d].close)
    if (i >= d - 1) {
      out.push({
        time: valid[i].trade_date as string,
        value: sum / d + off,
      })
    }
  }
  return out
}

function renderMaLines(state: IndexChartState) {
  if (!state.chart) return

  // 移除已不存在的均线系列
  for (const [id, series] of state.maSeries.entries()) {
    if (!maConfigs.value.some((m) => m.id === id)) {
      state.chart.removeSeries(series)
      state.maSeries.delete(id)
    }
  }

  // 新增/更新
  for (const ma of maConfigs.value) {
    let series = state.maSeries.get(ma.id)
    if (!series) {
      series = state.chart.addSeries(LineSeries, { color: ma.color, lineWidth: 2 })
      state.maSeries.set(ma.id, series)
    } else {
      series.applyOptions({ color: ma.color })
    }
    const data = computeMa(state.bars, ma.days, ma.offset)
    series.setData(data)
  }
}

function renderAllMaLines() {
  for (const state of indexStates.value.values()) {
    renderMaLines(state)
  }
}

function initChart(state: IndexChartState, container: HTMLElement) {
  state.chartContainer = container
  state.chart = createChart(container, {
    width: container.clientWidth,
    height: 480,
    layout: { background: { color: 'transparent' }, textColor: '#9CA3AF' },
    grid: {
      vertLines: { color: 'rgba(156, 163, 175, 0.1)' },
      horzLines: { color: 'rgba(156, 163, 175, 0.1)' },
    },
    rightPriceScale: { borderColor: 'rgba(156, 163, 175, 0.3)' },
    timeScale: { borderColor: 'rgba(156, 163, 175, 0.3)', timeVisible: false },
    crosshair: { mode: 0 },
    // 鼠标在图表上时不抢页面滚轮：禁用滚轮缩放/滚动，保留拖拽平移
    handleScroll: { mouseWheel: false, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: true },
    handleScale: { mouseWheel: false, pinch: true, axisPressedMouseMove: true },
  })

  state.candleSeries = state.chart.addSeries(CandlestickSeries, {
    upColor: '#ef4444',
    downColor: '#22c55e',
    borderUpColor: '#ef4444',
    borderDownColor: '#22c55e',
    wickUpColor: '#ef4444',
    wickDownColor: '#22c55e',
  })

  // 响应式调整
  const resizeObserver = new ResizeObserver(() => {
    if (state.chart && container) {
      state.chart.applyOptions({ width: container.clientWidth })
    }
  })
  resizeObserver.observe(container)
}

// ═══ 数据加载 ════════════════════════════════════════════════════════
async function loadKline(symbol: string) {
  const state = indexStates.value.get(symbol)
  if (!state) return

  state.loading = true
  state.error = null

  try {
    const res = await indexApi.kline(symbol, state.period, 800)
    state.bars = res.bars

    if (state.candleSeries) {
      state.candleSeries.setData(toCandles(state.bars))
      state.chart?.timeScale().fitContent()
    }

    renderMaLines(state)
  } catch (e) {
    state.error = e instanceof Error ? e.message : String(e)
  } finally {
    state.loading = false
  }
}

function selectPeriod(symbol: string, period: Period) {
  const state = indexStates.value.get(symbol)
  if (!state || state.period === period) return

  state.period = period
  loadKline(symbol)
}

async function refreshAll() {
  for (const symbol of indexStates.value.keys()) {
    await loadKline(symbol)
  }
}

// ═══ 生命周期 ════════════════════════════════════════════════════════
onMounted(async () => {
  try {
    indices.value = await indexApi.list()

    // 为每个指数初始化状态
    for (const idx of indices.value) {
      indexStates.value.set(idx.symbol, {
        symbol: idx.symbol,
        name: idx.name,
        period: 'day',
        loading: false,
        error: null,
        bars: [],
        chart: null,
        candleSeries: null,
        maSeries: new Map(),
        chartContainer: null,
      })
    }

    // 等待 DOM 渲染后初始化图表
    await nextTick()

    for (const idx of indices.value) {
      const container = chartRefs.value[idx.symbol]
      if (container) {
        const state = indexStates.value.get(idx.symbol)
        if (state) {
          initChart(state, container)
          await loadKline(idx.symbol)
        }
      }
    }
  } catch (e) {
    console.error('Failed to load indices:', e)
  }
})

onUnmounted(() => {
  for (const state of indexStates.value.values()) {
    if (state.chart) {
      state.chart.remove()
    }
  }
})
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden">
    <!-- 固定的顶部导航 -->
    <div
      :class="[
        'sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60',
        'border-b transition-shadow',
        navSticky && 'shadow-md',
      ]"
    >
      <div class="container py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <h1 class="text-2xl font-bold tracking-tight">指数行情</h1>
            <div class="flex gap-2">
              <button
                v-for="idx in indices"
                :key="idx.symbol"
                @click="scrollToIndex(idx.symbol)"
                class="px-4 py-2 text-sm font-medium rounded-md border transition-colors hover:bg-accent"
              >
                {{ idx.name }}
              </button>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            @click="refreshAll"
            class="gap-2"
          >
            <RefreshCw class="size-4" />
            刷新全部
          </Button>
        </div>
      </div>
    </div>

    <!-- 可滚动的内容区 -->
    <div
      ref="scrollContainerRef"
      @scroll="handleScroll"
      class="flex-1 overflow-y-auto"
    >
      <div class="container py-6 space-y-8">
        <!-- 每个指数一个图表区域 -->
        <div
          v-for="idx in indices"
          :key="idx.symbol"
          :ref="(el) => (sectionRefs[idx.symbol] = el as HTMLElement)"
          class="scroll-mt-20"
        >
          <Card>
            <CardHeader>
              <div class="flex items-center justify-between">
                <CardTitle>{{ idx.name }}</CardTitle>
                <!-- 周期选择放在图表内部 -->
                <div class="flex gap-1 rounded-md border p-1">
                  <button
                    v-for="p in PERIODS"
                    :key="p.value"
                    @click="selectPeriod(idx.symbol, p.value)"
                    :class="[
                      'rounded px-3 py-1 text-sm font-medium transition-colors',
                      indexStates.get(idx.symbol)?.period === p.value
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent',
                    ]"
                  >
                    {{ p.label }}
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div class="relative">
                <div
                  :ref="(el) => (chartRefs[idx.symbol] = el as HTMLElement)"
                  class="w-full h-[480px]"
                />
                <div
                  v-if="indexStates.get(idx.symbol)?.loading"
                  class="absolute inset-0 flex items-center justify-center text-sm text-muted-foreground bg-background/50"
                >
                  加载中…
                </div>
                <div
                  v-if="indexStates.get(idx.symbol)?.error"
                  class="absolute inset-0 flex items-center justify-center text-sm text-destructive bg-background/50"
                >
                  加载失败：{{ indexStates.get(idx.symbol)?.error }}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- 均线设置（全局共享） -->
        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <CardTitle>均线设置（最多 3 条，自动保存）</CardTitle>
              <Button
                variant="outline"
                size="sm"
                class="gap-1"
                :disabled="maConfigs.length >= 3"
                @click="addMa"
              >
                <Plus class="size-4" />
                添加均线
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div class="flex flex-col gap-3">
              <div
                v-for="ma in maConfigs"
                :key="ma.id"
                class="flex flex-wrap items-center gap-4 rounded-md border p-3"
              >
                <div class="flex items-center gap-2">
                  <input
                    type="color"
                    v-model="ma.color"
                    class="size-8 cursor-pointer rounded border bg-transparent"
                  />
                </div>
                <label class="flex items-center gap-2 text-sm">
                  <span class="text-muted-foreground">周期(天)</span>
                  <input
                    type="number"
                    min="1"
                    v-model.number="ma.days"
                    class="w-20 rounded-md border bg-transparent px-2 py-1 text-sm"
                  />
                </label>
                <label class="flex items-center gap-2 text-sm">
                  <span class="text-muted-foreground">偏移量(点)</span>
                  <input
                    type="number"
                    v-model.number="ma.offset"
                    class="w-24 rounded-md border bg-transparent px-2 py-1 text-sm"
                  />
                </label>
                <span class="text-xs text-muted-foreground">
                  {{ ma.days }}日均线{{
                    ma.offset > 0
                      ? ` 上浮 ${ma.offset} 点`
                      : ma.offset < 0
                        ? ` 下浮 ${-ma.offset} 点`
                        : ''
                  }}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  class="ml-auto gap-1 text-destructive hover:text-destructive"
                  :disabled="maConfigs.length <= 1"
                  @click="removeMa(ma.id)"
                >
                  <Trash2 class="size-4" />
                  删除
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
