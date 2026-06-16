<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const computedClass = computed(() => cn('[&_tr:last-child]:border-0', props.class))
</script>

<template>
  <tbody :class="computedClass">
    <slot />
  </tbody>
</template>
