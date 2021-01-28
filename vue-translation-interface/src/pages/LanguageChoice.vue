<template>
  <h3>Elektu la lingvon, al kiu vi volas traduki</h3>
  <div class="row">
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
</template>