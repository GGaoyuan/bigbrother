import { createWebHistory, createRouter } from 'vue-router'

import HomePage from "./pages/home/HomePage.vue";
import ContentView from "./components/ContentView.vue";

const routes = [
    {
        path: '/',
        name: 'Home',
        component: HomePage
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router