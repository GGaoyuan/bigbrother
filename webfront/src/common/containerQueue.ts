import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  CONTAINER_TYPE,
  WORKSPACE_ID,
  WORKSPACE_TYPE,
  type PageConfig,
  type WorkspaceId,
  type WorkspaceTabConfig,
} from './appConfig'

export interface WorkspaceContainerConfig {
  id: string;
  type: typeof CONTAINER_TYPE.DATA | typeof CONTAINER_TYPE.AI;
  title: string;
}

export interface RouteContainerConfig {
  id: string;
  type: typeof CONTAINER_TYPE.ROUTE;
  pageId: string;
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
    const cached = containers.value.find((item) => item.id === container.id)

    if (!cached) {
      containers.value.push(container)
    }

    activeContainerId.value = container.id
  }

  function activateWorkspace(workspace: WorkspaceTabConfig) {
    activeWorkspaceId.value = workspace.id

    if (workspace.type === WORKSPACE_TYPE.DATA) {
      cacheAndActivate({
        id: workspace.id,
        type: CONTAINER_TYPE.DATA,
        title: workspace.containerTitle,
      })
    } else if (workspace.type === WORKSPACE_TYPE.AI) {
      cacheAndActivate({
        id: workspace.id,
        type: CONTAINER_TYPE.AI,
        title: workspace.containerTitle,
      })
    }
  }

  function openPage(page: PageConfig) {
    activeWorkspaceId.value = WORKSPACE_ID.PAGES
    cacheAndActivate({
      id: `page:${page.id}`,
      type: CONTAINER_TYPE.ROUTE,
      pageId: page.id,
      title: page.label,
      path: page.path,
      routeNames: page.routeNames,
    })
  }

  function syncRoute(routeName: string, pages: PageConfig[]) {
    const matchedPage = pages.find((page) => page.routeNames.includes(routeName))
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
