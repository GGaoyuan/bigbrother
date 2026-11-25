import type {
  AutoscaleInfo,
  IPrimitivePaneRenderer,
  IPrimitivePaneView,
  ISeriesPrimitive,
  Logical,
  SeriesAttachedParameter,
} from 'lightweight-charts'
import { candleIndicesForRange } from './chartRangeSelection'
import type { MarketCandle, TimeRange } from './profileMarketData'
import type { ProfileLevel, VolumeProfile } from './volumeProfile'

const BUY_COLOR = '#d95d52'
const SELL_COLOR = '#27866d'
const NEUTRAL_COLOR = '#768aa6'
const POC_COLOR = '#b77920'
const HVN_COLOR = '#346bc4'
const LVN_COLOR = '#845bb7'

type RenderTarget = Parameters<IPrimitivePaneRenderer['draw']>[0]

type PriceProjection = (price: number) => number | null
type BandBounds = Pick<ProfileLevel, 'lowPriceCents' | 'highPriceCents'>

interface ReferenceLine {
  price: number
  label: string
  color: string
  dash: number[]
}

export function profileStripWidth(paneWidth: number) {
  return Math.floor(Math.min(paneWidth * 0.4, Math.max(80, Math.min(210, paneWidth * 0.26))))
}

export function projectPriceBand(priceCents: number, project: PriceProjection, bounds?: BandBounds) {
  const center = project(priceCents / 100)
  const upper = project(((bounds?.highPriceCents ?? priceCents) + 0.5) / 100)
  const lower = project(((bounds?.lowPriceCents ?? priceCents) - 0.5) / 100)
  if (center === null || upper === null || lower === null) return null

  return {
    center,
    top: Math.min(upper, lower),
    bottom: Math.max(upper, lower),
  }
}

export function pixelAtLogicalIndex(logical: number, coordinateAt: (index: Logical) => number | null) {
  const index = Math.floor(logical)
  const left = coordinateAt(index as Logical)
  if (left === null || index === logical) return left

  const right = coordinateAt((index + 1) as Logical)
  return right === null ? null : left + (right - left) * (logical - index)
}

function profileReferences(profile: VolumeProfile) {
  const lines = new Map<number, ReferenceLine>()
  const area = profile.valueArea
  const poc = profile.poc

  if (area) {
    lines.set(area.high, {
      price: area.high,
      label: 'VAH',
      color: '#587db7',
      dash: [
        6,
        4,
      ],
    })
    lines.set(area.low, {
      price: area.low,
      label: area.low === area.high ? 'VAH / VAL' : 'VAL',
      color: '#7286a3',
      dash: [
        2,
        4,
      ],
    })
  }
  if (poc) {
    const previous = lines.get(poc.priceCents)
    lines.set(poc.priceCents, {
      price: poc.priceCents,
      label: previous ? `POC / ${previous.label}` : 'POC',
      color: POC_COLOR,
      dash: [],
    })
  }

  return [...lines.values()]
}

function drawSegments(
  context: CanvasRenderingContext2D,
  level: ProfileLevel,
  widthPerLot: number,
  right: number,
  top: number,
  height: number,
  hasDirection: boolean,
) {
  if (!hasDirection) {
    context.fillStyle = NEUTRAL_COLOR
    context.fillRect(right - level.total * widthPerLot, top, level.total * widthPerLot, height)
    return
  }

  context.fillStyle = BUY_COLOR
  let edge = right - level.buy * widthPerLot
  context.fillRect(edge, top, level.buy * widthPerLot, height)
  context.fillStyle = SELL_COLOR
  edge -= level.sell * widthPerLot
  context.fillRect(edge, top, level.sell * widthPerLot, height)
  context.fillStyle = NEUTRAL_COLOR
  const unsidedWidth = (level.neutral + level.unknown) * widthPerLot
  context.fillRect(edge - unsidedWidth, top, unsidedWidth, height)
}

function drawReference(
  context: CanvasRenderingContext2D,
  line: ReferenceLine,
  y: number,
  width: number,
  stripLeft: number,
) {
  context.strokeStyle = line.color
  context.setLineDash(line.dash)
  context.beginPath()
  context.moveTo(0, y)
  context.lineTo(width, y)
  context.stroke()
  context.font = '600 10px ui-monospace, monospace'
  context.textBaseline = 'middle'
  const label = `${line.label} ${(line.price / 100).toFixed(2)}`
  const textWidth = context.measureText(label).width
  const right = width - 4
  context.fillStyle = '#fff'
  context.fillRect(Math.max(stripLeft, right - textWidth - 8), y - 14, textWidth + 8, 13)
  context.fillStyle = line.color
  context.textAlign = 'right'
  context.fillText(label, right - 4, y - 7, Math.max(0, right - stripLeft - 6))
}

export class VolumeProfilePrimitive implements ISeriesPrimitive {
  private attachment?: SeriesAttachedParameter
  private profile: VolumeProfile | null = null
  private maxVolume = 1
  private references: ReferenceLine[] = []
  private autoScaleRange: AutoscaleInfo | null = null
  private readonly paneRenderer: IPrimitivePaneRenderer = {
    draw: (target) => this.draw(target),
  }
  private readonly views: readonly IPrimitivePaneView[] = [
    {
      zOrder: () => 'normal',
      renderer: () => this.paneRenderer,
    },
  ]

  attached(attachment: SeriesAttachedParameter) {
    this.attachment = attachment
  }

  detached() {
    this.attachment = undefined
  }

  paneViews() {
    return this.views
  }

  autoscaleInfo() {
    return this.autoScaleRange
  }

