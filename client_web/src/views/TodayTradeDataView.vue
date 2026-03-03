<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'

const router = useRouter()

type TabKey = 'limitUp' | 'continuous' | 'broken' | 'firstBoard'

interface TradeItem {
  rank: number
  code: string
  name: string
  price: number
  change: number
  changePercent: number
  turnover: number
  sealTime: string
  boardCount?: number
}

const selectedDate = ref(formatDate(new Date()))
const activeTab = ref<TabKey>('limitUp')

function formatDate(d: Date) {
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
}

// 市场概览 mock
const overview = ref({
  limitUp: 42,
  continuous: 15,
  broken: 8,
  firstBoard: 27,
})

// 涨停板 mock 数据
const limitUpList = ref<TradeItem[]>([
  { rank: 1, code: '600519', name: '贵州茅台', price: 1688.00, change: 153.46, changePercent: 10.00, turnover: 0.52, sealTime: '09:25', boardCount: 2 },
  { rank: 2, code: '000858', name: '五粮液', price: 145.20, change: 13.20, changePercent: 10.00, turnover: 1.23, sealTime: '09:30', boardCount: 1 },
  { rank: 3, code: '002594', name: '比亚迪', price: 258.60, change: 23.51, changePercent: 10.00, turnover: 2.15, sealTime: '09:32', boardCount: 3 },
  { rank: 4, code: '300750', name: '宁德时代', price: 189.50, change: 17.23, changePercent: 10.00, turnover: 1.88, sealTime: '09:35' },
  { rank: 5, code: '601012', name: '隆基绿能', price: 18.92, change: 1.72, changePercent: 10.00, turnover: 3.42, sealTime: '09:41' },
  { rank: 6, code: '000001', name: '平安银行', price: 12.56, change: 1.14, changePercent: 9.99, turnover: 2.01, sealTime: '10:05' },
  { rank: 7, code: '600036', name: '招商银行', price: 36.88, change: 3.35, changePercent: 9.99, turnover: 0.98, sealTime: '10:12' },
  { rank: 8, code: '300059', name: '东方财富', price: 14.52, change: 1.32, changePercent: 10.00, turnover: 4.56, sealTime: '10:25' },
])

// 连板股（复用部分数据并加连板数）
const continuousList = computed(() =>
  limitUpList.value
    .filter((_, i) => i < 5)
    .map((item, i) => ({ ...item, boardCount: (item.boardCount ?? 1) + i }))
)

// 炸板 mock（涨但未封住）
const brokenList = ref<TradeItem[]>([
  { rank: 1, code: '000333', name: '美的集团', price: 68.50, change: 5.20, changePercent: 8.21, turnover: 1.55, sealTime: '-' },
  { rank: 2, code: '601318', name: '中国平安', price: 42.30, change: 2.88, changePercent: 7.30, turnover: 2.11, sealTime: '-' },
  { rank: 3, code: '000651', name: '格力电器', price: 36.88, change: 2.45, changePercent: 7.10, turnover: 1.89, sealTime: '-' },
])

// 首板（当日首板）
const firstBoardList = computed(() =>
  limitUpList.value.filter((item) => (item.boardCount ?? 1) === 1)
)

const tabs = [
  { key: 'limitUp' as TabKey, label: '涨停板' },
  { key: 'continuous' as TabKey, label: '连板股' },
  { key: 'broken' as TabKey, label: '炸板' },
  { key: 'firstBoard' as TabKey, label: '首板' },
]

const currentList = computed(() => {
  switch (activeTab.value) {
    case 'limitUp': return limitUpList.value
    case 'continuous': return continuousList.value
    case 'broken': return brokenList.value
    case 'firstBoard': return firstBoardList.value
    default: return limitUpList.value
  }
})

const showBoardCount = computed(() => activeTab.value === 'continuous' || activeTab.value === 'limitUp')

// ---------- 图表 ----------
const chartRefMarket = ref<HTMLElement | null>(null)
const chartRefTurnover = ref<HTMLElement | null>(null)
const chartRefDistribution = ref<HTMLElement | null>(null)
let chartMarket: echarts.ECharts | null = null
let chartTurnover: echarts.ECharts | null = null
let chartDistribution: echarts.ECharts | null = null

