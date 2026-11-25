<script setup lang="ts">
import { computed, onActivated, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import {
  CandlestickSeries,
  ColorType,
  createChart,
  CrosshairMode,
  TickMarkType,
  type IChartApi,
  type IRange,
  type ISeriesApi,
  type MouseEventParams,
  type Time,
  type UTCTimestamp,
} from 'lightweight-charts'
import type { HistoryPeriod, MarketCandle, TimeRange } from './profileMarketData'
import type { ProfileLevel, VolumeProfile } from './volumeProfile'
import { candleIndicesForRange } from './chartRangeSelection'
import RangeSelectionOverlay from './RangeSelectionOverlay.vue'
import {
  CandleSelectionPrimitive,
  VolumeProfilePrimitive,
  pixelAtLogicalIndex,
  profileStripWidth,
} from './VolumeProfilePrimitive'

const props = defineProps<{
  candles: readonly MarketCandle[]
  period: HistoryPeriod
  selection: TimeRange | null
  selectionActive: boolean
  profile: VolumeProfile | null
  appliedRange: TimeRange | null
}>()

const emit = defineEmits<{
  'update:selection': [range: TimeRange]
  'cancel-selection': []
}>()

const host = ref<HTMLDivElement | null>(null)
const plot = shallowRef({
  width: 0,
  height: 0,
})
const plotRevision = ref(0)
const hoveredCandle = shallowRef<MarketCandle>()
const hoveredLevel = shallowRef<ProfileLevel>()
const readoutCandle = computed(() => hoveredCandle.value ?? props.candles[props.candles.length - 1])
const volumePrimitive = new VolumeProfilePrimitive()
const selectionPrimitive = new CandleSelectionPrimitive()
const candlesByTime = new Map<number, MarketCandle>()
let chart: IChartApi | undefined
let series: ISeriesApi<'Candlestick'> | undefined
let resizeObserver: ResizeObserver | undefined
let lastSize = {
  width: 0,
  height: 0,
}

const volumeFormat = new Intl.NumberFormat('zh-CN')
const dateFormat = new Intl.DateTimeFormat('sv-SE', {
  timeZone: 'Asia/Shanghai',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
})
const timeFormat = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Asia/Shanghai',
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
})

function dateAt(time: Time) {
  if (typeof time === 'number') return new Date(time * 1000)
  if (typeof time === 'string') return new Date(time)
  return new Date(Date.UTC(time.year, time.month - 1, time.day))
}

function crosshairTime(time: Time) {
  const date = dateAt(time)
  const day = dateFormat.format(date)
  return props.period === 'day' ? day : `${day} ${timeFormat.format(date)}`
}

function timeAxisLabel(time: Time, type: TickMarkType) {
  const date = dateAt(time)
  if (type === TickMarkType.Time || type === TickMarkType.TimeWithSeconds) {
    return timeFormat.format(date)
  }

  const day = dateFormat.format(date)
  if (type === TickMarkType.Year) return day.slice(0, 4)
  if (type === TickMarkType.Month) return day.slice(0, 7)
  return day.slice(5)
}

function formatPrice(cents: number) {
  return (cents / 100).toFixed(2)
}

function formatBandPrice(level: ProfileLevel) {
  const low = level.lowPriceCents ?? level.priceCents
  const high = level.highPriceCents ?? level.priceCents
  return low === high ? formatPrice(low) : `${formatPrice(low)} 至 ${formatPrice(high)}`
}

function observeVisibleRange(range: IRange<Time> | null) {
  if (!host.value) return
  if (!range) {
    delete host.value.dataset.visibleFrom
    delete host.value.dataset.visibleTo
    return
  }

  host.value.dataset.visibleFrom = String(range.from)
  host.value.dataset.visibleTo = String(range.to)
}

function onCrosshairMove(event: MouseEventParams<Time>) {
  const point = event.point
  hoveredLevel.value = point ? volumePrimitive.levelAt(point.x, point.y) : undefined
  hoveredCandle.value = typeof event.time === 'number' ? candlesByTime.get(event.time) : undefined
}

function updateAppliedRange() {
  selectionPrimitive.update(props.candles, props.appliedRange)
}

function refreshPlot() {
  if (!chart) return

  const { width, height } = chart.paneSize(0)
  plot.value = {
    width: Math.max(0, width - profileStripWidth(width)),
    height,
  }
  plotChanged()
}

