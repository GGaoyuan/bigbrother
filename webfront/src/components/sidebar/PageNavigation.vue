<script setup lang="ts">
import { RouterLink } from 'vue-router'

const pageLinks: [string, string][] = [
  ['行情', '/'],
  ['市场情绪', '/market_sentiment'],
  ['今日大盘', '/today'],
  ['大盘异动', '/market_anomaly'],
  ['市场面', '/recap'],
  ['指标面', '/recap/indicators'],
  ['宏观经济', '/recap/macro'],
  ['股息率测算', '/recap/dividend_yield'],
  ['热力图（复盘）', '/recap/heatmap'],
  ['板块分析', '/recap/sector'],
  ['题材热力图', '/heatmap/theme'],
  ['行业热力图', '/heatmap/industry'],
  ['涨跌热力图', '/heatmap/change'],
  ['时间轴', '/timeline'],
  ['题材库', '/theme_lib'],
  ['订单流', '/order_flow'],
  ['分时资金流', '/intraday_flow'],
  ['龙虎榜统计', '/popularity/top-list'],
  ['热榜', '/popularity/hot-rank'],
]
</script>

<template>
  <section class="pages-section workspace-pane">
    <div class="section-title pages-title">
      <span>页面导航</span><span class="section-hint">{{ pageLinks.length }} PAGES</span>
    </div>
    <nav class="sidebar-nav" aria-label="页面导航">
      <RouterLink v-for="[label, path] in pageLinks" :key="path" :to="path" class="nav-item">{{
        label
      }}</RouterLink>
    </nav>
  </section>
</template>

<style>
.pages-section {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px 13px 8px;
}
.pages-title {
  padding: 0 5px 9px;
}
.sidebar-nav {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px 4px;
  padding: 0;
}
.nav-item {
  display: block;
  overflow: hidden;
  padding: 5px 7px !important;
  border: 0;
  border-radius: 5px;
  color: #788496 !important;
  font-size: 10px;
  line-height: 1.4;
  text-decoration: none;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.nav-item:hover {
  background: #f5f7fa !important;
  color: #3478f6 !important;
}
.nav-item.router-link-active {
  background: #eef4ff !important;
  color: #3478f6 !important;
}
</style>
