export const VALUE_AREA_TARGET = 70

export interface ProfileLevel {
  priceCents: number
  lowPriceCents?: number
  highPriceCents?: number
  total: number
  buy: number
  sell: number
  neutral: number
  unknown: number
  delta: number | null
  node: 'HVN' | 'LVN' | null
}

export interface VolumeProfile {
  levels: ProfileLevel[]
  poc?: ProfileLevel
  valueArea?: {
    low: number
    high: number
    volume: number
  }
  total: number
  hasDirection: boolean
}
