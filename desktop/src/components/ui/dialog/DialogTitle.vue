<script setup lang="ts">
import { DialogTitle, type DialogTitleProps } from 'radix-vue'
import { type HTMLAttributes, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<DialogTitleProps & { class?: HTMLAttributes['class'] }>()

const computedClass = computed(() => cn('text-lg font-semibold leading-none tracking-tight', props.class))
</script>

<template>
  <DialogTitle :class="computedClass" v-bind="props">
    <slot />
  </DialogTitle>
</template>
