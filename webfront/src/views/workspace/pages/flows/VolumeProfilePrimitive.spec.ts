import { describe, expect, it } from 'vitest'
import type { SeriesAttachedParameter } from 'lightweight-charts'
import { candleIndicesForRange } from './chartRangeSelection'
import {
  pixelAtLogicalIndex,
  profileStripWidth,
  projectPriceBand,
  VolumeProfilePrimitive,
} from './VolumeProfilePrimitive'

describe('成交量分布图的价格坐标', () => {
  it('柱中心和标线取自同一价格投影，并随价格缩放和平移更新', () => {
    const priceCents = 1146
    const firstScale = (price: number) => 200 - 100 * (price - 11.00)
    const zoomedScale = (price: number) => 120 - 250 * (price - 11.00)

    const before = projectPriceBand(priceCents, firstScale)!
    const after = projectPriceBand(priceCents, zoomedScale)!
    expect(before.center).toBe(firstScale(11.46))
    expect(after.center).toBe(zoomedScale(11.46))
    expect((before.top + before.bottom) / 2).toBeCloseTo(before.center)
    expect((after.top + after.bottom) / 2).toBeCloseTo(after.center)
    expect(after.bottom - after.top).toBeCloseTo(2.5)
  })

  it('价格轴尚不可用时跳过绘制，窄屏给 K 线保留主要空间', () => {
    expect(projectPriceBand(1000, () => null)).toBeNull()
    expect(profileStripWidth(270)).toBeLessThanOrEqual(270 * 0.4)
    expect(profileStripWidth(1500)).toBeLessThanOrEqual(220)
  })

  it('投影包含整个估算价格档，保留原有一分宽价格档的投影', () => {
    const project = (price: number) => 160 - (price - 10) * 100

    expect(projectPriceBand(1150, project, {
      lowPriceCents: 1145,
      highPriceCents: 1154,
    })).toEqual({
      center: project(11.5),
      top: project(11.545),
      bottom: project(11.445),
    })
  })

  it('自动价格缩放包含曾经的统计价位，并在清除分布后复原', () => {
    const primitive = new VolumeProfilePrimitive()
    primitive.setProfile({
      levels: [
        {
          priceCents: 1246,
          lowPriceCents: 1242,
          highPriceCents: 1250,
          total: 80,
          buy: 80,
          sell: 0,
          neutral: 0,
          unknown: 0,
          delta: 80,
          node: null,
        },
        {
          priceCents: 1146,
          total: 60,
          buy: 0,
          sell: 60,
          neutral: 0,
          unknown: 0,
          delta: -60,
          node: null,
        },
      ],
      total: 140,
      hasDirection: true,
    })
    expect(primitive.autoscaleInfo()?.priceRange).toEqual({
      minValue: 11.455,
      maxValue: 12.505,
    })

    primitive.setProfile(null)
    expect(primitive.autoscaleInfo()).toBeNull()
    expect(primitive.paneViews()[0]!.renderer()).not.toBeNull()
  })

  it('根据整个价格档识别指针，分界线只有一个价格档，空档保持为空', () => {
    const primitive = new VolumeProfilePrimitive()
    const first = {
      priceCents: 1025,
      lowPriceCents: 1020,
      highPriceCents: 1029,
      total: 80,
      buy: 0,
      sell: 0,
      neutral: 0,
      unknown: 80,
      delta: null,
      node: null,
    }
    const second = {
      ...first,
      priceCents: 1035,
      lowPriceCents: 1030,
      highPriceCents: 1039,
    }
    primitive.attached({
      chart: {
        timeScale: () => ({
          width: () => 800,
        }),
      },
      series: {
        coordinateToPrice: (y: number) => y / 100,
      },
      requestUpdate: () => {},
    } as unknown as SeriesAttachedParameter)
    primitive.setProfile({
      levels: [
        first,
        second,
      ],
      total: 160,
      hasDirection: false,
    })

    expect(primitive.levelAt(700, 1029)).toBe(first)
    expect(primitive.levelAt(700, 1030)).toBe(second)
    expect(primitive.levelAt(700, 1040)).toBeUndefined()
    expect(primitive.levelAt(100, 1029)).toBeUndefined()
  })
})

describe('历史选区到 K 线的映射', () => {
  const candles = [
    {
      start: 100,
      end: 150,
    },
    {
      start: 150,
      end: 200,
    },
    {
      start: 300,
      end: 350,
    },
  ]

  it('以半开时间区间映射跨时间空档的蜡烛，并保留部分重合的蜡烛', () => {
    expect(candleIndicesForRange(candles, {
      start: 149,
      end: 300,
    })).toEqual({
      first: 0,
      last: 1,
    })
    expect(candleIndicesForRange(candles, {
      start: 150,
      end: 350,
    })).toEqual({
      first: 1,
      last: 2,
    })
  })

  it('空档和没有数据的区间不涂色', () => {
    expect(candleIndicesForRange(candles, {
      start: 200,
      end: 300,
    })).toBeNull()
    expect(candleIndicesForRange([], {
      start: 100,
      end: 200,
    })).toBeNull()
    expect(candleIndicesForRange(candles, {
      start: 150,
      end: 150,
    })).toBeNull()
  })

  it('半根 K 线边界由相邻原生逻辑坐标插值，随平移与缩放变化', () => {
    const initial = (index: number) => Number.isInteger(index) ? 200 + index * 12 : null
    const zoomed = (index: number) => Number.isInteger(index) ? 230 + index * 26 : null

    expect(pixelAtLogicalIndex(2.5, initial)).toBe(230)
    expect(pixelAtLogicalIndex(2.5, zoomed)).toBe(295)
    expect(pixelAtLogicalIndex(-0.5, initial)).toBe(194)
    expect(pixelAtLogicalIndex(2.5, () => null)).toBeNull()
  })
})
