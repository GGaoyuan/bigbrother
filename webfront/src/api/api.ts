import type { UserInfo } from '../stores/userinfo'
import { request } from './request'
import type { LoginCredentials } from './types'

export async function login(credentials: LoginCredentials): Promise<UserInfo> {
  return request<UserInfo>('/auth/login', {
    body: credentials,
    withAuth: false,
  })
}

export async function fetchAppConfig<T>(): Promise<T> {
  return request<T>('/app/config')
}

export async function fetchWorkspaceData<T>(): Promise<T> {
  return request<T>('/workspace/data')
}

export async function fetchWorkspacePages<T>(): Promise<T> {
  return request<T>('/workspace/pages')
}

export async function fetchMarketSentiment<T>(date: string): Promise<T> {
  return request<T>('/market-sentiment', {
    body: {
      date,
    },
  })
}