function initCharts() {
  if (!chartRefMarket.value || !chartRefTurnover.value || !chartRefDistribution.value) return

  // 大盘异动 - 上证指数 折线 + 散点标注
  const timeAxis = ['09:30', '09:45', '10:00', '10:15', '10:30', '10:45', '11:00', '11:15', '11:30', '13:00', '14:00', '14:30', '15:00']
  const indexData = [0.38, 0.25, 0.05, -0.89, -0.65, -0.52, -0.48, -0.55, -0.62, -0.70, -0.75, -0.77, -0.77]
  const priceData = [4168, 4162, 4148, 4145.48, 4142, 4140, 4139, 4137, 4135, 4132, 4130, 4150.51, 4150.51]
  const volumeData = [2.1, 2.8, 3.2, 3.89, 4.1, 4.5, 4.8, 5.0, 5.2, 6.0, 6.5, 6.8, 7.0]
  const amountData = [35.2, 46.8, 53.5, 64.45, 68.2, 75.1, 80.2, 83.5, 86.8, 100, 108, 113, 118]

  const scatterPoints: { timeIdx: number; name: string; value: number; type: 'up' | 'down' }[] = [
    { timeIdx: 2, name: '光伏', value: 0.05, type: 'down' },
    { timeIdx: 3, name: '电力物联网', value: -0.89, type: 'down' },
    { timeIdx: 5, name: '火电', value: -0.52, type: 'down' },
    { timeIdx: 7, name: '军工', value: -0.55, type: 'up' },
    { timeIdx: 8, name: '农业种植', value: -0.62, type: 'up' },
    { timeIdx: 10, name: '教育', value: -0.75, type: 'up' },
  ]
  const scatterDown = scatterPoints.filter((p) => p.type === 'down').map((p) => [timeAxis[p.timeIdx], p.value, p.name] as [string, number, string])
  const scatterUp = scatterPoints.filter((p) => p.type === 'up').map((p) => [timeAxis[p.timeIdx], p.value, p.name] as [string, number, string])

  chartMarket = echarts.init(chartRefMarket.value)
  chartMarket.setOption({
    title: { text: `大盘异动 - 上证指数 ${selectedDate.value}`, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: {
      trigger: 'axis',
      formatter: (params: unknown) => {
        const p = Array.isArray(params) ? params[0] : null
        if (!p || p.dataIndex == null) return ''
        const i = p.dataIndex as number
        return `时间: ${timeAxis[i]}<br/>涨幅: ${indexData[i].toFixed(2)}%<br/>价格: ${priceData[i]}<br/>成交量: ${volumeData[i]}亿<br/>成交额: ${amountData[i]}亿`
      },
    },
    grid: { left: '10%', right: '8%', top: '18%', bottom: '15%' },
    xAxis: { type: 'category', data: timeAxis, boundaryGap: false },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}%' }, min: -1.2, max: 0.6, splitLine: { show: true, lineStyle: { type: 'dashed', opacity: 0.3 } } },
    series: [
      { type: 'line', data: indexData, smooth: true, symbol: 'none', lineStyle: { color: '#2196f3', width: 2 }, areaStyle: { color: 'rgba(33, 150, 243, 0.1)' } },
      {
        type: 'scatter',
        data: scatterDown,
        symbol: 'circle',
        symbolSize: 10,
        itemStyle: { color: '#e53935' },
        label: { show: true, formatter: (params: { data: [string, number, string] }) => (params.data && params.data[2]) || '', position: 'top', fontSize: 10 },
      },
      {
        type: 'scatter',
        data: scatterUp,
        symbol: 'circle',
        symbolSize: 10,
        itemStyle: { color: '#43a047' },
        label: { show: true, formatter: (params: { data: [string, number, string] }) => (params.data && params.data[2]) || '', position: 'top', fontSize: 10 },
      },
    ],
  })

  // 两市成交额 - 今 vs 昨 面积图
  const turnoverToday = [0, 3200, 6200, 9200, 11800, 13500, 15461]
  const turnoverYesterday = [0, 3300, 6400, 9600, 12200, 14200, 15927]
  const turnoverTime = ['09:30', '10:30', '11:30', '12:00', '14:00', '14:30', '15:00']
  const turnoverDiff = -466.36
  const turnoverPercent = -2.93
  const turnoverForecast = 29323

  chartTurnover = echarts.init(chartRefTurnover.value)
  chartTurnover.setOption({
    title: {
      text: `两市成交额 ${15461}亿 同比昨日(${turnoverDiff}亿, ${turnoverPercent}%) 预测: ${turnoverForecast}亿`,
      left: 'center',
      textStyle: { fontSize: 12 },
    },
    tooltip: { trigger: 'axis' },
    grid: { left: '10%', right: '8%', top: '22%', bottom: '18%' },
    legend: { data: ['今', '昨'], top: 8, right: 20 },
    xAxis: { type: 'category', data: turnoverTime, boundaryGap: false },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}' }, max: 20000, splitLine: { lineStyle: { opacity: 0.3 } } },
    series: [
      { name: '今', type: 'line', data: turnoverToday, smooth: true, symbol: 'none', lineStyle: { color: '#42a5f5' }, areaStyle: { color: 'rgba(66, 165, 245, 0.35)' } },
      { name: '昨', type: 'line', data: turnoverYesterday, smooth: true, symbol: 'none', lineStyle: { color: '#ef5350' }, areaStyle: { color: 'rgba(239, 83, 80, 0.2)' } },
    ],
  })

  // 涨跌分布 柱状图
  const distCategories = ['跌停', '-10~-8%', '-8~-6%', '-6~-4%', '-4~-2%', '-2~0%', '0~2%', '2~4%', '4~6%', '6~8%', '8~10%', '涨停']
  const distValues = [6, 0, 110, 339, 2814, 815, 137, 604, 59, 30, 40, 35]
  const distColors = distValues.map((_, i) => (i < 6 ? '#43a047' : '#e53935'))

  chartDistribution = echarts.init(chartRefDistribution.value)
  chartDistribution.setOption({
    title: { text: '涨跌分布', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis' },
    grid: { left: '8%', right: '5%', top: '15%', bottom: '12%' },
    xAxis: { type: 'category', data: distCategories, axisLabel: { rotate: 25, fontSize: 10 } },
    yAxis: { type: 'value', max: 3000, splitLine: { lineStyle: { opacity: 0.3 } } },
    series: [{ type: 'bar', data: distValues.map((v, i) => ({ value: v, itemStyle: { color: distColors[i] } })), barWidth: '60%' }],
  })
}

