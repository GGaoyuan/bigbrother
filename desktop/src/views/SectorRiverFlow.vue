<script setup lang="ts">
import { ref, onMounted, onUnmounted, shallowRef, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { RefreshCw } from '@lucide/vue'

// ═══ 类型 ════════════════════════════════════════════════════════════
interface SectorRow {
  name: string
  netInflow: number // 当日主力净流入（亿）
  changePct: number // 涨跌幅（%）
}

// 河流图单点：[日期, 数值, 板块名]
type RiverPoint = [string, number, string]

// ═══ 模拟数据 ════════════════════════════════════════════════════════
// 先用模拟数据，后续接后端
const SECTOR_NAMES = ['半导体', '新能源', '人工智能', '医药生物', '消费电子', '券商']

// 生成最近 N 天日期
function genDates(days: number): string[] {
  const out: string[] = []
  const today = new Date()
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(today.getDate() - i)
    out.push(`${d.getMonth() + 1}/${d.getDate()}`)
  }
  return out
}

// 生成河流图数据 + 板块列表（模拟）
function genMockData(): { river: RiverPoint[]; sectors: SectorRow[] } {
  const dates = genDates(20)
  const river: RiverPoint[] = []
  const sectors: SectorRow[] = []

  for (const name of SECTOR_NAMES) {
    // 每个板块一条随机游走的资金流曲线
    let base = 20 + Math.random() * 40
    for (const date of dates) {
      base += (Math.random() - 0.45) * 12
      base = Math.max(2, base) // themeRiver 需要非负值
      river.push([date, Math.round(base * 10) / 10, name])
    }
    // 板块列表用最后一天的值，净流入做正负随机
    const net = Math.round((Math.random() - 0.4) * 60 * 10) / 10
    sectors.push({
      name,
      netInflow: net,
      changePct: Math.round((Math.random() - 0.45) * 8 * 100) / 100,
    })
  }

  // 列表按净流入降序
  sectors.sort((a, b) => b.netInflow - a.netInflow)
  return { river, sectors }
}

// ═══ 状态 ════════════════════════════════════════════════════════════
const sectors = ref<SectorRow[]>([])
const riverData = ref<RiverPoint[]>([])

// ═══ 图表 ════════════════════════════════════════════════════════════
const chartContainer = ref<HTMLElement | null>(null)
const chart = shallowRef<echarts.ECharts | null>(null)

function buildOption(river: RiverPoint[]): echarts.EChartsOption {
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'line', lineStyle: { color: 'rgba(156,163,175,0.4)' } },
    },
    legend: {
      data: SECTOR_NAMES,
      textStyle: { color: '#9CA3AF' },
      top: 0,
    },
    singleAxis: {
      type: 'category',
      axisTick: {},
      axisLabel: { color: '#9CA3AF' },
      axisLine: { lineStyle: { color: 'rgba(156,163,175,0.3)' } },
      axisPointer: {
        animation: true,
        label: { show: true },
      },
      splitLine: {
        show: true,
        lineStyle: { type: 'dashed', opacity: 0.1, color: '#9CA3AF' },
      },
      top: '12%',
      bottom: '8%',
    },
    series: [
      {
        type: 'themeRiver',
        emphasis: { itemStyle: { shadowBlur: 20, shadowColor: 'rgba(0,0,0,0.5)' } },
        label: { show: false },
        data: river,
      },
    ],
  }
}

let resizeObserver: ResizeObserver | null = null

function initChart() {
  if (!chartContainer.value) return
  chart.value = echarts.init(chartContainer.value, undefined, { renderer: 'canvas' })
  chart.value.setOption(buildOption(riverData.value))

  // 容器尺寸变化时自适应（首帧宽度可能为 0，靠 observer 兜底重绘）
  resizeObserver = new ResizeObserver(() => chart.value?.resize())
  resizeObserver.observe(chartContainer.value)
}

function resize() {
  chart.value?.resize()
}

// ═══ 数据加载 ════════════════════════════════════════════════════════
function loadData() {
  const { river, sectors: rows } = genMockData()
  riverData.value = river
  sectors.value = rows
  chart.value?.setOption(buildOption(river))
}

function handleRefresh() {
  loadData()
}

// ═══ 格式化 ══════════════════════════════════════════════════════════
function fmtFlow(v: number): string {
  const sign = v >= 0 ? '+' : ''
  return `${sign}${v.toFixed(1)}亿`
}

function fmtPct(v: number): string {
  const sign = v >= 0 ? '+' : ''
  return `${sign}${v.toFixed(2)}%`
}

// ═══ 生命周期 ════════════════════════════════════════════════════════
onMounted(async () => {
  loadData()
  await nextTick()
  initChart()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  resizeObserver?.disconnect()
  resizeObserver = null
  chart.value?.dispose()
  chart.value = null
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- 页头 -->
    <div class="flex items-start justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">板块资金河流图</h1>
        <p class="text-muted-foreground">板块资金流随时间演化（数据模拟）</p>
      </div>
      <Button variant="outline" size="sm" class="gap-2" @click="handleRefresh">
        <RefreshCw class="size-4" />
        刷新
      </Button>
    </div>

    <!-- 上半部分：河流图 -->
    <Card>
      <CardHeader>
        <CardTitle>资金河流图</CardTitle>
      </CardHeader>
      <CardContent>
        <div ref="chartContainer" class="w-full h-[420px]" />
      </CardContent>
    </Card>

    <!-- 下半部分：板块列表 -->
    <Card>
      <CardHeader>
        <CardTitle>板块列表 ({{ sectors.length }})</CardTitle>
      </CardHeader>
      <CardContent class="p-0">
        <div class="max-h-[420px] overflow-y-auto">
          <table class="w-full text-sm">
            <thead class="sticky top-0 bg-background">
              <tr class="border-b text-left text-muted-foreground">
                <th class="px-4 py-2 font-medium">板块</th>
                <th class="px-4 py-2 font-medium text-right">主力净流入</th>
                <th class="px-4 py-2 font-medium text-right">涨跌幅</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr
                v-for="row in sectors"
                :key="row.name"
                class="hover:bg-muted/50 transition-colors"
              >
                <td class="px-4 py-2">{{ row.name }}</td>
                <td
                  class="px-4 py-2 text-right font-mono"
                  :class="row.netInflow >= 0 ? 'text-green-500' : 'text-red-500'"
                >
                  {{ fmtFlow(row.netInflow) }}
                </td>
                <td
                  class="px-4 py-2 text-right font-mono"
                  :class="row.changePct >= 0 ? 'text-green-500' : 'text-red-500'"
                >
                  {{ fmtPct(row.changePct) }}
                </td>
              </tr>
              <tr v-if="!sectors.length">
                <td colspan="3" class="px-4 py-6 text-center text-muted-foreground">
                  暂无数据
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
