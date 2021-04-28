<template>
  <button
    :disabled="loading || disabled"
    >
    <loading-spinner v-if="loading" inline white></loading-spinner>
    <slot v-else></slot>
  </button>
</template>

<script>
export default {
  props: {
    loading: {
      type: Boolean,
      required: true,
      default: false,
    },
    disabled: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
}
</script>