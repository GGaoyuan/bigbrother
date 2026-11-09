import { request } from './request'

export interface AppConfig {
  workspace: WorkspaceConfig[]
}

export interface WorkspaceConfig {
  id: number
  name: string
}

export async function fetchAppConfig(): Promise<AppConfig> {
  return request<AppConfig>('/app/config', {
    method: 'GET',
  })
}