function plotChanged() {
  plotRevision.value++
}

function toLogical(pixel: number) {
  return chart?.timeScale().coordinateToLogical(pixel) ?? null
}

function toX(logical: number) {
  const scale = chart?.timeScale()
  return scale ? pixelAtLogicalIndex(logical, (index) => scale.logicalToCoordinate(index)) : null
}

function forwardWheel(event: WheelEvent) {
  chart?.chartElement().dispatchEvent(new WheelEvent('wheel', {
    clientX: event.clientX,
    clientY: event.clientY,
    deltaX: event.deltaX,
    deltaY: event.deltaY,
    deltaMode: event.deltaMode,
    cancelable: true,
  }))
}

function updateCandles() {
  if (!chart || !series) return

  candlesByTime.clear()
  hoveredCandle.value = undefined
  hoveredLevel.value = undefined
  const candles = props.candles.map((candle) => {
    candlesByTime.set(candle.start, candle)
    return {
      time: candle.start as UTCTimestamp,
      open: candle.open / 100,
      high: candle.high / 100,
      low: candle.low / 100,
      close: candle.close / 100,
    }
  })
  series.setData(candles)
  updateAppliedRange()

  const timeScale = chart.timeScale()
  const width = timeScale.width() || Math.max(1, lastSize.width - 64)
  const reserve = profileStripWidth(width)
  timeScale.applyOptions({
    timeVisible: props.period !== 'day',
    rightOffsetPixels: reserve,
  })

  if (candles.length) {
    const focus = candleIndicesForRange(props.candles, props.selection ?? props.appliedRange)
    const focusCount = focus ? focus.last - focus.first + 11 : 0
    const minSpacing = timeScale.options().minBarSpacing
    const capacity = Math.max(1, Math.floor((width - reserve) / minSpacing))
    const count = Math.min(candles.length, capacity, Math.max(60, focusCount))
    const spacing = Math.max(minSpacing, (width - reserve) / count)
    const end = focus
      ? Math.min(candles.length - 1, Math.max(count - 1, focus.last + 5))
      : candles.length - 1
    chart.priceScale('right').setAutoScale(true)
    timeScale.setVisibleLogicalRange({
      from: end - count + 1,
      to: end + reserve / spacing,
    })
  }
  refreshPlot()
}

function resize() {
  if (!chart || !host.value) return

  const width = host.value.clientWidth
  const height = host.value.clientHeight
  if (!width || !height || (width === lastSize.width && height === lastSize.height)) return

  const timeScale = chart.timeScale()
  const visible = timeScale.getVisibleLogicalRange()
  const widthChanged = width !== lastSize.width
  lastSize = {
    width,
    height,
  }
  chart.resize(width, height, true)

  if (widthChanged) {
    timeScale.applyOptions({
      rightOffsetPixels: profileStripWidth(timeScale.width()),
    })
    if (visible) timeScale.setVisibleLogicalRange(visible)
  }
  refreshPlot()
}

watch([() => props.candles, () => props.period], updateCandles)
watch(() => props.appliedRange, updateAppliedRange)
watch(() => props.profile, (profile) => {
  hoveredLevel.value = undefined
  volumePrimitive.setProfile(profile)
})

