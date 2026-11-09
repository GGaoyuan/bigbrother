import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { loadConfig } from './common/config/config'

const app = createApp(App)

app.use(createPinia())
app.use(router)

async function startApp() {
  try {
    await loadConfig()
    await router.isReady()
    app.mount('#app')
  } catch (error) {
    console.error('Failed to load application config', error)
    const mountElement = document.querySelector('#app')

    if (mountElement) {
      mountElement.textContent = '应用配置加载失败，请检查网络后刷新页面。'
    }
  }
}

void startApp()
