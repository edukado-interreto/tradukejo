<template>
  <div class="alert alert-success">
    {{ $t('translate.deleted', {name: '#' + string.name}) }}
  </div>
</template>

<script>

export default {
  props: ["string"],
};
</script>