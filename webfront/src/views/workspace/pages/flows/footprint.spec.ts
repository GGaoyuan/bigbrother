import { describe, expect, it } from 'vitest'
import { buildFootprint, createDemoTrades } from './footprint'

describe('订单流足迹聚合', () => {
  it('按时间和整数分价位累计手数，并排除中性成交计算 Delta', () => {
    const data = buildFootprint([
      {
        seconds: 34500,
        priceCents: 1001,
        lots: 7,
        side: 'sell',
      },
      {
        seconds: 34200,
        priceCents: 1000,
        lots: 3,
        side: 'buy',
      },
      {
        seconds: 34201,
        priceCents: 1000,
        lots: 9,
        side: 'neutral',
      },
      {
        seconds: 34203,
        priceCents: 1000,
        lots: 2,
        side: 'sell',
      },
    ])

    expect(data.periods.map((period) => period.delta)).toEqual([
      1,
      -7,
    ])
    expect(data.periods.map((period) => period.cumulativeDelta)).toEqual([
      1,
      -6,
    ])
    expect(data.periods[0]?.levels[0]).toMatchObject({
      buy: 3,
      sell: 2,
      neutral: 9,
    })
    expect(data.profile.map((level) => level.total)).toEqual([
      7,
      14,
    ])
    expect(data.poc?.priceCents).toBe(1000)
    expect(data.amountDelta).toBe(3 * 1000 - 2 * 1000 - 7 * 1001)
  })

  it('按股票代码生成可重复的模拟数据，并保留无成交的中间时段和价位', () => {
    const trades = createDemoTrades('600519')
    expect(createDemoTrades('600519')).toEqual(trades)
    expect(createDemoTrades('000001')).not.toEqual(trades)
    expect(buildFootprint(trades).periods.length).toBeGreaterThan(1)

    const data = buildFootprint([
      {
        seconds: 34200,
        priceCents: 1000,
        lots: 3,
        side: 'buy',
      },
      {
        seconds: 34800,
        priceCents: 1002,
        lots: 7,
        side: 'sell',
      },
    ])
    expect(data.periods[1]?.trades).toEqual([])
    expect(data.periods[1]?.cumulativeDelta).toBe(3)
    expect(data.profile[1]?.total).toBe(0)
    expect(buildFootprint([]).periods).toEqual([])
  })
})
