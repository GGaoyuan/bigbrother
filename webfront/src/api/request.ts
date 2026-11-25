import axios, {
  AxiosHeaders,
  type AxiosRequestConfig,
} from 'axios'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim()
export const DEFAULT_HEADERS = {
  Accept: 'application/json',
  'Content-Type': 'application/json',
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: DEFAULT_HEADERS,
  timeout: 3000,
})

export interface RequestOptions extends Omit<AxiosRequestConfig, 'data' | 'url'> {
  body?: unknown
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

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const {
    body,
    headers: initialHeaders,
    method = 'POST',
    ...requestOptions
  } = options
  const headers = AxiosHeaders.from(DEFAULT_HEADERS)
  const customHeaders = initialHeaders as Record<string, unknown> | undefined

  Object.entries(customHeaders ?? {}).forEach(([key, value]) => {
    if (value !== undefined) {
      headers.set(key, value as string)
    }
  })

  if (body instanceof FormData) {
    headers.delete('Content-Type')
  } else if (body !== undefined) {
    headers.set('Content-Type', 'application/json')
  } else if (method === 'GET' || method === 'HEAD') {
    headers.delete('Content-Type')
  }

  let response

  try {
    response = await apiClient.request<ApiEnvelope<unknown>>({
      ...requestOptions,
      url: path,
      method,
      headers,
      data: body,
    })
  } catch (error) {
    if (!axios.isAxiosError<ApiEnvelope<unknown>>(error)) {
      throw error
    }

    const payload = error.response?.data
    const message = typeof payload?.message === 'string'
      ? payload.message
      : error.message || '网络请求失败'

    throw new ApiRequestError(
      message,
      error.response?.status ?? 0,
      payload?.code ?? null,
    )
  }

  const payload = response.data as ApiEnvelope<unknown> | null

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
