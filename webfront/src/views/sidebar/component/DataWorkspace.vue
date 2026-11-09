<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchWorkspaceData } from '../../../api/workspace'
import type { DataCategory, DataChartSelection } from '../../../api/workspace'
import MetricDataCategory from './MetricDataCategory.vue'
import SeriesDataCategory from './SeriesDataCategory.vue'

const emit = defineEmits<{
  addToChart: [selection: DataChartSelection]
}>()

const categories = ref<DataCategory[]>([])
const activeCategoryId = ref<string | null>(null)
const loading = ref(false)
const loadError = ref('')
const lastSelection = ref<DataChartSelection | null>(null)
const lastSelectionSummary = computed(() => {
  if (!lastSelection.value) {
    return ''
  }

  const category = categories.value.find((item) => item.id === lastSelection.value?.categoryId)
  const series = category?.series?.find((item) => item.id === lastSelection.value?.seriesId)
  const metric = category?.metrics.find((item) => item.id === lastSelection.value?.metricId)

  if (!category || !metric) {
    return ''
  }

  return `${series?.name ?? category.name} · ${metric.name} · ${lastSelection.value.chartName}`
})

async function loadCategories() {
  loading.value = true
  loadError.value = ''

  try {
    const response = await fetchWorkspaceData()
    categories.value = response.dataCategories
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '数据加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

function toggleCategory(categoryId: string) {
  activeCategoryId.value = activeCategoryId.value === categoryId ? null : categoryId
  lastSelection.value = null
}

function addToChart(selection: DataChartSelection) {
  lastSelection.value = selection
  emit('addToChart', selection)
}

onMounted(() => {
  void loadCategories()
})
</script>

<template>
  <section class="data-browser workspace-pane">
    <div class="section-title">
      <span>数据源</span>
      <span class="section-hint">MARKET DATA</span>
    </div>

    <div v-if="loading" class="request-state" role="status">
      正在加载数据目录…
    </div>

    <div v-else-if="loadError" class="request-state request-error" role="alert">
      <span>{{ loadError }}</span>
      <button type="button" @click="loadCategories">重试</button>
    </div>

    <nav v-else class="group-list" aria-label="数据类别">
      <div v-for="category in categories" :key="category.id" class="group-entry">
        <button
          class="group-item"
          :class="{ selected: activeCategoryId === category.id }"
          type="button"
          :aria-expanded="activeCategoryId === category.id"
          @click="toggleCategory(category.id)"
        >
          <span>{{ category.name }}</span>
          <span class="chevron" :class="{ expanded: activeCategoryId === category.id }">
            ›
          </span>
        </button>

        <SeriesDataCategory
          v-if="activeCategoryId === category.id && category.series"
          :category="category"
          @add-to-chart="addToChart"
        />
        <MetricDataCategory
          v-else-if="activeCategoryId === category.id"
          :category="category"
          @add-to-chart="addToChart"
        />
      </div>
    </nav>

    <p v-if="lastSelectionSummary" class="selection-summary" role="status">
      已选择：{{ lastSelectionSummary }}
    </p>
  </section>
</template>

<style scoped>
.data-browser {
  display: flex;
  min-height: 0;
  flex: 1;
  flex-direction: column;
  overflow-y: auto;
  padding: 16px 13px 13px;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 5px 10px;
  color: #344256;
  font-size: 13px;
  font-weight: 700;
}

.section-hint {
  color: #a5afbc;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.09em;
}

.group-list {
  display: grid;
  gap: 8px;
}

.group-entry {
  min-width: 0;
  overflow: hidden;
  border: 1px solid #d9e2ef;
  border-radius: 10px;
  background: #fff;
}

.group-item {
  display: flex;
  width: 100%;
  min-height: 48px;
  align-items: center;
  gap: 8px;
  padding: 8px 11px;
  border: 0;
  background: #fff;
  color: #263244;
  font: inherit;
  font-size: 13px;
  font-weight: 650;
  text-align: left;
  cursor: pointer;
}

.group-item.selected {
  border-bottom: 1px solid #d9e2ef;
  background: #edf4ff;
}

.chevron {
  margin-left: auto;
  color: #77859a;
  font-size: 19px;
  font-weight: 400;
  line-height: 1;
}

.chevron.expanded {
  transform: rotate(90deg);
}

.request-state {
  display: grid;
  gap: 10px;
  padding: 18px 12px;
  border: 1px solid #dce4ef;
  border-radius: 9px;
  background: #fff;
  color: #768398;
  font-size: 12px;
  text-align: center;
}

.request-error {
  color: #a33c4b;
}

.request-state button {
  min-height: 34px;
  border: 1px solid #2455e6;
  border-radius: 7px;
  background: #2455e6;
  color: #fff;
  font: inherit;
  cursor: pointer;
}

.selection-summary {
  margin: 10px 2px 0;
  padding: 9px 10px;
  border: 1px solid #dce4ef;
  border-radius: 8px;
  background: #f8faff;
  color: #53627a;
  font-size: 11px;
}
</style>
