export const WORKSPACE_ID = {
  DATA: 1,
  AI: 2,
  PAGES: 3,
} as const

export const CONTAINER_TYPE = {
  DATA: 'data',
  AI: 'ai',
  ROUTE: 'route',
} as const

export const DATA_CATEGORY_ID = {
  A_SHARE: 'a-share-equities',
  A_INDEX: 'a-share-indices',
  A_VALUATION: 'a-share-index-valuations',
  MARGIN: 'margin-trading',
} as const

export const METRIC_ID = {
  CLOSE: 'close',
  OPEN: 'open',
  HIGH: 'high',
  LOW: 'low',
  VOLUME: 'volume',
  AMOUNT: 'amount',
  CHANGE_PERCENT: 'change-percent',
} as const

export const PAGE_ID = {
  MARKET_QUOTES: 101,
  MARKET_SENTIMENT: 102,
  TODAY_MARKET: 103,
  MARKET_ANOMALY: 104,
  RECAP_MARKET: 105,
  RECAP_INDICATORS: 106,
  RECAP_MACRO: 107,
  RECAP_DIVIDEND_YIELD: 108,
  RECAP_HEATMAP: 109,
  RECAP_SECTOR: 110,
  HEATMAP_THEME: 111,
  HEATMAP_INDUSTRY: 112,
  HEATMAP_CHANGE: 113,
  TIMELINE: 114,
  THEME_LIBRARY: 115,
  ORDER_FLOW: 116,
  INTRADAY_FLOW: 117,
  TOP_LIST: 118,
  HOT_RANK: 119,
} as const

export type WorkspaceId = (typeof WORKSPACE_ID)[keyof typeof WORKSPACE_ID]
export type PageId = (typeof PAGE_ID)[keyof typeof PAGE_ID]
export type DataCategoryId = (typeof DATA_CATEGORY_ID)[keyof typeof DATA_CATEGORY_ID]
export type MetricId = (typeof METRIC_ID)[keyof typeof METRIC_ID]
