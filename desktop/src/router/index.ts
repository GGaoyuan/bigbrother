import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import Users from '@/views/Users.vue'
import Settings from '@/views/Settings.vue'
import VolumeProfile from '@/views/VolumeProfile.vue'
import MarketCap from '@/views/MarketCap.vue'
import VolumeShare from '@/views/VolumeShare.vue'
import SectorFlow from '@/views/SectorFlow.vue'
import SectorIntradayFlow from '@/views/SectorIntradayFlow.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { title: 'Dashboard' },
  },
  {
    path: '/users',
    name: 'users',
    component: Users,
    meta: { title: 'Users' },
  },
  {
    path: '/market-cap',
    name: 'market-cap',
    component: MarketCap,
    meta: { title: 'A股总市值' },
  },
  {
    path: '/volume-share',
    name: 'volume-share',
    component: VolumeShare,
    meta: { title: '成交量占比' },
  },
  {
    path: '/sector-flow',
    name: 'sector-flow',
    component: SectorFlow,
    meta: { title: '板块资金流' },
  },
  {
    path: '/sector-intraday',
    name: 'sector-intraday',
    component: SectorIntradayFlow,
    meta: { title: '日内资金流向' },
  },
  {
    path: '/volume-profile',
    name: 'volume-profile',
    component: VolumeProfile,
    meta: { title: 'Volume Profile' },
  },
  {
    path: '/settings',
    name: 'settings',
    component: Settings,
    meta: { title: 'Settings' },
  },
]

export const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
