<template>
  <form @submit.prevent="sendForm" class="translation-form">
    <transition name="jump">
      <div v-if="!!error" class="alert alert-danger">
        {{ error }}
      </div>
    </transition>
    <template v-if="editMode">
      <div class="form-group">
        <input
          type="text"
          class="form-control"
          v-model.trim="enteredName"
          :placeholder="$t('translate.string_name')"
          :disabled="loading"
          required
        />
      </div>
      <div class="form-group">
        <input
          type="text"
          class="form-control"
          v-model.trim="enteredPath"
          :placeholder="$t('translate.string_path')"
          :disabled="loading"
        />
      </div>
    </template>
    
    <template v-if="enteredPluralized">
      <div
        v-for="(text, example, index) in textsWithPluralExamples"
        :key="example"
        class="form-group"
      >
        <div class="plural-number-explanation">
          <label :for="'txt' + stringId + '-' + index">
            {{ $t('translate.number', {n: example}) }}
          </label>
        </div>
        <textarea
          rows="4"
          class="form-control"
          :dir="currentLanguage.direction"
          :lang="currentLanguage.code"
          :ref="index === 0 ? 'textarea' : null"
          :title="index === 0 ? 'textarea' : null"
          :id="'txt' + stringId + '-' + index"
          v-model.trim="enteredTexts[index]"
          :disabled="loading"
          required
        ></textarea>
      </div>
    </template>
    <div v-else class="form-group">
      <textarea
        rows="6"
        class="form-control"
        :dir="currentLanguage.direction"
        :lang="currentLanguage.code"
        ref="textarea"
        v-model.trim="enteredTexts[0]"
        :disabled="loading"
        required
      ></textarea>
    </div>

    <template v-if="editMode">
      <div class="form-group">
        <input
          type="text"
          class="form-control"
          :dir="currentLanguage.direction"
          v-model.trim="enteredContext"
          placeholder="Helpa teksto por tradukistoj"
          :disabled="loading"
        />
      </div>
      <div class="form-group">
        <div class="custom-control custom-checkbox">
          <input
            type="checkbox"
            class="custom-control-input pluralized"
            v-model="enteredPluralized"
            :id="'pluralized' + stringId"
            :disabled="loading"
          />
          <label class="custom-control-label" :for="'pluralized' + stringId"
            >Ĉeno kun pluralaj formoj</label
          >
        </div>
      </div>
      <div class="form-group" v-if="!newString">
        <div class="custom-control custom-checkbox">
          <input
            type="checkbox"
            class="custom-control-input minor-change"
            v-model="minor"
            :id="'minor' + stringId"
            :disabled="loading"
          />
          <label class="custom-control-label" :for="'minor' + stringId"
            >Malgrava ŝanĝo (ne marki la ĉenon kiel retradukendan)</label
          >
        </div>
      </div>
    </template>

    <proposed-translations
      v-if="proposedTranslations.length > 0"
      :translations="proposedTranslations"
      @pick-translation="setTranslation($event)"
      />

    <div class="form-group">
      <button
        class="btn btn-primary mr-2 text-center"
        :class="{'can-submit': canSubmit}"
        :disabled="loading || !canSubmit"
      >
        <loading-spinner v-if="loading" inline white></loading-spinner>
        <template v-else>{{ $t('translate.save') }}</template>
      </button>
      <input
        type="button"
        class="btn btn-secondary"
        :value="$t('translate.cancel')"
        @click="cancel"
        :disabled="loading"
      />
    </div>
  </form>
</template>

<script>
import { defineAsyncComponent } from 'vue';
const ProposedTranslations = defineAsyncComponent(() => import('./ProposedTranslations'));

export default {
  components: { ProposedTranslations },
  emits: ["save-translation", "cancel"],
  inject: ["stringId"],
  props: {
    path: {
      type: String,
      required: false,
      default: ''
    },
    name: {
      type: String,
      required: false,
      default: ''
    },
    pluralized: {
      type: Boolean,
      required: false,
      default: false
    },
    texts: {
      type: Object,
      required: false,
      default: () => {return {}}
    },
    loading: {
      type: Boolean,
      required: false,
      default: false
    },
    context: {
      type: String,
      required: false,
      default: ''
    },
    error: {
      type: String,
      required: false,
      default: null
    },
    newString: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  data() {
    return {
      showForm: false,
      enteredTexts: Object.values(this.texts),
      enteredPluralized: this.pluralized,
      enteredContext: this.context,
      enteredName: this.name,
      enteredPath: this.path,
      minor: false,
      proposedTranslations: [],
    };
  },
  computed: {
    newTranslation() {
      return Object.keys(this.texts).length === 0;
    },
    textsWithPluralExamples() {
      if (!this.newTranslation) {
        const texts = {};
        this.currentLanguage.plural_examples_list.forEach((example) => {
          texts[example] = this.texts[example] || "";
        });
        return texts;
      } else {
        const texts = {};
        this.currentLanguage.plural_examples_list.forEach((example) => {
          texts[example] = "";
        });
        return texts;
      }
    },
    canSubmit() {
      if (this.newString && this.enteredName == '') {
        return false;
      }
      if (!this.newTranslation) {
        const oldTexts = Object.values(this.texts);
        let differences = false;

        for (let i = 0; i < this.enteredTexts.length; i++) {
          if (this.enteredTexts[i] !== oldTexts[i]) {
            differences = true;
          }
        }
        if (
          this.context != this.enteredContext ||
          this.pluralized != this.enteredPluralized ||
          this.name != this.enteredName ||
          this.path != this.enteredPath
        ) {
          differences = true;
        }
        if (!differences) {
          return false;
        }
      } else {
        if (
          Object.keys(this.enteredTexts).length === 0 ||
          (this.enteredPluralized &&
            Object.keys(this.enteredTexts).length <
              this.currentLanguage.plural_examples_list.length)
        ) {
          return false;
        }
      }

      for (let i = 0; i < this.enteredTexts.length; i++) {
        if (this.enteredTexts[i] === "") {
          return false;
        }
      }

      return true;
    },
  },
  methods: {
    sendForm() {
      if (this.canSubmit) {
        this.$emit("save-translation", {
          trstring_id: this.stringId,
          text: this.enteredTexts,
          name: this.enteredName,
          path: this.enteredPath,
          pluralized: this.enteredPluralized,
          context: this.enteredContext,
          minor: this.minor,
        });
      }
    },
    cancel() {
      this.$emit("cancel");
    },
    setTranslation(texts) {
      for (let i = 0; i < texts.length; i++) {
        this.enteredTexts[i] = texts[i];
      }
    }
  },
  async created() {
    if (!this.newString && Object.keys(this.texts).length === 0) {
      await this.postCsrf("/vue/get-translation-suggestions/", {
        trstring_id: this.stringId,
        language: this.currentLanguage.code,
      }).then((response) => {
        this.proposedTranslations = response.data;
      });
    }
  },
  mounted() {
    this.$refs.textarea.focus();
  },
};
</script>

<style lang="scss" scoped>
.translation-form .plural-number-explanation {
  margin-bottom: 0;
  margin-top: 0;
}

:invalid {
    box-shadow: none;
}
</style>