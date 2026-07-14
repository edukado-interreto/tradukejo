<script setup lang="ts">
import { useGlobals } from "@/composables/useGlobals"

const {
  vueTranslationInterface: { imgURL },
} = useGlobals()

const props = defineProps<{
  languageFrom: Language
  languageTo: Language
  texts: TrStringText["raw_text"]
}>()

const firstText = computed(() => Object.values(props.texts)[0] as string)
const googleLink = computed(() => {
  return `https://translate.google.com/?sl=${props.languageFrom.code}&tl=${props.languageTo.code}&text=${firstText.value}`
})
const yandexLink = computed(() => {
  return `https://translate.yandex.ru/?lang=${props.languageFrom.code}-${props.languageTo.code}&text=${firstText.value}`
})
const deeplLink = computed(() => {
  return `https://www.deepl.com/translator#${props.languageFrom.code}/${props.languageTo.code}/${firstText.value.replaceAll("/", "\\%2F")}`
})
</script>

<template>
  <span class="online-translators-links" v-if="languageFrom.code !== languageTo.code">
    <a
      v-if="languageFrom.google && languageTo.google"
      :href="googleLink"
      target="_blank"
      :title="$t('translate.auto_translate', { name: 'Google' })"
    >
      <img
        :src="imgURL + '/icons/google.png'"
        :alt="$t('translate.auto_translate', { name: 'Google' })"
      />
    </a>
    <a
      v-if="languageFrom.yandex && languageTo.yandex"
      :href="yandexLink"
      target="_blank"
      :title="$t('translate.auto_translate', { name: 'Yandex' })"
    >
      <img
        :src="imgURL + '/icons/yandex.png'"
        :alt="$t('translate.auto_translate', { name: 'Yandex' })"
      />
    </a>
    <a
      v-if="languageFrom.deepl && languageTo.deepl"
      :href="deeplLink"
      target="_blank"
      :title="$t('translate.auto_translate', { name: 'DeepL' })"
    >
      <img
        :src="imgURL + '/icons/deepl.svg'"
        :alt="$t('translate.auto_translate', { name: 'DeepL' })"
      />
    </a>
  </span>
</template>

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
