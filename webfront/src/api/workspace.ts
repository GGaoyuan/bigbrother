import { request } from './request'

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

export interface WorkspaceDataResponse {
  workspaceId: number
  dataCategories: DataCategory[]
}

export interface WorkspacePage {
  id: number
  name: string
  path: string
}

export interface WorkspacePagesResponse {
  workspaceId: number
  pages: WorkspacePage[]
}

export async function fetchWorkspaceData(): Promise<WorkspaceDataResponse> {
  return request<WorkspaceDataResponse>('/workspace/data', {
    method: 'POST',
  })
}

export async function fetchWorkspacePages(): Promise<WorkspacePagesResponse> {
  return request<WorkspacePagesResponse>('/workspace/pages', {
    method: 'POST',
  })
}
