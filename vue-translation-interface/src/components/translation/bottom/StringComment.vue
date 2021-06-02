<template>
  <article>
    <loading-button
      v-if="canComment"
      class="btn btn-sm btn-danger float-right mb-1"
      @click="deleteThis"
      :loading="beingDeleted"
      >
      {{ $t('delete') }}
    </loading-button>
    <blockquote :lang="language.code" :dir="language.direction" v-html="formattedComment"></blockquote>

    <hr class="my-2" style="clear: right" />

    {{ comment.create_date }}
    <template v-if="comment.author">
      –
      <a :href="comment.author.profile_url">{{ comment.author.username }}</a>
    </template>
  </article>
</template>

<script>
import escape from 'escape-html';

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
    },
    formattedComment() {
      let text = escape(this.comment.text);
      text = text.replaceAll('\n', '<br>');
      const urlRegex = /(((https?:\/\/)|(www\.))[^\s]+)/g;
      text = text.replace(urlRegex, function (url) {
        let hyperlink = url;
        if (!hyperlink.match('^https?://')) {
          hyperlink = 'http://' + hyperlink;
        }
        return '<a href="' + hyperlink + '" target="_blank" rel="noopener noreferrer">' + url + '</a>'
      });
      return text;
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