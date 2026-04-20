import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'marketQuotes',
      component: () => import('../views/MarketQuotesView.vue'),
    },
    {
      path: '/today',
      name: 'todayMarket',
      component: () => import('../views/TodayTradeDataView.vue'),
    },
    {
      path: '/market_anomaly',
      name: 'marketAnomaly',
      component: () => import('../views/MarketAnomalyView.vue'),
    },
    {
      path: '/recap',
      name: 'recapMarket',
      component: () => import('../views/RecapMarketView.vue'),
    },
    {
      path: '/recap/indicators',
      name: 'recapIndicators',
      component: () => import('../views/RecapIndicatorsView.vue'),
    },
    {
      path: '/recap/macro',
      name: 'recapMacro',
      component: () => import('../views/RecapMacroView.vue'),
    },
    {
      path: '/recap/dividend_yield',
      name: 'recapDividendYield',
      component: () => import('../views/RecapDividendYieldView.vue'),
    },
    {
      path: '/recap/heatmap',
      name: 'recapHeatmap',
      component: () => import('../views/RecapHeatmapView.vue'),
    },
    {
      path: '/recap/sector',
      name: 'recapSector',
      component: () => import('../views/RecapSectorView.vue'),
      redirect: { name: 'recapSectorTab1' },
      children: [
        { path: 'tab1', name: 'recapSectorTab1', component: () => import('../views/sector/SectorTab1View.vue') },
        { path: 'tab2', name: 'recapSectorTab2', component: () => import('../views/sector/SectorTab2View.vue') },
        { path: 'tab3', name: 'recapSectorTab3', component: () => import('../views/sector/SectorTab3View.vue') },
      ],
    },
    {
      path: '/heatmap',
      name: 'heatmap',
      redirect: { name: 'heatmapTheme' },
    },
    {
      path: '/heatmap/theme',
      name: 'heatmapTheme',
      component: () => import('../views/heatmap/HeatmapThemeView.vue'),
    },
    {
      path: '/heatmap/industry',
      name: 'heatmapIndustry',
      component: () => import('../views/heatmap/HeatmapIndustryView.vue'),
    },
    {
      path: '/heatmap/change',
      name: 'heatmapChange',
      component: () => import('../views/heatmap/HeatmapChangeView.vue'),
    },
    {
      path: '/timeline',
      name: 'timeline',
      component: () => import('../views/RecapThemesView.vue'),
    },
    {
      path: '/theme_lib',
      name: 'themeLibrary',
      component: () => import('../views/ThemeLibraryView.vue'),
    },
    {
      path: '/order_flow',
      name: 'orderFlow',
      component: () => import('../views/OrderFlowView.vue'),
    },
    {
      path: '/intraday_flow',
      name: 'intradayFlow',
      component: () => import('../views/IntradayFlowView.vue'),
    },
  ],
})

export default router
