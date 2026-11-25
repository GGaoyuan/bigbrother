<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import VolumeProfileChart from './VolumeProfileChart.vue'
import { formatSelectionEdge } from './chartRangeSelection'
import type { HistoryPeriod, TimeRange } from './profileMarketData'
import { useHistoricalProfile } from './useHistoricalProfile'
import { VALUE_AREA_TARGET } from './volumeProfile'

const periods: { id: HistoryPeriod; label: string }[] = [
  {
    id: 'day',
    label: '日线',
  },
  {
    id: '60m',
    label: '60 分钟',
  },
  {
    id: '5m',
    label: '5 分钟',
  },
]

const inputCode = ref('')
const {
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
} = useHistoricalProfile()

const profile = computed(() => applied.value?.profile)
const numberFormat = new Intl.NumberFormat('zh-CN')
const coverage = computed(() => {
  const value = profile.value
  return value?.valueArea ? (value.valueArea.volume / value.total * 100).toFixed(1) : '—'
})
const actualRangeLabel = computed(() => {
  const result = applied.value
  if (!result || (result.range.start === result.actualRange.start && result.range.end === result.actualRange.end)) {
    return ''
  }
  return rangeLabel(result.actualRange)
})

function rangeLabel(range: TimeRange) {
  return `${formatSelectionEdge(range.start, 'start')} 至 ${formatSelectionEdge(range.end, 'end')}`
}

function priceLabel(price?: number) {
  return price === undefined ? '—' : (price / 100).toFixed(2)
}

function sourceLabel(source: string) {
  if (source === 'a-stock-data' || source === 'tencent') return '腾讯行情 · a-stock-data'
  if (source === 'mootdx') return '通达信'
  if (source === 'akshare-sina') return '新浪财经'
  return source
}

function exchangeLabel(exchange: string) {
  switch (exchange.toUpperCase()) {
    case 'SH':
    case 'SSE':
      return '上海证券交易所'
    case 'SZ':
    case 'SZSE':
      return '深圳证券交易所'
    case 'BJ':
    case 'BSE':
      return '北京证券交易所'
    default:
      return exchange
  }
}

function query() {
  void selectSymbol(inputCode.value)
}

onBeforeUnmount(dispose)
</script>

<template>
  <section class="volume-page">
    <header class="page-header">
      <h1>成交量分布图</h1>
      <form class="symbol-form" @submit.prevent="query">
        <label for="profile-code">股票代码</label>
        <input
          id="profile-code"
          v-model.trim="inputCode"
          name="stock-code"
          inputmode="numeric"
          placeholder="例如 600519"
          pattern="[0-9]{6}"
          title="请输入 6 位股票代码"
          required
        />
        <button type="submit">查询</button>
      </form>
    </header>

    <p v-if="instrumentLoading" class="query-status" role="status">正在查询股票基本信息…</p>
    <p v-if="instrumentError" class="error-message" role="alert">{{ instrumentError }}</p>

    <section v-if="instrument" class="profile-panel" aria-label="固定区间成交量分布">
      <div class="chart-toolbar">
        <div class="symbol-caption">
          <strong class="profile-chart-symbol">{{ instrument.symbol }}</strong>
          <span>{{ instrument.name }}</span>
          <span v-if="instrument.exchange">{{ exchangeLabel(instrument.exchange) }}</span>
          <span v-if="history" class="source-label">
            前复权 K 线 · {{ sourceLabel(history.source) }}
          </span>
        </div>

        <div class="periods" role="group" aria-label="K 线周期">
          <button
            v-for="option in periods"
            :key="option.id"
            type="button"
            :aria-pressed="period === option.id"
            @click="selectPeriod(option.id)"
          >
            {{ option.label }}
          </button>
        </div>

        <div class="calculation-actions">
          <button
            type="button"
            class="tool-button"
            :aria-pressed="selectionActive"
            :disabled="!history || historyLoading"
            @click="toggleSelectionTool"
          >
            固定区间成交量分布
          </button>
          <button
            type="button"
            class="confirm-button"
            :disabled="!selection || historyLoading || profileLoading"
            @click="confirm"
          >
            {{ profileLoading ? '计算中…' : '确认计算' }}
          </button>
          <button
            type="button"
            :disabled="!selectionActive && !selection"
            @click="cancelSelection"
          >
            取消选区
          </button>
          <button
            type="button"
            :disabled="!applied && !profileLoading"
            @click="clear"
          >
            清除分布
          </button>
        </div>
      </div>

      <div class="selection-summary">
        <span v-if="history" class="source-label">估算型 Volume Profile · 基于 1 分钟 K 线</span>
        <span v-if="selection">
          当前选区 <strong data-draft-range>{{ rangeLabel(selection) }}</strong>
        </span>
        <span v-if="applied">
          已计算 <strong data-applied-range>{{ rangeLabel(applied.range) }}</strong>
        </span>
        <span v-if="actualRangeLabel">
          实际统计 <strong>{{ actualRangeLabel }}</strong>
        </span>
        <span v-if="historyLoading" role="status">正在加载前复权 K 线…</span>
        <span v-else-if="profileLoading" role="status">正在使用 1 分钟 K 线估算成交量分布…</span>
        <span v-else-if="pending" role="status" class="pending-label">选区已修改，尚未重新计算</span>
        <span v-else-if="selectionActive && !selection" role="status">在 K 线图上按住并拖动以选择区间</span>
        <span v-else-if="selection && !applied && !profileLoading" role="status">选区待计算</span>
        <span v-else-if="history && !selection && !applied" role="status">启用固定区间工具后可在主图选区</span>
      </div>

      <p v-if="historyError" class="error-message" role="alert">{{ historyError }}</p>
      <div v-if="profileIssue?.kind === 'coverage'" class="coverage-notice">
        <p role="status">该区间的 1 分钟 K 线覆盖不足或未通过校验，已保留选区。</p>
        <details>
          <summary>查看数据源详情</summary>
          <p>{{ profileIssue.message }}</p>
        </details>
      </div>
      <div v-else-if="profileIssue?.kind === 'adjustment'" class="error-message">
        <span role="alert">{{ profileIssue.message }}</span>
        <button type="button" :disabled="historyLoading" @click="refreshHistory">刷新 K 线</button>
      </div>
      <p v-else-if="profileIssue" class="error-message" role="alert">{{ profileIssue.message }}</p>

      <dl v-if="profile" class="profile-metrics">
        <div class="poc-value">
          <dt>POC</dt>
          <dd>{{ priceLabel(profile.poc?.priceCents) }}</dd>
        </div>
        <div>
          <dt>VAH</dt>
          <dd>{{ priceLabel(profile.valueArea?.high) }}</dd>
        </div>
        <div>
          <dt>VAL</dt>
          <dd>{{ priceLabel(profile.valueArea?.low) }}</dd>
        </div>
        <div>
          <dt>统计成交量</dt>
          <dd data-profile-volume>{{ numberFormat.format(profile.total) }} 股</dd>
        </div>
        <div v-if="applied">
          <dt>1 分钟 K 线来源</dt>
          <dd>{{ sourceLabel(applied.source) }}</dd>
        </div>
        <div>
          <dt>价值区覆盖（目标 {{ VALUE_AREA_TARGET }}%）</dt>
          <dd>{{ coverage }}%</dd>
        </div>
      </dl>

      <VolumeProfileChart
        v-if="history"
        :candles="history.bars"
        :period="period"
        :profile="profile ?? null"
        :selection="selection"
        :selection-active="selectionActive"
        :applied-range="applied?.actualRange ?? null"
        @update:selection="selection = $event"
        @cancel-selection="cancelSelection"
      />
    </section>
  </section>
