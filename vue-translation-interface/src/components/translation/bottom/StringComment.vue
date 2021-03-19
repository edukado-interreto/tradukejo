<template>
  <article>
    <button
      v-if="canComment"
      @click="deleteThis"
      :disabled="beingDeleted"
      class="btn btn-sm btn-danger float-right mb-1"
    >
      <loading-spinner v-if="beingDeleted" inline small white></loading-spinner>
      <template v-else>{{ $t('delete') }}</template>
    </button>
    <blockquote :lang="language.code" :dir="language.direction">
      {{ comment.text }}
    </blockquote>

    <hr class="my-2" style="clear: right" />

    {{ comment.create_date }}
    <template v-if="comment.author">
      –
      <a :href="comment.author.profile_url">{{ comment.author.username }}</a>
    </template>
  </article>
</template>

<script>
export default {
  inject: ['deleteComment'],
  props: ["comment", "language"],
  data() {
    return {
      beingDeleted: false
    }
  },
  computed: {
    canComment() {
      return this.comment.author.id === this.userId || this.isAdmin;
    }
  },
  methods: {
    deleteThis() {
      if (confirm(this.$t('comments.delete_confirm'))) {
        this.beingDeleted = true;
        this.deleteComment(this.comment.id);
      }
    }
  }
};
</script>