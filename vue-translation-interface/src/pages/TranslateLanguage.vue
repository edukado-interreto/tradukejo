<template>
  <filter-bar></filter-bar>
  <navigation-bar></navigation-bar>
  <translation-zone
    :strings="trstrings"
    >
  </translation-zone>
</template>

<script>
import axios from "axios";
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
      currentDirectory: "",
      searchString: "",
      stateFilter: "",
      sort: "",
      trstrings: [],
    };
  },
  computed: {
    paramLang() {
      return this.$route.params.lang;
    },
    currentLanguage() {
      return this.$store.getters.currentLanguage;
    },
  },
  watch: {
    paramLang(newValue) {
      this.setLanguage(newValue);
    },
  },
  methods: {
    setLanguage(code) {
      this.$store.dispatch("setLanguage", code);
    },
    async fetchStrings() {
      await axios
        .post(`/vue/get-strings/${this.projectId}/${this.currentLanguage.pk}/`, {
          dir: this.currentDirectory,
          q: this.searchString,
          state: this.stateFilter,
          sort: this.sort,
        })
        .then((response) => {
          this.trstrings = response.data.strings;
        })
        .catch(function (error) {
          console.log(error);
        });
    },
  },
  created() {
    this.setLanguage(this.paramLang);
    this.fetchStrings();
  },
};
</script>
