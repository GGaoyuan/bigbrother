import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'marketQuotes',
      component: () => import('../views/pages/market/MarketQuotesView.vue'),
    },
    {
      path: '/market_sentiment',
      name: 'marketSentiment',
      component: () => import('../views/pages/market/MarketSentimentView.vue'),
    },
    {
      path: '/today',
      name: 'todayMarket',
      component: () => import('../views/pages/market/TodayTradeDataView.vue'),
    },
    {
      path: '/market_anomaly',
      name: 'marketAnomaly',
      component: () => import('../views/pages/market/MarketAnomalyView.vue'),
    },
    {
      path: '/recap',
      name: 'recapMarket',
      component: () => import('../views/pages/recap/RecapMarketView.vue'),
    },
    {
      path: '/recap/indicators',
      name: 'recapIndicators',
      component: () => import('../views/pages/recap/RecapIndicatorsView.vue'),
    },
    {
      path: '/recap/macro',
      name: 'recapMacro',
      component: () => import('../views/pages/recap/RecapMacroView.vue'),
    },
    {
      path: '/recap/dividend_yield',
      name: 'recapDividendYield',
      component: () => import('../views/pages/recap/RecapDividendYieldView.vue'),
    },
    {
      path: '/recap/heatmap',
      name: 'recapHeatmap',
      component: () => import('../views/pages/recap/RecapHeatmapView.vue'),
    },
    {
      path: '/recap/sector',
      name: 'recapSector',
      component: () => import('../views/pages/recap/RecapSectorView.vue'),
      redirect: { name: 'recapSectorTab1' },
      children: [
        {
          path: 'tab1',
          name: 'recapSectorTab1',
          component: () => import('../views/pages/recap/sector/SectorTab1View.vue'),
        },
        {
          path: 'tab2',
          name: 'recapSectorTab2',
          component: () => import('../views/pages/recap/sector/SectorTab2View.vue'),
        },
        {
          path: 'tab3',
          name: 'recapSectorTab3',
          component: () => import('../views/pages/recap/sector/SectorTab3View.vue'),
        },
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
      component: () => import('../views/pages/heatmap/HeatmapThemeView.vue'),
    },
    {
      path: '/heatmap/industry',
      name: 'heatmapIndustry',
      component: () => import('../views/pages/heatmap/HeatmapIndustryView.vue'),
    },
    {
      path: '/heatmap/change',
      name: 'heatmapChange',
      component: () => import('../views/pages/heatmap/HeatmapChangeView.vue'),
    },
    {
      path: '/timeline',
      name: 'timeline',
      component: () => import('../views/pages/themes/RecapThemesView.vue'),
    },
    {
      path: '/theme_lib',
      name: 'themeLibrary',
      component: () => import('../views/pages/themes/ThemeLibraryView.vue'),
    },
    {
      path: '/order_flow',
      name: 'orderFlow',
      component: () => import('../views/pages/flows/OrderFlowView.vue'),
    },
    {
      path: '/intraday_flow',
      name: 'intradayFlow',
      component: () => import('../views/pages/flows/IntradayFlowView.vue'),
    },
    {
      path: '/popularity/top-list',
      name: 'topList',
      component: () => import('../views/pages/popularity/TopListView.vue'),
    },
    {
      path: '/popularity/hot-rank',
      name: 'hotRank',
      component: () => import('../views/pages/popularity/HotRankView.vue'),
    },
  ],
})

export default router
