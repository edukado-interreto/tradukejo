<template>
  <div class="translation-author">
    {{ stringtext.last_change }}
    <template v-if="stringtext.translated_by">
      –
      <a :href="stringtext.translated_by.profile_url">{{
        stringtext.translated_by.username
      }}</a>
    </template>
    <template v-if="stringtext.old_versions > 0">
      |

      <a href="#" @click.prevent="toggleHistory">
        Historio ({{ stringtext.old_versions + 1 }} versioj)
      </a>

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
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue';
const StringHistory = defineAsyncComponent(() => import('./StringHistory'));

export default {
  props: ["stringtext"],
  components: { StringHistory },
  data() {
    return {
      showHistory: false,
      historyLoading: false,
      history: null,
    };
  },
  watch: {
    stringtext() {
      if (this.showHistory) {
        this.loadHistory();
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
    async loadHistory() {
      this.historyLoading = true;
      await this.postCsrf("/vue/get-history/", {
        trstringtext_id: this.stringtext.id,
      }).then((response) => {
        this.history = response.data;
      });
      this.historyLoading = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.translation-author {
  font-size: .9em;
  margin-top: .5rem;
  padding-top: .5rem;
  border-top: 1px solid rgba(200, 200, 200, .6);
}
</style>