import { request } from './request'

export async function loadWithDemo<T>(
  path: string,
  demo: () => T,
  body?: unknown,
  hasData: (data: T) => boolean = (data) => !Array.isArray(data) || data.length > 0,
): Promise<{
  data: T
  simulated: boolean
}> {
  if (import.meta.env.VITE_API_BASE_URL?.trim()) {
    try {
      const data = await request<T>(path, { body })
      if (data != null && hasData(data)) {
        return {
          data,
          simulated: false,
        }
      }
    } catch {
      // Keep the demo usable when the optional service cannot supply data.
    }
  }

  return {
    data: demo(),
    simulated: true,
  }
}
