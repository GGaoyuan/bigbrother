// 简易 v2 API 客户端：统一 baseURL、鉴权 header、响应解包。
// baseURL 可通过 VITE_API_BASE 覆盖，默认本地后端。

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'

// beta 鉴权（与后端 verify_auth 约定一致）
const AUTH_HEADERS: Record<string, string> = {
  token: 'gaoyuanzuishuai',
  uid: '1993',
}

interface ApiResponse<T> {
  code: number
  message: string
  data: T | null
}

/**
 * 调用 v2 POST 接口。后端统一返回 { code, message, data } 信封。
 * code !== 200 时抛出错误，调用方需处理。
 */
export async function postV2<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}/api/v2${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...AUTH_HEADERS,
    },
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${res.statusText}`)
  }

  const json = (await res.json()) as ApiResponse<T>
  if (json.code !== 200) {
    throw new Error(json.message || `API error ${json.code}`)
  }
  if (json.data === null) {
    throw new Error('API returned empty data')
  }
  return json.data
}

// ─── 市值相关类型 ─────────────────────────────────────────────────────
export interface TrendPoint {
  time: string // YYYY-MM-DD
  value: number
}

export interface TotalMarketCap {
  symbol: string
  name: string
  points: TrendPoint[]
}

export interface IndustryTrend {
  symbol: string
  points: TrendPoint[]
}

export interface IndustryNode {
  sw_level: number | null
  sw_industry_code: string | null
  sw_industry_name: string | null
  sw_parent_industry: string | null
  sw_component_count: number | null
}

export interface IndustryTree {
  first: IndustryNode[]
  second: IndustryNode[]
  third: IndustryNode[]
}

export const marketCapApi = {
  total: () => postV2<TotalMarketCap>('/market-cap/total'),
  industryTree: () => postV2<IndustryTree>('/market-cap/industry-tree'),
  industryTrend: (symbol: string) =>
    postV2<IndustryTrend>('/market-cap/industry-trend', { symbol }),
  totalVolume: () => postV2<TotalMarketCap>('/market-cap/total-volume'),
  industryVolume: (symbol: string) =>
    postV2<IndustryTrend>('/market-cap/industry-volume', { symbol }),
}

// ─── 板块资金流类型 ───────────────────────────────────────────────────
export interface SectorFlowItem {
  sector_name: string
  change_pct: number | null
  fund_net_inflow: number | null
  datasource?: string
}

export interface SectorFlowRanking {
  inflow: SectorFlowItem[]
  outflow: SectorFlowItem[]
  all: SectorFlowItem[]
}

export interface SectorFlowTrend {
  sector_name: string
  points: TrendPoint[]
}

export const sectorFlowApi = {
  ranking: () => postV2<SectorFlowRanking>('/sector-flow/ranking'),
  trend: (sectorName: string) =>
    postV2<SectorFlowTrend>('/sector-flow/trend', { sector_name: sectorName }),
}

// ─── 板块日内资金流类型 ───────────────────────────────────────────────
export interface SectorIntradaySnapshot {
  code: string
  name: string
  net_inflow: number // 亿元
}

export interface IntradayPoint {
  time: string // HH:MM
  net_inflow: number // 截至该分钟累计（亿）
}

export interface SectorIntradayTrend {
  code: string
  name: string
  points: IntradayPoint[]
}

export interface SectorIntradayRanking {
  ranking: SectorIntradaySnapshot[]
  inflow_trends: SectorIntradayTrend[]
  outflow_trends: SectorIntradayTrend[]
}

export const sectorIntradayApi = {
  ranking: (topN: number = 12, bottomN: number = 12) =>
    postV2<SectorIntradayRanking>('/sector-intraday/ranking', {
      top_n: topN,
      bottom_n: bottomN,
    }),
}

// ─── 指数 K 线类型 ────────────────────────────────────────────────────
export interface IndexInfo {
  symbol: string
  name: string
}

export interface IndexKlineBar {
  trade_date: string | null
  open: number | null
  high: number | null
  low: number | null
  close: number | null
  volume: number | null
  amount: number | null
  change_pct: number | null
}

export interface IndexKline {
  symbol: string
  name: string
  period: string // day | week | month
  bars: IndexKlineBar[]
}

export const indexApi = {
  list: () => postV2<IndexInfo[]>('/index/list'),
  kline: (symbol: string, period: string = 'day', limit: number = 500) =>
    postV2<IndexKline>('/index/kline', { symbol, period, limit }),
}

// ─── 成交量分布 K 线类型 ──────────────────────────────────────────────
export interface VolumeKlineBar {
  datetime: string | null
  open: number | null
  high: number | null
  low: number | null
  close: number | null
  volume: number | null
  amount: number | null
}

export interface VolumeKline {
  symbol: string
  period: string // 1m | 5m | 30m | day
  bars: VolumeKlineBar[]
}

export const volumeProfileApi = {
  kline: (symbol: string, period: string = 'day', count: number = 300) =>
    postV2<VolumeKline>('/volume-profile/kline', { symbol, period, count }),
}
