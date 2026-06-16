<script setup lang="ts">
import { DialogOverlay, type DialogOverlayProps } from 'radix-vue'
import { type HTMLAttributes, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<DialogOverlayProps & { class?: HTMLAttributes['class'] }>()

const computedClass = computed(() =>
  cn('fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0', props.class)
)
</script>

<template>
  <DialogOverlay :class="computedClass" v-bind="props">
    <slot />
  </DialogOverlay>
</template>
