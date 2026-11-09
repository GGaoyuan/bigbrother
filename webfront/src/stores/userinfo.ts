import { defineStore } from 'pinia'

export interface UserInfo {
  password: string | null
  phone: string
  nickName: string | null
  mail: string | null
  userId: string
  token: string
}

export const useUserInfoStore = defineStore('userinfo', {
  state: (): UserInfo => ({
    password: null,
    phone: '',
    nickName: null,
    mail: null,
    userId: '',
    token: '',
  }),
  actions: {
    setUserInfo(userInfo: Partial<UserInfo>) {
      Object.assign(this, userInfo)
    },
    clearUserInfo() {
      this.password = null
      this.phone = ''
      this.nickName = null
      this.mail = null
      this.userId = ''
      this.token = ''
    },
  },
})
