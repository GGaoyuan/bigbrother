<script setup lang="ts">
import { shallowRef } from 'vue'
import PageNavigation from './component/PageNavigation.vue'
import SidebarHeader from './component/SidebarHeader.vue'

const MIN_WIDTH = 160
const MAX_WIDTH = 440
const KEYBOARD_STEP = 16
const width = defineModel<number>('width', {
  required: true,
})

const drag = shallowRef<{
  pointerId: number
  startX: number
  startWidth: number
} | null>(null)

function setWidth(value: number) {
  width.value = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, value))
}

function startResize(event: PointerEvent) {
  if (!event.isPrimary || event.button !== 0) return

  const handle = event.currentTarget as HTMLElement
  handle.setPointerCapture(event.pointerId)
  drag.value = {
    pointerId: event.pointerId,
    startX: event.clientX,
    startWidth: width.value,
  }
}

function resize(event: PointerEvent) {
  if (drag.value?.pointerId !== event.pointerId) return

  setWidth(drag.value.startWidth + event.clientX - drag.value.startX)
}

function stopResize(event: PointerEvent) {
  if (drag.value?.pointerId === event.pointerId) drag.value = null
}
</script>

<template>
  <aside id="app-sidebar" class="sidebar">
    <SidebarHeader />
    <PageNavigation />
    <div
      class="sidebar-resize"
      :class="{ 'is-dragging': drag }"
      role="separator"
      aria-label="调整侧栏宽度"
      aria-orientation="vertical"
      aria-controls="app-sidebar"
      :aria-valuemin="MIN_WIDTH"
      :aria-valuemax="MAX_WIDTH"
      :aria-valuenow="width"
      tabindex="0"
      @pointerdown="startResize"
      @pointermove="resize"
      @pointerup="stopResize"
      @pointercancel="stopResize"
      @lostpointercapture="stopResize"
      @keydown.left.prevent="setWidth(width - KEYBOARD_STEP)"
      @keydown.right.prevent="setWidth(width + KEYBOARD_STEP)"
    ></div>
  </aside>
</template>

<style>
.sidebar {
  position: fixed;
  z-index: 100;
  top: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  width: var(--rail-width);
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
  background: #fff;
  border-right: 1px solid var(--line);
}
.sidebar a:focus-visible {
  outline: 2px solid #3478f6;
  outline-offset: 2px;
}
.sidebar-resize {
  position: absolute;
  inset: 0 0 0 auto;
  width: 8px;
  cursor: col-resize;
  touch-action: none;
  user-select: none;
}
.sidebar-resize:hover,
.sidebar-resize:focus-visible,
.sidebar-resize.is-dragging {
  outline: none;
  background: #eaf1ff;
  box-shadow: inset -2px 0 var(--blue);
}
@media (max-width: 760px) {
  .sidebar {
    width: 260px;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
  }
  .sidebar:focus-within,
  .sidebar:hover {
    transform: translateX(0);
  }
  .sidebar-resize {
    display: none;
  }
  .sidebar::after {
    content: '';
    position: fixed;
    left: 100%;
    top: 50%;
    width: 12px;
    height: 60px;
    border-radius: 0 8px 8px 0;
    background: #3478f6;
  }
}
</style>
