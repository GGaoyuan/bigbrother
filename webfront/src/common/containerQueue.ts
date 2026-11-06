import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { CONTAINER_TYPE, PAGE_ID, WORKSPACE_ID, type PageId, type WorkspaceId } from './config'
import type { PageTabConfig } from './config/pageTabs'
import { PAGE_ROUTE_NAMES } from './config/pageRouteNames'

export interface WorkspaceContainerConfig {
  id: string;
  type: typeof CONTAINER_TYPE.DATA | typeof CONTAINER_TYPE.AI;
  title: string;
}

export interface RouteContainerConfig {
  id: string;
  type: typeof CONTAINER_TYPE.ROUTE;
  pageId: PageId;
  title: string;
  path: string;
  routeNames: string[];
}

export type ContainerConfig = WorkspaceContainerConfig | RouteContainerConfig

export const useContainerQueueStore = defineStore('container-queue', () => {
  const containers = ref<ContainerConfig[]>([])
  const activeContainerId = ref<string | null>(null)
  const activeWorkspaceId = ref<WorkspaceId>(WORKSPACE_ID.DATA)

  const activeContainer = computed(
    () => containers.value.find((container) => container.id === activeContainerId.value) ?? null,
  )

  function cacheAndActivate(container: ContainerConfig) {
    if (!containers.value.some((item) => item.id === container.id)) containers.value.push(container)
    activeContainerId.value = container.id
  }

  function activateWorkspace(workspaceId: WorkspaceId, title: string) {
    activeWorkspaceId.value = workspaceId
    if (workspaceId === WORKSPACE_ID.PAGES) return

    cacheAndActivate({
      id: `workspace:${workspaceId}`,
      type: workspaceId === WORKSPACE_ID.DATA ? CONTAINER_TYPE.DATA : CONTAINER_TYPE.AI,
      title,
    })
  }

  function openPage(page: PageTabConfig) {
    activeWorkspaceId.value = WORKSPACE_ID.PAGES
    cacheAndActivate({
      id: `page:${page.id}`,
      type: CONTAINER_TYPE.ROUTE,
      pageId: page.id,
      title: page.name,
      path: page.path,
      routeNames: PAGE_ROUTE_NAMES[page.id],
    })
  }

  function syncRoute(routeName: string, pages: PageTabConfig[]) {
    const matchedPage = pages.find((page) => PAGE_ROUTE_NAMES[page.id].includes(routeName))
    if (matchedPage) openPage(matchedPage)
  }

  return {
    containers,
    activeContainerId,
    activeContainer,
    activeWorkspaceId,
    activateWorkspace,
    openPage,
    syncRoute,
  }
})
