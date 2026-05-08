<template>
  <div class="top-list-container">
    <!-- 标题 -->
    <h1 class="page-title">龙虎榜统计</h1>

    <!-- 当前日期时间 -->
    <div class="current-datetime">{{ currentDatetime }}</div>

    <!-- 日期选择器 -->
    <div class="date-pickers">
      <label>
        起始日期
        <input type="date" v-model="startDate" @change="onDateChange" />
      </label>
      <span class="date-sep">—</span>
      <label>
        结束日期
        <input type="date" v-model="endDate" @change="onDateChange" />
      </label>
    </div>

    <div v-if="loading" class="status-text">加载中...</div>
    <div v-if="error" class="status-text error">{{ error }}</div>

    <!-- 单日模式：完整列表 -->
    <div v-if="mode === 'single' && singleRecords.length > 0" class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="col in singleCols" :key="col.key" @click="sortBy(col.key)" class="sortable-th">
              {{ col.label }}
              <span class="sort-icon">{{ sortKey === col.key ? (sortAsc ? '▲' : '▼') : '⇅' }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in sortedSingleRecords" :key="row.code + row.date">
            <td>{{ row.code }}</td>
            <td>{{ row.name }}</td>
            <td>{{ row.date }}</td>
            <td>{{ row.interpretation }}</td>
            <td>{{ row.close.toFixed(2) }}</td>
            <td :class="row.change_pct >= 0 ? 'up' : 'down'">{{ fmt(row.change_pct, 2) }}%</td>
            <td>{{ fmt(row.turnover_rate, 2) }}%</td>
            <td :class="row.net_buy >= 0 ? 'up' : 'down'">{{ fmtWan(row.net_buy) }}</td>
            <td>{{ fmtWan(row.buy_amount) }}</td>
            <td>{{ fmtWan(row.sell_amount) }}</td>
            <td>{{ fmtWan(row.lhb_turnover) }}</td>
            <td>{{ fmtWan(row.market_turnover) }}</td>
            <td>{{ fmt(row.net_buy_ratio, 2) }}%</td>
            <td>{{ fmt(row.turnover_ratio, 2) }}%</td>
            <td>{{ fmtYi(row.float_market_cap) }}</td>
            <td>{{ row.reason }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 范围模式：分组列表 -->
    <div v-if="mode === 'range' && groups.length > 0" class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="sortBy('count')" class="sortable-th">
              上榜次数 <span class="sort-icon">{{ sortKey === 'count' ? (sortAsc ? '▲' : '▼') : '⇅' }}</span>
            </th>
            <th @click="sortBy('code')" class="sortable-th">
              代码 <span class="sort-icon">{{ sortKey === 'code' ? (sortAsc ? '▲' : '▼') : '⇅' }}</span>
            </th>
            <th @click="sortBy('name')" class="sortable-th">
              名称 <span class="sort-icon">{{ sortKey === 'name' ? (sortAsc ? '▲' : '▼') : '⇅' }}</span>
            </th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="group in sortedGroups" :key="group.code">
            <tr class="group-row" @click="toggleGroup(group.code)">
              <td>{{ group.count }}</td>
              <td>{{ group.code }}</td>
              <td>{{ group.name }}</td>
              <td class="expand-icon">{{ expandedGroups.has(group.code) ? '▲' : '▼' }}</td>
            </tr>
            <tr v-if="expandedGroups.has(group.code)" class="sub-row">
              <td colspan="4" class="sub-cell">
                <table class="sub-table">
                  <thead>
                    <tr>
                      <th>上榜日期</th>
                      <th>解读</th>
                      <th>收盘价</th>
                      <th>涨跌幅</th>
                      <th>换手率</th>
                      <th>净买额(万)</th>
                      <th>买入额(万)</th>
                      <th>卖出额(万)</th>
                      <th>龙虎榜成交(万)</th>
                      <th>市场总成交(万)</th>
                      <th>净买额占比</th>
                      <th>成交额占比</th>
                      <th>流通市值(亿)</th>
                      <th>上榜原因</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="r in group.records" :key="r.date">
                      <td>{{ r.date }}</td>
                      <td>{{ r.interpretation }}</td>
                      <td>{{ r.close.toFixed(2) }}</td>
                      <td :class="r.change_pct >= 0 ? 'up' : 'down'">{{ fmt(r.change_pct, 2) }}%</td>
                      <td>{{ fmt(r.turnover_rate, 2) }}%</td>
                      <td :class="r.net_buy >= 0 ? 'up' : 'down'">{{ fmtWan(r.net_buy) }}</td>
                      <td>{{ fmtWan(r.buy_amount) }}</td>
                      <td>{{ fmtWan(r.sell_amount) }}</td>
                      <td>{{ fmtWan(r.lhb_turnover) }}</td>
                      <td>{{ fmtWan(r.market_turnover) }}</td>
                      <td>{{ fmt(r.net_buy_ratio, 2) }}%</td>
                      <td>{{ fmt(r.turnover_ratio, 2) }}%</td>
                      <td>{{ fmtYi(r.float_market_cap) }}</td>
                      <td>{{ r.reason }}</td>
                    </tr>
                  </tbody>
                </table>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div v-else-if="!loading && mode && (singleRecords.length === 0 && groups.length === 0)" class="empty-tip">
      暂无数据
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const BASE_URL = 'http://127.0.0.1:8000/api/v1'
const WEEK_DAYS = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']

interface TopListRecord {
  code: string
  name: string
  date: string
  interpretation: string
  close: number
  change_pct: number
  turnover_rate: number
  net_buy: number
  buy_amount: number
  sell_amount: number
  lhb_turnover: number
  market_turnover: number
  net_buy_ratio: number
  turnover_ratio: number
  float_market_cap: number
  reason: string
}

interface TopListGroup {
  code: string
  name: string
  count: number
  records: TopListRecord[]
}

function toLocalDateString(d: Date) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function toApiDate(s: string) {
  return s.replace(/-/g, '')
}

function fmt(val: number, decimals = 2) {
  const sign = val >= 0 ? '+' : ''
  return `${sign}${val.toFixed(decimals)}`
}

function fmtWan(val: number) {
  return (val / 10000).toFixed(0) + ''
}

function fmtYi(val: number) {
  return (val / 1e8).toFixed(2)
}

// 当前时间
const currentDatetime = ref('')
let timer: ReturnType<typeof setInterval>

function updateDatetime() {
  const now = new Date()
  const y = now.getFullYear()
  const mo = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  const h = String(now.getHours()).padStart(2, '0')
  const mi = String(now.getMinutes()).padStart(2, '0')
  const s = String(now.getSeconds()).padStart(2, '0')
  currentDatetime.value = `${y}-${mo}-${d} ${h}:${mi}:${s} ${WEEK_DAYS[now.getDay()]}`
}

const today = toLocalDateString(new Date())
const startDate = ref(today)
const endDate = ref(today)

const loading = ref(false)
const error = ref('')
const mode = ref<'single' | 'range' | null>(null)
const singleRecords = ref<TopListRecord[]>([])
const groups = ref<TopListGroup[]>([])
const expandedGroups = ref<Set<string>>(new Set())

const sortKey = ref('')
const sortAsc = ref(true)

const singleCols = [
  { key: 'code', label: '代码' },
  { key: 'name', label: '名称' },
  { key: 'date', label: '上榜日期' },
  { key: 'interpretation', label: '解读' },
  { key: 'close', label: '收盘价' },
  { key: 'change_pct', label: '涨跌幅' },
  { key: 'turnover_rate', label: '换手率' },
  { key: 'net_buy', label: '净买额(万)' },
  { key: 'buy_amount', label: '买入额(万)' },
  { key: 'sell_amount', label: '卖出额(万)' },
  { key: 'lhb_turnover', label: '龙虎榜成交(万)' },
  { key: 'market_turnover', label: '市场总成交(万)' },
  { key: 'net_buy_ratio', label: '净买额占比' },
  { key: 'turnover_ratio', label: '成交额占比' },
  { key: 'float_market_cap', label: '流通市值' },
  { key: 'reason', label: '上榜原因' },
]

function sortBy(key: string) {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = true
  }
}

const sortedSingleRecords = computed(() => {
  if (!sortKey.value) return singleRecords.value
  return [...singleRecords.value].sort((a, b) => {
    const av = (a as any)[sortKey.value]
    const bv = (b as any)[sortKey.value]
    if (typeof av === 'number') return sortAsc.value ? av - bv : bv - av
    return sortAsc.value ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av))
  })
})

