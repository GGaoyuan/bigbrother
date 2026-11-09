<script setup lang="ts">
import { computed, ref } from 'vue'
import type { DataCategory, DataChartSelection, DataChartType } from '../../../api/workspace'

const props = defineProps<{
  category: DataCategory
}>()

const emit = defineEmits<{
  addToChart: [selection: DataChartSelection]
}>()

const search = ref('')
const series = computed(() => props.category.series ?? [])
const chartTypes = computed<DataChartType[]>(() => props.category.chartTypes ?? ['line'])
const selectedSeriesId = ref(series.value[0]?.id ?? '')
const selectedMetricId = ref(props.category.metrics[0]?.id ?? '')
const selectedChartType = ref<DataChartType>(props.category.chartTypes?.[0] ?? 'line')
const selectedChartName = ref('图表1')
const color = ref('#c31649')
const visibleSeries = computed(() => {
  const keyword = search.value.trim().toLowerCase()

  if (!keyword) {
    return series.value
  }

  return series.value.filter((item) => `${item.name}${item.code}`.toLowerCase().includes(keyword))
})
const selectedSeries = computed(
  () => series.value.find((item) => item.id === selectedSeriesId.value) ?? null,
)

function chartTypeLabel(chartType: DataChartType) {
  if (chartType === 'line') {
    return '曲线'
  }

  if (chartType === 'bar') {
    return '柱状'
  }

  return 'K线'
}

function addToChart() {
  if (!selectedSeries.value || !selectedMetricId.value) {
    return
  }

  emit('addToChart', {
    categoryId: props.category.id,
    seriesId: selectedSeries.value.id,
    metricId: selectedMetricId.value,
    chartName: selectedChartName.value,
    chartType: selectedChartType.value,
    color: color.value,
  })
}
</script>

<template>
  <div class="series-category-content">
    <label class="series-search">
      <span aria-hidden="true">⌕</span>
      <input
        v-model="search"
        type="search"
        placeholder="搜索指数名称或代码"
        aria-label="搜索指数名称或代码"
      />
    </label>

    <div class="series-list" role="listbox" aria-label="指数列表">
      <button
        v-for="item in visibleSeries"
        :key="item.id"
        class="series-row"
        :class="{ 'is-selected': item.id === selectedSeriesId }"
        type="button"
        role="option"
        :aria-selected="item.id === selectedSeriesId"
        @click="selectedSeriesId = item.id"
      >
        <span>{{ item.name }}</span>
        <code>{{ item.code }}</code>
      </button>
      <p v-if="visibleSeries.length === 0" class="empty-series">没有匹配的指数</p>
    </div>

    <div v-if="selectedSeries" class="selected-series">
      <strong>{{ selectedSeries.name }}</strong>
      <code>{{ selectedSeries.code }}</code>
      <button type="button" aria-label="清除所选指数" @click="selectedSeriesId = ''">
        清除
      </button>
    </div>

    <section class="metrics-section" aria-labelledby="series-metrics-title">
      <h3 id="series-metrics-title">指标</h3>
      <div class="metric-options">
        <button
          v-for="metric in category.metrics"
          :key="metric.id"
          type="button"
          :class="{ 'is-active': selectedMetricId === metric.id }"
          :aria-pressed="selectedMetricId === metric.id"
          @click="selectedMetricId = metric.id"
        >
          {{ metric.name }}
        </button>
      </div>
    </section>

    <section class="chart-options" aria-labelledby="chart-options-title">
      <h3 id="chart-options-title">添加到图表</h3>
      <label class="chart-target">
        <span class="visually-hidden">目标图表</span>
        <select v-model="selectedChartName">
          <option>图表1</option>
        </select>
      </label>
      <div class="chart-controls">
        <label class="color-picker" :style="{ '--series-color': color }">
          <span class="visually-hidden">曲线颜色</span>
          <input v-model="color" type="color" />
        </label>
        <div class="chart-type-options" aria-label="图表类型">
          <button
          v-for="chartType in chartTypes"
            :key="chartType"
            type="button"
            :class="{ 'is-active': selectedChartType === chartType }"
            :aria-pressed="selectedChartType === chartType"
            @click="selectedChartType = chartType"
          >
            {{ chartTypeLabel(chartType) }}
          </button>
        </div>
        <button
          class="add-button"
          type="button"
          :disabled="!selectedSeries || !selectedMetricId"
          @click="addToChart"
        >
          添加
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.series-category-content {
  padding: 12px 14px 14px;
}

