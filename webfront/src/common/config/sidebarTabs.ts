import { WORKSPACE_ID, type WorkspaceId } from './ids'

export interface SidebarTabConfig {
  id: WorkspaceId;
  name: string;
}

export const SIDEBAR_TABS: SidebarTabConfig[] = [
  { id: WORKSPACE_ID.DATA, name: '数据' },
  { id: WORKSPACE_ID.AI, name: 'AI' },
  { id: WORKSPACE_ID.PAGES, name: '页面' },
]
