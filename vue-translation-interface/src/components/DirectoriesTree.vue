<template>
  <ul>
    <directory-node :first="true" :node="tree['']"></directory-node>
  </ul>
</template>

<script>
import DirectoryNode from './DirectoryNode';

export default {
  props: ['tree'],
  components: { DirectoryNode }
};
</script>

<style lang="scss" scoped>
ul {
  margin: 0;
  padding: 0;
  border: 0;
  list-style-type: none;
}
</style>