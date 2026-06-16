<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const computedClass = computed(() => cn('relative w-full overflow-auto', props.class))
</script>

<template>
  <div :class="computedClass">
    <slot />
  </div>
</template>
