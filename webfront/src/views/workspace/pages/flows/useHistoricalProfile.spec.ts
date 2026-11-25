import { describe, expect, it, vi } from 'vitest'
import { ApiRequestError } from '@/api/request'
import type {
  MarketHistory,
  MarketInstrument,
  MarketProfileResult,
  ProfileMarketData,
} from './profileMarketData'
import { useHistoricalProfile } from './useHistoricalProfile'

const instrument: MarketInstrument = {
  symbol: '600519',
  name: '贵州茅台',
  exchange: 'SSE',
  market: 'CN',
  currency: 'CNY',
  price_tick: 0.01,
  source: 'tencent',
}

const history: MarketHistory = {
  symbol: instrument.symbol,
  source: 'tencent',
  adjust: 'qfq',
  adjustment_version: 'qfq-v1',
  bars: [
    {
      start: 10,
      end: 20,
      open: 1234,
      high: 1234,
      low: 1234,
      close: 1234,
      volume: 50,
    },
  ],
}

const firstRange = {
  start: 10,
  end: 20,
}
const secondRange = {
  start: 30,
  end: 40,
}

function profileResponse(symbol: string, start: number, end: number, total = 50): MarketProfileResult {
  return {
    symbol,
    source: 'mootdx',
    start,
    end,
    actual_start: Math.floor(start / 60) * 60,
    actual_end: Math.ceil(end / 60) * 60,
    complete: true,
    calculation_method: 'estimated_1m_weighted_range',
    adjustment_version: 'qfq-v1',
    price_step: 0.01,
    profile: {
      levels: [
        {
          priceCents: 1234,
          total,
          buy: 0,
          sell: 0,
          neutral: 0,
          unknown: total,
          delta: null,
          node: null,
        },
      ],
      total,
      hasDirection: false,
    },
  }
}

function testMarket() {
  return {
    getInstrument: vi.fn<ProfileMarketData['getInstrument']>(async (symbol) => ({
      ...instrument,
      symbol,
    })),
    getHistory: vi.fn<ProfileMarketData['getHistory']>(async (symbol) => ({
      ...history,
      symbol,
    })),
    calculateProfile: vi.fn<ProfileMarketData['calculateProfile']>(async (symbol, range) =>
      profileResponse(symbol, range.start, range.end, range.start === 10 ? 50 : 400),
    ),
  }
}

function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => {
    resolve = done
  })
  return {
    promise,
    resolve,
  }
}

