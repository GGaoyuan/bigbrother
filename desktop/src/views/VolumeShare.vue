<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { createChart, AreaSeries, LineSeries, type IChartApi } from 'lightweight-charts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { RefreshCw } from '@lucide/vue'
import {
  marketCapApi,
  type IndustryNode,
  type TrendPoint,
} from '@/lib/api'

// ═══ State ═══════════════════════════════════════════════════════════
const loading = ref(true)
const error = ref<string | null>(null)

const totalName = ref('A股成交额')
const L1 = ref<IndustryNode[]>([])
const L2 = ref<IndustryNode[]>([])
const L3 = ref<IndustryNode[]>([])

const selectedCodes = ref<Set<string>>(new Set())
const loadingCodes = ref<Set<string>>(new Set())

// ═══ Color Palette ═══════════════════════════════════════════════════
const COLORS = [
  '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6',
  '#06b6d4', '#f97316', '#ec4899', '#14b8a6', '#64748b',
  '#0ea5e9', '#f43f5e', '#84cc16', '#eab308', '#a855f7',
  '#fb923c', '#f472b6', '#2dd4bf', '#94a3b8', '#d946ef',
]
let colorCursor = 0
const codeColor = new Map<string, string>()

function getColor(code: string): string {
  if (!codeColor.has(code)) {
    codeColor.set(code, COLORS[colorCursor % COLORS.length])
    colorCursor += 1
  }
  return codeColor.get(code)!
}

// ═══ Chart ═══════════════════════════════════════════════════════════
const chartContainer = ref<HTMLElement | null>(null)
let chart: IChartApi | null = null
let mainSeries: any = null
const activeSeries = new Map<string, any>() // code -> LineSeries
const volumeCache = new Map<string, TrendPoint[]>() // code -> points

