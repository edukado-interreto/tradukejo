const mixins = {
  computed: {
    currentLanguage() {
      return this.$store.getters.currentLanguage;
    },
    editMode() {
      return this.projectLanguage === this.currentLanguage.code;
    },
    queryStringState() {
      if (this.currentLanguage !== null && this.editMode) {
        return '';
      }
      return this.$route.query.state || '';
    },
    queryStringDir() {
      return this.$route.query.dir || '';
    },
    queryStringSort() {
      return this.$route.query.sort || '';
    },
    queryStringQ() {
      return this.$route.query.q || '';
    },
    chosenStringId() { // The chosen string ID is the anchor at the end of the URL
      if (this.$route.hash) {
        return parseInt(this.$route.hash.substring(1)); // Remove first #
      }
      return null;
    }
  },
  methods: {
    translateLink(parameters) {
      const obj = {
        name: 'translateLanguage',
        params: {
          lang: parameters.lang || this.currentLanguage.code
        },
        query: { }
      };

      const possibleParameters = ['dir', 'state', 'sort', 'q'];
      possibleParameters.forEach((p) => {
        if (p in parameters) {
          if (parameters[p]) {
            obj.query[p] = parameters[p];
          }
        }
        else if (this.$route.query[p]) {
          obj.query[p] = this.$route.query[p];
        }
      });

      if (this.projectLanguage === obj.params.lang) { // No state filter for the source language
        delete obj.query.state;
      }
      console.log('mdr ' + obj.params.lang);

      return obj;
    },
    async fetchDirectoriesTree() {
      await this.$store.dispatch("fetchDirectoriesTree", {
        q: this.queryStringQ,
        state: this.queryStringState,
      });
    },
  }
};

export default mixins;