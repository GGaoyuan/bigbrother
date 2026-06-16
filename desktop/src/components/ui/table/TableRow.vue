<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const computedClass = computed(() =>
  cn('border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted', props.class)
)
</script>

<template>
  <tr :class="computedClass">
    <slot />
  </tr>
</template>