function resizeCharts() {
  chartMarket?.resize()
  chartTurnover?.resize()
  chartDistribution?.resize()
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  chartMarket?.dispose()
  chartTurnover?.dispose()
  chartDistribution?.dispose()
})
</script>

<template>
  <div class="today-trade-page">
    <header class="page-header">
      <h1 class="page-title">今日交易数据</h1>
      <div class="header-meta">
        <label class="date-label">交易日期</label>
        <input v-model="selectedDate" type="date" class="date-input" />
      </div>
    </header>

    <section class="charts-row">
      <div class="chart-box chart-market chart-market-clickable" @click="router.push('/market_anomaly')">
        <div ref="chartRefMarket" class="chart-dom"></div>
      </div>
      <div class="chart-right">
        <div class="chart-box chart-turnover">
          <div ref="chartRefTurnover" class="chart-dom"></div>
        </div>
        <div class="chart-box chart-distribution">
          <div ref="chartRefDistribution" class="chart-dom"></div>
        </div>
      </div>
    </section>

    <section class="overview-cards">
      <div class="card card-up">
        <span class="card-value">{{ overview.limitUp }}</span>
        <span class="card-label">涨停</span>
      </div>
      <div class="card card-continuous">
        <span class="card-value">{{ overview.continuous }}</span>
        <span class="card-label">连板</span>
      </div>
      <div class="card card-broken">
        <span class="card-value">{{ overview.broken }}</span>
        <span class="card-label">炸板</span>
      </div>
      <div class="card card-first">
        <span class="card-value">{{ overview.firstBoard }}</span>
        <span class="card-label">首板</span>
      </div>
    </section>

    <section class="tabs-section">
      <div class="tabs">
        <button
          v-for="t in tabs"
          :key="t.key"
          type="button"
          class="tab"
          :class="{ active: activeTab === t.key }"
          @click="activeTab = t.key"
        >
          {{ t.label }}
        </button>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>代码</th>
              <th>名称</th>
              <th>现价</th>
              <th>涨跌</th>
              <th>涨跌幅</th>
              <th>换手率</th>
              <th v-show="showBoardCount">连板</th>
              <th>封板时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in currentList" :key="row.code">
              <td>{{ row.rank }}</td>
              <td class="code">{{ row.code }}</td>
              <td class="name">{{ row.name }}</td>
              <td>{{ row.price.toFixed(2) }}</td>
              <td class="cell-up">+{{ row.change.toFixed(2) }}</td>
              <td class="cell-up">+{{ row.changePercent.toFixed(2) }}%</td>
              <td>{{ row.turnover.toFixed(2) }}%</td>
              <td v-show="showBoardCount">
                <span v-if="row.boardCount" class="board-badge">{{ row.boardCount }}板</span>
                <span v-else>-</span>
              </td>
              <td>{{ row.sealTime }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <footer class="page-footer">
      <span>数据仅供参考，不构成投资建议</span>
    </footer>
  </div>
</template>

<style scoped>
.today-trade-page {
  min-height: 100vh;
  background: var(--color-background);
  color: var(--color-text);
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-heading);
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-label {
  font-size: 0.9rem;
  color: var(--color-text);
  opacity: 0.9;
}

.date-input {
  padding: 0.4rem 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.95rem;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.chart-box {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-background-soft);
  overflow: hidden;
}

.chart-market {
  min-height: 320px;
}

.chart-market-clickable {
  cursor: pointer;
}

.chart-right {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chart-turnover {
  min-height: 200px;
}

.chart-distribution {
  min-height: 240px;
}

.chart-dom {
  width: 100%;
  height: 300px;
}

.chart-market .chart-dom {
  height: 320px;
}

.chart-turnover .chart-dom {
  height: 200px;
}

.chart-distribution .chart-dom {
  height: 240px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.card {
  padding: 1rem 1.25rem;
  border-radius: 8px;
  text-align: center;
  border: 1px solid var(--color-border);
  background: var(--color-background-soft);
}

.card-value {
  display: block;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.3;
}

.card-label {
  font-size: 0.9rem;
  opacity: 0.85;
}

.card-up .card-value { color: #c62828; }
.card-continuous .card-value { color: #d84315; }
.card-broken .card-value { color: #ef6c00; }
.card-first .card-value { color: #2e7d32; }

.tabs-section {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
  background: var(--color-background-soft);
}

.tabs {
  display: flex;
  background: var(--color-background-mute);
  border-bottom: 1px solid var(--color-border);
}

.tab {
  padding: 0.75rem 1.25rem;
  border: none;
  background: none;
  color: var(--color-text);
  font-size: 0.95rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.tab:hover {
  background: var(--color-border-hover);
}

.tab.active {
  font-weight: 600;
  color: #1565c0;
  border-bottom-color: #1565c0;
  background: var(--color-background);
}

.table-wrap {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.data-table th,
.data-table td {
  padding: 0.6rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  font-weight: 600;
  background: var(--color-background-mute);
  color: var(--color-heading);
}

.data-table tbody tr:hover {
  background: var(--color-border-hover);
}

.data-table .code {
  font-family: ui-monospace, monospace;
  color: #1565c0;
}

.data-table .name {
  font-weight: 500;
}

.cell-up {
  color: #c62828;
  font-weight: 500;
}

.board-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #ffebee;
  color: #c62828;
  font-size: 0.85rem;
}

.page-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.85rem;
  opacity: 0.8;
  text-align: center;
}

@media (max-width: 768px) {
  .charts-row {
    grid-template-columns: 1fr;
  }

  .chart-market .chart-dom {
    height: 280px;
  }

  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .tabs {
    flex-wrap: wrap;
  }

  .tab {
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
  }
}
</style>
