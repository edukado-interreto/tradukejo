<template>
  <filter-bar></filter-bar>
  <navigation-bar></navigation-bar>
  <directories-list
    v-if="!directoriesLoading"
    :directories="directories"
  ></directories-list>
  <loading-spinner v-else-if="!isLoading"></loading-spinner>

  <loading-spinner v-if="isLoading"></loading-spinner>
  <translation-zone v-else :strings="strings">
  </translation-zone>
  <div
    v-if="strings.length === 0 && Object.keys(directories).length === 0 && !directoriesLoading"
    class="alert alert-info"
  >
    Neniu ĉeno estis trovita.
  </div>
</template>

<script>
import FilterBar from "../components/FilterBar";
import NavigationBar from "../components/NavigationBar";
import DirectoriesList from "../components/DirectoriesList";
import TranslationZone from "../components/translation/TranslationZone";

export default {
  components: {
    FilterBar,
    NavigationBar,
    DirectoriesList,
    TranslationZone,
  },
  data() {
    return {
      isLoading: false,
      directoriesLoading: false,
    };
  },
  computed: {
    paramLang() {
      return this.$route.params.lang;
    },
    strings() {
      return this.$store.getters.strings;
    },
    directories() {
      return this.$store.getters.directories;
    },
  },
  watch: {
    paramLang(newValue) {
      this.setLanguage(newValue);
      this.fetchStrings();
      this.fetchDirectories();
    },
    queryStringState() {
      this.fetchStrings();
      this.fetchDirectories();
    },
    queryStringSort() {
      this.fetchStrings();
    },
    queryStringDir() {
      this.fetchStrings();
      this.fetchDirectories();
    },
    queryStringQ() {
      this.fetchStrings();
      this.fetchDirectories();
    },
  },
  methods: {
    setLanguage(code) {
      this.$store.dispatch("setLanguage", code);
      if (!this.currentLanguage) {
        this.$router.push({ name: "languageChoice" });
      }
    },
    async fetchStrings() {
      this.isLoading = true;
      await this.$store.dispatch("fetchStrings", {
        dir: this.queryStringDir,
        q: this.queryStringQ,
        state: this.queryStringState,
        sort: this.queryStringSort,
      });
      this.isLoading = false;
    },
    async fetchDirectories() {
      this.directoriesLoading = true;
      await this.$store.dispatch("fetchDirectories", {
        dir: this.queryStringDir,
        q: this.queryStringQ,
        state: this.queryStringState,
      });
      this.directoriesLoading = false;
    },
    isAllowedToLeave() {
      const textareas = document.querySelectorAll("#app textarea");
      if (textareas.length > 0) {
        return window.confirm(
          "Vi havas nekonservitajn ŝanĝojn, ĉu vi certe volas eliri el ĉi tiu paĝo?"
        );
      }
      return true;
    },
    handlerClose(e) {
      if (!this.isAllowedToLeave()) {
      console.log('ici');
        e.preventDefault();
        e.returnValue = "";
        return;
      }
      console.log('la');
    },
  },
  created() {
    this.setLanguage(this.paramLang);
    this.fetchStrings();
    this.fetchDirectories();

    window.addEventListener("beforeunload", this.handlerClose);
  },
  beforeRouteUpdate() {
    return this.isAllowedToLeave();
  },
  beforeRouteLeave() {
    return this.isAllowedToLeave();
  },
};
</script>
