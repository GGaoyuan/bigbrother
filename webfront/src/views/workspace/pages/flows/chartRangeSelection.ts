import type { MarketCandle, TimeRange } from './profileMarketData'

type CandleTime = Pick<MarketCandle, 'start' | 'end'>

interface CandleIndices {
  first: number
  last: number
}

export type RangeDragPart = 'create' | 'start' | 'end' | 'selection'

const sessionDate = new Intl.DateTimeFormat('sv-SE', {
  timeZone: 'Asia/Shanghai',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
})

const sessionTime = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Asia/Shanghai',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hourCycle: 'h23',
})

export function formatSelectionEdge(timestamp: number, edge: 'start' | 'end'): string {
  const datetime = timestamp * 1000
  const time = sessionTime.format(datetime)
  if (time === '00:00:00') {
    return sessionDate.format(edge === 'end' ? datetime - 1 : datetime)
  }
  return `${sessionDate.format(datetime)} ${time.slice(0, 5)}`
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}

function firstMatchingIndex(candles: readonly CandleTime[], predicate: (candle: CandleTime) => boolean) {
  let left = 0
  let right = candles.length
  while (left < right) {
    const middle = Math.floor((left + right) / 2)
    if (predicate(candles[middle]!)) right = middle
    else left = middle + 1
  }
  return left
}

export function candleIndicesForRange(
  candles: readonly CandleTime[],
  range: TimeRange | null,
): CandleIndices | null {
  if (!range || range.start >= range.end || !candles.length) return null

  const first = firstMatchingIndex(candles, (candle) => candle.end > range.start)
  const stop = firstMatchingIndex(candles, (candle) => candle.start >= range.end)
  if (first >= stop) return null

  return {
    first,
    last: stop - 1,
  }
}

export function projectSelection(
  candles: readonly CandleTime[],
  range: TimeRange | null,
  width: number,
  logicalToX: (logical: number) => number | null,
) {
  const indices = candleIndicesForRange(candles, range)
  if (!indices || width <= 0) return null

  const firstCenter = logicalToX(indices.first)
  const nextCenter = logicalToX(indices.first + 1)
  const lastCenter = logicalToX(indices.last)
  if (firstCenter === null || nextCenter === null || lastCenter === null || nextCenter <= firstCenter) return null

  // Lightweight Charts projects integer indices. Derive the two half-bar edges from bar spacing.
  const halfBar = (nextCenter - firstCenter) / 2
  const start = firstCenter - halfBar
  const end = lastCenter + halfBar
  if (end <= 0 || start >= width) return null

  return {
    left: Math.max(start, 0),
    right: Math.min(end, width),
    startVisible: start >= 0,
    endVisible: end <= width,
  }
}

export function rangeForDrag(
  candles: readonly CandleTime[],
  part: RangeDragPart,
  anchor: number,
  cursor: number,
  original: TimeRange | null,
): TimeRange | null {
  if (!candles.length) return original

  const lastIndex = candles.length - 1
  if (part === 'create') {
    const first = clamp(Math.min(anchor, cursor), 0, lastIndex)
    const last = clamp(Math.max(anchor, cursor), 0, lastIndex)
    return {
      start: candles[first]!.start,
      end: candles[last]!.end,
    }
  }

  const indices = candleIndicesForRange(candles, original)
  if (!indices || !original) return original

  const { first, last } = indices
  const delta = cursor - anchor
  if (part === 'start') {
    const next = clamp(first + delta, 0, last)
    if (next === first) return original
    return {
      start: candles[next]!.start,
      end: original.end,
    }
  }
  if (part === 'end') {
    const next = clamp(last + delta, first, lastIndex)
    if (next === last) return original
    return {
      start: original.start,
      end: candles[next]!.end,
    }
  }

  const shift = clamp(delta, -first, lastIndex - last)
  if (shift === 0) return original
  return {
    start: candles[first + shift]!.start,
    end: candles[last + shift]!.end,
  }
}
