// 全局 stores - 直接导出实例，无需 import 即可使用
import { useDataCoreStore } from './dataCore'
import { useExampleStore } from './example'

// 直接创建并导出 store 实例
export const dataCore = useDataCoreStore()
export const example = useExampleStore()

