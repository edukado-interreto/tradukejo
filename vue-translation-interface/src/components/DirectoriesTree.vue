<script setup lang="ts">
const { tree } = defineProps<{ tree: DirectoryTree }>()
</script>

<template>
  <ul class="directory-tree-root">
    <DirectoryNode first :node="tree['']" />
  </ul>
</template>

<style lang="scss" scoped>
.directory-tree-root {
  margin: 0;
  padding: 0;
  border: 0;
  list-style-type: none;
}
</style>
