<template>
  <header class="row">
    <div class="col-6">
      <strong title="Titolo de la ĉeno, ne traduku ĝin">
        #{{ string.name }}
      </strong>
      –
      <language-change-dropdown :string="string"></language-change-dropdown>
      <online-translator-links
        :language-from="string.original_text.language"
        :language-to="currentLanguage"
      ></online-translator-links>
    </div>
    <div class="col-6 text-right translation-state-bar">
      <template v-if="!stateLoading">
        <button v-if="editMode" class="btn btn-danger btn-sm">Forigi</button>
        <template v-else>
          <a
            v-if="string.state === globals.TRANSLATION_STATE_TRANSLATED"
            href="#"
            @click.prevent="updateState(string.translated_text.id, globals.TRANSLATION_STATE_OUTDATED)"
            >Marki kiel retradukendan</a
          >
          <a
            v-else-if="string.state === globals.TRANSLATION_STATE_OUTDATED"
            href="#"
            @click.prevent="updateState(string.translated_text.id, globals.TRANSLATION_STATE_TRANSLATED)"
            >Marki kiel tradukitan</a
          >

          <span
            v-if="string.state === globals.TRANSLATION_STATE_TRANSLATED"
            class="badge badge-success"
            >Tradukita</span
          >
          <span
            v-else-if="string.state === globals.TRANSLATION_STATE_OUTDATED"
            class="badge badge-warning"
            >Retradukenda</span
          >
          <span v-else class="badge badge-danger">Netradukita</span>
        </template>
      </template>
      <loading-spinner v-else inline></loading-spinner>
    </div>
  </header>
</template>

<script>
import LanguageChangeDropdown from "./translatingFrom/LanguageChangeDropdown";
import OnlineTranslatorLinks from "./translatingFrom/OnlineTranslatorLinks";

export default {
  components: { LanguageChangeDropdown, OnlineTranslatorLinks },
  props: ["string"],
  data() {
    return {
      stateLoading: false,
    };
  },
  computed: {
    editMode() {
      return this.projectLanguage === this.currentLanguage.code;
    },
  },
  methods: {
    async updateState(id, newState) {
      this.stateLoading = true;
      await this.$store.dispatch('updateStringState', { id: id, translated: newState === this.globals.TRANSLATION_STATE_TRANSLATED });
      this.stateLoading = false;
    },
  },
};
</script>