function initChart() {
  if (!chartContainer.value) return
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 400,
    layout: { background: { color: 'transparent' }, textColor: '#9CA3AF' },
    grid: {
      vertLines: { color: 'rgba(156, 163, 175, 0.1)' },
      horzLines: { color: 'rgba(156, 163, 175, 0.1)' },
    },
    rightPriceScale: { borderColor: 'rgba(156, 163, 175, 0.3)' },
    timeScale: { borderColor: 'rgba(156, 163, 175, 0.3)', timeVisible: false },
  })

  mainSeries = chart.addSeries(AreaSeries, {
    topColor: 'rgba(34, 197, 94, 0.4)',
    bottomColor: 'rgba(34, 197, 94, 0.0)',
    lineColor: 'rgba(34, 197, 94, 1)',
    lineWidth: 2,
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
    const [volume, tree] = await Promise.all([
      marketCapApi.totalVolume(),
      marketCapApi.industryTree(),
    ])

    totalName.value = volume.name
    if (mainSeries) {
      mainSeries.setData(volume.points)
      chart?.timeScale().fitContent()
    }

    L1.value = tree.first
    L2.value = tree.second
    L3.value = tree.third
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

async function handleRefresh() {
  // 清空已选中的行业和缓存
  selectedCodes.value = new Set()

  // 移除所有叠加的系列
  for (const series of activeSeries.values()) {
    if (chart) {
      chart.removeSeries(series)
    }
  }
  activeSeries.clear()
  volumeCache.clear()

  // 重新加载数据
  await loadInitialData()
}

// ═══ Toggle Industry Overlay ═════════════════════════════════════════
async function toggleIndustry(code: string | null) {
  if (!code || !chart) return

  // 取消选中：移除曲线
  if (selectedCodes.value.has(code)) {
    const next = new Set(selectedCodes.value)
    next.delete(code)
    selectedCodes.value = next
    const series = activeSeries.get(code)
    if (series) {
      chart.removeSeries(series)
      activeSeries.delete(code)
    }
    return
  }

  // 选中：拉取数据（带缓存）并叠加
  const next = new Set(selectedCodes.value)
  next.add(code)
  selectedCodes.value = next

  try {
    let points = volumeCache.get(code)
    if (!points) {
      const loadingNext = new Set(loadingCodes.value)
      loadingNext.add(code)
      loadingCodes.value = loadingNext

      const volume = await marketCapApi.industryVolume(code)
      points = volume.points
      volumeCache.set(code, points)
    }

    // 拉取期间可能已被取消勾选
    if (!selectedCodes.value.has(code) || !chart) return

    const series = chart.addSeries(LineSeries, {
      color: getColor(code),
      lineWidth: 2,
    })
    series.setData(points)
    activeSeries.set(code, series)
  } catch (e) {
    // 失败则回滚勾选状态
    const rollback = new Set(selectedCodes.value)
    rollback.delete(code)
    selectedCodes.value = rollback
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    const loadingNext = new Set(loadingCodes.value)
    loadingNext.delete(code)
    loadingCodes.value = loadingNext
  }
}

function isSelected(code: string | null): boolean {
  return code ? selectedCodes.value.has(code) : false
}

function isLoading(code: string | null): boolean {
  return code ? loadingCodes.value.has(code) : false
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
        <h1 class="text-3xl font-bold tracking-tight">成交量占比</h1>
        <p class="text-muted-foreground">
          Trading volume distribution across industries
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

    <!-- Chart Card -->
    <Card>
      <CardHeader>
        <div class="flex items-center justify-between">
          <CardTitle>{{ totalName }}走势</CardTitle>
          <Badge variant="secondary">{{ selectedCodes.size }} 行业已选中</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div class="relative">
          <div ref="chartContainer" class="w-full h-[400px]" />
          <div
            v-if="loading"
            class="absolute inset-0 flex items-center justify-center text-sm text-muted-foreground"
          >
            加载中…
          </div>
        </div>
        <p class="mt-2 text-xs text-muted-foreground">
          勾选下方行业，在图表中叠加显示该行业成交额走势（与全市场同量纲，便于对比占比）
        </p>
      </CardContent>
    </Card>

    <!-- Industry Tables -->
    <div class="grid gap-6 lg:grid-cols-3">
      <Card v-for="group in [
        { title: '申万一级行业', items: L1, decimals: 0 },
        { title: '申万二级行业', items: L2, decimals: 0 },
        { title: '申万三级行业', items: L3, decimals: 0 },
      ]" :key="group.title">
        <CardHeader>
          <CardTitle>{{ group.title }} ({{ group.items.length }})</CardTitle>
        </CardHeader>
        <CardContent class="p-0">
          <div class="max-h-[500px] overflow-y-auto">
            <table class="w-full text-sm">
              <thead class="sticky top-0 bg-card border-b">
                <tr>
                  <th class="w-12 px-3 py-2 text-left font-medium">选择</th>
                  <th class="px-3 py-2 text-left font-medium">名称</th>
                  <th class="px-3 py-2 text-right font-medium">成份</th>
                </tr>
              </thead>
              <tbody class="divide-y">
                <tr
                  v-for="industry in group.items"
                  :key="industry.sw_industry_code ?? ''"
                  class="hover:bg-muted/50 transition-colors"
                >
                  <td class="px-3 py-2">
                    <input
                      type="checkbox"
                      :checked="isSelected(industry.sw_industry_code)"
                      :disabled="isLoading(industry.sw_industry_code)"
                      @change="toggleIndustry(industry.sw_industry_code)"
                      class="size-4 rounded border-input cursor-pointer accent-primary disabled:opacity-50"
                    />
                  </td>
                  <td class="px-3 py-2 text-xs">
                    <span
                      v-if="isSelected(industry.sw_industry_code)"
                      class="mr-1.5 inline-block size-2 rounded-full align-middle"
                      :style="{ backgroundColor: getColor(industry.sw_industry_code ?? '') }"
                    />
                    {{ industry.sw_industry_name }}
                    <span v-if="isLoading(industry.sw_industry_code)" class="text-muted-foreground">…</span>
                  </td>
                  <td class="px-3 py-2 text-right text-muted-foreground">
                    {{ industry.sw_component_count ?? '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
