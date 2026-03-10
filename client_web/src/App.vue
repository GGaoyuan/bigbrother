<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

const route = useRoute()
const showTodaySubTabs = computed(() => route.path === '/' || route.path === '/market_anomaly')
const showRecapSubTabs = computed(() => route.path.startsWith('/recap'))
const showSectorSubTabs = computed(() => route.path.startsWith('/recap/sector'))

const isTodayDataActive = computed(() => route.path === '/' || route.path === '/market_anomaly')
const isRecapActive = computed(() => route.path.startsWith('/recap'))
const isTimelineActive = computed(() => route.path === '/timeline')
const isThemeLibActive = computed(() => route.path === '/theme_lib')
const isOrderFlowActive = computed(() => route.path === '/order_flow')
</script>

<template>
  <header class="top-tabs">
    <div class="tabs-wrap">
      <nav class="tabs-nav">
        <RouterLink to="/" class="title-icon-link" aria-label="首页">
          <img src="/favicon.png" alt="" class="title-icon" />
        </RouterLink>
        <RouterLink to="/" class="tab" :class="{ 'tab--active': isTodayDataActive }">今日数据</RouterLink>
        <RouterLink to="/recap" class="tab" :class="{ 'tab--active': isRecapActive }">复盘</RouterLink>
        <RouterLink to="/timeline" class="tab" :class="{ 'tab--active': isTimelineActive }">时间轴</RouterLink>
        <RouterLink to="/theme_lib" class="tab" :class="{ 'tab--active': isThemeLibActive }">题材库</RouterLink>
        <RouterLink to="/order_flow" class="tab" :class="{ 'tab--active': isOrderFlowActive }">订单流</RouterLink>
      </nav>
      <nav v-show="showTodaySubTabs" class="sub-tabs-nav">
        <RouterLink to="/" class="sub-tab" active-class="sub-tab--active" exact-active-class="sub-tab--active">今日大盘</RouterLink>
        <RouterLink to="/market_anomaly" class="sub-tab" active-class="sub-tab--active">大盘异动</RouterLink>
      </nav>
      <nav v-show="showRecapSubTabs" class="sub-tabs-nav">
        <RouterLink to="/recap" class="sub-tab" active-class="sub-tab--active" exact-active-class="sub-tab--active">市场面</RouterLink>
        <RouterLink to="/recap/indicators" class="sub-tab" active-class="sub-tab--active">指标面</RouterLink>
        <RouterLink to="/recap/macro" class="sub-tab" active-class="sub-tab--active">宏观经济</RouterLink>
        <RouterLink to="/recap/dividend_yield" class="sub-tab" active-class="sub-tab--active">股息率测算</RouterLink>
        <RouterLink to="/recap/heatmap" class="sub-tab" active-class="sub-tab--active">热力图</RouterLink>
        <RouterLink to="/recap/sector" class="sub-tab" active-class="sub-tab--active">板块分析</RouterLink>
      </nav>
      <nav v-show="showSectorSubTabs" class="sub-tabs-nav">
        <RouterLink to="/recap/sector/tab1" class="sub-tab" active-class="sub-tab--active">热力图</RouterLink>
        <RouterLink to="/recap/sector/tab2" class="sub-tab" active-class="sub-tab--active">Tab2</RouterLink>
        <RouterLink to="/recap/sector/tab3" class="sub-tab" active-class="sub-tab--active">Tab3</RouterLink>
      </nav>
    </div>
  </header>

  <main class="main-content" :class="{ 'main-content--with-sub-tabs': (showTodaySubTabs || showRecapSubTabs) && !showSectorSubTabs, 'main-content--with-sector-tabs': showSectorSubTabs }">
    <RouterView />
  </main>
</template>

<style scoped>
.top-tabs {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.tabs-wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.tabs-nav {
  display: flex;
  height: 52px;
  align-items: center;
  gap: 0.5rem;
}

.sub-tabs-nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0 0 0 40px;
  margin-top: -1px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--color-border);
}

.sub-tab {
  padding: 0.35rem 0.75rem;
  font-size: 0.9rem;
  color: var(--color-text);
  text-decoration: none;
  border-radius: 4px;
  transition: color 0.2s, background 0.2s;
}

.sub-tab:hover {
  color: var(--color-heading);
  background: var(--color-background-mute);
}

.sub-tab--active {
  font-weight: 600;
  color: #1565c0;
  background: var(--color-background-soft);
}

.title-icon-link {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  margin-right: 0.25rem;
}

.title-icon {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 6px;
}

.tab {
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  color: var(--color-text);
  text-decoration: none;
  border-bottom: 3px solid transparent;
  margin-bottom: -1px;
  transition: color 0.2s, border-color 0.2s;
}

.tab:hover {
  color: var(--color-heading);
}

.tab--active {
  color: #1565c0;
  border-bottom-color: #1565c0;
}

.main-content {
  flex: 1;
  padding-top: 52px;
  min-height: 100vh;
}

.main-content--with-sub-tabs {
  padding-top: 92px;
}

.main-content--with-sector-tabs {
  padding-top: 132px;
}
</style>
