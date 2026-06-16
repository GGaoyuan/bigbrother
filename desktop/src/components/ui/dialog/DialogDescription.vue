<script setup lang="ts">
import { DialogDescription, type DialogDescriptionProps } from 'radix-vue'
import { type HTMLAttributes, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<DialogDescriptionProps & { class?: HTMLAttributes['class'] }>()

const computedClass = computed(() => cn('text-sm text-muted-foreground', props.class))
</script>

<template>
  <DialogDescription :class="computedClass" v-bind="props">
    <slot />
  </DialogDescription>
</template>
