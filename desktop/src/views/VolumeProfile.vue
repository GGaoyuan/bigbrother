<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import {
  createChart,
  CandlestickSeries,
  type IChartApi,
  type CandlestickData,
} from 'lightweight-charts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { RefreshCw } from '@lucide/vue'
import {
  volumeProfileApi,
  type VolumeKlineBar,
} from '@/lib/api'

// ═══ 周期 ════════════════════════════════════════════════════════════
type Period = '1m' | '5m' | '30m' | 'day'
const PERIODS: { value: Period; label: string }[] = [
  { value: '1m', label: '1分钟' },
  { value: '5m', label: '5分钟' },
  { value: '30m', label: '30分钟' },
  { value: 'day', label: '日线' },
]
const period = ref<Period>('day')

// ═══ 标的 ════════════════════════════════════════════════════════════
const symbol = ref('600519')
const symbolInput = ref('600519')

// 默认右侧基准向前的 K 线数量
const DEFAULT_WINDOW = 20

// ═══ 状态 ════════════════════════════════════════════════════════════
const loading = ref(false)
const error = ref<string | null>(null)
const bars = ref<VolumeKlineBar[]>([])

// 选区索引（含两端），默认最后 DEFAULT_WINDOW 根
const rangeStart = ref(0)
const rangeEnd = ref(0)

// ═══ 图表 ════════════════════════════════════════════════════════════
const chartContainer = ref<HTMLElement | null>(null)
let chart: IChartApi | null = null
let candleSeries: any = null
let resizeObserver: ResizeObserver | null = null

function toCandles(src: VolumeKlineBar[]): CandlestickData[] {
  // 分钟线用 unix 秒时间戳，日线用日期字符串
  return src
    .filter((b) => b.datetime && b.close !== null)
    .map((b) => {
      const dt = b.datetime as string
      const time =
        period.value === 'day'
          ? (dt.slice(0, 10) as any)
          : (Math.floor(new Date(dt.replace(' ', 'T')).getTime() / 1000) as any)
      return {
        time,
        open: b.open ?? 0,
        high: b.high ?? 0,
        low: b.low ?? 0,
        close: b.close ?? 0,
      }
    })
}

// ═══ 成交量分布计算 ══════════════════════════════════════════════════
interface VolumeAtPrice {
  price: number
  volume: number
}

const PRICE_LEVELS = 40

const volumeProfile = computed<VolumeAtPrice[]>(() => {
  const sliced = bars.value.slice(rangeStart.value, rangeEnd.value + 1)
  if (sliced.length === 0) return []

  let minPrice = Infinity
  let maxPrice = -Infinity
  for (const b of sliced) {
    if (b.low !== null) minPrice = Math.min(minPrice, b.low)
    if (b.high !== null) maxPrice = Math.max(maxPrice, b.high)
  }
  if (!isFinite(minPrice) || !isFinite(maxPrice) || maxPrice <= minPrice) {
    return []
  }

  const step = (maxPrice - minPrice) / PRICE_LEVELS
  const buckets = new Array(PRICE_LEVELS).fill(0)

  for (const b of sliced) {
    const vol = b.volume ?? 0
    if (vol <= 0 || b.low === null || b.high === null) continue
    const lo = Math.floor((b.low - minPrice) / step)
    const hi = Math.floor((b.high - minPrice) / step)
    const start = Math.max(0, Math.min(PRICE_LEVELS - 1, lo))
    const end = Math.max(0, Math.min(PRICE_LEVELS - 1, hi))
    const span = end - start + 1
    const per = vol / span
    for (let i = start; i <= end; i++) buckets[i] += per
  }

  const out: VolumeAtPrice[] = []
  for (let i = PRICE_LEVELS - 1; i >= 0; i--) {
    out.push({ price: minPrice + (i + 0.5) * step, volume: buckets[i] })
  }
  return out
})

const maxVolume = computed(() =>
  Math.max(...volumeProfile.value.map((v) => v.volume), 1),
)

const pocPrice = computed(() => {
  if (volumeProfile.value.length === 0) return null
  let best = volumeProfile.value[0]
  for (const v of volumeProfile.value) if (v.volume > best.volume) best = v
  return best.price
})

const rangeLabel = computed(() => {
  const s = bars.value[rangeStart.value]?.datetime ?? ''
  const e = bars.value[rangeEnd.value]?.datetime ?? ''
  return `${s} ~ ${e}`
})