const sortedGroups = computed(() => {
  if (!sortKey.value) return groups.value
  return [...groups.value].sort((a, b) => {
    const av = (a as any)[sortKey.value]
    const bv = (b as any)[sortKey.value]
    if (typeof av === 'number') return sortAsc.value ? av - bv : bv - av
    return sortAsc.value ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av))
  })
})

function toggleGroup(code: string) {
  if (expandedGroups.value.has(code)) {
    expandedGroups.value.delete(code)
  } else {
    expandedGroups.value.add(code)
  }
  expandedGroups.value = new Set(expandedGroups.value)
}

async function fetchData() {
  loading.value = true
  error.value = ''
  sortKey.value = ''
  expandedGroups.value = new Set()
  try {
    const url = `${BASE_URL}/popularity/top-list?start_date=${toApiDate(startDate.value)}&end_date=${toApiDate(endDate.value)}`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`请求失败: ${res.status}`)
    const json = await res.json()
    const data = json.data
    mode.value = data.mode
    if (data.mode === 'single') {
      singleRecords.value = data.records ?? []
      groups.value = []
    } else {
      groups.value = data.groups ?? []
      singleRecords.value = []
    }
  } catch (e: any) {
    error.value = e.message ?? '请求失败'
  } finally {
    loading.value = false
  }
}

