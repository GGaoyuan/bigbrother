import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 板块数据接口
export interface SectorData {
  id: string
  name: string
  code: string
  value: number
  change: number // 涨跌幅
  isAnchor?: boolean // 是否为锚定板块（如银行、券商）
}

// 指数数据接口
export interface IndexData {
  id: string
  name: string
  code: string
  value: number
  change: number
}

// 策略配置接口
export interface StrategyConfig {
  anchorSectors: string[] // 锚定板块代码列表
  anchorIndexes: string[] // 锚定指数代码列表
  maxSectors: number // 最大板块数量
}

export const useDataCoreStore = defineStore('dataCore', () => {
  // ========== State ==========
  
  // 板块数据列表
  const sectors = ref<SectorData[]>([
    { id: '1', name: '银行', code: 'BK0475', value: 1200.5, change: 2.5, isAnchor: true },
    { id: '2', name: '券商', code: 'BK0473', value: 980.3, change: -1.2, isAnchor: true },
    { id: '3', name: '房地产', code: 'BK0451', value: 750.8, change: 0.8 },
    { id: '4', name: '医药', code: 'BK0727', value: 1100.2, change: 1.5 },
    { id: '5', name: '科技', code: 'BK0726', value: 1350.6, change: 3.2 }
  ])

  // 指数数据列表
  const indexes = ref<IndexData[]>([
    { id: '1', name: '上证指数', code: '000001', value: 3200.5, change: 1.2 },
    { id: '2', name: '深证成指', code: '399001', value: 11500.3, change: 0.8 },
    { id: '3', name: '创业板指', code: '399006', value: 2450.6, change: 2.1 }
  ])

  // 策略配置
  const strategyConfig = ref<StrategyConfig>({
    anchorSectors: ['BK0475', 'BK0473'], // 银行、券商作为锚定
    anchorIndexes: ['000001'], // 上证指数作为锚定
    maxSectors: 10
  })

  // 加载状态
  const loading = ref(false)

  // 错误信息
  const error = ref<string | null>(null)

  // ========== Getters ==========
  
  // 获取所有锚定板块
  const anchorSectors = computed(() => {
    return sectors.value.filter(sector => sector.isAnchor)
  })

  // 获取所有非锚定板块
  const nonAnchorSectors = computed(() => {
    return sectors.value.filter(sector => !sector.isAnchor)
  })

  // 根据代码获取板块
  const getSectorByCode = computed(() => {
    return (code: string) => sectors.value.find(sector => sector.code === code)
  })

  // 根据代码获取指数
  const getIndexByCode = computed(() => {
    return (code: string) => indexes.value.find(index => index.code === code)
  })

  // 获取所有锚定板块和指数的代码列表
  const allAnchorCodes = computed(() => {
    return [
      ...strategyConfig.value.anchorSectors,
      ...strategyConfig.value.anchorIndexes
    ]
  })

  // ========== Actions ==========
  
  // 添加板块
  function addSector(sector: SectorData) {
    if (!sectors.value.find(s => s.code === sector.code)) {
      sectors.value.push(sector)
    }
  }

  // 更新板块数据
  function updateSector(code: string, data: Partial<SectorData>) {
    const index = sectors.value.findIndex(s => s.code === code)
    if (index !== -1) {
      sectors.value[index] = { ...sectors.value[index], ...data }
    }
  }

  // 删除板块
  function removeSector(code: string) {
    const index = sectors.value.findIndex(s => s.code === code)
    if (index !== -1) {
      sectors.value.splice(index, 1)
    }
  }

  // 设置板块为锚定
  function setSectorAsAnchor(code: string, isAnchor: boolean = true) {
    const sector = sectors.value.find(s => s.code === code)
    if (sector) {
      sector.isAnchor = isAnchor
      if (isAnchor && !strategyConfig.value.anchorSectors.includes(code)) {
        strategyConfig.value.anchorSectors.push(code)
      } else if (!isAnchor) {
        const index = strategyConfig.value.anchorSectors.indexOf(code)
        if (index !== -1) {
          strategyConfig.value.anchorSectors.splice(index, 1)
        }
      }
    }
  }

  // 添加指数
  function addIndex(index: IndexData) {
    if (!indexes.value.find(i => i.code === index.code)) {
      indexes.value.push(index)
    }
  }

  // 更新指数数据
  function updateIndex(code: string, data: Partial<IndexData>) {
    const index = indexes.value.findIndex(i => i.code === code)
    if (index !== -1) {
      indexes.value[index] = { ...indexes.value[index], ...data }
    }
  }

  // 更新策略配置
  function updateStrategyConfig(config: Partial<StrategyConfig>) {
    strategyConfig.value = { ...strategyConfig.value, ...config }
  }

  // 获取板块数据（模拟 API 调用）
  async function fetchSectors() {
    loading.value = true
    error.value = null
    
    try {
      // 这里可以调用实际的 API
      // const response = await api.getSectors()
      // sectors.value = response.data
      
      // 模拟异步操作
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 示例：更新一些随机数据
      sectors.value.forEach(sector => {
        sector.value += Math.random() * 10 - 5
        sector.change = (Math.random() * 6 - 3).toFixed(2) as any
      })
    } catch (err: any) {
      error.value = err.message || '获取板块数据失败'
      console.error('获取板块数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 获取指数数据（模拟 API 调用）
  async function fetchIndexes() {
    loading.value = true
    error.value = null
    
    try {
      // 这里可以调用实际的 API
      // const response = await api.getIndexes()
      // indexes.value = response.data
      
      // 模拟异步操作
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 示例：更新一些随机数据
      indexes.value.forEach(index => {
        index.value += Math.random() * 20 - 10
        index.change = (Math.random() * 4 - 2).toFixed(2) as any
      })
    } catch (err: any) {
      error.value = err.message || '获取指数数据失败'
      console.error('获取指数数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 重置所有数据
  function reset() {
    sectors.value = []
    indexes.value = []
    error.value = null
    loading.value = false
  }

  // 清除错误
  function clearError() {
    error.value = null
  }

  return {
    // State
    sectors,
    indexes,
    strategyConfig,
    loading,
    error,
    
    // Getters
    anchorSectors,
    nonAnchorSectors,
    getSectorByCode,
    getIndexByCode,
    allAnchorCodes,
    
    // Actions
    addSector,
    updateSector,
    removeSector,
    setSectorAsAnchor,
    addIndex,
    updateIndex,
    updateStrategyConfig,
    fetchSectors,
    fetchIndexes,
    reset,
    clearError
  }
})

