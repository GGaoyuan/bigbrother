import { reactive } from 'vue'
import { fetchAppConfig, fetchWorkspacePages } from '../../api/api'

export interface TabsConfig {
  id: number
  name: string
}

export interface PagesConfig {
  id: number
  name: string
  path: string
}

export interface Config {
  tabsConfig: TabsConfig[]
  pagesConfig: PagesConfig[]
}

interface ConfigSource {
  workspace: TabsConfig[]
}

interface WorkspacePagesSource {
  pages: PagesConfig[]
}

export const config = reactive<Config>({
  tabsConfig: [],
  pagesConfig: [],
})

export async function loadConfig(): Promise<void> {
  const [appConfig, workspacePages] = await Promise.all([
    fetchAppConfig<ConfigSource>(),
    fetchWorkspacePages<WorkspacePagesSource>(),
  ])

  config.tabsConfig = appConfig.workspace
  config.pagesConfig = workspacePages.pages
}
