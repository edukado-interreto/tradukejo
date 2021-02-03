<template>
  <div class="comments">
    <h5>Komentoj</h5>
    <article
      v-for="comment in comments"
      :key="comment.id">
      <blockquote :lang="language.code" :dir="language.direction">
        {{ comment.text }}
      </blockquote>

      <hr class="my-2" />

      {{ comment.create_date }}
      <template v-if="comment.author">
        –
        <a :href="comment.author.profile_url">{{
          comment.author.username
        }}</a>
      </template>
    </article>

    <form @submit.prevent="saveComment">
      <div class="form-group">
        <textarea
          rows="3"
          class="form-control"
          required
          :lang="language.code"
          :dir="language.direction"
          placeholder="Skribu vian komenton ĉi tie…"
          v-model.trim="enteredComment"
          :disabled="loading"
          ></textarea>
      </div>
      <div class="form-group">
        <button
          class="btn btn-primary"
          :class="{'can-submit': canSubmit}"
          :disabled="!canSubmit || loading"
          >
          <loading-spinner v-if="loading" inline white></loading-spinner>
          <template v-else>Aldoni komenton</template>
        </button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  emits: ['save'],
  props: ["comments", "language", "loading"],
  data() {
    return {
      enteredComment: ''
    }
  },
  computed: {
    canSubmit() {
      return (this.enteredComment != '');
    }
  },
  watch: {
    loading(newVal) {
      if (!newVal) {
        this.enteredComment = '';
      }
    }
  },
  methods: {
    saveComment() {
      this.$emit('save', this.enteredComment);
    }
  },
};
</script>

<style lang="scss" scoped>
form {
  margin-top: 1rem;
}

h5 {
  margin-top: .7rem;
  font-weight: bold;
  font-size: 1.2rem;
  color: rgb(81, 79, 78);
}

article {
  background: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-top: 1rem;
  padding: 0.6rem 0.8rem;

  blockquote {
    font-size: 1rem;
    margin-bottom: 0;
  }
}

textarea:invalid {
    box-shadow: none;
}
</style>