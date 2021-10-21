<template>
  <span class="online-translators-links" v-if="languageFrom.code !== languageTo.code">
    <a v-if="languageFrom.google && languageTo.google" :href="googleLink" target="_blank" :title="$t('translate.auto_translate', {name: 'Google'})">
      <img :src="imgURL + '/icons/google.png'" :alt="$t('translate.auto_translate', {name: 'Google'})">
    </a>
    <a v-if="languageFrom.yandex && languageTo.yandex" :href="yandexLink" target="_blank" :title="$t('translate.auto_translate', {name: 'Yandex'})">
      <img :src="imgURL + '/icons/yandex.png'" :alt="$t('translate.auto_translate', {name: 'Yandex'})">
    </a>
    <a v-if="languageFrom.deepl && languageTo.deepl" :href="deeplLink" target="_blank" :title="$t('translate.auto_translate', {name: 'DeepL'})">
      <img :src="imgURL + '/icons/deepl.svg'" :alt="$t('translate.auto_translate', {name: 'DeepL'})">
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
      return `https://www.deepl.com/translator#${this.languageFrom.code}/${this.languageTo.code}/${this.firstText.replaceAll("/", "\\%2F")}`;
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