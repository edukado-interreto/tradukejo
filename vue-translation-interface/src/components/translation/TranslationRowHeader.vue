<template>
  <header class="row mb-2">
    <div class="col-6">
      <strong>
        <a :href="'#' + string.id" class="string-anchor" :title="$t('translate.link')" ref="title">#{{ string.name }}</a>
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
        <button v-if="editMode" @click="deleteString(string.id)" class="btn btn-danger btn-sm">{{ $t('delete') }}</button>
        <template v-else>
          <a
            v-if="string.state === globals.TRANSLATION_STATE_TRANSLATED"
            href="#"
            @click.prevent="updateState(string.translated_text.id, globals.TRANSLATION_STATE_OUTDATED)"
            >{{ $t('translate.mark_outdated') }}</a
          >
          <a
            v-else-if="string.state === globals.TRANSLATION_STATE_OUTDATED"
            href="#"
            @click.prevent="updateState(string.translated_text.id, globals.TRANSLATION_STATE_TRANSLATED)"
            >{{ $t('translate.mark_translated') }}</a
          >

          <span
            v-if="string.state === globals.TRANSLATION_STATE_TRANSLATED"
            class="badge badge-success"
            >{{ $t('translate.translated') }}</span
          >
          <span
            v-else-if="string.state === globals.TRANSLATION_STATE_OUTDATED"
            class="badge badge-warning"
            >{{ $t('translate.outdated') }}</span
          >
          <span v-else class="badge badge-danger">{{ $t('translate.untranslated') }}</span>
        </template>
      </template>
      <loading-spinner v-else inline></loading-spinner>
    </div>
  </header>
</template>

<script>
import LanguageChangeDropdown from "./translatingFrom/LanguageChangeDropdown";
import OnlineTranslatorLinks from "./translatingFrom/OnlineTranslatorLinks";
import Mark from 'mark.js';

export default {
  components: { LanguageChangeDropdown, OnlineTranslatorLinks },
  props: ["string"],
  data() {
    return {
      stateLoading: false,
    };
  },
  computed: {
    stringName() {
      let name = this.escapeHTML(this.string.name);
      if (this.queryStringQ) {
        const search = this.escapeHTML(this.queryStringQ);
        name = name.replace(search, `<mark>${search}</mark>`);
      }
      return '#' + name;
    }
  },
  methods: {
    async updateState(id, newState) {
      this.stateLoading = true;
      await this.$store.dispatch('updateStringState', { id: id, translated: newState === this.globals.TRANSLATION_STATE_TRANSLATED });
      this.stateLoading = false;
      if (this.queryStringState !== this.globals.STATE_FILTER_ALL) {
        this.fetchDirectoriesTree();
      }
    },
    async deleteString(id) {
      if (confirm('Ĉu vi certe volas forigi ĉi tiun ĉenon?')) {
        await this.$store.dispatch('deleteString', id);
        this.fetchDirectoriesTree();
      }
    }
  },
  mounted() {
    if (this.queryStringQ) {
      const context = this.$refs.title;
      const instance = new Mark(context);
      instance.mark(this.queryStringQ, {
        separateWordSearch: false,
        diacritics: false
      });
    }
  }
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