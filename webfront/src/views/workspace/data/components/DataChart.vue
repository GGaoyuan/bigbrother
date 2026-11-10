<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { mockChartSeries, type ChartSeries } from './mockChartSeries'

interface AxisScale {
  min: number
  max: number
  interval: number
}

const AXIS_PITCH = 58

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

function monthTickDates(dates: string[]): string[] {
  const ticks: string[] = []
  let lastMonth = ''

  for (const date of dates) {
    const month = date.slice(0, 7)
    if (month !== lastMonth) {
      ticks.push(date)
      lastMonth = month
    }
  }

  return ticks
}

function niceStep(span: number): number {
  const rough = span / 4
  const exponent = Math.floor(Math.log10(rough))
  const fraction = rough / 10 ** exponent
  const nice = fraction <= 1 ? 1 : fraction <= 2 ? 2 : fraction <= 5 ? 5 : 10
  return nice * 10 ** exponent
}

function niceAxis(values: number[]): AxisScale {
  const rawMin = Math.min(...values)
  const rawMax = Math.max(...values)
  const span = rawMax - rawMin || Math.abs(rawMax) * 0.2 || 1
  const interval = niceStep(span)
  const min = Math.floor(rawMin / interval) * interval
  const max = Math.ceil(rawMax / interval) * interval

  return {
    min,
    max: max === min ? min + interval : max,
    interval,
  }
}

function formatAxisTick(value: number, interval: number): string {
  if (interval >= 1) {
    return String(Math.round(value))
  }

  return value.toFixed(interval >= 0.1 ? 1 : 2)
}

function axisLayout(selected: Record<string, boolean>) {
  const leftIndexes: number[] = []
  const rightIndexes: number[] = []

  mockChartSeries.forEach((spec, index) => {
    if (selected[spec.id] === false) {
      return
    }

    if (spec.side === 'left') {
      leftIndexes.push(index)
    } else {
      rightIndexes.push(index)
    }
  })

  const offsets = mockChartSeries.map(() => 0)
  leftIndexes.forEach((index, order) => {
    offsets[index] = order * AXIS_PITCH
  })
  rightIndexes.forEach((index, order) => {
    offsets[index] = order * AXIS_PITCH
  })

  return {
    offsets,
    left: 16 + leftIndexes.length * AXIS_PITCH,
    right: 16 + rightIndexes.length * AXIS_PITCH,
  }
}

function buildYAxes(samples: number[][], selected: Record<string, boolean>) {
  const layout = axisLayout(selected)

  return {
    layout,
    yAxis: mockChartSeries.map((spec, index) => {
      const visible = selected[spec.id] !== false
      const scale = niceAxis(samples[index] ?? [])

      return {
        show: visible,
        type: 'value' as const,
        min: scale.min,
        max: scale.max,
        interval: scale.interval,
        position: spec.side,
        offset: layout.offsets[index] ?? 0,
        axisLine: {
          show: visible,
          lineStyle: {
            color: spec.color,
            width: 1,
          },
        },
        axisTick: {
          show: false,
        },
        splitLine: {
          show: false,
        },
        axisPointer: {
          show: visible,
          type: 'line' as const,
          lineStyle: {
            color: spec.color,
            type: 'dashed' as const,
            width: 1,
          },
          label: {
            show: visible,
            backgroundColor: spec.color,
          },
        },
        axisLabel: {
          show: visible,
          color: spec.color,
          fontSize: 12,
          margin: 8,
          formatter: (value: number) => formatAxisTick(value, scale.interval),
        },
      }
    }),
  }
}

const seriesById = new Map(mockChartSeries.map((item) => [item.id, item]))

function displayName(id: string): string {
  return seriesById.get(id)?.name ?? id
}

function seriesValues(series: ChartSeries): number[] {
  return series.points.map((point) => point.value)
}

function seriesDates(): string[] {
  return mockChartSeries[0]?.points.map((point) => point.date) ?? []
}

function formatNumber(value: number, digits: number): string {
  return digits === 0 ? Math.round(value).toLocaleString('zh-CN') : value.toFixed(digits)
}

function formatMonthLabel(date: string): string {
  const [year, monthText] = date.split('-')
  if (!year || !monthText) {
    return ''
  }

  return `${year}/${Number(monthText)}/1`
}

function formatTooltipDate(date: string): string {
  const [year, monthText, dayText] = date.split('-')
  if (!year || !monthText || !dayText) {
    return date
  }

  return `${year}/${Number(monthText)}/${Number(dayText)}`
}

function readTooltipValue(value: unknown): number {
  if (typeof value === 'number') {
    return value
  }

  if (Array.isArray(value)) {
    const last = value[value.length - 1]
    return typeof last === 'number' ? last : Number(last)
  }

  return Number(value)
}