// ═══ 数据加载 ════════════════════════════════════════════════════════
async function loadData() {
  loading.value = true
  error.value = null
  try {
    const res = await volumeProfileApi.kline(symbol.value, period.value, 300)
    bars.value = res.bars
    if (candleSeries) {
      chart?.applyOptions({ timeScale: { timeVisible: period.value !== 'day' } })
      candleSeries.setData(toCandles(res.bars))
      chart?.timeScale().fitContent()
    }
    // 默认：右侧在最新 K 线，向前 DEFAULT_WINDOW 根
    const n = res.bars.length
    rangeEnd.value = Math.max(0, n - 1)
    rangeStart.value = Math.max(0, n - DEFAULT_WINDOW)

    // 同步图表可视范围到选区
    syncChartVisibleRange()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

function selectPeriod(p: Period) {
  if (period.value === p) return
  period.value = p
  loadData()
}

function applySymbol() {
  const v = symbolInput.value.trim()
  if (!v || v === symbol.value) return
  symbol.value = v
  loadData()
}

// ═══ 拖动滑块（按 K 线粒度） ═════════════════════════════════════════
const sliderContainer = ref<HTMLElement | null>(null)
const dragging = ref<'start' | 'end' | null>(null)

function indexFromEvent(event: MouseEvent): number {
  if (!sliderContainer.value || bars.value.length === 0) return 0
  const rect = sliderContainer.value.getBoundingClientRect()
  const pct = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width))
  return Math.round(pct * (bars.value.length - 1))
}

function syncChartVisibleRange() {
  if (!chart || bars.value.length === 0) return

  // 获取选区对应的时间范围
  const startBar = bars.value[rangeStart.value]
  const endBar = bars.value[rangeEnd.value]

  if (!startBar?.datetime || !endBar?.datetime) return

  // 转换为图表时间格式
  const toChartTime = (dt: string) => {
    if (period.value === 'day') {
      return dt.slice(0, 10)
    } else {
      return Math.floor(new Date(dt.replace(' ', 'T')).getTime() / 1000)
    }
  }

  const fromTime = toChartTime(startBar.datetime)
  const toTime = toChartTime(endBar.datetime)

  // 设置图表可视范围
  chart.timeScale().setVisibleRange({ from: fromTime as any, to: toTime as any })
}

function onHandleDown(type: 'start' | 'end', event: MouseEvent) {
  event.preventDefault()
  dragging.value = type
}

function onWindowMove(event: MouseEvent) {
  if (!dragging.value) return
  const idx = indexFromEvent(event)
  if (dragging.value === 'start') {
    rangeStart.value = Math.min(idx, rangeEnd.value - 1)
  } else {
    rangeEnd.value = Math.max(idx, rangeStart.value + 1)
  }
  // 实时同步图表可视范围
  syncChartVisibleRange()
}

function onWindowUp() {
  dragging.value = null
}

// ═══ 图表初始化 ══════════════════════════════════════════════════════
function initChart() {
  if (!chartContainer.value) return
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 500,
    layout: { background: { color: 'transparent' }, textColor: '#9CA3AF' },
    grid: {
      vertLines: { color: 'rgba(156, 163, 175, 0.1)' },
      horzLines: { color: 'rgba(156, 163, 175, 0.1)' },
    },
    rightPriceScale: { borderColor: 'rgba(156, 163, 175, 0.3)' },
    timeScale: {
      borderColor: 'rgba(156, 163, 175, 0.3)',
      timeVisible: period.value !== 'day',
    },
  })

  candleSeries = chart.addSeries(CandlestickSeries, {
    upColor: '#ef4444',
    downColor: '#22c55e',
    borderUpColor: '#ef4444',
    borderDownColor: '#22c55e',
    wickUpColor: '#ef4444',
    wickDownColor: '#22c55e',
  })

  resizeObserver = new ResizeObserver(() => {
    if (chart && chartContainer.value) {
      chart.applyOptions({ width: chartContainer.value.clientWidth })
    }
  })
  resizeObserver.observe(chartContainer.value)
}

onMounted(async () => {
  initChart()
  window.addEventListener('mousemove', onWindowMove)
  window.addEventListener('mouseup', onWindowUp)
  await loadData()
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onWindowMove)
  window.removeEventListener('mouseup', onWindowUp)
  resizeObserver?.disconnect()
  if (chart) {
    chart.remove()
    chart = null
  }
})

