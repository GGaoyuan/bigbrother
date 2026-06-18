<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { createChart, CandlestickSeries, type IChartApi, type CandlestickData } from 'lightweight-charts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

// 生成模拟 K线数据 - 更真实的市场行为
function generateCandlestickData(count: number): CandlestickData[] {
  const data: CandlestickData[] = []
  const basePrice = 50000
  const startTime = Date.now() - count * 3600 * 1000

  let currentPrice = basePrice
  let trendDirection = 1 // 1=上涨, -1=下跌, 0=震荡
  let trendStrength = 0.5 // 趋势强度 0-1
  let volatility = 0.01 // 当前波动率
  let trendDuration = 0 // 当前趋势持续时长

  // 关键支撑/阻力位
  const keyLevels = [
    basePrice * 0.95,
    basePrice,
    basePrice * 1.05,
    basePrice * 1.10,
  ]

  for (let i = 0; i < count; i++) {
    // 每隔一段时间切换趋势
    if (trendDuration > Math.random() * 30 + 20) {
      const rand = Math.random()
      if (rand < 0.4) {
        trendDirection = 1 // 上涨
        trendStrength = 0.3 + Math.random() * 0.5
      } else if (rand < 0.8) {
        trendDirection = -1 // 下跌
        trendStrength = 0.3 + Math.random() * 0.5
      } else {
        trendDirection = 0 // 震荡
        trendStrength = 0.2
      }
      trendDuration = 0
      volatility = 0.005 + Math.random() * 0.015 // 切换趋势时调整波动率
    }
    trendDuration++

    // 基础价格变动（带趋势）
    const trendComponent = trendDirection * trendStrength * volatility * currentPrice
    const randomComponent = (Math.random() - 0.5) * 2 * volatility * currentPrice
    const priceChange = trendComponent + randomComponent

    // 检查是否接近关键位，产生支撑/阻力效果
    let resistanceEffect = 0
    for (const level of keyLevels) {
      const distance = Math.abs(currentPrice - level)
      if (distance < currentPrice * 0.02) { // 距离关键位2%以内
        // 价格接近关键位时减速（阻力）
        const resistance = (1 - distance / (currentPrice * 0.02)) * 0.5
        if ((currentPrice < level && priceChange > 0) || (currentPrice > level && priceChange < 0)) {
          resistanceEffect -= priceChange * resistance
        }
      }
    }

    const open = currentPrice
    const close = currentPrice + priceChange + resistanceEffect

    // 影线长度：震荡时影线长，趋势时影线短
    const wickRange = Math.abs(close - open) * (1 + (1 - trendStrength) * 2)
    const highWick = Math.random() * wickRange * 0.6
    const lowWick = Math.random() * wickRange * 0.6

    const high = Math.max(open, close) + highWick
    const low = Math.min(open, close) - lowWick

    // 成交量：突破关键位或趋势转折时放量
    let volumeMultiplier = 1
    const isBreakout = keyLevels.some(level =>
      (open < level && close > level) || (open > level && close < level)
    )
    if (isBreakout) {
      volumeMultiplier = 2 + Math.random() * 2 // 突破时放量2-4倍
    } else if (trendDuration === 1) {
      volumeMultiplier = 1.5 + Math.random() // 趋势转折初期放量
    } else if (trendDirection === 0) {
      volumeMultiplier = 0.5 + Math.random() * 0.5 // 震荡时缩量
    }

    const baseVolume = 5000 + Math.random() * 3000
    const volume = baseVolume * volumeMultiplier

    data.push({
      time: Math.floor((startTime + i * 3600 * 1000) / 1000) as any,
      open,
      high,
      low,
      close,
      // 注意：lightweight-charts 的 CandlestickData 不直接支持 volume 字段
      // 但我们在 calculateVolumeProfile 里会用到，所以存在这里
      ...(volume && { customVolume: volume }), // 自定义字段
    })

    currentPrice = close

    // 避免价格跌到负数或过度偏离
    if (currentPrice < basePrice * 0.80) {
      currentPrice = basePrice * 0.80
      trendDirection = 1 // 强制反弹
    } else if (currentPrice > basePrice * 1.25) {
      currentPrice = basePrice * 1.25
      trendDirection = -1 // 强制回调
    }
  }

  return data
}

// 计算筹码峰分布
interface VolumeAtPrice {
  price: number
  volume: number
}

