<template>
  <article class="translation-row" :class="translationRowClasses">
    <translation-row-header :string="stringToShow"></translation-row-header>
    <div class="row mt-1" :class="rowAlignClasses">
      <text-from v-if="!languageFromLoading" :stringtext="currentOriginalText" :context="string.context"></text-from>
      <loading-spinner v-else small></loading-spinner>
      <text-to :string="stringToShow"></text-to>
    </div>
  </article>
</template>

<script>
import TranslationRowHeader from './TranslationRowHeader';
import TextFrom from './translatingFrom/TextFrom';
import TextTo from './translatingTo/TextTo';

export default {
  components: { TranslationRowHeader, TextFrom, TextTo },
  props: ["string"],
  data() {
    return {
      translationIsBeingEdited: false,
      languageFromLoading: false,
      currentOriginalText: this.string.original_text,
    };
  },
  computed: {
    stringToShow() {
      return {
        ...this.string,
        original_text: this.currentOriginalText,
      };
    },
    translationRowClasses() {
      return {
        translated: this.string.state === this.globals.TRANSLATION_STATE_TRANSLATED,
        outdated: this.string.state === this.globals.TRANSLATION_STATE_OUTDATED,
        untranslated: this.string.state === this.globals.TRANSLATION_STATE_UNTRANSLATED,
      };
    },
    rowAlignClasses() {
      return {
        "d-flex": this.string.state === this.globals.TRANSLATION_STATE_UNTRANSLATED && !this.translationIsBeingEdited,
        "align-items-center": this.string.state === this.globals.TRANSLATION_STATE_UNTRANSLATED && !this.translationIsBeingEdited,
      };
    },
  },
  methods: {
    async loadLanguageFrom(code) {
      this.languageFromLoading = true;
      await this.postCsrf('/vue/get-string-translation/', {
          trstring_id: this.string.id,
          language: code,
        })
        .then((response) => {
          this.currentOriginalText = response.data;
        })
        .catch(function (error) {
          console.log(error);
        });
      this.languageFromLoading = false;
    },
    setTranslationIsBeingEdited(status) {
      this.translationIsBeingEdited = status;
    },
  },
  provide() {
    return {
      loadLanguageFrom: this.loadLanguageFrom,
      stringId: this.stringToShow.id,
      setTranslationIsBeingEdited: this.setTranslationIsBeingEdited,
    }
  },
};
</script>