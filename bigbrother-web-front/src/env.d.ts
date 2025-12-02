/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module '@vue/runtime-core' {
  export interface GlobalComponents {
    RouterView: typeof import('vue-router')['RouterView']
    RouterLink: typeof import('vue-router')['RouterLink']
  }
  
  export interface ComponentCustomProperties {
    $stores: typeof import('./stores/global')['stores']
  }
}

// 全局类型声明
declare global {
  var $stores: typeof import('./stores/global')['stores']
}

// 确保 Vue 的类型可以被正确识别
import 'vue'

