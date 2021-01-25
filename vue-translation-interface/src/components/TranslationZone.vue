<template>
  <translation-row v-for="string in strings" :key="string.id" :string="string"></translation-row>
</template>

<script>
import TranslationRow from './translation/TranslationRow';

export default {
  components: {
    TranslationRow,
  },
  props: ['strings']
};
</script>
