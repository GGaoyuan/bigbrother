import { request } from './request'

export interface DataSeries {
  id: string
  label: string
  code: string
  categoryLabel: string
}

export interface DataCategory {
  id: string
  type: string
  label: string
  icon: string
  series: DataSeries[]
}

export interface DataMetric {
  id: string
  label: string
}

export interface WorkspaceDataResponse {
  workspaceId: number
  data: {
    sidebar: Record<string, string>
    dataCategories: DataCategory[]
    metrics: DataMetric[]
  }
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
    method: 'GET',
  })
}

export async function fetchWorkspacePages(): Promise<WorkspacePagesResponse> {
  return request<WorkspacePagesResponse>('/workspace/pages', {
    method: 'GET',
  })
}
