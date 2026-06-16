<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { type ButtonVariants, buttonVariants } from './variants'
import { cn } from '@/lib/utils'

interface Props extends /* @vue-ignore */ HTMLAttributes {
  variant?: ButtonVariants['variant']
  size?: ButtonVariants['size']
  as?: string
}

const props = withDefaults(defineProps<Props>(), {
  as: 'button',
  variant: 'default',
  size: 'default',
})

const computedClass = computed(() => cn(buttonVariants({ variant: props.variant, size: props.size }), props.class))
</script>

<template>
  <component :is="as" :class="computedClass">
    <slot />
  </component>
</template>
