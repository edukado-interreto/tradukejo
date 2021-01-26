import axios from "axios";

const mixins = {
  computed: {
    currentLanguage() {
      return this.$store.getters.currentLanguage;
    },
  },
  methods: {
    async postCsrf(url, data) {
      return await axios.post(url, data, {headers: {'X-CSRFToken': this.csrf}});
    }
  }
};

export default mixins;