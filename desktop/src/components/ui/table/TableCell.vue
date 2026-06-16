<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const computedClass = computed(() => cn('p-4 align-middle [&:has([role=checkbox])]:pr-0', props.class))
</script>

<template>
  <td :class="computedClass">
    <slot />
  </td>
</template>
