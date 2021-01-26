<template>
  <div class="col-md-6 translation-widget">
    <template v-if="stringtext">
      <display-text :texts="stringtext.text" :pluralized="stringtext.pluralized"></display-text>
      <author-and-history
        :stringtext="stringtext"
      ></author-and-history>
    </template>
  </div>
</template>

<script>
import AuthorAndHistory from '../AuthorAndHistory';
import DisplayText from '../DisplayText';

export default {
  props: ['stringtext'],
  components: { AuthorAndHistory, DisplayText },
}
</script>