onMounted(() => {
  if (!host.value) return

  lastSize = {
    width: host.value.clientWidth,
    height: host.value.clientHeight,
  }
  chart = createChart(host.value, {
    width: lastSize.width,
    height: lastSize.height,
    layout: {
      background: {
        type: ColorType.Solid,
        color: '#fff',
      },
      textColor: '#51637b',
      fontFamily: 'system-ui, sans-serif',
      attributionLogo: true,
    },
    grid: {
      vertLines: {
        color: '#edf2f7',
      },
      horzLines: {
        color: '#e7edf5',
      },
    },
    rightPriceScale: {
      borderColor: '#dce6f2',
      scaleMargins: {
        top: 0.14,
        bottom: 0.09,
      },
    },
    timeScale: {
      borderColor: '#dce6f2',
      fixLeftEdge: true,
      lockVisibleTimeRangeOnResize: true,
      tickMarkFormatter: timeAxisLabel,
    },
    localization: {
      locale: 'zh-CN',
      timeFormatter: crosshairTime,
    },
    crosshair: {
      mode: CrosshairMode.Normal,
      vertLine: {
        color: '#8c9fb8',
        labelBackgroundColor: '#273b58',
      },
      horzLine: {
        color: '#8c9fb8',
        labelBackgroundColor: '#273b58',
      },
    },
    handleScroll: {
      mouseWheel: false,
      pressedMouseMove: true,
      horzTouchDrag: true,
      vertTouchDrag: false,
    },
    handleScale: {
      mouseWheel: true,
      pinch: true,
      axisPressedMouseMove: {
        time: true,
        price: true,
      },
      axisDoubleClickReset: {
        time: true,
        price: true,
      },
    },
  })

  series = chart.addSeries(CandlestickSeries, {
    upColor: '#d95d52',
    downColor: '#27866d',
    borderVisible: false,
    wickUpColor: '#c94c40',
    wickDownColor: '#22745f',
    priceLineVisible: false,
    priceFormat: {
      type: 'price',
      precision: 2,
      minMove: 0.01,
    },
  })
  series.attachPrimitive(selectionPrimitive)
  series.attachPrimitive(volumePrimitive)
  chart.subscribeCrosshairMove(onCrosshairMove)
  chart.timeScale().subscribeVisibleTimeRangeChange(observeVisibleRange)
  chart.timeScale().subscribeVisibleLogicalRangeChange(plotChanged)
  chart.timeScale().subscribeSizeChange(refreshPlot)
  volumePrimitive.setProfile(props.profile)
  updateCandles()

  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(host.value)
})

onActivated(resize)
onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  chart?.unsubscribeCrosshairMove(onCrosshairMove)
  chart?.timeScale().unsubscribeVisibleTimeRangeChange(observeVisibleRange)
  chart?.timeScale().unsubscribeVisibleLogicalRangeChange(plotChanged)
  chart?.timeScale().unsubscribeSizeChange(refreshPlot)
  series?.detachPrimitive(volumePrimitive)
  series?.detachPrimitive(selectionPrimitive)
  chart?.remove()
  chart = undefined
  series = undefined
  candlesByTime.clear()
})
</script>

<template>
  <div class="profile-chart-frame">
    <div ref="host" class="profile-chart-canvas" role="img" aria-label="K 线与成交量分布"></div>

    <RangeSelectionOverlay
      v-if="plot.width && plot.height"
      :candles="candles"
      :range="selection"
      :active="selectionActive"
      :width="plot.width"
      :height="plot.height"
      :revision="plotRevision"
      :to-logical="toLogical"
      :to-x="toX"
      @update:range="emit('update:selection', $event)"
      @cancel="emit('cancel-selection')"
      @wheel-request="forwardWheel"
    />

    <div v-if="hoveredLevel" class="chart-readout" aria-label="估算价位成交量">
      <strong>{{ formatBandPrice(hoveredLevel) }}</strong>
      <span>估算 {{ volumeFormat.format(hoveredLevel.total) }} 股</span>
      <span v-if="hoveredLevel.node">{{ hoveredLevel.node }}</span>
    </div>
    <div v-else-if="readoutCandle" class="chart-readout" aria-label="当前蜡烛价位">
      <strong>{{ crosshairTime(readoutCandle.start as UTCTimestamp) }}</strong>
      <span>开 {{ formatPrice(readoutCandle.open) }}</span>
      <span>高 {{ formatPrice(readoutCandle.high) }}</span>
      <span>低 {{ formatPrice(readoutCandle.low) }}</span>
      <span>收 {{ formatPrice(readoutCandle.close) }}</span>
    </div>
  </div>
</template>

<style scoped>
.profile-chart-frame {
  position: relative;
  flex: 1;
  min-width: 0;
}

.profile-chart-canvas {
  width: 100%;
  height: clamp(335px, 55dvh, 625px);
}

.chart-readout {
  position: absolute;
  inset: 9px 75px auto 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 3px 10px;
  width: fit-content;
  max-width: calc(100% - 87px);
  padding: 3px 6px;
  border: 1px solid #e5edf6;
  border-radius: 4px;
  background: #ffffffeb;
  color: #53647b;
  font-size: 11px;
  font-variant-numeric: tabular-nums;
  pointer-events: none;
}

.chart-readout strong {
  color: #233853;
  font-weight: 650;
}
</style>
