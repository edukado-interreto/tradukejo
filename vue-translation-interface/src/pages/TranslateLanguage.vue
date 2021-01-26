<template>
  <filter-bar></filter-bar>
  <navigation-bar></navigation-bar>
  <translation-zone
    v-if="!isLoading"
    :strings="strings"
    >
  </translation-zone>
  <loading-spinner v-else></loading-spinner>
</template>

<script>
import FilterBar from "../components/FilterBar";
import NavigationBar from "../components/NavigationBar";
import TranslationZone from "../components/TranslationZone";

export default {
  components: {
    FilterBar,
    NavigationBar,
    TranslationZone
  },
  data() {
    return {
      isLoading: false,
      currentDirectory: "",
      searchString: "",
      stateFilter: "",
      sort: "",
    };
  },
  computed: {
    paramLang() {
      return this.$route.params.lang;
    },
    strings() {
      return this.$store.getters.strings;
    }
  },
  watch: {
    paramLang(newValue) {
      this.setLanguage(newValue);
      this.fetchStrings();
    },
  },
  methods: {
    setLanguage(code) {
      this.$store.dispatch("setLanguage", code);
    },
    async fetchStrings() {
      this.isLoading = true;
      await this.$store.dispatch('fetchStrings', {
          dir: this.currentDirectory,
          q: this.searchString,
          state: this.stateFilter,
          sort: this.sort,
        });
      this.isLoading = false;
    },
  },
  created() {
    this.setLanguage(this.paramLang);
    this.fetchStrings();
  },
};
</script>
