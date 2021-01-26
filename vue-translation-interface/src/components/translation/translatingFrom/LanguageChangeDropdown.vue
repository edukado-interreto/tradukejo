<template>
  <span class="dropdown">
    <a
      class="dropdown-toggle"
      href="#"
      type="button"
      :id="'dropdownLanguageButton' + string.id"
      data-toggle="dropdown"
      aria-haspopup="true"
      aria-expanded="false"
      >{{ currentLanguage.fields.name }}</a
    >
    <div
      class="dropdown-menu dropdown-language-menu"
      :aria-labelledby="'dropdownLanguageButton' + string.id"
    >
      <a
        v-for="(language, code) in string.translated_languages"
        :key="code"
        class="dropdown-item"
        href="#"
        @click.prevent="loadLanguageFrom(code)"
        >{{ language }}</a
      >
    </div>
  </span>
</template>

<script>
export default {
  inject: ['loadLanguageFrom'],
  props: ["string"],
}
</script>