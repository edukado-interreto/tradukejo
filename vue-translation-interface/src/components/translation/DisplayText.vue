<template>
  <div v-if="!pluralized" class="original-text" v-html="firstText">
  </div>
  <div v-else class="original-text">
    <div class="context mt-1">
      <i class="fas fa-question-circle" title="Klarigoj pri la ĉeno"></i> Ĉi tiu ĉeno havas diversajn formojn depende de nombro.
    </div>
    <template v-for="(text, numbers) in texts" :key="numbers">
      <div class="plural-number-explanation">Se la nombro estas {{ numbers }}:</div>
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
  },
  computed: {
    firstText() {
      return this.texts[Object.keys(this.texts)[0]];
    }
  }
};
</script>