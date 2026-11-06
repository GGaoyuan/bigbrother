<template>
  <div class="hot-rank-container">
    <div class="top-bar">
      <button class="refresh-btn" @click="fetchData" :disabled="loading">刷新</button>
      <span v-if="loading" class="status-text">加载中...</span>
      <span v-if="error" class="status-text error">{{ error }}</span>
    </div>

    <table class="data-table" v-if="items.length > 0">
      <thead>
        <tr>
          <th>排名</th>
          <th>代码</th>
          <th>名称</th>
          <th>最新价</th>
          <th>涨跌幅</th>
          <th>热度</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.code">
          <td>{{ item.rank }}</td>
          <td>{{ item.code }}</td>
          <td>{{ item.name }}</td>
          <td>{{ item.price.toFixed(2) }}</td>
          <td :class="item.change_pct >= 0 ? 'up' : 'down'">
            {{ item.change_pct >= 0 ? '+' : '' }}{{ item.change_pct.toFixed(2) }}%
          </td>
          <td>{{ item.hot_value }}</td>
        </tr>
      </tbody>
    </table>

    <div v-else-if="!loading" class="empty-tip">暂无数据</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const BASE_URL = 'http://127.0.0.1:8000/api/v1'

interface HotRankItem {
  rank: number
  code: string
  name: string
  price: number
  change_pct: number
  hot_value: number
}

const items = ref<HotRankItem[]>([])
const loading = ref(false)
const error = ref('')

async function fetchData() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${BASE_URL}/popularity/hot-rank`)
    if (!res.ok) throw new Error(`请求失败: ${res.status}`)
    const json = await res.json()
    items.value = json.data ?? []
  } catch (e: any) {
    error.value = e.message ?? '请求失败'
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.hot-rank-container {
  padding: 1rem;
}

.top-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.refresh-btn {
  padding: 0.4rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.9rem;
  cursor: pointer;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-text {
  font-size: 0.875rem;
  color: var(--color-text);
}

.status-text.error {
  color: #e53935;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table th,
.data-table td {
  padding: 0.6rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  font-weight: 600;
  color: var(--color-heading);
  background: var(--color-background-soft);
}

.data-table tr:hover td {
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
