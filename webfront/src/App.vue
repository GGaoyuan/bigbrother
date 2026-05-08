<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <RouterLink to="/" class="title-icon-link" aria-label="首页">
          <img src="/favicon.png" alt="" class="title-icon" />
        </RouterLink>
      </div>

      <nav class="sidebar-nav">
        <RouterLink to="/" class="nav-item">行情</RouterLink>
        <RouterLink to="/market_sentiment" class="nav-item">市场情绪</RouterLink>
        <RouterLink to="/today" class="nav-item">今日大盘</RouterLink>
        <RouterLink to="/market_anomaly" class="nav-item">大盘异动</RouterLink>
        <RouterLink to="/recap" class="nav-item" exact-active-class="nav-item--active">市场面</RouterLink>
        <RouterLink to="/recap/indicators" class="nav-item">指标面</RouterLink>
        <RouterLink to="/recap/macro" class="nav-item">宏观经济</RouterLink>
        <RouterLink to="/recap/dividend_yield" class="nav-item">股息率测算</RouterLink>
        <RouterLink to="/recap/heatmap" class="nav-item">热力图（复盘）</RouterLink>
        <RouterLink to="/recap/sector" class="nav-item">板块分析</RouterLink>
        <RouterLink to="/heatmap/theme" class="nav-item">题材热力图</RouterLink>
        <RouterLink to="/heatmap/industry" class="nav-item">行业热力图</RouterLink>
        <RouterLink to="/heatmap/change" class="nav-item">涨跌热力图</RouterLink>
        <RouterLink to="/timeline" class="nav-item">时间轴</RouterLink>
        <RouterLink to="/theme_lib" class="nav-item">题材库</RouterLink>
        <RouterLink to="/order_flow" class="nav-item">订单流</RouterLink>
        <RouterLink to="/intraday_flow" class="nav-item">分时资金流</RouterLink>
        <RouterLink to="/popularity/top-list" class="nav-item">龙虎榜统计</RouterLink>
        <RouterLink to="/popularity/hot-rank" class="nav-item">热榜</RouterLink>
      </nav>
    </aside>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 220px;
  background: var(--color-background);
  border-right: 1px solid var(--color-border);
  box-shadow: 1px 0 3px rgba(0, 0, 0, 0.06);
  overflow-y: auto;
  z-index: 100;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.title-icon-link {
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-icon {
  width: 40px;
  height: 40px;
  object-fit: contain;
  border-radius: 8px;
}

.sidebar-nav {
  padding: 0.5rem 0;
}

.nav-item {
  display: block;
  padding: 0.75rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--color-text);
  text-decoration: none;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}

.nav-item:hover {
  color: var(--color-heading);
  background: var(--color-background-mute);
}

.nav-item.router-link-active,
.nav-item--active {
  color: #1565c0;
  background: var(--color-background-soft);
  border-left-color: #1565c0;
}

.main-content {
  flex: 1;
  margin-left: 220px;
  min-height: 100vh;
  padding: 1rem;
}
</style>
