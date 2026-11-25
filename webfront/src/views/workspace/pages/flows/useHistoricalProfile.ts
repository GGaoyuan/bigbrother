import { computed, ref, shallowRef } from 'vue'
import { ApiRequestError } from '@/api/request'
import {
  ESTIMATED_PROFILE_METHOD,
  profileMarket,
  type HistoryPeriod,
  type MarketHistory,
  type MarketInstrument,
  type ProfileMarketData,
  type TimeRange,
} from './profileMarketData'
import type { VolumeProfile } from './volumeProfile'

interface AppliedProfile {
  range: TimeRange
  actualRange: TimeRange
  profile: VolumeProfile
  source: string
}

interface ProfileIssue {
  kind: 'coverage' | 'adjustment' | 'error'
  message: string
}

export function useHistoricalProfile(market: ProfileMarketData = profileMarket) {
  const instrument = shallowRef<MarketInstrument | null>(null)
  const history = shallowRef<MarketHistory | null>(null)
  const period = ref<HistoryPeriod>('day')
  const selection = ref<TimeRange | null>(null)
  const selectionActive = ref(false)
  const applied = shallowRef<AppliedProfile | null>(null)
  const instrumentLoading = ref(false)
  const historyLoading = ref(false)
  const profileLoading = ref(false)
  const instrumentError = ref('')
  const historyError = ref('')
  const profileIssue = shallowRef<ProfileIssue | null>(null)
  let instrumentRequest: AbortController | undefined
  let historyRequest: AbortController | undefined
  let profileRequest: AbortController | undefined

  const pending = computed(() => Boolean(
    applied.value && selection.value && (
      applied.value.range.start !== selection.value.start || applied.value.range.end !== selection.value.end
    ),
  ))

  function stopCalculation() {
    profileRequest?.abort()
    profileRequest = undefined
    profileLoading.value = false
    profileIssue.value = null
  }

  function clear() {
    stopCalculation()
    applied.value = null
  }

  function toggleSelectionTool() {
    if (history.value && !historyLoading.value) selectionActive.value = !selectionActive.value
  }

  function cancelSelection() {
    selectionActive.value = false
    selection.value = null
    stopCalculation()
  }

  async function loadHistory(symbol: string, nextPeriod: HistoryPeriod) {
    historyRequest?.abort()
    const request = new AbortController()
    historyRequest = request
    historyLoading.value = true
    historyError.value = ''
    try {
      const result = await market.getHistory(symbol, nextPeriod, request.signal)
      if (request.signal.aborted) return
      if (result.symbol !== symbol || !Array.isArray(result.bars) || !result.bars.length) {
        throw new Error('该股票没有可用的历史行情')
      }
      if (history.value && history.value.adjustment_version !== result.adjustment_version) {
        const needsRecalculation = applied.value !== null || profileLoading.value
        clear()
        if (needsRecalculation) {
          profileIssue.value = {
            kind: 'error',
            message: 'K 线的前复权版本已更新，请重新确认计算。',
          }
        }
      }
      history.value = result
      period.value = nextPeriod
    } catch (error) {
      if (!request.signal.aborted) {
        historyError.value = error instanceof Error ? error.message : '历史行情加载失败'
      }
    } finally {
      if (historyRequest === request) {
        historyLoading.value = false
        historyRequest = undefined
      }
    }
  }

  async function selectSymbol(code: string) {
    const symbol = code.trim()
    if (!/^\d{6}$/.test(symbol)) {
      instrumentError.value = '请输入 6 位股票代码'
      return
    }

    instrumentRequest?.abort()
    historyRequest?.abort()
    historyRequest = undefined
    historyLoading.value = false
    historyError.value = ''
    history.value = null
    instrument.value = null
    instrumentError.value = ''
    selection.value = null
    selectionActive.value = false
    clear()

    const request = new AbortController()
    instrumentRequest = request
    instrumentLoading.value = true
    try {
      const result = await market.getInstrument(symbol, request.signal)
      if (request.signal.aborted) return
      if (result.symbol !== symbol || !result.name) throw new Error('未获取到有效的股票基本信息')
      instrument.value = result
    } catch (error) {
      if (!request.signal.aborted) {
        instrumentError.value = error instanceof Error ? error.message : '股票基本信息加载失败'
      }
    } finally {
      if (instrumentRequest === request) {
        instrumentLoading.value = false
        instrumentRequest = undefined
      }
    }

    if (!request.signal.aborted && instrument.value?.symbol === symbol) {
      await loadHistory(symbol, period.value)
    }
  }

  function selectPeriod(nextPeriod: HistoryPeriod) {
    const stock = instrument.value
    if (!stock || (history.value && nextPeriod === period.value && !historyLoading.value)) return
    return loadHistory(stock.symbol, nextPeriod)
  }

  function refreshHistory() {
    if (instrument.value) return loadHistory(instrument.value.symbol, period.value)
  }

  async function confirm() {
    const stock = instrument.value
    if (!stock || !history.value || !selection.value || historyLoading.value || profileLoading.value) return

    const request = new AbortController()
    const range = {
      ...selection.value,
    }
    selectionActive.value = false
    profileRequest = request
    profileLoading.value = true
    profileIssue.value = null
    try {
      const result = await market.calculateProfile(stock.symbol, range, request.signal)
      if (request.signal.aborted) return
      if (result.symbol !== stock.symbol || result.start !== range.start || result.end !== range.end) {
        throw new Error('成交量分布返回的股票或区间与请求不一致')
      }
      if (result.complete !== true) {
        throw new Error('所选区间的 1 分钟 K 线覆盖不完整')
      }
      if (result.calculation_method !== ESTIMATED_PROFILE_METHOD) {
        throw new Error('成交量分布接口未返回基于 1 分钟 K 线的估算结果')
      }
      if (result.adjustment_version !== history.value?.adjustment_version) {
        profileIssue.value = {
          kind: 'adjustment',
          message: '估算结果与当前 K 线的前复权版本不一致，请刷新 K 线后重新计算。',
        }
        return
      }
      if (!Number.isSafeInteger(result.actual_start) || !Number.isSafeInteger(result.actual_end)
        || result.actual_start < 0 || result.actual_start >= result.actual_end) {
        throw new Error('成交量分布返回的实际统计区间无效')
      }
      if (!result.profile?.levels.length) throw new Error('所选区间没有可估算的成交量')

      applied.value = {
        range,
        actualRange: {
          start: result.actual_start,
          end: result.actual_end,
        },
        profile: result.profile,
        source: result.source,
      }
    } catch (error) {
      if (!request.signal.aborted) {
        profileIssue.value = {
          kind: error instanceof ApiRequestError && error.status === 409 ? 'coverage' : 'error',
          message: error instanceof Error ? error.message : '成交量分布计算失败',
        }
      }
    } finally {
      if (profileRequest === request) {
        profileLoading.value = false
        profileRequest = undefined
      }
    }
  }

  function dispose() {
    instrumentRequest?.abort()
    historyRequest?.abort()
    profileRequest?.abort()
  }

  return {
    instrument,
    history,
    period,
    selection,
    selectionActive,
    applied,
    pending,
    instrumentLoading,
    historyLoading,
    profileLoading,
    instrumentError,
    historyError,
    profileIssue,
    selectSymbol,
    selectPeriod,
    refreshHistory,
    toggleSelectionTool,
    cancelSelection,
    confirm,
    clear,
    dispose,
  }
}
