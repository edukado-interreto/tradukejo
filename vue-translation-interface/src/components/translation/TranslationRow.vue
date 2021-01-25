<template>
  <div
    class="translation-row"
    :class="translationRowClasses"
  >
    <div class="row">
      <div class="col-6">
        <strong title="Titolo de la ĉeno, ne traduku ĝin"
          >#{{ string.name }}</strong
        >
        –
      </div>
      <div class="col-6 text-right translation-state-bar"></div>
    </div>
    <div
      class="row mt-1{% if str.state == TRANSLATION_STATE_UNTRANSLATED %} d-flex align-items-center{% endif %}"
    >
      <div class="col-md-6 original-string">
        {{ string.original_text.text }}
      </div>
      <div class="col-md-6 translation-widget">
        {{ string.translated_text.text }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['string'],
  computed: {
    translationRowClasses() {
      return {
        translated: this.string.state === this.globals.TRANSLATION_STATE_TRANSLATED,
        outdated: this.string.state === this.globals.TRANSLATION_STATE_OUTDATED,
        untranslated: this.string.state === this.globals.TRANSLATION_STATE_UNTRANSLATED,
      };
    }
  }
}
</script>