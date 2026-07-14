<script setup lang="ts">
const props = defineProps<{
  loading: boolean
  disabled?: boolean
}>()
</script>

<template>
  <button :disabled="loading || disabled">
    <loading-spinner v-if="loading" inline white></loading-spinner>
    <slot v-else></slot>
  </button>
</template>
