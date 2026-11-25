<script setup lang="ts">
import { computed, onActivated, onBeforeUnmount, onDeactivated, onMounted, ref, shallowRef, watch } from 'vue'
import {
  candleIndicesForRange,
  formatSelectionEdge,
  projectSelection,
  rangeForDrag,
  type RangeDragPart,
} from './chartRangeSelection'
import type { MarketCandle, TimeRange } from './profileMarketData'

const props = defineProps<{
  candles: readonly MarketCandle[]
  range: TimeRange | null
  active: boolean
  width: number
  height: number
  revision: number
  toLogical: (pixel: number) => number | null
  toX: (logical: number) => number | null
}>()

const emit = defineEmits<{
  'update:range': [range: TimeRange]
  cancel: []
  'wheel-request': [event: WheelEvent]
}>()

const EDGE_DATE_WIDTH = 140
const HANDLE_HIT_WIDTH = 14
const overlay = ref<HTMLDivElement>()
let keyboardAttached = false
const drag = shallowRef<{
  pointerId: number
  part: RangeDragPart
  anchor: number
  original: TimeRange | null
}>()

const geometry = computed(() => {
  // The chart's conversion functions keep their identity when the viewport changes.
  void props.revision
  return projectSelection(props.candles, props.range, props.width, props.toX)
})
const indices = computed(() => candleIndicesForRange(props.candles, props.range))
const startLabel = computed(() => props.range ? formatSelectionEdge(props.range.start, 'start') : '')
const endLabel = computed(() => props.range ? formatSelectionEdge(props.range.end, 'end') : '')
const selectionLabel = computed(() => `${startLabel.value} 至 ${endLabel.value}`)
const overlayStyle = computed(() => ({
  width: `${props.width}px`,
  height: `${props.height}px`,
}))

function publish(next: TimeRange | null) {
  if (next && (next.start !== props.range?.start || next.end !== props.range?.end)) {
    emit('update:range', next)
  }
}

function logicalAt(clientX: number) {
  if (!overlay.value || props.width <= 0) return null

  const left = overlay.value.getBoundingClientRect().left
  const local = Math.max(0, Math.min(clientX - left, props.width - 0.01))
  return props.toLogical(local)
}

function startPointer(event: PointerEvent, part: RangeDragPart) {
  if (!props.active || event.button !== 0 || drag.value || !props.candles.length) return
  if (part !== 'create' && !indices.value) return

  const anchor = logicalAt(event.clientX)
  if (anchor === null || !overlay.value) return

  event.preventDefault()
  drag.value = {
    pointerId: event.pointerId,
    part,
    anchor,
    original: props.range,
  }
  overlay.value.setPointerCapture(event.pointerId)
  if (part === 'create') publish(rangeForDrag(props.candles, part, anchor, anchor, null))
}

function movePointer(event: PointerEvent) {
  const current = drag.value
  if (!current || event.pointerId !== current.pointerId) return

  const cursor = logicalAt(event.clientX)
  if (cursor !== null) {
    publish(rangeForDrag(props.candles, current.part, current.anchor, cursor, current.original))
  }
}

function stopDrag() {
  const current = drag.value
  if (!current) return

  drag.value = undefined
  if (overlay.value?.hasPointerCapture(current.pointerId)) {
    overlay.value.releasePointerCapture(current.pointerId)
  }
}

function cancelPointer(event: PointerEvent) {
  if (event.pointerId === drag.value?.pointerId) stopDrag()
}

function finishPointer(event: PointerEvent) {
  movePointer(event)
  cancelPointer(event)
}

function editByKeyboard(event: KeyboardEvent, part: Exclude<RangeDragPart, 'create'>) {
  if (!props.active || !indices.value) return

  let delta: number
  switch (event.key) {
    case 'ArrowLeft':
    case 'ArrowDown':
      delta = -1
      break
    case 'ArrowRight':
    case 'ArrowUp':
      delta = 1
      break
    case 'Home':
      delta = -props.candles.length
      break
    case 'End':
      delta = props.candles.length
      break
    default:
      return
  }

  event.preventDefault()
  publish(rangeForDrag(props.candles, part, 0, delta, props.range))
}

