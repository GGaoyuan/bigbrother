<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const computedClass = computed(() => cn('[&_tr]:border-b', props.class))
</script>

<template>
  <thead :class="computedClass">
    <slot />
  </thead>
</template>
