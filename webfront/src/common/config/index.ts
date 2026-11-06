import { DATA_CATEGORIES, METRICS } from './dataBrowser'
import { PAGE_TABS } from './pageTabs'
import { SIDEBAR_COPY } from './sidebarCopy'
import { SIDEBAR_TABS } from './sidebarTabs'

export * from './ids'
export * from './dataBrowser'
export * from './pageRouteNames'
export * from './pageTabs'
export * from './sidebarCopy'
export * from './sidebarTabs'

export interface AppConfig {
  workspaces: typeof SIDEBAR_TABS;
  pages: typeof PAGE_TABS;
  sidebar: typeof SIDEBAR_COPY;
  dataCategories: typeof DATA_CATEGORIES;
  metrics: typeof METRICS;
}

export const PROJECT_CONFIG: AppConfig = {
  workspaces: SIDEBAR_TABS,
  pages: PAGE_TABS,
  sidebar: SIDEBAR_COPY,
  dataCategories: DATA_CATEGORIES,
  metrics: METRICS,
}
