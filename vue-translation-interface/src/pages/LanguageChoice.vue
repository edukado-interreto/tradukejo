<template>
  <h3>Elektu la lingvon, al kiu vi volas traduki</h3>
  <div class="row">
    <div
      class="col-6 col-sm-4 col-md-3 col-lx-2 vue-language-selector"
      v-for="language in availableLanguages"
      :key="language.pk"
      :lang="language.pk"
      :dir="language.fields.direction"
    >
      <router-link
        :to="{ name: 'translateLanguage', params: { lang: language.pk } }"
      >
        {{ language.fields.name }}
      </router-link>
    </div>
  </div>
</template>