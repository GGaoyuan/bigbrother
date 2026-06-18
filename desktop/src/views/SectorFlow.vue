<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { createChart, LineSeries, type IChartApi } from 'lightweight-charts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { RefreshCw } from '@lucide/vue'
import { sectorFlowApi, type SectorFlowItem, type TrendPoint } from '@/lib/api'

// ═══ State ═══════════════════════════════════════════════════════════
const loading = ref(true)
const error = ref<string | null>(null)

const inflow = ref<SectorFlowItem[]>([])
const outflow = ref<SectorFlowItem[]>([])
const allSectors = ref<SectorFlowItem[]>([])

// 选中的板块名称（左右联动的唯一真相来源）
const selectedSectors = ref<Set<string>>(new Set())
const loadingSectors = ref<Set<string>>(new Set())

// ═══ Color Palette ═══════════════════════════════════════════════════
const COLORS = [
  '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6',
  '#06b6d4', '#f97316', '#ec4899', '#14b8a6', '#64748b',
  '#0ea5e9', '#f43f5e', '#84cc16', '#eab308', '#a855f7',
  '#fb923c', '#f472b6', '#2dd4bf', '#94a3b8', '#d946ef',
]
let colorCursor = 0
const sectorColor = new Map<string, string>()

function getColor(name: string): string {
  if (!sectorColor.has(name)) {
    sectorColor.set(name, COLORS[colorCursor % COLORS.length])
    colorCursor += 1
  }
  return sectorColor.get(name)!
}

// ═══ Chart ═══════════════════════════════════════════════════════════
const chartContainer = ref<HTMLElement | null>(null)
let chart: IChartApi | null = null
const activeSeries = new Map<string, any>() // name -> LineSeries
const trendCache = new Map<string, TrendPoint[]>() // name -> points

function initChart() {
  if (!chartContainer.value) return
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 320,
    layout: { background: { color: 'transparent' }, textColor: '#9CA3AF' },
    grid: {
      vertLines: { color: 'rgba(156, 163, 175, 0.1)' },
      horzLines: { color: 'rgba(156, 163, 175, 0.1)' },
    },
    rightPriceScale: { borderColor: 'rgba(156, 163, 175, 0.3)' },
    timeScale: { borderColor: 'rgba(156, 163, 175, 0.3)', timeVisible: false },
  })

  const resizeObserver = new ResizeObserver(() => {
    if (chart && chartContainer.value) {
      chart.applyOptions({ width: chartContainer.value.clientWidth })
    }
  })
  resizeObserver.observe(chartContainer.value)
}