function calculateVolumeProfile(
  candleData: CandlestickData[],
  startIndex: number,
  endIndex: number,
  priceLevels: number = 50
): VolumeAtPrice[] {
  const sliced = candleData.slice(startIndex, endIndex + 1)
  if (sliced.length === 0) return []

  const allPrices = sliced.flatMap(c => [c.high, c.low])
  const minPrice = Math.min(...allPrices)
  const maxPrice = Math.max(...allPrices)
  const priceStep = (maxPrice - minPrice) / priceLevels

  const volumeMap: Map<number, number> = new Map()

  for (const candle of sliced) {
    // 使用生成时存的成交量，如果没有则根据实体大小估算
    const volume = (candle as any).customVolume || Math.abs(candle.close - candle.open) * 10000

    // 将这根K线的成交量分配到它覆盖的价格区间
    const startLevel = Math.floor((candle.low - minPrice) / priceStep)
    const endLevel = Math.floor((candle.high - minPrice) / priceStep)

    for (let level = startLevel; level <= endLevel; level++) {
      const levelPrice = minPrice + level * priceStep
      const currentVol = volumeMap.get(levelPrice) || 0
      volumeMap.set(levelPrice, currentVol + volume / (endLevel - startLevel + 1))
    }
  }

  return Array.from(volumeMap.entries())
    .map(([price, volume]) => ({ price, volume }))
    .sort((a, b) => b.price - a.price)
}

const chartContainer = ref<HTMLElement | null>(null)
const sliderContainer = ref<HTMLElement | null>(null)
let chart: IChartApi | null = null
let candleSeries: any = null

const candleData = ref<CandlestickData[]>(generateCandlestickData(200))
const rangeStart = ref(0)
const rangeEnd = ref(199)
const isDraggingStart = ref(false)
const isDraggingEnd = ref(false)

// 计算当前可见K线的价格范围
const priceRange = computed(() => {
  const sliced = candleData.value.slice(rangeStart.value, rangeEnd.value + 1)
  if (sliced.length === 0) return { min: 0, max: 0 }

  const allPrices = sliced.flatMap(c => [c.high, c.low])
  return {
    min: Math.min(...allPrices),
    max: Math.max(...allPrices),
  }
})

// 计算 POC 在图表中的垂直位置（百分比）
const pocPositionPercent = computed(() => {
  if (!pocPrice.value || priceRange.value.max === priceRange.value.min) return null

  const priceSpan = priceRange.value.max - priceRange.value.min
  const pocOffset = priceRange.value.max - pocPrice.value
  return (pocOffset / priceSpan) * 100
})

const volumeProfile = computed(() =>
  calculateVolumeProfile(candleData.value, rangeStart.value, rangeEnd.value)
)

const maxVolume = computed(() =>
  Math.max(...volumeProfile.value.map(v => v.volume), 1)
)

// 计算 POC 价格
const pocPrice = computed(() => {
  if (volumeProfile.value.length === 0) return null
  const maxVol = Math.max(...volumeProfile.value.map(v => v.volume))
  return volumeProfile.value.find(v => v.volume === maxVol)?.price || null
})

onMounted(() => {
  if (!chartContainer.value) return

  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 500,
    layout: {
      background: { color: 'transparent' },
      textColor: '#9CA3AF',
    },
    grid: {
      vertLines: { color: 'rgba(156, 163, 175, 0.1)' },
      horzLines: { color: 'rgba(156, 163, 175, 0.1)' },
    },
    rightPriceScale: {
      borderColor: 'rgba(156, 163, 175, 0.3)',
    },
    timeScale: {
      borderColor: 'rgba(156, 163, 175, 0.3)',
      timeVisible: true,
    },
  })

  candleSeries = chart.addSeries(CandlestickSeries, {
    upColor: '#22c55e',
    downColor: '#ef4444',
    borderUpColor: '#22c55e',
    borderDownColor: '#ef4444',
    wickUpColor: '#22c55e',
    wickDownColor: '#ef4444',
  })

  if (candleSeries) {
    candleSeries.setData(candleData.value)
  }

  // 响应式调整
  const resizeObserver = new ResizeObserver(() => {
    if (chart && chartContainer.value) {
      chart.applyOptions({ width: chartContainer.value.clientWidth })
    }
  })
  resizeObserver.observe(chartContainer.value)

  // 全局监听鼠标事件，避免拖动超出容器时失去事件
  window.addEventListener('mousemove', handleWindowMouseMove)
  window.addEventListener('mouseup', handleMouseUp)
})

// 清理
const chartDestroyed = ref(false)
function destroyChart() {
  if (chartDestroyed.value) return
  window.removeEventListener('mousemove', handleWindowMouseMove)
  window.removeEventListener('mouseup', handleMouseUp)
  if (chart) {
    chart.remove()
    chart = null
  }
  chartDestroyed.value = true
}

onUnmounted(destroyChart)

// 拖动逻辑
function handleMouseDown(type: 'start' | 'end', event: MouseEvent) {
  event.preventDefault()
  if (type === 'start') isDraggingStart.value = true
  else isDraggingEnd.value = true
}

function handleWindowMouseMove(event: MouseEvent) {
  if (!isDraggingStart.value && !isDraggingEnd.value) return
  if (!sliderContainer.value) return

  const rect = sliderContainer.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const percent = Math.max(0, Math.min(1, x / rect.width))
  const index = Math.round(percent * (candleData.value.length - 1))

  if (isDraggingStart.value) {
    rangeStart.value = Math.min(index, rangeEnd.value - 1)
  } else if (isDraggingEnd.value) {
    rangeEnd.value = Math.max(index, rangeStart.value + 1)
  }
}

