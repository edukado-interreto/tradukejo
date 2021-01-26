<template>
  <span class="online-translators-links" v-if="languageFrom.code !== languageTo.code">
    {{ languageFrom.code }} → {{ languageTo.code }} (todo)
  </span>
</template>

<script>
export default {
  props: ["languageFrom", "languageTo"],
}
</script>