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
}
