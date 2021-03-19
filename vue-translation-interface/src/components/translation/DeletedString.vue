<template>
  <div class="alert alert-success">
    {{ $t('translated.deleted', {name: '#' + string.name}) }}
  </div>
</template>

<script>

export default {
  props: ["string"],
};
</script>