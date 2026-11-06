import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { PAGE_ID, WORKSPACE_ID } from './common/config'
import { PAGE_ROUTE_NAMES } from './common/config/pageRouteNames'
import { useAppConfigStore } from './common/appConfigStore'
import { useContainerQueueStore } from './common/containerQueue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

async function startApp() {
  const appConfigStore = useAppConfigStore(pinia)
  await appConfigStore.loadAppConfig()

  const containerQueue = useContainerQueueStore(pinia)
  const config = appConfigStore.config!
  const dataWorkspace = config.workspaces.find((workspace) => workspace.id === WORKSPACE_ID.DATA)!
  containerQueue.activateWorkspace(dataWorkspace.id, dataWorkspace.name)

  await router.isReady()
  const initialRoute = router.currentRoute.value
  const initialPage = config.pages.find((page) =>
    PAGE_ROUTE_NAMES[page.id].includes(String(initialRoute.name)),
  )
  if (initialPage && initialPage.id !== PAGE_ID.MARKET_QUOTES) {
    containerQueue.syncRoute(String(initialRoute.name), config.pages)
  }

  app.mount('#app')
}

void startApp()
