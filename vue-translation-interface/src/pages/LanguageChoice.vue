<template>
  <h3>Elektu la lingvon, al kiu vi volas traduki</h3>
  <div v-if="availableLanguages.length > 0" class="row">
    <div
      class="col-6 col-sm-4 col-md-3 col-lx-2 py-2 vue-language-selector"
      v-for="language in availableLanguages"
      :key="language.code"
      :lang="language.code"
      :dir="language.direction"
    >
      <router-link
        :to="{ name: 'translateLanguage', params: { lang: language.code } }"
      >
        {{ language.name }}
      </router-link>
    </div>
  </div>
  <loading-spinner v-else></loading-spinner>
</template>

<style lang="scss" scoped>
.vue-language-selector {
  text-align: center;
  a {
    background: $title-color;
    color: white;
    padding: 10px;
    display: block;
    font-size: 1.5rem;
    border-radius: 6px;
    font-weight: bold;

    &:hover {
      background: $header-bgcolor;
      color: $title-dark-color;
      text-decoration: none;
    }
  }
}
</style>