<template>
  <div class="comments">
    <h5>{{ $t('comments.comments') }}</h5>
    <transition-group name="slide">
      <string-comment v-for="comment in comments" :key="comment.id" :comment="comment" :language="language" />
    </transition-group>

    <form @submit.prevent="saveComment">
      <div class="form-group">
        <textarea
          rows="3"
          class="form-control"
          required
          :lang="language.code"
          :dir="language.direction"
          :placeholder="$t('comments.write')"
          v-model.trim="enteredComment"
          :disabled="loading"
          ></textarea>
      </div>
      <div class="form-group">
        <loading-button
          class="btn btn-primary"
          :class="{'can-submit': canSubmit}"
          :disabled="!canSubmit"
          :loading="loading"
          >
          {{ $t('comments.add') }}
        </loading-button>
      </div>
    </form>
  </div>
</template>

<script>
import StringComment from './StringComment';

export default {
  emits: ['save', 'delete-comment'],
  props: ["comments", "language", "loading"],
  components: { StringComment },
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
    },
    deleteComment(id) {
      this.$emit('delete-comment', id);
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