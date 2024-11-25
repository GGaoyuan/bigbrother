import { createWebHistory, createRouter } from 'vue-router'

import VerticalMenu from './components/VerticalMenu.vue'
import ContentView from "./components/ContentView.vue";
import HomePage from "./pages/home/HomePage.vue";

const routes = [
    { path: '/', component: HomePage },
    { path: '/login', component: LoginView }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})
export default router
