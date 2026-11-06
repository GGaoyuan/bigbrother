<script setup lang="ts">
import { computed, ref } from 'vue'

type Dataset = {
  name: string;
  code: string;
  category: string;
}

const groups = [
  'A股个股',
  'A股指数',
  'A股指数估值',
  '融资融券',
]
const activeGroup = ref<string | null>(null)
const search = ref('')
const selectedMetric = ref('收盘价')
const selected = ref<Dataset | null>(null)
const added = ref<(Dataset & {
  metric: string;
})[]>([])
const metrics = [
  '收盘价',
  '开盘价',
  '最高价',
  '最低价',
  '成交量',
  '成交额',
  '涨跌幅',
]
const datasets: Record<string, Dataset[]> = {
  A股个股: [
    { name: '贵州茅台', code: '600519.SH', category: '白酒' },
    { name: '宁德时代', code: '300750.SZ', category: '电池' },
    { name: '中国平安', code: '601318.SH', category: '保险' },
    { name: '比亚迪', code: '002594.SZ', category: '汽车' },
  ],
  A股指数: [
    { name: '上证指数', code: '000001.SH', category: '上交所' },
    { name: '深证成指', code: '399001.SZ', category: '深交所' },
    { name: '沪深300', code: '000300.SH', category: '宽基指数' },
    { name: '创业板指', code: '399006.SZ', category: '深交所' },
  ],
  A股指数估值: [
    { name: '沪深300 PE-TTM', code: '000300.SH', category: '市盈率' },
    { name: '上证指数 PE-TTM', code: '000001.SH', category: '市盈率' },
    { name: '中证500 PB', code: '000905.SH', category: '市净率' },
  ],
  融资融券: [
    { name: '两市融资余额', code: 'FIN.MARGIN', category: '融资余额' },
    { name: '沪市融资余额', code: 'SH.MARGIN', category: '上交所' },
    { name: '深市融资余额', code: 'SZ.MARGIN', category: '深交所' },
  ],
}
const visibleDatasets = computed(() =>
  (datasets[activeGroup.value ?? ''] ?? []).filter((row) =>
    `${row.name}${row.code}${row.category}`.toLowerCase().includes(search.value.toLowerCase()),
  ),
)

function toggleGroup(group: string) {
  activeGroup.value = activeGroup.value === group ? null : group
  selected.value = null
  search.value = ''
}

function addDataset() {
  if (!selected.value) return
  if (
    !added.value.some(
      (item) =>
        item.code === selected.value?.code &&
        item.name === selected.value?.name &&
        item.metric === selectedMetric.value,
    )
  ) {
    added.value.push({ ...selected.value, metric: selectedMetric.value })
  }
}
</script>

<template>
  <section class="data-browser workspace-pane">
    <div class="section-title">
      <span>数据源</span><span class="section-hint">MARKET DATA</span>
    </div>
    <nav class="group-list" aria-label="数据类别">
      <div v-for="group in groups" :key="group" class="group-entry">
        <button
          class="group-item"
          :class="{ selected: activeGroup === group }"
          :aria-expanded="activeGroup === group"
          @click="toggleGroup(group)"
        >
          <span class="group-icon">{{
            group === '融资融券'
              ? '↗'
              : group.includes('估值')
                ? '◷'
                : group.includes('指数')
                  ? '▥'
                  : '◉'
          }}</span
          >{{ group }}<span class="chevron" :class="{ expanded: activeGroup === group }">›</span>
        </button>
        <div v-if="activeGroup === group" class="dataset-panel">
          <div class="panel-heading">
            <div>
              <strong>{{ group }}</strong
              ><small>选择数据系列并添加到图表</small>
            </div>
            <span class="count">{{ visibleDatasets.length }}</span>
          </div>
          <label class="search-box"
            ><span>⌕</span><input v-model="search" :placeholder="`搜索${group}…`"
          /></label>
          <div class="rows-label">名称 <span>代码</span></div>
          <div class="dataset-list">
            <button
              v-for="row in visibleDatasets"
              :key="row.name"
              class="dataset-row"
              :class="{ chosen: selected?.name === row.name }"
              @click="selected = row"
            >
              <span class="row-dot"></span
              ><span class="row-info"
                ><strong>{{ row.name }}</strong
                ><small>{{ row.category }}</small></span
              ><code>{{ row.code }}</code>
            </button>
            <div v-if="!visibleDatasets.length" class="empty-results">没有匹配的数据</div>
          </div>
          <div class="metric-area">
            <div class="subhead">指标 <span>选择一个指标</span></div>
            <div class="metric-chips">
              <button
                v-for="metric in metrics"
                :key="metric"
                :class="{ active: selectedMetric === metric }"
                @click="selectedMetric = metric"
              >
                {{ metric }}
              </button>
            </div>
          </div>
          <button class="add-button" :disabled="!selected" @click="addDataset">
            <span>＋</span> 添加到图表
          </button>
        </div>
      </div>
    </nav>
  </section>
