import { getActivePinia } from 'pinia'
import { useUserInfoStore } from '../stores/userinfo'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'

export interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
  withAuth?: boolean
}

export interface ApiEnvelope<T> {
  code: number
  message: string
  data: T
}

export class ApiRequestError extends Error {
  status: number
  code: number | null

  constructor(message: string, status: number, code: number | null = null) {
    super(message)
    this.name = 'ApiRequestError'
    this.status = status
    this.code = code
  }
}

function serializeBody(body: unknown): BodyInit | undefined {
  if (body === undefined) {
    return undefined
  }

  if (body instanceof FormData) {
    return body
  }

  return JSON.stringify(body)
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const {
    body,
    headers: initialHeaders,
    withAuth = true,
    ...requestOptions
  } = options
  const headers = new Headers(initialHeaders)

  if (body !== undefined && !(body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  if (withAuth) {
    const pinia = getActivePinia()
    const token = pinia ? useUserInfoStore(pinia).token : ''

    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestOptions,
    headers,
    body: serializeBody(body),
  })
  const payload = await response.json().catch(() => null) as ApiEnvelope<unknown> | null

  if (!response.ok) {
    const message = typeof payload?.message === 'string'
      ? payload.message
      : `请求失败：${response.status}`
    throw new ApiRequestError(message, response.status, payload?.code ?? null)
  }

  if (!payload || typeof payload !== 'object') {
    throw new ApiRequestError('服务器返回了无效响应', response.status)
  }

  if (typeof payload.code === 'number' && payload.code !== 200) {
    throw new ApiRequestError(payload.message, response.status, payload.code)
  }

  if (typeof payload.code === 'number') {
    return payload.data as T
  }

  return payload as T
}
