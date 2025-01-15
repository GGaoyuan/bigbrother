import { createWebHistory, createRouter } from 'vue-router'

import HomePage from "./pages/home/HomePage.vue";
import CandleView from "./pages/home/views/candle/CandleView.vue";
import HeatmapView from "./pages/home/views/heatmap/HeatmapView.vue";

import HeatmapPage from "./pages/HeatmapPage.vue";
import SectorPage from "./pages/sectors/SectorPage.vue";
import ZDTPage from "./pages/zdt/ZDTPage.vue";

const routes = [
    {
        path: '/',
        redirect: '/home'
    },
    {
        path: '/home',
        component: HomePage
    },
    {
        //涨跌停榜单
        path: '/zdt',
        component: ZDTPage
    }
    // {
    //     path: '/heatmap',
    //     component: HeatmapPage
    // },
    // {
    //     path: '/sector',
    //     component: SectorPage
    // },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router