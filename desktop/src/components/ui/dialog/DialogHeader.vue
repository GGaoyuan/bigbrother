<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const computedClass = computed(() => cn('flex flex-col space-y-1.5 text-center sm:text-left', props.class))
</script>

<template>
  <div :class="computedClass">
    <slot />
  </div>
</template>
