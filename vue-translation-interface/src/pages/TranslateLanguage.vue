<template>
  <filter-bar></filter-bar>
  <navigation-bar></navigation-bar>

  <div class="row">
    <div class="col-12 col-lg-3 col-xl-2" v-if="!noDirectories">
      <div class="card">
        <div class="card-body">
          <loading-spinner v-if="directoriesTreeLoading"></loading-spinner>
          <directories-tree v-else :tree="directoriesTree"></directories-tree>
        </div>
      </div>
    </div>
    <div class="col">
      <directories-list
        v-if="!directoriesTreeLoading"
        :directories="directories"
      ></directories-list>
      <loading-spinner v-if="isLoading"></loading-spinner>
      <translation-zone v-else :strings="strings">
      </translation-zone>
      <div
        v-if="strings.length === 0 && !isLoading && !directoriesTreeLoading && Object.keys(directories).length === 0"
        class="alert alert-info"
      >
        Neniu ĉeno estis trovita.
      </div>
    </div>
  </div>
</template>

<script>
import FilterBar from "../components/FilterBar";
import NavigationBar from "../components/NavigationBar";
import DirectoriesList from "../components/DirectoriesList";
import DirectoriesTree from "../components/DirectoriesTree";
import TranslationZone from "../components/translation/TranslationZone";

export default {
  components: {
    FilterBar,
    NavigationBar,
    DirectoriesList,
    DirectoriesTree,
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
    directoriesTree() {
      return this.$store.getters.directoriesTree;
    },
    directories() {
      let currentDir = this.directoriesTree[""];

      if (this.queryStringDir != '') {
        const directories = this.queryStringDir.split('/');
        let notFound = false;
        directories.forEach((d) => {
          if (d in currentDir.children) {
            currentDir = currentDir.children[d];
          }
          else {
            notFound = true;
          }
        });
        if (notFound) {
          return {};
        }
      }

      return currentDir.children;
    },
    directoriesTreeLoading() {
      return this.$store.getters.directoriesTreeLoading;
    },
    noDirectories() {
      return this.directoriesTreeLoading || Object.keys(this.directoriesTree[""].children).length === 0;
    }
  },
  watch: {
    paramLang(newValue) {
      this.setLanguage(newValue);
      this.fetchStrings();
      this.fetchDirectoriesTree();
    },
    queryStringState() {
      this.fetchStrings();
      this.fetchDirectoriesTree();
    },
    queryStringSort() {
      this.fetchStrings();
    },
    queryStringDir() {
      this.fetchStrings();
    },
    queryStringQ() {
      this.fetchStrings();
      this.fetchDirectoriesTree();
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
        chosen_string: this.chosenStringId,
      });
      this.isLoading = false;
    },
    isAllowedToLeave() {
      const saveButtons = document.querySelectorAll("#app .can-submit");
      if (saveButtons.length > 0) {
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
    this.fetchDirectoriesTree();

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
