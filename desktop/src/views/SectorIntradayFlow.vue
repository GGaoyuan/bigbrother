<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { createChart, LineSeries, type IChartApi, type UTCTimestamp } from 'lightweight-charts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { RefreshCw, AlertCircle } from '@lucide/vue'
import {
  sectorIntradayApi,
  type SectorIntradaySnapshot,
} from '@/lib/api'

// ═══ 类型 ═════════════════════════════════════════════════════════════
interface ChartTrend {
  name: string
  netInflow: number
  points: Array<{ time: UTCTimestamp; value: number }>
}

// ═══ State ═════════════════════════════════════════════════════════════
const loading = ref(true)
const error = ref<string | null>(null)
const lastUpdated = ref<string>('')

const ranking = ref<SectorIntradaySnapshot[]>([])
const inflowTrends = ref<ChartTrend[]>([])
const outflowTrends = ref<ChartTrend[]>([])

const allTrends = computed(() => [...inflowTrends.value, ...outflowTrends.value])

// ═══ 时间转换：HH:MM → UTCTimestamp ═════════════════════════════════════
function parseTime(hhMM: string): UTCTimestamp {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const [h, m] = hhMM.split(':').map(Number)
  return Math.floor(today.getTime() / 1000 + h * 3600 + m * 60) as UTCTimestamp
}

// ═══ 颜色映射：净流入越大越红，越流出越绿 ═════════════════════════════
function colorFor(netInflow: number, maxAbs: number): string {
  const intensity = Math.min(1, Math.abs(netInflow) / Math.max(1, maxAbs))
  if (netInflow >= 0) {
    const h = 0 + (1 - intensity) * 30
    const l = 45 + (1 - intensity) * 15
    return `hsl(${h}, 78%, ${l}%)`
  }
  const h = 110 + (1 - intensity) * 30
  const l = 38 + (1 - intensity) * 18
  return `hsl(${h}, 65%, ${l}%)`
}

const maxAbs = computed(() =>
  ranking.value.reduce((m, t) => Math.max(m, Math.abs(t.net_inflow)), 1),
)

// ═══ Chart ═══════════════════════════════════════════════════════════
const chartContainer = ref<HTMLElement | null>(null)
let chart: IChartApi | null = null
let resizeObserver: ResizeObserver | null = null

function initChart() {
  if (!chartContainer.value) return
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 520,
    layout: { background: { color: 'transparent' }, textColor: '#9CA3AF' },
    grid: {
      vertLines: { color: 'rgba(156, 163, 175, 0.08)' },
      horzLines: { color: 'rgba(156, 163, 175, 0.12)' },
    },
    rightPriceScale: { borderColor: 'rgba(156, 163, 175, 0.3)' },
    timeScale: {
      borderColor: 'rgba(156, 163, 175, 0.3)',
      timeVisible: true,
      secondsVisible: false,
    },
    crosshair: { mode: 1 },
  })
  resizeObserver = new ResizeObserver(() => {
    if (chart && chartContainer.value) {
      chart.applyOptions({ width: chartContainer.value.clientWidth })
    }
  })
  resizeObserver.observe(chartContainer.value)
}

function renderSeries() {
  if (!chart) return
  const ma = maxAbs.value
  for (const t of allTrends.value) {
    const series = chart.addSeries(LineSeries, {
      color: colorFor(t.netInflow, ma),
      lineWidth: 2,
      priceFormat: { type: 'custom', formatter: (v: number) => `${v.toFixed(2)}亿` },
      lastValueVisible: false,
      priceLineVisible: false,
    })
    series.setData(t.points)
  }
  chart.timeScale().fitContent()
}

// ═══ Data Loading ════════════════════════════════════════════════════
async function reload() {
  loading.value = true
  error.value = null
  if (chart) {
    chart.remove()
    chart = null
  }

  try {
    const data = await sectorIntradayApi.ranking(12, 12)
    ranking.value = data.ranking
    inflowTrends.value = data.inflow_trends.map((t) => ({
      name: t.name,
      netInflow: t.points.length ? t.points[t.points.length - 1].net_inflow : 0,
      points: t.points.map((p) => ({ time: parseTime(p.time), value: p.net_inflow })),
    }))
    outflowTrends.value = data.outflow_trends.map((t) => ({
      name: t.name,
      netInflow: t.points.length ? t.points[t.points.length - 1].net_inflow : 0,
      points: t.points.map((p) => ({ time: parseTime(p.time), value: p.net_inflow })),
    }))

    await new Promise((r) => requestAnimationFrame(() => r(null)))
    initChart()
    renderSeries()
    lastUpdated.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  reload()
})

onUnmounted(() => {
  resizeObserver?.disconnect()
  if (chart) chart.remove()
})

function fmtNet(v: number): string {
  return `${v >= 0 ? '+' : ''}${v.toFixed(2)}亿`
}
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-4">
    <!-- 顶部标题栏 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">板块日内资金流向</h1>
        <p class="text-sm text-muted-foreground">
          概念板块逐分钟主力净流入，左图展示 top 12 流入 + top 12 流出
          <Badge v-if="!error" variant="outline" class="ml-2">efinance 实时</Badge>
        </p>
      </div>
      <div class="flex items-center gap-3">
        <span v-if="lastUpdated" class="text-xs text-muted-foreground">
          更新于 {{ lastUpdated }}
        </span>
        <Button variant="outline" size="sm" :disabled="loading" @click="reload">
          <RefreshCw class="size-4" :class="{ 'animate-spin': loading }" />
          刷新
        </Button>
      </div>
    </div>

    <!-- 错误提示 -->
    <div
      v-if="error"
      class="flex items-center gap-2 rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive"
    >
      <AlertCircle class="size-4 shrink-0" />
      <span>{{ error }}</span>
    </div>

    <!-- 主内容：左图 + 右榜 -->
    <div class="grid flex-1 grid-cols-[1fr_320px] gap-4 overflow-hidden">
      <!-- 左侧 K 线图 -->
      <Card class="flex flex-col overflow-hidden">
        <CardHeader class="py-3">
          <CardTitle class="text-base">日内分时走势（亿元）</CardTitle>
        </CardHeader>
        <CardContent class="flex-1 p-3">
          <div ref="chartContainer" class="h-full w-full" />
        </CardContent>
      </Card>

      <!-- 右侧排行榜 -->
      <Card class="flex flex-col overflow-hidden">
        <CardHeader class="py-3">
          <CardTitle class="text-base">板块资金流向</CardTitle>
          <p class="text-xs text-muted-foreground">单位：亿元 · 按最新净流入排序</p>
        </CardHeader>
        <CardContent class="flex-1 overflow-y-auto p-0">
          <ul class="divide-y">
            <li
              v-for="item in ranking"
              :key="item.code"
              class="flex items-center justify-between gap-3 px-4 py-2 transition-colors hover:bg-accent/40"
            >
              <div class="flex min-w-0 items-center gap-2">
                <span
                  class="size-2.5 shrink-0 rounded-full"
                  :style="{ backgroundColor: colorFor(item.net_inflow, maxAbs) }"
                />
                <span class="truncate text-sm">{{ item.name }}</span>
              </div>
              <span
                class="text-sm font-medium tabular-nums"
                :class="item.net_inflow >= 0 ? 'text-red-500' : 'text-green-500'"
              >
                {{ fmtNet(item.net_inflow) }}
              </span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
