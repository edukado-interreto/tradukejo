<template>
  <span class="online-translators-links" v-if="languageFrom.code !== languageTo.code">
    <a v-if="languageFrom.google && languageTo.google" :href="googleLink" target="_blank" title="Traduki per Google">
      <img :src="imgURL + '/icons/google.png'" alt="Traduki per Google">
    </a>
    <a v-if="languageFrom.yandex && languageTo.yandex" :href="yandexLink" target="_blank" title="Traduki per Yandex">
      <img :src="imgURL + '/icons/yandex.png'" alt="Traduki per Yandex">
    </a>
    <a v-if="languageFrom.deepl && languageTo.deepl" :href="deeplLink" target="_blank" title="Traduki per DeepL">
      <img :src="imgURL + '/icons/deepl.svg'" alt="Traduki per DeepL">
    </a>
  </span>
</template>

<script>
export default {
  props: ["languageFrom", "languageTo", "texts"],
  computed: {
    googleLink() {
      return `https://translate.google.com/?sl=${this.languageFrom.code}&tl=${this.languageTo.code}&text=${this.firstText}`;
    },
    yandexLink() {
      return `https://translate.yandex.ru/?lang=${this.languageFrom.code}-${this.languageTo.code}&text=${this.firstText}`;
    },
    deeplLink() {
      return `https://www.deepl.com/translator#${this.languageFrom.code}/${this.languageTo.code}/${this.firstText}`;
    },
    firstText() {
      return encodeURI(this.texts[Object.keys(this.texts)[0]]);
    }
  },
}
</script>

<style lang="scss" scoped>
.online-translators-links {
  margin-left: 0.3rem;

  img {
    height: 1rem;
  }
  a {
    margin-left: 0.25rem;
  }
}
</style>