import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
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
  ],
})

export default router