.series-search {
  display: flex;
  min-height: 44px;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  border: 1px solid #d4deec;
  border-radius: 8px;
  color: #738199;
  background: #fff;
}

.series-search span {
  font-size: 22px;
  line-height: 1;
}

.series-search input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: #29364a;
  font: inherit;
  font-size: 13px;
}

.series-search input::placeholder {
  color: #8792a2;
}

.series-list {
  max-height: 196px;
  overflow-y: auto;
  margin-top: 8px;
  border: 1px solid #dce4ef;
  border-radius: 8px;
  background: #fff;
}

.series-row {
  display: flex;
  width: 100%;
  min-height: 42px;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 0 12px;
  border: 0;
  border-bottom: 1px solid #e1e7ef;
  background: #fff;
  color: #303b4d;
  font: inherit;
  font-size: 13px;
  text-align: left;
  cursor: pointer;
}

.series-row:last-child {
  border-bottom: 0;
}

.series-row:hover {
  background: #f6f9ff;
}

.series-row.is-selected {
  background: #edf4ff;
  color: #174cc6;
}

.series-row code,
.selected-series code {
  color: #718098;
  font: inherit;
  font-size: 12px;
  white-space: nowrap;
}

.empty-series {
  margin: 0;
  padding: 18px 12px;
  color: #8792a2;
  font-size: 12px;
  text-align: center;
}

.selected-series {
  display: flex;
  min-height: 46px;
  align-items: center;
  gap: 10px;
  padding: 0 10px;
  border: 1px solid #dce4ef;
  border-top: 0;
  border-radius: 0 0 8px 8px;
  background: #fbfcfe;
  color: #303b4d;
  font-size: 12px;
}

.selected-series strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-series button {
  margin-left: auto;
  padding: 4px 0 4px 8px;
  border: 0;
  background: transparent;
  color: #718098;
  font: inherit;
  cursor: pointer;
}

.selected-series button:hover {
  color: #2458cb;
}

.metrics-section {
  padding: 15px 0 14px;
}

.metrics-section h3,
.chart-options h3 {
  margin: 0 0 11px;
  color: #738098;
  font-size: 13px;
  font-weight: 650;
}

.metric-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.metric-options button,
.chart-type-options button {
  min-height: 36px;
  padding: 0 12px;
  border: 1px solid #d7e0ec;
  border-radius: 8px;
  background: #fff;
  color: #354154;
  font: inherit;
  font-size: 12px;
  cursor: pointer;
}

.metric-options button.is-active,
.chart-type-options button.is-active {
  border-color: #2455e6;
  background: #2455e6;
  color: #fff;
}

.chart-options {
  margin: 0 -14px -14px;
  padding: 14px;
  border-top: 1px solid #dce4ef;
  background: #fbfcfe;
}

.chart-target {
  display: block;
}

.chart-target select {
  width: 100%;
  min-height: 42px;
  padding: 0 12px;
  border: 1px solid #d7e0ec;
  border-radius: 8px;
  appearance: none;
  background: #fff;
  color: #354154;
  font: inherit;
  font-size: 13px;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 11px;
}

.color-picker {
  display: grid;
  width: 28px;
  height: 28px;
  flex: 0 0 auto;
  place-items: center;
  overflow: hidden;
  border: 1px solid #e2e7ef;
  border-radius: 50%;
  background: var(--series-color);
}

.color-picker input {
  width: 38px;
  height: 38px;
  padding: 0;
  border: 0;
  opacity: 0;
  cursor: pointer;
}

.chart-type-options {
  display: flex;
  flex: 1;
  gap: 6px;
}

.chart-type-options button {
  min-height: 34px;
  flex: 1;
  padding: 0 7px;
}

.add-button {
  min-width: 66px;
  min-height: 38px;
  padding: 0 14px;
  border: 1px solid #2455e6;
  border-radius: 8px;
  background: #2455e6;
  color: #fff;
  font: inherit;
  font-size: 13px;
  cursor: pointer;
}

.add-button:disabled {
  border-color: #b9c7dc;
  background: #b9c7dc;
  cursor: not-allowed;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}
</style>