</template>

<style scoped>
.volume-page {
  --caption: #52637c;
  --rule: #dbe5f1;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 12px;
}

.page-header,
.symbol-form,
.chart-toolbar,
.symbol-caption,
.periods,
.calculation-actions,
.selection-summary,
.profile-metrics {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 12px;
}

h1 {
  font-size: 1.45rem;
  font-weight: 650;
}

.symbol-form,
.source-label,
.periods,
.calculation-actions,
.selection-summary,
.profile-metrics {
  font-size: 12px;
}

input,
button {
  padding: 5px 8px;
  border: 1px solid #cbd7e7;
  border-radius: 5px;
  background: #fff;
  color: var(--ink);
  font: inherit;
}

input {
  width: 7.4rem;
}

button {
  cursor: pointer;
}

button:disabled {
  opacity: 0.57;
  cursor: default;
}

button:focus-visible,
input:focus-visible {
  outline: 2px solid #4e83c8;
  outline-offset: 2px;
}

button[type='submit'],
.confirm-button {
  border-color: #24436d;
  background: #24436d;
  color: #fff;
}

.pending-label {
  padding: 3px 7px;
  border: 1px solid #ebd4a7;
  border-radius: 4px;
  background: #fff7e6;
  color: #765019;
}

.coverage-notice {
  padding: 8px 13px;
  background: #fff7e6;
  color: #765019;
  font-size: 12px;
}

.coverage-notice p {
  margin: 0;
}

.coverage-notice details {
  margin-top: 4px;
}

.coverage-notice summary {
  cursor: pointer;
}

.query-status {
  color: var(--caption);
  font-size: 12px;
}

.source-label {
  padding: 3px 7px;
  border: 1px solid #c2d3ea;
  border-radius: 4px;
  background: #edf4fd;
  color: #34577f;
}

.profile-panel {
  min-width: 0;
  border: 1px solid var(--rule);
  border-radius: 9px;
  background: #fff;
}

.chart-toolbar {
  padding: 11px 13px;
  border-bottom: 1px solid var(--rule);
  border-radius: 9px 9px 0 0;
  background: #f4f7fc;
}

.symbol-caption {
  color: var(--caption);
  font-size: 12px;
}

.profile-chart-symbol,
.selection-summary strong,
.profile-metrics dd {
  color: var(--ink);
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;
  font-variant-numeric: tabular-nums;
}

.profile-chart-symbol {
  font-size: 17px;
}

.periods {
  gap: 4px;
}

.periods button[aria-pressed='true'],
.tool-button[aria-pressed='true'] {
  border-color: #9cb9e0;
  background: #e7f0fd;
  color: #25456f;
}

.calculation-actions {
  margin-left: auto;
}

.selection-summary,
.profile-metrics {
  padding: 8px 13px;
  border-bottom: 1px solid var(--rule);
  color: var(--caption);
}

.profile-metrics {
  gap: 8px 18px;
}

.profile-metrics > div {
  display: flex;
  gap: 6px;
  align-items: baseline;
}

.profile-metrics dd {
  font-weight: 650;
}

.poc-value {
  color: #8c5313;
}

.poc-value dd {
  color: #8c5313;
}

.error-message {
  padding: 6px 13px;
  background: #fff1ef;
  color: #a13428;
  font-size: 12px;
}
</style>
