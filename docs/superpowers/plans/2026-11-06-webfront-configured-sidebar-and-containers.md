# Webfront Configured Sidebar and Containers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Load typed UI configuration globally at startup and route sidebar selections through a cached main content container queue.

**Architecture:** Keep application config and runtime container queue in separate Pinia stores. The sidebar emits ID-based workspace/page selections; a workspace container renders data/AI content or the Vue Router page component and retains route component instances with KeepAlive.

**Tech Stack:** Vue 3, TypeScript, Pinia, Vue Router.

**Spec:** `docs/superpowers/specs/2026-11-06-webfront-configured-sidebar-and-containers-design.md`

## Global Constraints

- Do not add dependencies.
- Sidebar content decisions use stable IDs or types, never visible labels.
- Load the global app configuration before mounting Vue.
- Keep the sidebar footer outside the switched tab content.
- Keep data/API backend requirements unchanged.

## Review Focus

- Initial `/` route should still open the data workspace; explicit page selection of `/` should open the market quotes route container.
- Repeated selection of one page must not create duplicate queue entries.
- Nested sector routes and redirects must render the matched route component in the host.
- Browser back/forward must synchronize the active page container.
- Switching workspace tabs must not remove the sidebar footer or corrupt queued container state.

### Task 1: Typed application configuration and startup loading

**Files:**
- Create: `webfront/src/common/appConfig.ts`
- Create: `webfront/src/common/appConfigStore.ts`
- Modify: `webfront/src/main.ts`

**Interfaces:**
- Provide typed workspace IDs, data category IDs, page IDs, config record, and `loadAppConfig()` action.
- Export the loaded config from Pinia for all UI components.

- [x] Define config records for workspace tabs, sidebar copy, data categories/mock data/metrics, and page routes.
- [x] Initialize Pinia and load config before app mount; mount only after successful local config load.
- [x] Run `npm run build-only` and `npm run type-check`; changed files compile, while type-check reports existing errors in four unrelated views.

### Task 2: Runtime container queue and main host

**Files:**
- Create: `webfront/src/common/containerQueue.ts`
- Create: `webfront/src/views/workspace/WorkspaceContainer.vue`
- Create: `webfront/src/views/data/DataPage.vue`
- Create: `webfront/src/views/ai/AiPage.vue`
- Modify: `webfront/src/App.vue`

**Interfaces:**
- Define a discriminated `WorkspaceContainerConfig` union for data, AI, and route page content.
- Store `containers`, `activeContainerId`, and ID-deduplicating open/activate actions in Pinia.
- Host chooses content using container `type`/`id`; route pages remain rendered by Vue Router.

- [x] Implement queue add/reuse/activate operations with stable IDs.
- [x] Render data/AI pages directly and route pages through RouterView + KeepAlive.
- [x] Make `/` default to the data page on initial launch and synchronize explicit route navigation with the queue.
- [x] Run `npm run build-only` and `npm run type-check`; changed files compile, while type-check reports existing errors in four unrelated views.

### Task 3: Config-driven sidebar interactions

**Files:**
- Modify: `webfront/src/views/sidebar/AppSidebar.vue`
- Modify: `webfront/src/views/sidebar/SidebarHeader.vue`
- Modify: `webfront/src/views/data/DataWorkspace.vue`
- Modify: `webfront/src/views/pages/PageNavigation.vue`

**Interfaces:**
- Sidebar header consumes configured workspace entries and emits the selected workspace ID.
- Data categories and page entries consume configured labels and IDs.
- Workspace selection opens the corresponding data/AI container; page selection opens its configured route container.

- [x] Replace label comparisons and local duplicate label data with globally loaded config values.
- [x] Wire tab/page actions to the container queue and router.
- [x] Run `npm run build-only`, `npm run type-check`, and `git diff --check`.

### Task 4: PRD update and final review

**Files:**
- Modify: `prd/v1.md`

- [x] Document startup config, ID/type-based sidebar entries, main content container, queue reuse, and route caching.
- [x] Review final diff against the spec; ensure no stale behavior or user-facing sidebar text remains hard-coded in the sidebar components.
- [x] Run the final build/type check and report existing type errors separately.
