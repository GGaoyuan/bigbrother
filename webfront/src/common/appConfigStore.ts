import { defineStore } from 'pinia'
import { ref } from 'vue'
import { PROJECT_CONFIG, type AppConfig } from './config'

export const useAppConfigStore = defineStore('app-config', () => {
  const config = ref<AppConfig | null>(null)
  const isLoaded = ref(false)

  async function loadAppConfig() {
    if (isLoaded.value) return

    config.value = structuredClone(PROJECT_CONFIG)
    isLoaded.value = true
  }

  return {
    config,
    isLoaded,
    loadAppConfig,
  }
})
