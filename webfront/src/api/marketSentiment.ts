const BASE_URL = 'http://127.0.0.1:8000/api/v1'

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
  const res = await fetch(`${BASE_URL}/market-sentiment`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ date }),
  })
  if (!res.ok) throw new Error(`请求失败: ${res.status}`)
  return res.json()
}