const fmtPrice = (p: number) => p.toFixed(2)
const fmtVol = (v: number) => {
  if (v >= 1e8) return (v / 1e8).toFixed(2) + '亿'
  if (v >= 1e4) return (v / 1e4).toFixed(2) + '万'
  return v.toFixed(0)
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Page Header -->
    <div class="flex items-start justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">成交量分布图</h1>
        <p class="text-muted-foreground">
          K 线右侧叠加成交量分布，底部拖动栏按 K 线粒度调整统计区间
        </p>
      </div>
      <Button
        variant="outline"
        size="sm"
        :disabled="loading"
        @click="loadData"
        class="gap-2"
      >
        <RefreshCw :class="['size-4', loading && 'animate-spin']" />
        刷新
      </Button>
    </div>

    <!-- Error banner -->
    <div
      v-if="error"
      class="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-2 text-sm text-destructive"
    >
      加载失败：{{ error }}
    </div>

    <!-- 标的 + 周期 -->
    <div class="flex flex-wrap items-center gap-4">
      <div class="flex items-center gap-2">
        <span class="text-sm text-muted-foreground">代码</span>
        <input
          v-model="symbolInput"
          @keyup.enter="applySymbol"
          placeholder="6 位代码，如 600519"
          class="w-40 rounded-md border bg-transparent px-2 py-1 text-sm"
        />
        <Button variant="outline" size="sm" @click="applySymbol">确定</Button>
      </div>

      <div class="flex items-center gap-2">
        <span class="text-sm text-muted-foreground">周期</span>
        <div class="flex gap-1 rounded-md border p-1">
          <button
            v-for="p in PERIODS"
            :key="p.value"
            @click="selectPeriod(p.value)"
            :class="[
              'rounded px-3 py-1 text-sm font-medium transition-colors',
              period === p.value
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-accent',
            ]"
          >
            {{ p.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- K线图 + 成交量分布 -->
    <Card>
      <CardHeader>
        <div class="flex items-center justify-between">
          <CardTitle>{{ symbol }} K 线 + 成交量分布</CardTitle>
          <Badge variant="secondary">
            {{ rangeEnd - rangeStart + 1 }} 根 K线 · {{ rangeLabel }}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <!-- K线（左） + 成交量分布（右） -->
        <div class="flex gap-3">
          <div class="relative flex-1">
            <div ref="chartContainer" class="w-full h-[500px]" />
            <div
              v-if="loading"
              class="absolute inset-0 flex items-center justify-center text-sm text-muted-foreground"
            >
              加载中…
            </div>
          </div>

          <!-- 成交量分布（横向柱状，价格从上到下递减） -->
          <div class="w-44 shrink-0">
            <div class="mb-2 text-xs text-muted-foreground">
              成交量分布<span v-if="pocPrice"> · POC {{ fmtPrice(pocPrice) }}</span>
            </div>
            <div class="flex h-[500px] flex-col">
              <div
                v-for="item in volumeProfile"
                :key="item.price"
                class="relative flex flex-1 items-center gap-1"
              >
                <div class="relative h-full flex-1 overflow-hidden rounded-sm bg-muted/30" :title="`量 ${fmtVol(item.volume)}`">
                  <div
                    class="absolute left-0 top-0 h-full"
                    :class="
                      item.price === pocPrice ? 'bg-primary/70' : 'bg-primary/30'
                    "
                    :style="{ width: `${(item.volume / maxVolume) * 100}%` }"
                  />
                </div>
                <span class="w-12 text-right font-mono text-[10px] text-muted-foreground">
                  {{ fmtPrice(item.price) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部拖动栏（按 K 线粒度） -->
        <div class="mt-6 flex flex-col gap-2">
          <div class="text-sm text-muted-foreground">
            拖动调整成交量分布的时间范围（粒度：每根 K 线）
          </div>
          <div
            ref="sliderContainer"
            class="relative h-12 select-none rounded bg-muted"
          >
            <!-- 选中区域 -->
            <div
              class="pointer-events-none absolute top-0 h-full bg-accent/60"
              :style="{
                left: `${(rangeStart / Math.max(1, bars.length - 1)) * 100}%`,
                width: `${((rangeEnd - rangeStart) / Math.max(1, bars.length - 1)) * 100}%`,
              }"
            />
            <!-- 左手柄 -->
            <div
              class="absolute top-0 h-full w-1.5 cursor-ew-resize bg-primary hover:w-2"
              :style="{ left: `${(rangeStart / Math.max(1, bars.length - 1)) * 100}%` }"
              @mousedown="(e) => onHandleDown('start', e)"
            />
            <!-- 右手柄 -->
            <div
              class="absolute top-0 h-full w-1.5 cursor-ew-resize bg-primary hover:w-2"
              :style="{ left: `${(rangeEnd / Math.max(1, bars.length - 1)) * 100}%` }"
              @mousedown="(e) => onHandleDown('end', e)"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

