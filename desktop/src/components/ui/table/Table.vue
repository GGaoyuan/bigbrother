<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const computedClass = computed(() => cn('w-full caption-bottom text-sm', props.class))
</script>

<template>
  <table :class="computedClass">
    <slot />
  </table>
</template>
