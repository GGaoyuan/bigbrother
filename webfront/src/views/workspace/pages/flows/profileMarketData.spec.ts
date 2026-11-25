import { beforeEach, describe, expect, it, vi } from 'vitest'
import { request } from '@/api/request'
import { profileMarket } from './profileMarketData'

vi.mock('@/api/request', () => ({
  request: vi.fn(),
}))

const mockRequest = vi.mocked(request)

beforeEach(() => mockRequest.mockReset())

describe('真实成交量分布 API', () => {
  it('分别查询股票元信息和前复权 K 线，保留复权版本并转换时间和价格', async () => {
    const info = {
      symbol: '600519',
      name: '贵州茅台',
      exchange: 'SSE',
      market: 'CN',
      currency: 'CNY',
      price_tick: 0.01,
      source: 'tencent',
    }
    const candle = {
      timestamp: 10,
      end_timestamp: 20,
      open: 12.34,
      high: 12.45,
      low: 12.01,
      close: 12.39,
      volume: 12345,
      amount: 150000.15,
    }
    mockRequest.mockResolvedValueOnce(info).mockResolvedValueOnce({
      symbol: '600519',
      source: 'tencent',
      adjust: 'qfq',
      adjustment_version: 'qfq-v2',
      bars: [
        {
          ...candle,
          timestamp: 20,
          end_timestamp: 30,
        },
        candle,
      ],
    })
    const signal = new AbortController().signal

    await expect(profileMarket.getInstrument('600519', signal)).resolves.toEqual(info)
    const history = await profileMarket.getHistory('600519', 'day', signal)
    expect(history.adjustment_version).toBe('qfq-v2')
    expect(history.adjust).toBe('qfq')
    expect(history.bars[0]).toEqual({
      start: 10,
      end: 20,
      open: 1234,
      high: 1245,
      low: 1201,
      close: 1239,
      volume: 12345,
    })
    expect(mockRequest).toHaveBeenNthCalledWith(1, '/stocks/600519', expect.objectContaining({
      method: 'GET',
      signal,
    }))
    expect(mockRequest).toHaveBeenNthCalledWith(2, '/stocks/600519/klines', expect.objectContaining({
      method: 'POST',
      body: {
        interval: '1d',
      },
      signal,
    }))
  })

  it('只发送区间申请服务器估算，并传递覆盖不足的原始错误', async () => {
    const error = new Error('1 分钟 K 线覆盖不足')
    mockRequest.mockRejectedValueOnce(error)
    const signal = new AbortController().signal
    await expect(profileMarket.calculateProfile('600519', {
      start: 10,
      end: 20,
    }, signal)).rejects.toBe(error)
    expect(mockRequest).toHaveBeenCalledWith('/stocks/600519/volume-profile', expect.objectContaining({
      method: 'POST',
      body: {
        start: 10,
        end: 20,
      },
      signal,
    }))
  })
})
