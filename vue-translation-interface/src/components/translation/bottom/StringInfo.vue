<template>
  <div class="translation-author">
    {{ stringtext.last_change }}
    –
    <template v-if="stringtext.translated_by">
      <a :href="stringtext.translated_by.profile_url">{{
        stringtext.translated_by.username
      }}</a>
      |
    </template>
    <a href="#" @click.prevent="toggleComments" class="toggle" :class="{open: showComments}">
      {{ commentCount == 0 ? $t('comments.link') : $tc('comments.number', {n: commentCount}) }}
    </a>
    <template v-if="stringtext.old_versions > 0">
      |
      <a href="#" @click.prevent="toggleHistory" class="toggle" :class="{open: showHistory}">
        {{ $tc('history.versions', {n: stringtext.old_versions + 1}) }}<!--
      --></a>

      <loading-spinner
          small
          v-if="showHistory && historyLoading"
        ></loading-spinner>
      <transition name="slide">
        <string-history
          v-if="showHistory && !historyLoading"
          :history="history"
        ></string-history>
      </transition>
    </template>

    <loading-spinner
        small
        v-if="showComments && commentsLoading"
      ></loading-spinner>
    <transition name="slide">
      <comments-list
        v-if="showComments && !commentsLoading"
        :comments="comments"
        :language="stringtext.language"
        :loading="commentBeingSaved"
        @save="saveComment($event)"
      ></comments-list>
    </transition>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue';
const StringHistory = defineAsyncComponent(() => import('./StringHistory'));
const CommentsList = defineAsyncComponent(() => import('./CommentsList'));

export default {
  inject: ['rowIsSelected'],
  props: ["stringtext", "isTranslation"],
  components: { StringHistory, CommentsList },
  data() {
    return {
      showHistory: false,
      historyLoading: false,
      history: null,
      showComments: false,
      commentsLoading: false,
      comments: null,
      commentBeingSaved: false,
    };
  },
  watch: {
    stringtext() {
      if (this.showHistory) {
        this.loadHistory();
      }
      if (this.showComments) {
        this.loadComments();
      }
    }
  },
  computed: {
    commentCount() {
      if (this.comments === null) {
        return this.stringtext.comments;
      }
      else {
        return this.comments.length;
      }
    }
  },
  methods: {
    toggleHistory() {
      this.showHistory = !this.showHistory;

      if (this.showHistory && this.history === null) {
        this.loadHistory();
      }
    },
    toggleComments() {
      this.showComments = !this.showComments;

      if (this.showComments && this.comments === null && this.stringtext.comments > 0) {
        this.loadComments();
      }
    },
    async loadHistory() {
      this.historyLoading = true;
      await this.postCsrf("/vue/get-history/", {
        trstringtext_id: this.stringtext.id,
      }).then((response) => {
        this.history = response.data;
      });
      this.historyLoading = false;
    },
    async loadComments() {
      this.commentsLoading = true;
      await this.postCsrf("/vue/get-comments/", {
        trstringtext_id: this.stringtext.id,
      }).then((response) => {
        this.comments = response.data;
      });
      this.commentsLoading = false;
    },
    async saveComment(text) {
      this.commentBeingSaved = true;
      await this.postCsrf("/vue/save-comment/", {
        trstringtext_id: this.stringtext.id,
        text: text,
      }).then((response) => {
        if (this.comments === null) {
          this.comments = [response.data];
        } else {
          this.comments.push(response.data);
        }
      });
      this.commentBeingSaved = false;
    },
    async deleteComment(id) {
      await this.postCsrf("/vue/delete-comment/", {
        comment_id: id,
      }).then(response => {
        if (response.data.ok) {
          const index = this.comments.findIndex(el => el.id === id);
          this.comments.splice(index, 1);
        }
      }).catch(function (error) {
        console.log(error);
      });
    }
  },
  provide() {
    return {
      deleteComment: this.deleteComment
    }
  },
  mounted() {
    if (this.rowIsSelected && this.commentCount > 0 && !this.showComments && !(this.isTranslation && this.editMode)) {
      this.toggleComments();
    }
  }
};
</script>

<style lang="scss" scoped>
.translation-author {
  font-size: .9em;
  margin-top: .5rem;
  padding-top: .5rem;
  border-top: 1px solid rgba(200, 200, 200, .6);
}

.toggle::after {
  display: inline-block;
  margin-left: 0.35em;
  vertical-align: 0.255em;
  content: "";
  border-top: 0.3em solid;
  border-right: 0.3em solid transparent;
  border-bottom: 0;
  border-left: 0.3em solid transparent;
  transform: rotate(0);
  transition: transform .2s;
}

.toggle.open::after {
  transform: rotate(180deg);
}
</style>