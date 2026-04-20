<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

const route = useRoute()
const showTodaySubTabs = computed(() => route.path === '/today' || route.path === '/market_anomaly')
const showRecapSubTabs = computed(() => route.path.startsWith('/recap'))
const showSectorSubTabs = computed(() => route.path.startsWith('/recap/sector'))
const showHeatmapSubTabs = computed(() => route.path.startsWith('/heatmap'))

const isMarketQuotesActive = computed(() => route.path === '/')
const isTodayDataActive = computed(() => route.path === '/today' || route.path === '/market_anomaly')
const isRecapActive = computed(() => route.path.startsWith('/recap'))
const isHeatmapActive = computed(() => route.path.startsWith('/heatmap'))
const isTimelineActive = computed(() => route.path === '/timeline')
const isThemeLibActive = computed(() => route.path === '/theme_lib')
const isOrderFlowActive = computed(() => route.path === '/order_flow')
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
        <RouterLink to="/" class="nav-item" :class="{ 'nav-item--active': isMarketQuotesActive }">
          行情
        </RouterLink>

        <div class="nav-group">
          <RouterLink to="/today" class="nav-item" :class="{ 'nav-item--active': isTodayDataActive }">
            今日数据
          </RouterLink>
          <nav v-show="showTodaySubTabs" class="sub-nav">
            <RouterLink to="/today" class="sub-nav-item" active-class="sub-nav-item--active" exact-active-class="sub-nav-item--active">今日大盘</RouterLink>
            <RouterLink to="/market_anomaly" class="sub-nav-item" active-class="sub-nav-item--active">大盘异动</RouterLink>
          </nav>
        </div>

        <div class="nav-group">
          <RouterLink to="/recap" class="nav-item" :class="{ 'nav-item--active': isRecapActive }">
            复盘
          </RouterLink>
          <nav v-show="showRecapSubTabs" class="sub-nav">
            <RouterLink to="/recap" class="sub-nav-item" active-class="sub-nav-item--active" exact-active-class="sub-nav-item--active">市场面</RouterLink>
            <RouterLink to="/recap/indicators" class="sub-nav-item" active-class="sub-nav-item--active">指标面</RouterLink>
            <RouterLink to="/recap/macro" class="sub-nav-item" active-class="sub-nav-item--active">宏观经济</RouterLink>
            <RouterLink to="/recap/dividend_yield" class="sub-nav-item" active-class="sub-nav-item--active">股息率测算</RouterLink>
            <RouterLink to="/recap/heatmap" class="sub-nav-item" active-class="sub-nav-item--active">热力图</RouterLink>
            <RouterLink to="/recap/sector" class="sub-nav-item" active-class="sub-nav-item--active">板块分析</RouterLink>
          </nav>
          <nav v-show="showSectorSubTabs" class="sub-nav sub-nav--nested">
            <RouterLink to="/recap/sector/tab1" class="sub-nav-item" active-class="sub-nav-item--active">热力图</RouterLink>
            <RouterLink to="/recap/sector/tab2" class="sub-nav-item" active-class="sub-nav-item--active">Tab2</RouterLink>
            <RouterLink to="/recap/sector/tab3" class="sub-nav-item" active-class="sub-nav-item--active">Tab3</RouterLink>
          </nav>
        </div>

        <div class="nav-group">
          <RouterLink to="/heatmap" class="nav-item" :class="{ 'nav-item--active': isHeatmapActive }">
            热力图
          </RouterLink>
          <nav v-show="showHeatmapSubTabs" class="sub-nav">
            <RouterLink to="/heatmap/theme" class="sub-nav-item" active-class="sub-nav-item--active">题材热力图</RouterLink>
            <RouterLink to="/heatmap/industry" class="sub-nav-item" active-class="sub-nav-item--active">行业热力图</RouterLink>
            <RouterLink to="/heatmap/change" class="sub-nav-item" active-class="sub-nav-item--active">涨跌热力图</RouterLink>
          </nav>
        </div>

        <RouterLink to="/timeline" class="nav-item" :class="{ 'nav-item--active': isTimelineActive }">
          时间轴
        </RouterLink>
        <RouterLink to="/theme_lib" class="nav-item" :class="{ 'nav-item--active': isThemeLibActive }">
          题材库
        </RouterLink>
        <RouterLink to="/order_flow" class="nav-item" :class="{ 'nav-item--active': isOrderFlowActive }">
          订单流
        </RouterLink>
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

.nav-group {
  margin-bottom: 0.25rem;
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

.nav-item--active {
  color: #1565c0;
  background: var(--color-background-soft);
  border-left-color: #1565c0;
}

.sub-nav {
  padding: 0.25rem 0;
  background: var(--color-background-mute);
}

.sub-nav--nested {
  background: var(--color-background-soft);
}

.sub-nav-item {
  display: block;
  padding: 0.5rem 1.25rem 0.5rem 2.5rem;
  font-size: 0.875rem;
  color: var(--color-text);
  text-decoration: none;
  transition: all 0.2s;
}

.sub-nav-item:hover {
  color: var(--color-heading);
  background: rgba(0, 0, 0, 0.03);
}

.sub-nav-item--active {
  font-weight: 600;
  color: #1565c0;
}

.sub-nav--nested .sub-nav-item {
  padding-left: 3.5rem;
}

.main-content {
  flex: 1;
  margin-left: 220px;
  min-height: 100vh;
  padding: 1rem;
}
</style>