describe('真实行情查询和固定区间确认', () => {
  it('初始空白，仅在提交后分两步加载股票信息和行情', async () => {
    const market = testMarket()
    const view = useHistoricalProfile(market)
    expect(view.instrument.value).toBeNull()
    expect(view.history.value).toBeNull()
    expect(view.selection.value).toBeNull()
    expect(market.getInstrument).not.toHaveBeenCalled()
    expect(market.getHistory).not.toHaveBeenCalled()

    const info = deferred<MarketInstrument>()
    const chart = deferred<MarketHistory>()
    market.getInstrument.mockReturnValueOnce(info.promise)
    market.getHistory.mockReturnValueOnce(chart.promise)
    const query = view.selectSymbol(instrument.symbol)
    expect(view.instrumentLoading.value).toBe(true)
    expect(view.historyLoading.value).toBe(false)
    expect(market.getHistory).not.toHaveBeenCalled()

    info.resolve(instrument)
    await Promise.resolve()
    expect(view.instrument.value?.name).toBe('贵州茅台')
    expect(view.instrumentLoading.value).toBe(false)
    expect(view.historyLoading.value).toBe(true)
    expect(view.history.value).toBeNull()
    expect(market.getHistory).toHaveBeenCalledWith(instrument.symbol, 'day', expect.any(AbortSignal))

    chart.resolve(history)
    await query
    expect(view.history.value).toBe(history)
    expect(view.historyLoading.value).toBe(false)
    expect(market.calculateProfile).not.toHaveBeenCalled()
  })

  it('选区和周期变化保留上次结果，只在确认时请求服务端分布', async () => {
    const market = testMarket()
    const view = useHistoricalProfile(market)
    await view.selectSymbol(instrument.symbol)
    view.selection.value = firstRange
    expect(market.calculateProfile).not.toHaveBeenCalled()

    await view.confirm()
    expect(view.applied.value?.profile.total).toBe(50)
    expect(view.applied.value?.source).toBe('mootdx')
    expect(view.applied.value?.range).toEqual(firstRange)
    expect(view.applied.value?.actualRange).toEqual({
      start: 0,
      end: 60,
    })
    expect(view.pending.value).toBe(false)
    view.selection.value = secondRange
    await view.selectPeriod('5m')
    expect(view.selection.value).toEqual(secondRange)
    expect(view.pending.value).toBe(true)
    expect(view.applied.value?.profile.total).toBe(50)
    expect(market.calculateProfile).toHaveBeenCalledTimes(1)
    expect(market.getInstrument).toHaveBeenCalledTimes(1)

    await view.confirm()
    expect(view.applied.value?.profile.total).toBe(400)
    expect(view.pending.value).toBe(false)
    view.clear()
    expect(view.applied.value).toBeNull()
    expect(view.selection.value).toEqual(secondRange)
  })

  it('覆盖不足或服务器结果不完整时保留草稿和上一次成功结果', async () => {
    const market = testMarket()
    const view = useHistoricalProfile(market)
    await view.selectSymbol(instrument.symbol)
    view.selection.value = firstRange
    await view.confirm()
    const last = view.applied.value

    view.selection.value = secondRange
    market.calculateProfile.mockRejectedValueOnce(new ApiRequestError('所选区间 1 分钟 K 线不可用', 409))
    await view.confirm()
    expect(view.applied.value).toBe(last)
    expect(view.selection.value).toEqual(secondRange)
    expect(view.pending.value).toBe(true)
    expect(view.profileIssue.value).toEqual({
      kind: 'coverage',
      message: '所选区间 1 分钟 K 线不可用',
    })

    market.calculateProfile.mockResolvedValueOnce({
      ...profileResponse(instrument.symbol, secondRange.start, secondRange.end),
      complete: false,
    })
    await view.confirm()
    expect(view.applied.value).toBe(last)
    expect(view.profileIssue.value?.kind).toBe('error')
    expect(view.profileIssue.value?.message).toMatch(/覆盖|完整/)

    market.calculateProfile.mockResolvedValueOnce({
      ...profileResponse(instrument.symbol, secondRange.start, secondRange.end),
      calculation_method: 'ticks',
    })
    await view.confirm()
    expect(view.applied.value).toBe(last)
    expect(view.profileIssue.value?.kind).toBe('error')
    expect(view.profileIssue.value?.message).toMatch(/1 分钟 K 线|估算/)
  })

  it('拒绝不同版本的估算，并在前复权 K 线换版时移除旧分布', async () => {
    const market = testMarket()
    const view = useHistoricalProfile(market)
    await view.selectSymbol(instrument.symbol)
    view.selection.value = firstRange
    await view.confirm()
    const prior = view.applied.value

    view.selection.value = secondRange
    market.calculateProfile.mockResolvedValueOnce({
      ...profileResponse(instrument.symbol, secondRange.start, secondRange.end),
      adjustment_version: 'qfq-v2',
    })
    await view.confirm()
    expect(view.applied.value).toBe(prior)
    expect(view.profileIssue.value?.message).toMatch(/复权版本/)

    market.getHistory.mockResolvedValueOnce({
      ...history,
      adjustment_version: 'qfq-v2',
    })
    await view.refreshHistory()
    expect(view.applied.value).toBeNull()
    expect(view.history.value?.adjustment_version).toBe('qfq-v2')
    expect(view.selection.value).toEqual(secondRange)

    market.calculateProfile.mockResolvedValueOnce({
      ...profileResponse(instrument.symbol, secondRange.start, secondRange.end),
      adjustment_version: 'qfq-v2',
    })
    await view.confirm()
    expect(view.applied.value?.range).toEqual(secondRange)
  })

  it('刷新图表复权版本后，未完成的旧版本估算无法恢复已清除的分布', async () => {
    const market = testMarket()
    const view = useHistoricalProfile(market)
    await view.selectSymbol(instrument.symbol)
    view.selection.value = firstRange
    await view.confirm()

    const late = deferred<MarketProfileResult>()
    market.calculateProfile.mockReturnValueOnce(late.promise)
    const calculation = view.confirm()
    const signal = market.calculateProfile.mock.lastCall?.[2]
    market.getHistory.mockResolvedValueOnce({
      ...history,
      adjustment_version: 'qfq-v2',
    })
    await view.selectPeriod('5m')
    late.resolve(profileResponse(instrument.symbol, firstRange.start, firstRange.end))
    await calculation

    expect(signal?.aborted).toBe(true)
    expect(view.applied.value).toBeNull()
    expect(view.selection.value).toEqual(firstRange)
  })

  it('取消选区中止正在进行的重算，已确认结果仍可查看', async () => {
    const market = testMarket()
    const view = useHistoricalProfile(market)
    await view.selectSymbol(instrument.symbol)
    view.selection.value = firstRange
    await view.confirm()
    const original = view.applied.value

    const late = deferred<MarketProfileResult>()
    market.calculateProfile.mockReturnValueOnce(late.promise)
    view.selection.value = secondRange
    const calculation = view.confirm()
    const signal = market.calculateProfile.mock.lastCall?.[2]
    view.cancelSelection()
    late.resolve(profileResponse(instrument.symbol, secondRange.start, secondRange.end))
    await calculation

    expect(signal?.aborted).toBe(true)
    expect(view.profileLoading.value).toBe(false)
    expect(view.selection.value).toBeNull()
    expect(view.applied.value).toBe(original)
  })

  it('提交新股票立即清空旧结果，丢弃先发但后到的股票信息与分布', async () => {
    const market = testMarket()
    const view = useHistoricalProfile(market)
    await view.selectSymbol(instrument.symbol)
    view.selection.value = firstRange
    await view.confirm()
    const lateProfile = deferred<MarketProfileResult>()
    market.calculateProfile.mockReturnValueOnce(lateProfile.promise)
    const calculation = view.confirm()

    const lateInfo = deferred<MarketInstrument>()
    market.getInstrument.mockReturnValueOnce(lateInfo.promise)
    const oldQuery = view.selectSymbol('600000')
    expect(view.instrument.value).toBeNull()
    expect(view.history.value).toBeNull()
    expect(view.selection.value).toBeNull()
    expect(view.applied.value).toBeNull()
    expect(view.profileLoading.value).toBe(false)

    await view.selectSymbol('000001')
    lateInfo.resolve({
      ...instrument,
      symbol: '600000',
    })
    lateProfile.resolve(profileResponse(instrument.symbol, firstRange.start, firstRange.end))
    await Promise.all([
      oldQuery,
      calculation,
    ])
    expect(market.getHistory).toHaveBeenCalledTimes(2)
    expect(view.instrument.value?.symbol).toBe('000001')
    expect(view.history.value?.symbol).toBe('000001')
    expect(view.applied.value).toBeNull()
  })

  it('切换周期后丢弃晚到的旧 K 线，并保留最后一次成功结果处理失败', async () => {
    const market = testMarket()
    const view = useHistoricalProfile(market)
    await view.selectSymbol(instrument.symbol)
    const late = deferred<MarketHistory>()
    market.getHistory.mockReturnValueOnce(late.promise)
    const oldPeriod = view.selectPeriod('60m')
    await view.selectPeriod('5m')
    late.resolve(history)
    await oldPeriod
    expect(view.period.value).toBe('5m')
    expect(market.getHistory).toHaveBeenLastCalledWith(instrument.symbol, '5m', expect.any(AbortSignal))

    market.getHistory.mockRejectedValueOnce(new Error('行情接口超时'))
    await view.selectPeriod('day')
    expect(view.period.value).toBe('5m')
    expect(view.history.value?.symbol).toBe(instrument.symbol)
    expect(view.historyError.value).toBe('行情接口超时')
  })

  it('股票信息失败时不发历史请求，行情失败时保留已获取的股票信息', async () => {
    const market = testMarket()
    const view = useHistoricalProfile(market)
    market.getInstrument.mockRejectedValueOnce(new Error('股票代码不存在'))
    await view.selectSymbol(instrument.symbol)
    expect(market.getHistory).not.toHaveBeenCalled()
    expect(view.instrumentError.value).toBe('股票代码不存在')
    expect(view.history.value).toBeNull()

    market.getHistory.mockRejectedValueOnce(new Error('行情源暂不可用'))
    await view.selectSymbol(instrument.symbol)
    expect(view.instrument.value?.symbol).toBe(instrument.symbol)
    expect(view.instrumentError.value).toBe('')
    expect(view.historyError.value).toBe('行情源暂不可用')
    expect(view.history.value).toBeNull()
  })
})
