import { request } from './request'
import { useUserInfoStore, type UserInfo } from '../stores/userinfo'

export interface LoginCredentials {
  phone: string
  password: string
}

export async function login(credentials: LoginCredentials): Promise<UserInfo> {
  const userInfo = await request<UserInfo>('/auth/login', {
    method: 'POST',
    body: credentials,
    withAuth: false,
  })

  useUserInfoStore().setUserInfo(userInfo)

  return userInfo
}