  setProfile(profile: VolumeProfile | null) {
    this.profile = profile
    this.maxVolume = 1
    this.references = profile ? profileReferences(profile) : []
    let lowest = Infinity
    let highest = -Infinity
    for (const level of profile?.levels ?? []) {
      if (level.total > this.maxVolume) this.maxVolume = level.total
      lowest = Math.min(lowest, level.lowPriceCents ?? level.priceCents)
      highest = Math.max(highest, level.highPriceCents ?? level.priceCents)
    }
    this.autoScaleRange = lowest <= highest
      ? {
          priceRange: {
            minValue: (lowest - 0.5) / 100,
            maxValue: (highest + 0.5) / 100,
          },
        }
      : null
    this.attachment?.requestUpdate()
  }

  levelAt(x: number, y: number) {
    if (!this.attachment || !this.profile) return undefined
    const { chart, series } = this.attachment
    const paneWidth = chart.timeScale().width()
    if (x < paneWidth - profileStripWidth(paneWidth) || x >= paneWidth) return undefined

    const price = series.coordinateToPrice(y)
    if (price === null) return undefined

    const priceCents = Math.round(price * 100)
    return this.profile.levels.find((level) =>
      priceCents >= (level.lowPriceCents ?? level.priceCents)
      && priceCents <= (level.highPriceCents ?? level.priceCents),
    )
  }

  private draw(target: RenderTarget) {
    const profile = this.profile
    const series = this.attachment?.series
    if (!series) return

    target.useMediaCoordinateSpace(({ context, mediaSize }) => {
      const { width, height } = mediaSize
      const stripWidth = profileStripWidth(width)
      const stripLeft = width - stripWidth

      context.save()
      context.fillStyle = profile?.levels.length ? '#f0f5fa' : '#f7f9fc'
      context.fillRect(stripLeft, 0, stripWidth, height)
      context.fillStyle = '#d5e0ed'
      context.fillRect(stripLeft, 0, 1, height)
      if (!profile?.levels.length) {
        context.restore()
        return
      }

      const barRight = width - 8
      const widthPerLot = Math.max(0, stripWidth - 22) / this.maxVolume
      const viewportHigh = series.coordinateToPrice(0)
      const viewportLow = series.coordinateToPrice(height)
      if (viewportHigh === null || viewportLow === null) {
        context.restore()
        return
      }

      const lowVisible = Math.min(viewportLow, viewportHigh) * 100 - 1
      const highVisible = Math.max(viewportLow, viewportHigh) * 100 + 1
      const project: PriceProjection = (price) => series.priceToCoordinate(price)
      const area = profile.valueArea
      const pocPrice = profile.poc?.priceCents
      let lastNodeY = -Infinity

      for (const level of profile.levels) {
        const low = level.lowPriceCents ?? level.priceCents
        const high = level.highPriceCents ?? level.priceCents
        if (!level.total || high < lowVisible || low > highVisible) continue
        const band = projectPriceBand(level.priceCents, project, level)
        if (!band) continue

        const gutter = band.bottom - band.top >= 3 ? 0.5 : 0
        const top = band.top + gutter
        const barHeight = band.bottom - band.top - gutter * 2
        context.globalAlpha = !area || (level.priceCents >= area.low && level.priceCents <= area.high)
          ? 0.84
          : 0.43
        drawSegments(context, level, widthPerLot, barRight, top, barHeight, profile.hasDirection)
        context.globalAlpha = 1

        if (level.priceCents === pocPrice) {
          const levelWidth = level.total * widthPerLot
          context.strokeStyle = POC_COLOR
          context.strokeRect(barRight - levelWidth, top, levelWidth, barHeight)
        } else if (level.node && Math.abs(band.center - lastNodeY) >= 5) {
          context.fillStyle = level.node === 'HVN' ? HVN_COLOR : LVN_COLOR
          context.beginPath()
          context.arc(stripLeft + 5, band.center, 2, 0, Math.PI * 2)
          context.fill()
          lastNodeY = band.center
        }
      }

      for (const line of this.references) {
        const y = series.priceToCoordinate(line.price / 100)
        if (y !== null && y >= 0 && y <= height) drawReference(context, line, y, width, stripLeft)
      }
      context.restore()
    })
  }
}

export class CandleSelectionPrimitive implements ISeriesPrimitive {
  private attachment?: SeriesAttachedParameter
  private applied: ReturnType<typeof candleIndicesForRange> = null
  private readonly paneRenderer: IPrimitivePaneRenderer = {
    draw: (target) => this.draw(target),
  }
  private readonly views: readonly IPrimitivePaneView[] = [
    {
      zOrder: () => 'bottom',
      renderer: () => this.applied ? this.paneRenderer : null,
    },
  ]

  attached(attachment: SeriesAttachedParameter) {
    this.attachment = attachment
  }

  detached() {
    this.attachment = undefined
  }

  paneViews() {
    return this.views
  }

  update(candles: readonly MarketCandle[], applied: TimeRange | null) {
    this.applied = candleIndicesForRange(candles, applied)
    this.attachment?.requestUpdate()
  }

  private draw(target: RenderTarget) {
    const timeScale = this.attachment?.chart.timeScale()
    if (!timeScale || !this.applied) return
    const coordinateAt = (index: Logical) => timeScale.logicalToCoordinate(index)
    const start = pixelAtLogicalIndex(this.applied.first - 0.5, coordinateAt)
    const end = pixelAtLogicalIndex(this.applied.last + 0.5, coordinateAt)
    if (start === null || end === null) return

    target.useMediaCoordinateSpace(({ context, mediaSize }) => {
      const left = Math.max(0, start)
      const right = Math.min(mediaSize.width, end)
      if (left >= right) return

      context.save()
      context.fillStyle = '#c1a47519'
      context.fillRect(left, 0, right - left, mediaSize.height)
      context.restore()
    })
  }
}
