import { login as loginApi } from '../api/api'
import type { LoginCredentials } from '../api/types'
import { useUserInfoStore, type UserInfo } from '../stores/userinfo'

export async function login(credentials: LoginCredentials): Promise<UserInfo> {
  const userInfo = await loginApi(credentials)
  useUserInfoStore().setUserInfo(userInfo)

  return userInfo
}
