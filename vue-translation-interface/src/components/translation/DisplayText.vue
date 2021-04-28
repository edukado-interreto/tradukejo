<template>
  <div
    v-if="!pluralized"
    class="original-text"
    :class="clickClasses"
    v-html="firstText"
    :lang="language.code"
    :dir="language.direction"
    @click="addSymbol($event, 0)"
    ref="text0"
    >
  </div>
  <div v-else class="original-text" :class="clickClasses">
    <div class="context mt-1">
      <i class="fas fa-question-circle" :title="$t('translate.context')"></i> {{ $t('translate.number_explanations') }}
    </div>
    <template v-for="(text, example, index) in texts" :key="example">
      <div class="plural-number-explanation">{{ $t('translate.number', {n: example}) }}</div>
      <div v-html="text" @click="addSymbol($event, index)" :ref="'text' + index"></div>
    </template>
  </div>
</template>

<script>
import Mark from 'mark.js';

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
    },
  },
  methods: {
    addSymbol(e, index) {
      if (this.canAddSymbols) {
        if (e.target.tagName === 'CODE') {
          this.eventBus.emit('insert-symbol', {index, stringId: this.stringId, text: e.target.textContent});
        }
      }
    }
  },
  mounted() {
    if (this.queryStringQ) {
      let i = 0;
      while (this.$refs['text' + i]) {
        const context = this.$refs['text' + i];
        const instance = new Mark(context);
        instance.mark(this.queryStringQ, {
          separateWordSearch: false,
          acrossElements: true
        });
        i++;
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
.original-text code {
  border: 1px solid transparent;
  padding: 1px 0;
  border-radius: 3px;
  transition: all .2s;
}

.can-add-symbols {
  code {
    cursor: pointer;
    background-color: rgba(220, 220, 220, 0.5);
    border-color: rgba(120, 120, 120, 0.6);
    
    &:hover {
      opacity: .75;
    }
  }
}
</style>