function handleMouseUp() {
  isDraggingStart.value = false
  isDraggingEnd.value = false
}

// 格式化
const formatPrice = (price: number) => `$${price.toFixed(0)}`
const formatVolume = (vol: number) => vol.toFixed(0)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div>
      <h1 class="text-3xl font-bold tracking-tight">Volume Profile</h1>
      <p class="text-muted-foreground">
        Price distribution with draggable range selector
        <span class="ml-4 text-xs">(Debug: {{ candleData.length }} candles loaded)</span>
      </p>
    </div>

    <Card>
      <CardHeader>
        <div class="flex items-center justify-between">
          <CardTitle>K-Line Chart with Volume Profile</CardTitle>
          <Badge variant="secondary">
            Range: {{ rangeStart }} - {{ rangeEnd }} ({{ rangeEnd - rangeStart + 1 }} candles)
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <!-- Chart + Volume Profile Overlay -->
        <div class="relative">
          <div ref="chartContainer" class="w-full h-[500px]" />

          <!-- POC 标记线 -->
          <div
            v-if="pocPrice && pocPositionPercent !== null"
            class="absolute left-0 right-32 flex items-center pointer-events-none"
            :style="{ top: `${pocPositionPercent}%` }"
          >
            <div class="flex-1 h-0.5 bg-primary/80" />
            <div class="ml-2 px-2 py-0.5 bg-primary text-primary-foreground text-xs font-semibold rounded">
              POC {{ formatPrice(pocPrice) }}
            </div>
          </div>

          <!-- 筹码峰叠加层 (半透明横向柱状图) -->
          <div class="absolute top-0 right-0 flex flex-col justify-between h-[500px] w-32 pointer-events-none">
            <div
              v-for="item in volumeProfile"
              :key="item.price"
              class="relative flex items-center"
              :style="{ height: `${100 / volumeProfile.length}%` }"
            >
              <div
                class="absolute right-0 h-full border-r-2 transition-all"
                :class="[
                  item.price === pocPrice
                    ? 'bg-primary/40 border-primary'
                    : 'bg-primary/20 border-primary/40',
                ]"
                :style="{ width: `${(item.volume / maxVolume) * 100}%` }"
              />
            </div>
          </div>
        </div>

        <!-- 时间范围滑块 -->
        <div class="mt-6 flex flex-col gap-2">
          <div class="text-sm text-muted-foreground">Drag to select time range:</div>
          <div
            ref="sliderContainer"
            class="relative h-12 bg-muted rounded cursor-pointer select-none"
          >
            <!-- 选中区域高亮 -->
            <div
              class="absolute top-0 h-full bg-accent/50 pointer-events-none"
              :style="{
                left: `${(rangeStart / (candleData.length - 1)) * 100}%`,
                width: `${((rangeEnd - rangeStart) / (candleData.length - 1)) * 100}%`,
              }"
            />

            <!-- 左边界拖动手柄 -->
            <div
              class="absolute top-0 h-full w-1 bg-primary cursor-ew-resize hover:w-2 transition-all"
              :style="{ left: `${(rangeStart / (candleData.length - 1)) * 100}%` }"
              @mousedown="(e) => handleMouseDown('start', e)"
            />

            <!-- 右边界拖动手柄 -->
            <div
              class="absolute top-0 h-full w-1 bg-primary cursor-ew-resize hover:w-2 transition-all"
              :style="{ left: `${(rangeEnd / (candleData.length - 1)) * 100}%` }"
              @mousedown="(e) => handleMouseDown('end', e)"
            />

            <!-- 刻度文字 -->
            <div class="absolute top-1/2 left-2 -translate-y-1/2 text-xs text-muted-foreground">
              Start
            </div>
            <div class="absolute top-1/2 right-2 -translate-y-1/2 text-xs text-muted-foreground">
              End
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- 筹码峰详细数据 -->
    <Card>
      <CardHeader>
        <CardTitle>Volume Distribution (Top 10 Price Levels)</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="flex flex-col gap-2">
          <div
            v-for="item in volumeProfile.slice(0, 10)"
            :key="item.price"
            class="flex items-center gap-3 p-2 rounded bg-muted/50"
          >
            <span class="w-24 font-mono text-sm">{{ formatPrice(item.price) }}</span>
            <div class="relative flex-1 h-6 bg-muted rounded overflow-hidden">
              <div
                class="absolute left-0 top-0 h-full bg-primary/40"
                :style="{ width: `${(item.volume / maxVolume) * 100}%` }"
              />
            </div>
            <span class="w-20 text-right font-mono text-sm text-muted-foreground">
              {{ formatVolume(item.volume) }}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
