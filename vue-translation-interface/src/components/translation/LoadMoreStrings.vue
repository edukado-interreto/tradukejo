<template>
  <div v-if="!loading" class="text-center">
    <button class="btn btn-primary btn-lg" @click="loadMore">Ŝargi pli</button>
  </div>
  <loading-spinner v-else></loading-spinner>
</template>

<script>
export default {
  data() {
    return {
      loading: false,
    };
  },
  methods: {
    async loadMore() {
      this.loading = true;
      await this.$store.dispatch("loadMore", {
        dir: this.queryStringDir,
        q: this.queryStringQ,
        state: this.queryStringState,
        sort: this.queryStringSort,
      });
      this.loading = false;
    },
  },
};
</script>