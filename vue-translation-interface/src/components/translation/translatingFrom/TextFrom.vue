<template>
  <div class="col-md-6 original-string">
    <display-text
      :texts="stringtext.text"
      :pluralized="stringtext.pluralized"
      :language="stringtext.language"
      :is-text-from="true"
      ></display-text>
    <div v-if="context" class="context">
      <i class="fas fa-question-circle" :title="$t('translate.context')"></i> {{ context }}
    </div>
    <string-info
      :stringtext="stringtext"
      :is-translation="false"
    ></string-info>
  </div>
</template>

<script>
import StringInfo from '../bottom/StringInfo';
import DisplayText from '../DisplayText';

export default {
  props: ['stringtext', 'context'],
  components: { StringInfo, DisplayText },
}
</script>