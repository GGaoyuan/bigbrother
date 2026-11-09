export interface LoginCredentials {
  phone: string
  password: string
}

export interface DataSeries {
  id: string
  name: string
  code: string
}

export interface DataMetric {
  id: string
  name: string
}

export interface DataCategory {
  id: string
  name: string
  series?: DataSeries[]
  metrics: DataMetric[]
  chartTypes?: Array<'line' | 'bar' | 'candlestick'>
}

export type DataChartType = NonNullable<DataCategory['chartTypes']>[number]

export interface DataChartSelection {
  categoryId: string
  seriesId?: string
  metricId: string
  chartName: string
  chartType: DataChartType
  color: string
}

export interface GridItem {
  label: string
  value: string
  color: string
  sub?: string
}
