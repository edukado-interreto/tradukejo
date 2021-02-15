<template>
  <article class="translation-row" :class="translationRowClasses" :id="string.id" ref="row">
    <translation-row-header :string="stringToShow"></translation-row-header>
    <div class="row mt-1" :class="rowAlignClasses">
      <text-from
        v-if="!languageFromLoading"
        :stringtext="currentOriginalText"
        :context="string.context"
      ></text-from>
      <loading-spinner v-else small></loading-spinner>
      <text-to :string="stringToShow"></text-to>
    </div>
  </article>
</template>

<script>
import TranslationRowHeader from "./TranslationRowHeader";
import TextFrom from "./translatingFrom/TextFrom";
import TextTo from "./translatingTo/TextTo";

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
        translated:
          this.string.state === this.globals.TRANSLATION_STATE_TRANSLATED,
        outdated: this.string.state === this.globals.TRANSLATION_STATE_OUTDATED,
        untranslated:
          this.string.state === this.globals.TRANSLATION_STATE_UNTRANSLATED,
        selected: this.isSelected
      };
    },
    rowAlignClasses() {
      return {
        "d-flex":
          this.string.state === this.globals.TRANSLATION_STATE_UNTRANSLATED &&
          !this.translationIsBeingEdited,
        "align-items-center":
          this.string.state === this.globals.TRANSLATION_STATE_UNTRANSLATED &&
          !this.translationIsBeingEdited,
      };
    },
    isSelected() {
      return this.chosenStringId === this.string.id;
    }
  },
  methods: {
    async loadLanguageFrom(code) {
      if (code === this.projectLanguage) {
        this.currentOriginalText = this.string.original_text;
      } else if (code === this.currentLanguage.code) {
        this.currentOriginalText = this.string.translated_text;
      } else {
        this.languageFromLoading = true;
        await this.postCsrf("/vue/get-string-translation/", {
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
      }
    },
    setTranslationIsBeingEdited(status) {
      this.translationIsBeingEdited = status;

      if (this.currentLanguage.id === this.currentOriginalText.language.id) {
        this.currentOriginalText = this.string.original_text; // Update original if it is being modified
      }
    },
  },
  provide() {
    return {
      loadLanguageFrom: this.loadLanguageFrom,
      stringId: this.stringToShow.id,
      setTranslationIsBeingEdited: this.setTranslationIsBeingEdited,
      rowIsSelected: this.isSelected
    };
  },
  mounted() {
    if (this.isSelected) {
      this.$refs.row.scrollIntoView({behavior: 'smooth'})
    }
  }
};
</script>

<style lang="scss">
.translation-row {
  border: 1px solid black;
  border-radius: 5px;
  margin: 0;
  margin-bottom: 1rem;
  padding: 0.5rem 0.6rem;

  &.translated {
    border-color: #90bda0;
    background-color: #d4edda;
  }

  &.untranslated {
    border-color: #bd9090;
    background-color: #f8d7da;
  }

  &.outdated {
    border-color: #bdb590;
    background-color: #fff3cd;
  }

  &.selected {
    border: 2px solid #007bff;
    box-shadow: 0 0 5px #333;
  }

  input[type="text"] {
    width: 100%;
  }

  code {
    font-weight: bold;
    color: #304060;
    font-size: 1em;
    line-height: 1em;
  }

  .context {
    color: #555;
    font-weight: bold;
    margin-top: 1rem;
    font-size: 0.9rem;

    svg {
      cursor: help;
    }
  }
}

.plural-number-explanation {
  color: #555;
  font-weight: bold;
  margin-top: 0.8rem;
  margin-bottom: 0.3rem;
  font-size: 0.9rem;

  &:first-child {
    margin-top: 0;
  }
}
</style>