// ═══ Data Loading ════════════════════════════════════════════════════
async function loadInitialData() {
  loading.value = true
  error.value = null
  try {
    const ranking = await sectorFlowApi.ranking()
    inflow.value = ranking.inflow
    outflow.value = ranking.outflow
    allSectors.value = ranking.all
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

async function handleRefresh() {
  selectedSectors.value = new Set()
  for (const series of activeSeries.values()) {
    if (chart) chart.removeSeries(series)
  }
  activeSeries.clear()
  trendCache.clear()
  await loadInitialData()
}

// ═══ Toggle Sector (左右联动核心) ════════════════════════════════════
async function toggleSector(name: string | null) {
  if (!name || !chart) return

  // 取消选中：移除曲线
  if (selectedSectors.value.has(name)) {
    const next = new Set(selectedSectors.value)
    next.delete(name)
    selectedSectors.value = next
    const series = activeSeries.get(name)
    if (series) {
      chart.removeSeries(series)
      activeSeries.delete(name)
    }
    return
  }

  // 选中：拉取数据并叠加
  const next = new Set(selectedSectors.value)
  next.add(name)
  selectedSectors.value = next

  try {
    let points = trendCache.get(name)
    if (!points) {
      const loadingNext = new Set(loadingSectors.value)
      loadingNext.add(name)
      loadingSectors.value = loadingNext

      const trend = await sectorFlowApi.trend(name)
      points = trend.points
      trendCache.set(name, points)
    }

    if (!selectedSectors.value.has(name) || !chart) return

    const series = chart.addSeries(LineSeries, {
      color: getColor(name),
      lineWidth: 2,
    })
    series.setData(points)
    activeSeries.set(name, series)
  } catch (e) {
    const rollback = new Set(selectedSectors.value)
    rollback.delete(name)
    selectedSectors.value = rollback
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    const loadingNext = new Set(loadingSectors.value)
    loadingNext.delete(name)
    loadingSectors.value = loadingNext
  }
}

function isSelected(name: string): boolean {
  return selectedSectors.value.has(name)
}

function isLoading(name: string): boolean {
  return loadingSectors.value.has(name)
}

// 亿元格式化
function fmtFlow(value: number | null): string {
  if (value === null) return '-'
  const yi = value / 1e8
  const sign = yi >= 0 ? '+' : ''
  return `${sign}${yi.toFixed(2)}亿`
}

function fmtPct(value: number | null): string {
  if (value === null) return '-'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

// ═══ Lifecycle ═══════════════════════════════════════════════════════
onMounted(async () => {
  initChart()
  await loadInitialData()
})

onUnmounted(() => {
  if (chart) {
    chart.remove()
    chart = null
  }
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Page Header -->
    <div class="flex items-start justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">板块资金流</h1>
        <p class="text-muted-foreground">
          Today's sector capital inflow / outflow ranking
        </p>
      </div>
      <Button
        variant="outline"
        size="sm"
        :disabled="loading"
        @click="handleRefresh"
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

    <!-- Main Layout: 左右两大块 -->
    <div class="grid gap-6 lg:grid-cols-3">
      <!-- 左侧：图表 + 流入/流出排行（占 2/3） -->
      <div class="flex flex-col gap-6 lg:col-span-2">
        <!-- 上部：图表 -->
        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <CardTitle>板块资金流走势</CardTitle>
              <Badge variant="secondary">{{ selectedSectors.size }} 板块已选中</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div class="relative">
              <div ref="chartContainer" class="w-full h-[320px]" />
              <div
                v-if="loading"
                class="absolute inset-0 flex items-center justify-center text-sm text-muted-foreground"
              >
                加载中…
              </div>
            </div>
            <p class="mt-2 text-xs text-muted-foreground">
              勾选任意板块，叠加显示其主力净流入历史走势（单位：元）
            </p>
          </CardContent>
        </Card>

        <!-- 下部：流入排行 + 流出排行 -->
        <div class="grid gap-6 sm:grid-cols-2">
          <!-- 流入排行 -->
          <Card>
            <CardHeader>
              <CardTitle class="text-base text-green-500">资金流入排行</CardTitle>
            </CardHeader>
            <CardContent class="p-0">
              <div class="max-h-[360px] overflow-y-auto">
                <ul class="divide-y">
                  <li
                    v-for="item in inflow"
                    :key="item.sector_name"
                    class="flex items-center gap-2 px-3 py-2 hover:bg-muted/50 transition-colors"
                  >
                    <input
                      type="checkbox"
                      :checked="isSelected(item.sector_name)"
                      :disabled="isLoading(item.sector_name)"
                      @change="toggleSector(item.sector_name)"
                      class="size-4 rounded border-input cursor-pointer accent-primary disabled:opacity-50"
                    />
                    <span
                      v-if="isSelected(item.sector_name)"
                      class="inline-block size-2 rounded-full"
                      :style="{ backgroundColor: getColor(item.sector_name) }"
                    />
                    <span class="flex-1 truncate text-sm">{{ item.sector_name }}</span>
                    <span class="text-xs font-mono text-green-500">{{ fmtFlow(item.fund_net_inflow) }}</span>
                  </li>
                  <li v-if="!inflow.length && !loading" class="px-3 py-6 text-center text-sm text-muted-foreground">
                    暂无数据
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>

          <!-- 流出排行 -->
          <Card>
            <CardHeader>
              <CardTitle class="text-base text-red-500">资金流出排行</CardTitle>
            </CardHeader>
            <CardContent class="p-0">
              <div class="max-h-[360px] overflow-y-auto">
                <ul class="divide-y">
                  <li
                    v-for="item in outflow"
                    :key="item.sector_name"
                    class="flex items-center gap-2 px-3 py-2 hover:bg-muted/50 transition-colors"
                  >
                    <input
                      type="checkbox"
                      :checked="isSelected(item.sector_name)"
                      :disabled="isLoading(item.sector_name)"
                      @change="toggleSector(item.sector_name)"
                      class="size-4 rounded border-input cursor-pointer accent-primary disabled:opacity-50"
                    />
                    <span
                      v-if="isSelected(item.sector_name)"
                      class="inline-block size-2 rounded-full"
                      :style="{ backgroundColor: getColor(item.sector_name) }"
                    />
                    <span class="flex-1 truncate text-sm">{{ item.sector_name }}</span>
                    <span class="text-xs font-mono text-red-500">{{ fmtFlow(item.fund_net_inflow) }}</span>
                  </li>
                  <li v-if="!outflow.length && !loading" class="px-3 py-6 text-center text-sm text-muted-foreground">
                    暂无数据
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <!-- 右侧：全部板块 A~Z 列表（占 1/3） -->
      <Card class="lg:col-span-1">
        <CardHeader>
          <CardTitle>全部板块 ({{ allSectors.length }})</CardTitle>
        </CardHeader>
        <CardContent class="p-0">
          <div class="max-h-[720px] overflow-y-auto">
            <ul class="divide-y">
              <li
                v-for="item in allSectors"
                :key="item.sector_name"
                class="flex items-center gap-2 px-3 py-2 hover:bg-muted/50 transition-colors"
              >
                <input
                  type="checkbox"
                  :checked="isSelected(item.sector_name)"
                  :disabled="isLoading(item.sector_name)"
                  @change="toggleSector(item.sector_name)"
                  class="size-4 rounded border-input cursor-pointer accent-primary disabled:opacity-50"
                />
                <span
                  v-if="isSelected(item.sector_name)"
                  class="inline-block size-2 rounded-full"
                  :style="{ backgroundColor: getColor(item.sector_name) }"
                />
                <span class="flex-1 truncate text-sm">{{ item.sector_name }}</span>
                <span
                  class="text-xs font-mono"
                  :class="(item.fund_net_inflow ?? 0) >= 0 ? 'text-green-500' : 'text-red-500'"
                >
                  {{ fmtPct(item.change_pct) }}
                </span>
              </li>
              <li v-if="!allSectors.length && !loading" class="px-3 py-6 text-center text-sm text-muted-foreground">
                暂无数据
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
