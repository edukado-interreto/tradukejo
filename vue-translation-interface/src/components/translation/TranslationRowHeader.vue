<template>
  <header class="row">
    <div class="col-6">
      <strong>
        <a :href="'#' + string.id" class="string-anchor" title="Rekta ligilo al ĉi tiu ĉeno">#{{ string.name }}</a>
      </strong>
      –
      <language-change-dropdown :string="string"></language-change-dropdown>
      <online-translator-links
        :language-from="string.original_text.language"
        :language-to="currentLanguage"
        :texts="string.original_text.raw_text"
      ></online-translator-links>
    </div>
    <div class="col-6 text-right translation-state-bar">
      <template v-if="!stateLoading">
        <button v-if="editMode" @click="deleteString(string.id)" class="btn btn-danger btn-sm">Forigi</button>
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
  methods: {
    async updateState(id, newState) {
      this.stateLoading = true;
      await this.$store.dispatch('updateStringState', { id: id, translated: newState === this.globals.TRANSLATION_STATE_TRANSLATED });
      this.stateLoading = false;
    },
    deleteString(id) {
      if (confirm('Ĉu vi certe volas forigi ĉi tiun ĉenon?')) {
        this.$store.dispatch('deleteString', id);
      }
    }
  },
};
</script>

<style lang="scss" scoped>
.translation-state-bar a {
  font-size: .9rem;
  top: 1px;
  position: relative;
  margin-right: 9px;
}

.string-anchor {
  color: inherit;

  &:hover {
    text-decoration: none;
    color: #484848;
  }
}
</style>