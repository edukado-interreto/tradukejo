<template>
  <div class="col-md-6 original-string">
    <display-text :texts="stringtext.text" :pluralized="stringtext.pluralized"></display-text>
    <div v-if="context" class="context">
      <i class="fas fa-question-circle" title="Klarigoj pri la kunteksto de la ĉeno"></i> {{ context }}
    </div>
    <author-and-history
      :stringtext="stringtext"
    ></author-and-history>
  </div>
</template>

<script>
import AuthorAndHistory from '../AuthorAndHistory';
import DisplayText from '../DisplayText';

export default {
  props: ['stringtext', 'context'],
  components: { AuthorAndHistory, DisplayText },
}
</script>