import { createWebHistory, createRouter } from 'vue-router'

import HomePage from "./pages/home/HomePage.vue";
import CandleView from "./pages/home/views/candle/CandleView.vue";
import HeatmapView from "./pages/home/views/heatmap/HeatmapView.vue";

import HeatmapPage from "./pages/HeatmapPage.vue";
import SectorPage from "./pages/sectors/SectorPage.vue";

const routes = [
    {
        path: '/',
        redirect: '/home'
    },
    {
        path: '/home',
        component: HomePage
    },
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