function createByKeyboard(event: KeyboardEvent) {
  if (!props.active || geometry.value || (event.key !== 'Enter' && event.key !== ' ')) return

  const center = props.toLogical(props.width / 2)
  if (center === null) return

  event.preventDefault()
  publish(rangeForDrag(props.candles, 'create', center, center, null))
}

function cancelByKeyboard(event: KeyboardEvent) {
  if (!props.active || event.key !== 'Escape' || event.defaultPrevented) return

  event.preventDefault()
  stopDrag()
  emit('cancel')
}

function passWheel(event: WheelEvent) {
  if (!props.active) return

  event.preventDefault()
  if (!drag.value) emit('wheel-request', event)
}

function datePosition(x: number, edge: 'start' | 'end') {
  const proposed = edge === 'start' ? x + 5 : x - EDGE_DATE_WIDTH - 5
  return Math.max(0, Math.min(proposed, props.width - EDGE_DATE_WIDTH))
}

watch([() => props.active, () => props.candles], stopDrag)

function attachKeyboard() {
  if (keyboardAttached) return
  document.addEventListener('keydown', cancelByKeyboard)
  keyboardAttached = true
}

function detachKeyboard() {
  if (keyboardAttached) {
    document.removeEventListener('keydown', cancelByKeyboard)
    keyboardAttached = false
  }
  stopDrag()
}

onMounted(attachKeyboard)
onActivated(attachKeyboard)
onDeactivated(detachKeyboard)
onBeforeUnmount(detachKeyboard)
</script>

<template>
  <div
    v-show="active || geometry"
    ref="overlay"
    class="range-overlay"
    :class="{
      'is-active': active,
      'is-moving': drag?.part === 'selection',
      'is-resizing': drag?.part === 'start' || drag?.part === 'end',
    }"
    :style="overlayStyle"
    data-range-overlay
    role="group"
    :tabindex="active ? 0 : -1"
    :aria-label="active && !geometry ? 'K 线图时间选区，按回车选中可见区间中央的 K 线' : 'K 线图时间选区'"
    :aria-hidden="!active"
    @pointerdown="startPointer($event, 'create')"
    @pointermove="movePointer"
    @pointerup="finishPointer"
    @pointercancel="cancelPointer"
    @lostpointercapture="cancelPointer"
    @keydown.self="createByKeyboard"
    @wheel="passWheel"
  >
    <template v-if="geometry && indices">
      <button
        type="button"
        class="selected-area"
        data-range-part="selection"
        :style="{
          left: `${geometry.left}px`,
          width: `${geometry.right - geometry.left}px`,
        }"
        role="slider"
        aria-label="移动选区"
        :aria-valuemin="1"
        :aria-valuemax="candles.length - (indices.last - indices.first)"
        :aria-valuenow="indices.first + 1"
        :aria-valuetext="selectionLabel"
        :tabindex="active ? 0 : -1"
        @pointerdown.stop="startPointer($event, 'selection')"
        @keydown="editByKeyboard($event, 'selection')"
      ></button>

      <template v-if="geometry.startVisible">
        <button
          type="button"
          class="range-handle handle-start"
          :class="{ 'is-inward': geometry.left < HANDLE_HIT_WIDTH }"
          data-range-part="start"
          :style="{
            left: `${geometry.left}px`,
          }"
          role="slider"
          aria-label="区间起点"
          :aria-valuemin="1"
          :aria-valuemax="indices.last + 1"
          :aria-valuenow="indices.first + 1"
          :aria-valuetext="startLabel"
          :tabindex="active ? 0 : -1"
          @pointerdown.stop="startPointer($event, 'start')"
          @keydown="editByKeyboard($event, 'start')"
        ></button>
        <span
          class="edge-date"
          :style="{
            left: `${datePosition(geometry.left, 'start')}px`,
          }"
          aria-hidden="true"
        >{{ startLabel }}</span>
      </template>

      <template v-if="geometry.endVisible">
        <button
          type="button"
          class="range-handle handle-end"
          :class="{ 'is-inward': geometry.right > width - HANDLE_HIT_WIDTH }"
          data-range-part="end"
          :style="{
            left: `${geometry.right}px`,
          }"
          role="slider"
          aria-label="区间终点"
          :aria-valuemin="indices.first + 1"
          :aria-valuemax="candles.length"
          :aria-valuenow="indices.last + 1"
          :aria-valuetext="endLabel"
          :tabindex="active ? 0 : -1"
          @pointerdown.stop="startPointer($event, 'end')"
          @keydown="editByKeyboard($event, 'end')"
        ></button>
        <span
          class="edge-date end-date"
          :class="{ 'is-raised': geometry.startVisible && geometry.right - geometry.left < EDGE_DATE_WIDTH * 2 + 10 }"
          :style="{
            left: `${datePosition(geometry.right, 'end')}px`,
          }"
          aria-hidden="true"
        >{{ endLabel }}</span>
      </template>
    </template>
  </div>
