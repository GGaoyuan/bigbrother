import { defineStore } from 'pinia'

// 使用 defineStore 定义 store
// 第一个参数是 store 的唯一 ID
export const useExampleStore = defineStore('example', {
  // 状态（state）
  state: () => ({
    count: 0,
    name: 'Example Store'
  }),

  // 计算属性（getters）
  getters: {
    doubleCount: (state) => state.count * 2
  },

  // 方法（actions）
  actions: {
    increment() {
      this.count++
    },
    decrement() {
      this.count--
    },
    reset() {
      this.count = 0
    }
  }
})

