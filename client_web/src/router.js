import { createWebHistory, createRouter } from 'vue-router'

import HomePage from "./pages/home/HomePage.vue";
import CandleView from "./pages/home/views/candle/CandleView.vue";
import HeatmapView from "./pages/home/views/heatmap/HeatmapView.vue";

const routes = [
    {
        path: '/',
        component: HomePage,
        children:[
            {
                path: '/candle',
                component: CandleView,
            },
            {
                path: '/heatmap',
                component: HeatmapView,
            },
        ]
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router