</template>

<style scoped>
.range-overlay {
  --selection-boundary: #4474b1;
  position: absolute;
  z-index: 2;
  top: 0;
  left: 0;
  overflow: hidden;
  pointer-events: none;
}

.range-overlay.is-active {
  cursor: crosshair;
  pointer-events: auto;
  touch-action: none;
  user-select: none;
}

.range-overlay:focus-visible {
  outline: 2px solid #285b9c;
  outline-offset: -2px;
}

.range-overlay.is-moving {
  cursor: grabbing;
}

.range-overlay.is-resizing {
  cursor: ew-resize;
}

.selected-area,
.range-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  height: 100%;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 0;
  touch-action: none;
  appearance: none;
}

.selected-area {
  border-block: 1px solid #4474b15c;
  background: #4b85cf14;
}

.is-active .selected-area {
  background: #4b85cf21;
  cursor: grab;
}

.is-moving .selected-area {
  cursor: grabbing;
}

.range-handle {
  z-index: 1;
  width: 14px;
  background: transparent;
}

.range-handle::before {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--selection-boundary);
  content: '';
}

.is-active .range-handle {
  cursor: ew-resize;
}

.is-active .range-handle::after {
  position: absolute;
  top: calc(50% - 11px);
  width: 7px;
  height: 22px;
  border: 1px solid var(--selection-boundary);
  border-radius: 3px;
  background: #edf5ff;
  content: '';
}

.handle-start,
.handle-end.is-inward {
  transform: translateX(-100%);
}

.handle-start.is-inward {
  transform: none;
}

.handle-start::before,
.handle-end.is-inward::before {
  right: 0;
}

.handle-end::before,
.handle-start.is-inward::before {
  right: auto;
  left: 0;
}

.handle-end.is-inward::before {
  left: auto;
}

.handle-start::after,
.handle-end.is-inward::after {
  right: 1px;
}

.handle-end::after,
.handle-start.is-inward::after {
  right: auto;
  left: 1px;
}

.handle-end.is-inward::after {
  left: auto;
}

.selected-area:focus-visible,
.range-handle:focus-visible {
  outline: 2px solid #285b9c;
  outline-offset: -2px;
}

.edge-date {
  position: absolute;
  bottom: 6px;
  box-sizing: border-box;
  width: 140px;
  padding: 3px 6px;
  overflow: hidden;
  border: 1px solid #a9c2e2;
  border-radius: 3px;
  background: #f1f7ffff;
  color: #274a76;
  font-size: 11px;
  line-height: 1.25;
  font-variant-numeric: tabular-nums;
  text-align: left;
  text-overflow: ellipsis;
  white-space: nowrap;
  pointer-events: none;
}

.end-date {
  text-align: right;
}

.end-date.is-raised {
  bottom: 28px;
}
</style>
