<template>
  <div class="col-md-6 translation-widget">
    <display-text
      v-if="string.translated_text && !editing"
      :texts="string.translated_text.text"
      :pluralized="string.translated_text.pluralized"
    ></display-text>

    <div class="text-center" v-if="!editing">
      <button v-if="string.translated_text" class="btn btn-secondary mb-2 mt-3" tabindex="45" @click="showForm">Redakti</button>
      <button v-else class="btn btn-secondary mb-3" tabindex="45" @click="showForm">Traduki</button>
    </div>
    <translate-form
      v-else
      :pluralized="pluralized"
      :texts="texts"
      @cancel="hideForm"
      ></translate-form>

    <author-and-history
      v-if="string.translated_text"
      :stringtext="string.translated_text"
    ></author-and-history>
  </div>
</template>

<script>
import AuthorAndHistory from "../AuthorAndHistory";
import DisplayText from "../DisplayText";
import TranslateForm from "./TranslateForm";

export default {
  props: ["string"],
  components: { AuthorAndHistory, DisplayText, TranslateForm },
  data() {
    return {
      editing: false,
    }
  },
  computed: {
    pluralized() {
      return this.string.original_text.pluralized;
    },
    texts() {
      if (this.string.translated_text) {
        return this.string.translated_text.text;
      }
      else {
        return {};
      }
    },
  },
  methods: {
    showForm() {
      this.editing = true;
    },
    hideForm() {
      this.editing = false;
    }
  }
};
</script>