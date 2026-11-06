import { parse } from 'yaml'
import configYaml from './config.yaml?raw'

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
  pages: PagesConfig[]
}

const configSource = parse(configYaml) as ConfigSource

export const config: Config = {
  tabsConfig: configSource.workspace,
  pagesConfig: configSource.pages,
}
