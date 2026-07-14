<script setup lang="ts">
const props = defineProps<{ string: TrString }>()
</script>

<template>
  <div class="alert alert-success">
    {{ $t("translate.deleted", { name: `#${string.name}` }) }}
  </div>
</template>
