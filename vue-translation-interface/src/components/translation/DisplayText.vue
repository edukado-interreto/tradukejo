<template>
  <div
    v-if="!pluralized"
    class="original-text"
    :class="clickClasses"
    v-html="firstText"
    :lang="language.code"
    :dir="language.direction"
     @click="addSymbol($event, 0)"
    >
  </div>
  <div v-else class="original-text" :class="clickClasses">
    <div class="context mt-1">
      <i class="fas fa-question-circle" :title="$t('translate.context')"></i> {{ $t('translate.number_explanations') }}
    </div>
    <template v-for="(text, example, index) in texts" :key="example">
      <div class="plural-number-explanation">{{ $t('translate.number', {n: example}) }}</div>
      <div v-html="text" @click="addSymbol($event, index)"></div>
    </template>
  </div>
</template>

<script>
export default {
  inject: ["translationIsBeingEdited", "stringId"],
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
    isTextFrom: {
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
    },
    clickClasses() {
      return {
        'click-to-edit': this.clickToEdit,
        'can-add-symbols': this.canAddSymbols
      };
    },
    canAddSymbols() {
      return this.isTextFrom && this.translationIsBeingEdited.value;
    }
  },
  methods: {
    addSymbol(e, index) {
      if (this.canAddSymbols) {
        if (e.target.tagName === 'CODE') {
          this.eventBus.emit('insert-symbol', {index, stringId: this.stringId, text: e.target.textContent});
        }
      }
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

<style lang="scss">
.can-add-symbols {
  code {
    cursor: pointer;
    
    &:hover {
      opacity: .75;
    }
  }
}
</style>