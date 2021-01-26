<template>
  <div class="translation-author">
    {{ stringtext.last_change }}
    <template v-if="stringtext.translated_by">
      –
      <a :href="stringtext.translated_by.profile_url">{{ stringtext.translated_by.username }}</a>
    </template>
    <template v-if="stringtext.old_versions > 0">
      |
      <a href="#" @click.prevent>
        Historio ({{ stringtext.old_versions + 1 }} versioj)
      </a>
    </template>
  </div>
</template>

<script>
export default {
  props: ["stringtext"],
};
</script>