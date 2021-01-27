<template>
  <div class="alert alert-success">
    La ĉeno #{{ string.name }} estis forigita.
  </div>
</template>

<script>

export default {
  props: ["string"],
};
</script>