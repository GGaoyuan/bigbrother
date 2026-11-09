import { request } from './request'

export interface GridItem {
  label: string
  value: string
  color: string
  sub?: string
}

export interface MarketSentimentData {
  score: number
  grid: GridItem[]
}

export async function fetchMarketSentiment(date: string): Promise<MarketSentimentData> {
  return request<MarketSentimentData>('/market-sentiment', {
    body: {
      date,
    },
  })
}
