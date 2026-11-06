import './assets/main.css'

import { createApp } from 'vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)

async function startApp() {
  await router.isReady()
  app.mount('#app')
}

void startApp()
