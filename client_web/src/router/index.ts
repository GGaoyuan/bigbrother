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
      name: 'recap',
      component: () => import('../views/RecapView.vue'),
    },
    {
      path: '/order_flow',
      name: 'orderFlow',
      component: () => import('../views/OrderFlowView.vue'),
    },
  ],
})

export default router
