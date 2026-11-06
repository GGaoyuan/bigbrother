import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { PAGE_ID, WORKSPACE_TYPE } from './common/appConfig'
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
  const dataWorkspace = config.workspaces.find(
    (workspace) => workspace.type === WORKSPACE_TYPE.DATA,
  )!
  containerQueue.activateWorkspace(dataWorkspace)

  await router.isReady()
  const initialRoute = router.currentRoute.value
  const initialPage = config.pages.find((page) =>
    page.routeNames.includes(String(initialRoute.name)),
  )
  if (initialPage && initialPage.id !== PAGE_ID.MARKET_QUOTES) {
    containerQueue.syncRoute(String(initialRoute.name), config.pages)
  }

  app.mount('#app')
}

void startApp()