function createChartOption(
  dates: string[],
  selected: Record<string, boolean>,
): echarts.EChartsOption {
  const samples = mockChartSeries.map((item) => seriesValues(item))
  const { layout, yAxis } = buildYAxes(samples, selected)

  return {
    color: mockChartSeries.map((item) => item.color),
    animation: false,
    animationDuration: 0,
    animationDurationUpdate: 0,
    textStyle: {
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    },
    legend: {
      top: 6,
      left: 8,
      icon: 'circle',
      itemWidth: 8,
      itemHeight: 8,
      itemGap: 18,
      textStyle: {
        color: '#5c6778',
        fontSize: 13,
      },
      formatter: (name: string) => displayName(name),
    },
    tooltip: {
      trigger: 'axis',
      confine: true,
      axisPointer: {
        type: 'cross',
        lineStyle: {
          color: '#b7c0cb',
          type: 'dashed',
          width: 1,
        },
        crossStyle: {
          color: '#b7c0cb',
          type: 'dashed',
          width: 1,
        },
      },
      backgroundColor: '#ffffff',
      borderColor: '#e6ebf2',
      borderWidth: 1,
      padding: [10, 12],
      textStyle: {
        color: '#334155',
        fontSize: 12,
      },
      extraCssText: 'box-shadow: 0 8px 24px rgba(30, 41, 59, 0.08); border-radius: 8px;',
      formatter: (params) => {
        const rows = Array.isArray(params) ? params : [params]
        const first = rows[0]
        const axisValue = first && 'axisValue' in first ? String(first.axisValue ?? '') : ''
        const lines = rows.map((item) => {
          const rawName = String(item.seriesName ?? '')
          const spec = seriesById.get(rawName)
          const numeric = readTooltipValue('value' in item ? item.value : undefined)
          const text = Number.isFinite(numeric) ? formatNumber(numeric, spec?.digits ?? 0) : '--'
          return `${item.marker ?? ''}${displayName(rawName)}　${text}`
        })

        return [formatTooltipDate(axisValue), ...lines].join('<br/>')
      },
    },
    grid: {
      left: layout.left,
      right: layout.right,
      top: 46,
      bottom: 62,
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100,
        zoomOnMouseWheel: true,
        moveOnMouseMove: true,
      },
      {
        type: 'slider',
        start: 0,
        end: 100,
        height: 14,
        bottom: 10,
        left: layout.left,
        right: layout.right,
        borderColor: 'transparent',
        backgroundColor: '#e7eef6',
        fillerColor: 'rgba(190, 208, 226, 0.55)',
        dataBackground: {
          lineStyle: {
            color: 'transparent',
          },
          areaStyle: {
            color: 'transparent',
          },
        },
        selectedDataBackground: {
          lineStyle: {
            color: 'transparent',
          },
          areaStyle: {
            color: 'transparent',
          },
        },
        handleSize: 12,
        handleStyle: {
          color: '#d7e2ee',
          borderColor: '#c5d3e2',
        },
        moveHandleSize: 0,
        showDetail: false,
        brushSelect: false,
      },
    ],
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: {
        show: false,
      },
      axisTick: {
        show: false,
      },
      axisLabel: {
        color: '#a0a8b3',
        fontSize: 12,
        margin: 14,
        hideOverlap: true,
        customValues: monthTickDates(dates),
        formatter: (value: string) => formatMonthLabel(value),
      },
      axisPointer: {
        show: true,
        type: 'line',
        lineStyle: {
          color: '#b7c0cb',
          type: 'dashed',
          width: 1,
        },
        label: {
          show: true,
          backgroundColor: '#8b95a3',
        },
      },
    },
    yAxis,
    series: mockChartSeries.map((item, index) => ({
      name: item.id,
      type: 'line' as const,
      yAxisIndex: index,
      data: samples[index],
      showSymbol: false,
      symbol: 'none',
      smooth: false,
      animation: false,
      animationDuration: 0,
      animationDurationUpdate: 0,
      sampling: 'lttb' as const,
      lineStyle: {
        color: item.color,
        width: 1.6,
      },
      itemStyle: {
        color: item.color,
      },
      emphasis: {
        focus: 'series' as const,
        lineStyle: {
          width: 2.2,
        },
      },
    })),
  }
}

function syncAxes(selected: Record<string, boolean>) {
  if (!chart || seriesDates().length === 0) {
    return
  }

  const samples = mockChartSeries.map((item) => seriesValues(item))
  const { layout, yAxis } = buildYAxes(samples, selected)
  chart.setOption({
    grid: {
      left: layout.left,
      right: layout.right,
    },
    yAxis,
    dataZoom: [
      {},
      {
        left: layout.left,
        right: layout.right,
      },
    ],
  })
}

function renderChart() {
  const element = chartRef.value
  if (!element) {
    return
  }

  chart ??= echarts.init(element)
  const dates = seriesDates()
  const selected = Object.fromEntries(mockChartSeries.map((item) => [item.id, true]))
  chart.setOption(createChartOption(dates, selected), true)
  chart.off('legendselectchanged')
  chart.on('legendselectchanged', (event) => {
    const nextSelected = (event as { selected?: Record<string, boolean> }).selected
    if (nextSelected) {
      syncAxes(nextSelected)
    }
  })
  chart.resize()
}

onMounted(() => {
  renderChart()

  if (chartRef.value) {
    resizeObserver = new ResizeObserver(() => {
      chart?.resize()
    })
    resizeObserver.observe(chartRef.value)
  }
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  resizeObserver = null
  chart?.dispose()
  chart = null
})
</script>

<template>
  <section class="chart-card" aria-label="当前面板图表">
    <div ref="chartRef" class="chart-canvas"></div>
  </section>
</template>

<style scoped>
.chart-card {
  display: flex;
  min-height: 560px;
  flex: 1;
  flex-direction: column;
  padding: 8px 10px 6px;
  border: 1px solid #dfe6ef;
  border-radius: 11px;
  background: #fff;
}

.chart-canvas {
  width: 100%;
  min-height: 520px;
  flex: 1;
}

@media (max-width: 760px) {
  .chart-card {
    min-height: 440px;
    padding: 6px;
  }

  .chart-canvas {
    min-height: 400px;
  }
}
</style>
