import { request } from '@/api/request'
import type { VolumeProfile } from './volumeProfile'

export type HistoryPeriod = 'day' | '60m' | '5m'
export const ESTIMATED_PROFILE_METHOD = 'estimated_1m_weighted_range'

/** Unix seconds, using an inclusive start and exclusive end. */
export interface TimeRange {
  start: number
  end: number
}

export interface MarketCandle extends TimeRange {
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface MarketInstrument {
  symbol: string
  name: string
  exchange: string
  market: string
  currency: string
  price_tick: number
  source: string
}

export interface MarketHistory {
  symbol: string
  source: string
  adjust: 'qfq'
  adjustment_version: string
  bars: MarketCandle[]
}

export interface MarketProfileResult extends TimeRange {
  symbol: string
  source: string
  complete: boolean
  profile: VolumeProfile
  calculation_method: string
  adjustment_version: string
  actual_start: number
  actual_end: number
  price_step: number
}

export interface ProfileMarketData {
  getInstrument(symbol: string, signal?: AbortSignal): Promise<MarketInstrument>
  getHistory(symbol: string, period: HistoryPeriod, signal?: AbortSignal): Promise<MarketHistory>
  calculateProfile(symbol: string, range: TimeRange, signal?: AbortSignal): Promise<MarketProfileResult>
}

interface ApiCandle {
  timestamp: number
  end_timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number | null
}

interface ApiHistory extends Omit<MarketHistory, 'bars'> {
  bars: ApiCandle[]
}

const baseURL = import.meta.env.VITE_API_BASE_URL?.trim() || 'http://localhost:8000/api/v1'

function stockPath(symbol: string) {
  return `/stocks/${encodeURIComponent(symbol)}`
}

function priceInCents(price: number) {
  const cents = Math.round(price * 100)
  if (!Number.isSafeInteger(cents) || cents <= 0) throw new Error('历史 K 线包含无效价格')
  return cents
}

function toCandles(rows: ApiCandle[]): MarketCandle[] {
  if (!Array.isArray(rows)) throw new Error('历史 K 线接口返回的格式无效')

  const bars = rows.map((row) => {
    if (!Number.isSafeInteger(row.timestamp) || !Number.isSafeInteger(row.end_timestamp)
      || row.timestamp <= 0 || row.end_timestamp <= row.timestamp
      || !Number.isFinite(row.volume) || row.volume < 0) {
      throw new Error('历史 K 线包含无效时间或成交量')
    }
    return {
      start: row.timestamp,
      end: row.end_timestamp,
      open: priceInCents(row.open),
      high: priceInCents(row.high),
      low: priceInCents(row.low),
      close: priceInCents(row.close),
      volume: row.volume,
    }
  }).sort((first, second) => first.start - second.start)

  if (bars.some((bar, index) => bar.start === bars[index - 1]?.start)) {
    throw new Error('历史 K 线包含重复时间')
  }
  return bars
}

export const profileMarket: ProfileMarketData = {
  getInstrument(symbol, signal) {
    return request<MarketInstrument>(stockPath(symbol), {
      baseURL,
      method: 'GET',
      signal,
      timeout: 10000,
    })
  },
  async getHistory(symbol, period, signal) {
    const response = await request<ApiHistory>(`${stockPath(symbol)}/klines`, {
      baseURL,
      method: 'POST',
      body: {
        interval: period === 'day' ? '1d' : period,
      },
      signal,
      timeout: 15000,
    })
    if (response.adjust !== 'qfq' || typeof response.adjustment_version !== 'string'
      || !response.adjustment_version.trim()) {
      throw new Error('历史 K 线接口缺少有效的前复权版本')
    }
    return {
      symbol: response.symbol,
      source: response.source,
      adjust: response.adjust,
      adjustment_version: response.adjustment_version,
      bars: toCandles(response.bars),
    }
  },
  calculateProfile(symbol, range, signal) {
    return request<MarketProfileResult>(`${stockPath(symbol)}/volume-profile`, {
      baseURL,
      method: 'POST',
      body: {
        start: range.start,
        end: range.end,
      },
      signal,
      timeout: 45000,
    })
  },
}