</template>

<style>
.data-browser {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px 13px 13px;
}
.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 5px 9px;
  color: #344256;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.section-hint {
  color: #a5afbc;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.09em;
}
.group-list {
  display: grid;
  gap: 3px;
}
.group-entry {
  min-width: 0;
}
.group-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  min-height: 35px;
  padding: 0 9px;
  text-align: left;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  color: #586679;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}
.group-icon {
  width: 18px;
  text-align: center;
  color: #98a5b5;
  font-size: 14px;
}
.group-item .chevron {
  margin-left: auto;
  color: #aeb8c5;
  font-size: 17px;
}
.group-item .chevron.expanded {
  transform: rotate(90deg);
}
.group-item:hover {
  background: #f7f9fc;
}
.group-item.selected {
  color: #286bdd;
  border-color: #e3edff;
  background: #f2f6ff;
  font-weight: 650;
}
.group-item.selected .group-icon {
  color: #3478f6;
}
.dataset-panel {
  margin: 4px 0 7px 26px;
  padding: 10px;
  border: 1px solid #e7edf5;
  border-radius: 7px;
  background: #fbfcfe;
}
.panel-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 11px;
}
.panel-heading strong {
  display: block;
  color: #27364a;
  font-size: 12px;
  font-weight: 650;
}
.panel-heading small {
  display: block;
  margin-top: 2px;
  color: #9aa5b2;
  font-size: 10px;
}
.count {
  min-width: 20px;
  padding: 1px 6px;
  border-radius: 9px;
  background: #f2f5f9;
  color: #768396;
  text-align: center;
  font-size: 10px;
}
.search-box {
  display: flex;
  align-items: center;
  height: 31px;
  gap: 7px;
  padding: 0 8px;
  border: 1px solid #e8edf3;
  border-radius: 5px;
  color: #9aa5b2;
}
.search-box input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  color: #334155;
  background: transparent;
  font-size: 10px;
}
.rows-label {
  display: flex;
  justify-content: space-between;
  padding: 10px 1px 5px;
  color: #a5aeba;
  font-size: 9px;
}
.dataset-list {
  max-height: 166px;
  overflow-y: auto;
}
.dataset-row {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 8px;
  padding: 7px 5px;
  border: 0;
  border-radius: 5px;
  text-align: left;
  background: transparent;
  cursor: pointer;
}
.dataset-row:hover {
  background: #f7f9fc;
}
.dataset-row.chosen {
  background: #f0f5ff;
}
.row-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #74a1fa;
}
.row-info {
  flex: 1;
  min-width: 0;
}
.row-info strong {
  display: block;
  overflow: hidden;
  color: #435166;
  font-size: 10px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.row-info small {
  display: block;
  color: #a0aab7;
  font-size: 9px;
}
.dataset-row code {
  color: #9aa5b2;
  font-size: 9px;
}
.empty-results {
  padding: 15px 0;
  color: #98a3b2;
  text-align: center;
  font-size: 10px;
}
.metric-area {
  margin-top: 9px;
  padding-top: 9px;
  border-top: 1px solid #f0f2f5;
}
.subhead {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #536176;
  font-size: 10px;
  font-weight: 650;
}
.subhead span {
  color: #a0aab7;
  font-weight: 400;
}
.metric-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 7px;
}
.metric-chips button {
  padding: 3px 7px;
  border: 1px solid #e9edf2;
  border-radius: 4px;
  background: #fff;
  color: #778396;
  font-size: 9px;
  cursor: pointer;
}
.metric-chips button.active {
  border-color: #cbdcff;
  background: #f2f6ff;
  color: #3478f6;
}
.add-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  width: 100%;
  height: 30px;
  margin-top: 11px;
  border: 0;
  border-radius: 5px;
  background: #3478f6;
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
}
.add-button:disabled {
  background: #e9eef6;
  color: #aab4c2;
  cursor: not-allowed;
}
</style>