function onDateChange() {
  fetchData()
}

onMounted(() => {
  updateDatetime()
  timer = setInterval(updateDatetime, 1000)
  fetchData()
})

onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.top-list-container {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--color-heading);
}

.current-datetime {
  font-size: 0.95rem;
  color: var(--color-text);
  margin-bottom: 1rem;
  opacity: 0.75;
}

.date-pickers {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.date-pickers label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
  color: var(--color-text);
}

.date-pickers input[type='date'] {
  padding: 0.35rem 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.9rem;
}

.date-sep {
  color: var(--color-text);
  opacity: 0.5;
}

.status-text {
  font-size: 0.875rem;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.status-text.error {
  color: #e53935;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
  overflow-y: auto;
  max-height: calc(100vh - 220px);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
  white-space: nowrap;
}

.data-table th,
.data-table td {
  padding: 0.5rem 0.65rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  font-weight: 600;
  color: var(--color-heading);
  background: var(--color-background-soft);
  position: sticky;
  top: 0;
  z-index: 1;
}

.sortable-th {
  cursor: pointer;
  user-select: none;
}

.sortable-th:hover {
  background: var(--color-background-mute);
}

.sort-icon {
  font-size: 0.7rem;
  margin-left: 0.25rem;
  opacity: 0.6;
}

.data-table tr:hover td {
  background: var(--color-background-mute);
}

.group-row {
  cursor: pointer;
}

.group-row:hover td {
  background: var(--color-background-mute);
}

.expand-icon {
  text-align: center;
  font-size: 0.75rem;
  opacity: 0.6;
}

.sub-row td {
  padding: 0;
  background: var(--color-background-soft);
}

.sub-cell {
  padding: 0.5rem 1rem !important;
}

.sub-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
}

.sub-table th,
.sub-table td {
  padding: 0.4rem 0.6rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.sub-table th {
  font-weight: 600;
  color: var(--color-heading);
  background: var(--color-background-mute);
}

.up {
  color: #e53935;
}

.down {
  color: #43a047;
}

.empty-tip {
  text-align: center;
  padding: 3rem;
  color: var(--color-text);
  opacity: 0.5;
}
</style>
