import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'marketQuotes',
      component: () => import('../views/workspace/pages/market/MarketQuotesView.vue'),
    },
    {
      path: '/market_sentiment',
      name: 'marketSentiment',
      component: () => import('../views/workspace/pages/market/MarketSentimentView.vue'),
    },
    {
      path: '/today',
      name: 'todayMarket',
      component: () => import('../views/workspace/pages/market/TodayTradeDataView.vue'),
    },
    {
      path: '/market_anomaly',
      name: 'marketAnomaly',
      component: () => import('../views/workspace/pages/market/MarketAnomalyView.vue'),
    },
    {
      path: '/recap',
      name: 'recapMarket',
      component: () => import('../views/workspace/pages/recap/RecapMarketView.vue'),
    },
    {
      path: '/recap/indicators',
      name: 'recapIndicators',
      component: () => import('../views/workspace/pages/recap/RecapIndicatorsView.vue'),
    },
    {
      path: '/recap/macro',
      name: 'recapMacro',
      component: () => import('../views/workspace/pages/recap/RecapMacroView.vue'),
    },
    {
      path: '/recap/dividend_yield',
      name: 'recapDividendYield',
      component: () => import('../views/workspace/pages/recap/RecapDividendYieldView.vue'),
    },
    {
      path: '/recap/heatmap',
      name: 'recapHeatmap',
      component: () => import('../views/workspace/pages/recap/RecapHeatmapView.vue'),
    },
    {
      path: '/recap/sector',
      name: 'recapSector',
      component: () => import('../views/workspace/pages/recap/RecapSectorView.vue'),
      redirect: { name: 'recapSectorTab1' },
      children: [
        {
          path: 'tab1',
          name: 'recapSectorTab1',
          component: () => import('../views/workspace/pages/recap/sector/SectorTab1View.vue'),
        },
        {
          path: 'tab2',
          name: 'recapSectorTab2',
          component: () => import('../views/workspace/pages/recap/sector/SectorTab2View.vue'),
        },
        {
          path: 'tab3',
          name: 'recapSectorTab3',
          component: () => import('../views/workspace/pages/recap/sector/SectorTab3View.vue'),
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
      component: () => import('../views/workspace/pages/heatmap/HeatmapThemeView.vue'),
    },
    {
      path: '/heatmap/industry',
      name: 'heatmapIndustry',
      component: () => import('../views/workspace/pages/heatmap/HeatmapIndustryView.vue'),
    },
    {
      path: '/heatmap/change',
      name: 'heatmapChange',
      component: () => import('../views/workspace/pages/heatmap/HeatmapChangeView.vue'),
    },
    {
      path: '/timeline',
      name: 'timeline',
      component: () => import('../views/workspace/pages/themes/RecapThemesView.vue'),
    },
    {
      path: '/theme_lib',
      name: 'themeLibrary',
      component: () => import('../views/workspace/pages/themes/ThemeLibraryView.vue'),
    },
    {
      path: '/order_flow',
      name: 'orderFlow',
      component: () => import('../views/workspace/pages/flows/OrderFlowView.vue'),
    },
    {
      path: '/intraday_flow',
      name: 'intradayFlow',
      component: () => import('../views/workspace/pages/flows/IntradayFlowView.vue'),
    },
    {
      path: '/popularity/top-list',
      name: 'topList',
      component: () => import('../views/workspace/pages/popularity/TopListView.vue'),
    },
    {
      path: '/popularity/hot-rank',
      name: 'hotRank',
      component: () => import('../views/workspace/pages/popularity/HotRankView.vue'),
    },
  ],
})

export default router
