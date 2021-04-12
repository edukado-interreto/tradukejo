<template>
  <div
    v-if="!pluralized"
    class="original-text"
    :class="{ 'click-to-edit': clickToEdit }"
    v-html="firstText"
    :lang="language.code"
    :dir="language.direction"
    >
  </div>
  <div v-else class="original-text" :class="{ 'click-to-edit': clickToEdit }">
    <div class="context mt-1">
      <i class="fas fa-question-circle" :title="$t('translate.context')"></i> {{ $t('translate.number_explanations') }}
    </div>
    <template v-for="(text, example) in texts" :key="example">
      <div class="plural-number-explanation">{{ $t('translate.number', {n: example}) }}</div>
      <div v-html="text"></div>
    </template>
  </div>
</template>

<script>
export default {
  props: {
    texts: {
      type: Object,
      required: true,
    },
    pluralized: {
      type: Boolean,
      required: false,
      default: false,
    },
    clickToEdit: {
      type: Boolean,
      required: false,
      default: false,
    },
    language: {
      type: Object,
      required: true,
    },
  },
  computed: {
    firstText() {
      return this.texts[Object.keys(this.texts)[0]];
    }
  }
};
</script>

<style lang="scss" scoped>
.click-to-edit {
  cursor: pointer !important;
  transition: opacity 100ms;

  &:hover {
    opacity: .86;
  }
}
</style>