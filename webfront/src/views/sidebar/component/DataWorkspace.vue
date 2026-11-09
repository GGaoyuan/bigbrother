<script setup lang="ts">
import { computed, ref } from 'vue'
import dataConfig from './data.json'

const categories = computed(() => dataConfig.dataCategories)
const activeCategoryId = ref<string | null>(null)
const search = ref('')
const selectedMetricId = ref<string>(dataConfig.metrics[0]?.id ?? '')
const selected = ref<(typeof dataConfig.dataCategories)[number]['series'][number] | null>(null)
const addedSeriesKeys = ref<string[]>([])
const activeCategory = computed(
  () => categories.value.find((category) => category.id === activeCategoryId.value) ?? null,
)
const visibleSeries = computed(() =>
  (activeCategory.value?.series ?? []).filter((series) =>
    `${series.label}${series.code}${series.categoryLabel}`
      .toLowerCase()
      .includes(search.value.toLowerCase()),
  ),
)

function toggleCategory(categoryId: string) {
  activeCategoryId.value = activeCategoryId.value === categoryId ? null : categoryId
  selected.value = null
  search.value = ''
}

function addDataset() {
  if (!selected.value) return
  const seriesKey = `${selected.value.id}:${selectedMetricId.value}`

  if (!addedSeriesKeys.value.includes(seriesKey)) {
    addedSeriesKeys.value.push(seriesKey)
  }
}
</script>

<template>
  <section class="data-browser workspace-pane">
    <div class="section-title">
      <span>{{ dataConfig.sidebar.marketDataLabel }}</span>
      <span class="section-hint">{{ dataConfig.sidebar.marketDataHint }}</span>
    </div>
    <nav class="group-list" :aria-label="dataConfig.sidebar.dataCategoriesLabel">
      <div v-for="category in categories" :key="category.id" class="group-entry">
        <button
          class="group-item"
          :class="{ selected: activeCategoryId === category.id }"
          :aria-expanded="activeCategoryId === category.id"
          @click="toggleCategory(category.id)"
        >
          <span class="group-icon">{{ category.icon }}</span>
          {{ category.label }}
          <span class="chevron" :class="{ expanded: activeCategoryId === category.id }">›</span>
        </button>
        <div v-if="activeCategoryId === category.id" class="dataset-panel">
          <div class="panel-heading">
            <div>
              <strong>{{ category.label }}</strong>
              <small>{{ dataConfig.sidebar.selectSeriesHint }}</small>
            </div>
            <span class="count">{{ visibleSeries.length }}</span>
          </div>
          <label class="search-box"
            ><span>⌕</span><input v-model="search" :placeholder="dataConfig.sidebar.searchPlaceholder"
          /></label>
          <div class="rows-label">
            {{ dataConfig.sidebar.seriesNameLabel }}
            <span>{{ dataConfig.sidebar.seriesCodeLabel }}</span>
          </div>
          <div class="dataset-list">
            <button
              v-for="series in visibleSeries"
              :key="series.id"
              class="dataset-row"
              :class="{ chosen: selected?.id === series.id }"
              @click="selected = series"
            >
              <span class="row-dot"></span
              ><span class="row-info"
                ><strong>{{ series.label }}</strong
                ><small>{{ series.categoryLabel }}</small></span
              ><code>{{ series.code }}</code>
            </button>
            <div v-if="!visibleSeries.length" class="empty-results">
              {{ dataConfig.sidebar.noResultsLabel }}
            </div>
          </div>
          <div class="metric-area">
            <div class="subhead">
              {{ dataConfig.sidebar.metricsLabel }}
              <span>{{ dataConfig.sidebar.metricHint }}</span>
            </div>
            <div class="metric-chips">
              <button
                v-for="metric in dataConfig.metrics"
                :key="metric.id"
                :class="{ active: selectedMetricId === metric.id }"
                @click="selectedMetricId = metric.id"
              >
                {{ metric.label }}
              </button>
            </div>
          </div>
          <button class="add-button" :disabled="!selected" @click="addDataset">
            <span>＋</span> {{ dataConfig.sidebar.addToChartLabel }}
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
