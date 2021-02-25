<template>
  <transition name="slide">
    <div class="card" v-if="editing">
      <div class="card-body">
        <h5 class="card-title">Aldoni ĉenon</h5>
        <translate-form
          :path="queryStringDir"
          :error="error"
          :loading="loading"
          :new-string="true"
          @cancel="hideForm"
          @save-translation="saveString($event)"
        ></translate-form>
      </div>
    </div>
  </transition>

  <div class="text-center mb-4" v-if="!editing">
    <button class="btn btn-primary" @click="showForm" ref="translate">
      Aldoni ĉenon
    </button>
  </div>
</template>

<script>
import TranslateForm from "./translatingTo/TranslateForm";

export default {
  components: { TranslateForm },
  data() {
    return {
      editing: false,
      loading: false,
      error: null,
    };
  },
  methods: {
    showForm() {
      this.editing = true;
    },
    hideForm() {
      this.editing = false;
    },
    async saveString(data) {
      this.loading = true;
      this.error = null;

      await this.$store
        .dispatch("addString", data)
        .then((response) => {
          this.hideForm();
          this.fetchDirectoriesTree();

          setTimeout(() => {
            if (response.path != this.queryStringDir) {
              this.$router.push(this.translateLink({ dir: response.path }));
              return;
            }
          }, 200); // Wait until end of transition
        })
        .catch((e) => {
          console.log(e);
          this.error = e.message;
        });

      this.loading = false;
    },
  },
  provide() {
    return {
      stringId: "add",
    };
  },
};
</script>

<style scoped>
.card {
  max-width: 800px;
  margin: auto;
  margin-bottom: 1rem;
}

.card-body {
  padding-bottom: 0;
}
</style>