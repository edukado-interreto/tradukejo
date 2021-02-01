<template>
  <div class="col-md-6">
    <display-text
      ref="zizi"
      v-if="string.translated_text && !editing"
      :texts="string.translated_text.text"
      :pluralized="string.translated_text.pluralized"
      :click-to-edit="true"
      @click="showForm"
    ></display-text>

    <div class="text-center" v-if="!editing" ref="buttonWrapper">
      <button
        v-if="string.translated_text"
        class="btn btn-secondary mb-2 mt-3"
        :tabindex="currentIndex"
        @click="showForm"
        ref="translate"
      >
        Redakti
      </button>
      <button
        v-else
        class="btn btn-secondary mb-3"
        :tabindex="currentIndex"
        @click="showForm"
        ref="translate"
      >
        Traduki
      </button>
    </div>

    <transition name="slide">
      <translate-form
        v-if="editing"
        :name="string.name"
        :path="string.path"
        :pluralized="pluralized"
        :texts="texts"
        :loading="loading"
        :context="string.context"
        :error="error"
        @cancel="hideForm"
        @save-translation="saveTranslation($event)"
      ></translate-form>
    </transition>

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
  inject: ["setTranslationIsBeingEdited"],
  props: ["string"],
  components: { AuthorAndHistory, DisplayText, TranslateForm },
  data() {
    return {
      editing: false,
      loading: false,
      error: null,
    };
  },
  computed: {
    currentIndex() {
      return this.$store.getters.indexOfString(this.string.id) + 1;
    },
    pluralized() {
      return this.string.original_text.pluralized;
    },
    texts() {
      if (this.string.translated_text) {
        return this.string.translated_text.raw_text;
      } else {
        return {};
      }
    },
  },
  methods: {
    showForm() {
      this.editing = true;
      this.setTranslationIsBeingEdited(true);
    },
    hideForm() {
      this.editing = false;
      this.setTranslationIsBeingEdited(false);
      this.$nextTick(() => {
        this.$refs.translate.focus();
      });
    },
    async saveTranslation(data) {
      this.loading = true;
      this.error = null;
      const oldPath = this.string.path;

      await this.$store
        .dispatch("saveTranslation", data)
        .then(() => {
          this.hideForm();

          setTimeout(() => {
            if (this.string.path != oldPath) {
              this.$router.push(this.translateLink({ dir: this.string.path, params: { force: true } }));
              return;
            }
          }, 200); // Wait until end of transition
        })
        .catch((e) => {
          this.error = e.message;
        });
      this.loading = false;
    },
  },
};
</script>
