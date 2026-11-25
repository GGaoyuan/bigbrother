type Side = 'buy' | 'sell' | 'neutral'

export interface Trade {
  seconds: number
  priceCents: number
  lots: number
  side: Side
}

export interface PriceLevel {
  priceCents: number
  buy: number
  sell: number
  neutral: number
  total: number
}

interface FootprintPeriod {
  start: number
  levels: PriceLevel[]
  trades: Trade[]
  delta: number
  cumulativeDelta: number
}

export const PERIOD_SECONDS = 5 * 60

const DEMO_CENTERS = [
  43,
  34,
  26,
  20,
  15,
  10,
  17,
  22,
  26,
  32,
  34,
  29,
  30,
  28,
]

export function createDemoTrades(code: string): Trade[] {
  let state = Number(code)
  const basePrice = 1000 + state % 7900
  const sessionStart = 9 * 3600 + 30 * 60

  function random() {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0
    return state / 2 ** 32
  }

  return DEMO_CENTERS.flatMap((center, period) => {
    const previous = DEMO_CENTERS[period - 1] ?? center + 6
    const advancing = center > previous
    const radius = 5 + Math.floor(random() * (period < 6 ? 7 : 4))
    const entries: Omit<Trade, 'seconds'>[] = []
    for (let distance = -radius; distance <= radius; distance++) {
      const priceCents = basePrice + center + (advancing ? distance : -distance)
      const weight = 1 - 0.65 * Math.abs(distance) / radius
      entries.push({
        priceCents,
        lots: Math.round(weight * (25 + random() * (advancing ? 440 : 260))),
        side: 'buy',
      })
      if (random() > 0.08) {
        entries.push({
          priceCents,
          lots: Math.round(weight * (20 + random() * (advancing ? 290 : 480))),
          side: 'sell',
        })
      }
      if (random() > 0.94) {
        entries.push({
          priceCents,
          lots: 5 + Math.floor(random() * 40),
          side: 'neutral',
        })
      }
    }

    // Include both price extremes within the period so candle bodies and wicks are distinct.
    const shift = advancing ? 1 : -1
    const openPrice = basePrice + center - (radius - 2) * shift
    const closePrice = basePrice + center + (radius - 2) * shift
    const open = entries.findIndex((entry) => entry.priceCents === openPrice)
    const close = entries.findIndex((entry) => entry.priceCents === closePrice)
    const ordered = [
      entries[open]!,
      ...entries.filter((_, index) => index !== open && index !== close),
      entries[close]!,
    ]
    const start = sessionStart + period * PERIOD_SECONDS
    return ordered.map((entry, index) => ({
      ...entry,
      seconds: start + Math.floor(index * PERIOD_SECONDS / entries.length),
    }))
  })
}

function emptyLevel(priceCents: number): PriceLevel {
  return {
    priceCents,
    buy: 0,
    sell: 0,
    neutral: 0,
    total: 0,
  }
}

function addTrade(levels: Map<number, PriceLevel>, trade: Trade) {
  const level = levels.get(trade.priceCents) ?? emptyLevel(trade.priceCents)
  level[trade.side] += trade.lots
  level.total += trade.lots
  levels.set(trade.priceCents, level)
}

function priceLadder(levels: Map<number, PriceLevel>): PriceLevel[] {
  if (!levels.size) return []
  const prices = [...levels.keys()]
  const top = Math.max(...prices)
  const bottom = Math.min(...prices)
  return Array.from({ length: top - bottom + 1 }, (_, offset) => {
    const price = top - offset
    return levels.get(price) ?? emptyLevel(price)
  })
}

function periodStart(seconds: number) {
  return Math.floor(seconds / PERIOD_SECONDS) * PERIOD_SECONDS
}

export function buildFootprint(trades: readonly Trade[]) {
  const sortedTrades = [...trades].sort((a, b) => a.seconds - b.seconds)
  const byPeriod = new Map<number, Trade[]>()
  const allLevels = new Map<number, PriceLevel>()
  let amountDelta = 0

  for (const trade of sortedTrades) {
    const start = periodStart(trade.seconds)
    const bucket = byPeriod.get(start) ?? []
    bucket.push(trade)
    byPeriod.set(start, bucket)
    addTrade(allLevels, trade)
    // A-share lots contain 100 shares, so cents × lots gives CNY.
    if (trade.side === 'buy') amountDelta += trade.priceCents * trade.lots
    if (trade.side === 'sell') amountDelta -= trade.priceCents * trade.lots
  }

  const periods: FootprintPeriod[] = []
  const first = sortedTrades[0]
  const lastTrade = sortedTrades[sortedTrades.length - 1]
  let cumulativeDelta = 0

  if (first && lastTrade) {
    const lastStart = periodStart(lastTrade.seconds)
    for (let start = periodStart(first.seconds); start <= lastStart; start += PERIOD_SECONDS) {
      const bucket = byPeriod.get(start) ?? []
      const byPrice = new Map<number, PriceLevel>()
      for (const trade of bucket) addTrade(byPrice, trade)

      const levels = priceLadder(byPrice)
      const delta = levels.reduce((sum, level) => sum + level.buy - level.sell, 0)
      cumulativeDelta += delta
      periods.push({
        start,
        levels,
        trades: bucket,
        delta,
        cumulativeDelta,
      })
    }
  }

  const profile = priceLadder(allLevels)
  let poc: PriceLevel | undefined
  for (const level of profile) {
    if (!poc || level.total > poc.total) poc = level
  }

  return {
    periods,
    profile,
    poc,
    lastTrade,
    amountDelta,
    cumulativeDelta,
  }
}

export type Footprint = ReturnType<typeof buildFootprint>

export function formatTime(seconds: number, showSeconds = false) {
  const hour = String(Math.floor(seconds / 3600)).padStart(2, '0')
  const minute = String(Math.floor(seconds / 60) % 60).padStart(2, '0')
  const second = String(seconds % 60).padStart(2, '0')
  return showSeconds ? `${hour}:${minute}:${second}` : `${hour}:${minute}`
}

export function formatPrice(cents: number) {
  return (cents / 100).toFixed(2)
}
