<script setup lang="ts">
import { computed, ref } from 'vue'
import FootprintChart from './FootprintChart.vue'
import { buildFootprint, createDemoTrades, formatPrice, formatTime } from './footprint'

const code = ref('600519')
const displayedCode = ref(code.value)
const selectedStart = ref<number | null>(null)
const details = ref<HTMLElement | null>(null)
const data = computed(() => buildFootprint(createDemoTrades(displayedCode.value)))
const selectedPeriod = computed(() =>
  data.value.periods.find((period) => period.start === selectedStart.value),
)

const formatter = new Intl.NumberFormat('zh-CN', {
  maximumFractionDigits: 0,
  signDisplay: 'exceptZero',
})

const sides = {
  buy: '主动买',
  sell: '主动卖',
  neutral: '中性',
}

function query() {
  displayedCode.value = code.value
  selectedStart.value = null
}
</script>

<template>
  <section class="order-flow">
    <div class="page-toolbar">
      <h1>订单流</h1>
      <form class="symbol-form" @submit.prevent="query">
        <label for="stock-code">股票代码</label>
        <input
          id="stock-code"
          v-model.trim="code"
          name="stock-code"
          inputmode="numeric"
          pattern="[0-9]{6}"
          title="请输入 6 位股票代码"
          placeholder="6 位股票代码"
          required
        />
        <button type="submit">查询</button>
      </form>
      <span class="demo-label">模拟数据</span>
      <p class="summary">
        主动买卖成交额差 <strong>{{ formatter.format(data.amountDelta) }} 元</strong>
      </p>
      <button
        v-if="selectedPeriod"
        type="button"
        class="details-button"
        @click="details?.scrollIntoView()"
      >
        查看 {{ formatTime(selectedPeriod.start) }} 分笔
      </button>
    </div>

    <FootprintChart
      :code="displayedCode"
      :data="data"
      :selected-start="selectedStart"
      @select="selectedStart = $event"
    />

    <div v-if="selectedPeriod" ref="details" class="table-wrap">
      <table>
        <caption>{{ displayedCode }} · {{ formatTime(selectedPeriod.start) }} 模拟分笔成交</caption>
        <thead>
          <tr>
            <th scope="col">时间</th>
            <th scope="col">价格（元）</th>
            <th scope="col">成交量（手）</th>
            <th scope="col">成交额（元）</th>
            <th scope="col">方向</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(trade, index) in selectedPeriod.trades" :key="index">
            <td>{{ formatTime(trade.seconds, true) }}</td>
            <td>{{ formatPrice(trade.priceCents) }}</td>
            <td>{{ trade.lots }}</td>
            <td>{{ (trade.priceCents * trade.lots).toLocaleString('zh-CN') }}</td>
            <td>{{ sides[trade.side] }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.order-flow {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 12px;
  min-width: 0;
}

.page-toolbar,
.symbol-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.page-toolbar {
  column-gap: 14px;
}

h1 {
  margin-right: 3px;
  font-size: 1.45rem;
  font-weight: 650;
}

.symbol-form,
.summary,
.demo-label,
.details-button {
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

input:focus-visible,
button:focus-visible {
  outline: 2px solid #3f79dc;
  outline-offset: 1px;
}

input {
  width: 7.4rem;
}

button {
  cursor: pointer;
}

button[type='submit'] {
  border-color: #24436d;
  background: #24436d;
  color: #fff;
}

.demo-label {
  padding: 3px 7px;
  border: 1px solid #ebd4a7;
  border-radius: 4px;
  background: #fff7e6;
  color: #765019;
}

.summary {
  margin-left: auto;
  color: #52637c;
  font-variant-numeric: tabular-nums;
}

.summary strong {
  color: var(--ink);
  font-weight: 650;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid #dbe3ef;
  border-radius: 7px;
  background: #fff;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
  text-align: right;
  white-space: nowrap;
}

caption,
th,
td {
  padding: 7px 10px;
  border-bottom: 1px solid #e9edf2;
}

caption {
  font-weight: 600;
}

caption,
th:first-child,
td:first-child {
  text-align: left;
}
</style>
